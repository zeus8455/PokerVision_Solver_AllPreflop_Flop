from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


TEXT_SUFFIXES = {
    ".py", ".ps1", ".txt", ".md", ".json", ".jsonl", ".yaml", ".yml", ".csv", ".ini", ".cfg", ".toml"
}

REFERENCE_SCAN_SUFFIXES = {
    ".py", ".ps1", ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"
}

TEMP_PATTERNS = [
    r"^apply_.*\.ps1$",
    r"^repair_.*\.ps1$",
    r"^stage_.*\.ps1$",
    r"^fix_.*\.ps1$",
    r"^run_v2_.*\.ps1$",
    r"^collect_v2_.*\.ps1$",
    r"^_tmp_.*",
    r".*\.zip$",
    r".*_probe\.txt$",
    r".*_audit.*\.txt$",
]

PROTECTED_PREFIXES = (
    "external/PokerVisionFinalVersionNoSolver_snapshot/",
    "solver_preflop/",
)

REFERENCE_SCAN_EXCLUDED_PREFIXES = (
    ".git/",
    "__pycache__/",
    ".pytest_cache/",
    "outputs/",
    "output/",
    "external/",
    "_v2_",
)

REFERENCE_SCAN_INCLUDED_PREFIXES = (
    "solver_preflop/",
    "tools/",
    "tests/",
)

MAX_REFERENCE_FILE_BYTES = 700_000
MAX_REFERENCE_READ_CHARS = 250_000


def _run(cmd: list[str], *, cwd: Path, timeout: int = 60) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(cwd),
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except Exception as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": "", "error": str(exc)}


def _git_tracked(root: Path) -> set[str]:
    result = _run(["git", "ls-files"], cwd=root)
    if not result["ok"]:
        return set()
    return {line.strip().replace("\\", "/") for line in result["stdout"].splitlines() if line.strip()}


def _git_status_map(root: Path) -> dict[str, str]:
    result = _run(["git", "status", "--short"], cwd=root)
    out: dict[str, str] = {}
    if not result["ok"]:
        return out
    for line in result["stdout"].splitlines():
        if not line.strip() or len(line) < 4:
            continue
        status = line[:2]
        rel = line[3:].strip().replace("\\", "/")
        out[rel] = status
    return out


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 256), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_temp_like(rel: str) -> bool:
    name = Path(rel).name
    return any(re.match(pattern, name, re.I) or re.match(pattern, rel, re.I) for pattern in TEMP_PATTERNS)


def _read_preview(path: Path, max_chars: int = 1800) -> str:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return ""
    if not path.exists() or path.stat().st_size > MAX_REFERENCE_FILE_BYTES:
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    text = text.replace("\r\n", "\n")
    return text[:max_chars]


def _line_count(path: Path) -> int | None:
    if not path.exists() or path.suffix.lower() not in TEXT_SUFFIXES:
        return None
    if path.stat().st_size > MAX_REFERENCE_FILE_BYTES:
        return None
    try:
        return len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
    except Exception:
        return None


def _should_scan_reference_file(root: Path, path: Path) -> bool:
    if not path.is_file():
        return False
    rel = str(path.relative_to(root)).replace("\\", "/")
    if path.suffix.lower() not in REFERENCE_SCAN_SUFFIXES:
        return False
    if any(rel.startswith(prefix) for prefix in REFERENCE_SCAN_EXCLUDED_PREFIXES):
        return False
    if not any(rel.startswith(prefix) for prefix in REFERENCE_SCAN_INCLUDED_PREFIXES):
        return False
    try:
        if path.stat().st_size > MAX_REFERENCE_FILE_BYTES:
            return False
    except OSError:
        return False
    return True


def _scan_references(root: Path, target_rel: str) -> list[dict[str, Any]]:
    # Fast conservative text search. We only scan small source/test/tool files.
    # We do NOT scan external snapshot, outputs, generated audit folders, images, or large text dumps.
    refs: list[dict[str, Any]] = []
    target_name = Path(target_rel).name
    needles = [target_rel, target_rel.replace("/", "\\"), target_name]
    needles = [needle for needle in needles if needle]
    if not needles:
        return refs

    scanned = 0
    for path in root.rglob("*"):
        if not _should_scan_reference_file(root, path):
            continue
        rel = str(path.relative_to(root)).replace("\\", "/")
        if rel == target_rel:
            continue
        scanned += 1
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")[:MAX_REFERENCE_READ_CHARS]
        except Exception:
            continue
        matched = [needle for needle in needles if needle in text]
        if matched:
            refs.append({"source": rel, "matched": matched[:4]})
            if len(refs) >= 50:
                break

    return refs


def _decision(item: dict[str, Any], *, rel: str, tracked: bool, exists: bool, refs: list[dict[str, Any]]) -> dict[str, Any]:
    reasons = list(item.get("reasons") or [])
    blocked: list[str] = []
    approve_reasons: list[str] = []

    if rel.startswith(PROTECTED_PREFIXES):
        blocked.append("protected_prefix")
    if tracked:
        blocked.append("git_tracked")
    if refs:
        blocked.append("referenced_by_project_text_search")
    if not exists:
        approve_reasons.append("file_missing_already")

    if _is_temp_like(rel) and not tracked and not refs and exists:
        verdict = "APPROVE_DELETE_CANDIDATE"
        approve_reasons.append("untracked_temp_or_generated_artifact")
    elif not exists:
        verdict = "ALREADY_MISSING"
    elif blocked:
        verdict = "BLOCK_DELETE_REVIEW"
    else:
        verdict = "REVIEW_DELETE_CANDIDATE"

    return {
        "verdict": verdict,
        "blocked_by": blocked,
        "approve_reasons": approve_reasons,
        "original_reasons": reasons,
    }


def _build_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# V2.58 Delete Candidate Inspection")
    lines.append("")
    lines.append("## Summary")
    for key, value in report["summary"].items():
        lines.append(f"- **{key}**: `{value}`")

    lines.append("")
    lines.append("## Policy")
    lines.append("- This report does **not** delete anything.")
    lines.append("- `APPROVE_DELETE_CANDIDATE` still requires a separate deletion block.")
    lines.append("- Tracked/protected/referenced files are blocked from immediate deletion.")
    lines.append("- Reference scan is deliberately bounded to small project source/test/tool files.")

    for verdict in ["APPROVE_DELETE_CANDIDATE", "REVIEW_DELETE_CANDIDATE", "BLOCK_DELETE_REVIEW", "ALREADY_MISSING"]:
        rows = [row for row in report["candidates"] if row["decision"]["verdict"] == verdict]
        lines.append("")
        lines.append(f"## {verdict}")
        if not rows:
            lines.append("- none")
            continue
        for row in rows:
            decision = row["decision"]
            lines.append(
                f"- `{row['relpath']}` exists=`{row['exists']}` tracked=`{row['git_tracked']}` "
                f"status=`{row['git_status']}` size=`{row['size_bytes']}` refs=`{row['references_count']}` "
                f"blocked=`{decision['blocked_by']}` approve=`{decision['approve_reasons']}`"
            )
            if row.get("preview"):
                preview = row["preview"].replace("```", "` ` `")
                lines.append("  ```text")
                lines.append("  " + preview[:800].replace("\n", "\n  "))
                lines.append("  ```")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect V2.57 DELETE_CANDIDATE files without deleting anything.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--cleanup-json", default="outputs/v2_57_cleanup_review_report.json")
    parser.add_argument("--output-json", default="outputs/v2_58_delete_candidate_inspection.json")
    parser.add_argument("--output-md", default="outputs/v2_58_delete_candidate_inspection.md")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    cleanup_path = (root / args.cleanup_json).resolve()
    cleanup = _load_json(cleanup_path)

    tracked = _git_tracked(root)
    status_map = _git_status_map(root)

    raw_candidates = cleanup.get("groups", {}).get("DELETE_CANDIDATE", [])
    inspected: list[dict[str, Any]] = []

    print("V2.58 DELETE CANDIDATE INSPECTION")
    print(f"delete_candidates_total: {len(raw_candidates)}")

    for index, item in enumerate(raw_candidates, start=1):
        rel = item.get("relpath")
        if not rel:
            continue
        rel = str(rel).replace("\\", "/")
        print(f"[v2.58] inspect {index}/{len(raw_candidates)}: {rel}", flush=True)

        path = root / rel
        exists = path.exists()
        refs = _scan_references(root, rel) if exists else []
        tracked_flag = rel in tracked
        decision = _decision(item, rel=rel, tracked=tracked_flag, exists=exists, refs=refs)

        inspected.append(
            {
                "relpath": rel,
                "exists": exists,
                "git_tracked": tracked_flag,
                "git_status": status_map.get(rel, ""),
                "size_bytes": path.stat().st_size if exists and path.is_file() else None,
                "line_count": _line_count(path),
                "sha256": _sha256(path),
                "suffix": path.suffix.lower(),
                "category": item.get("category"),
                "original_cleanup_item": item,
                "references_count": len(refs),
                "references_sample": refs[:12],
                "preview": _read_preview(path),
                "decision": decision,
            }
        )

    verdict_counts: dict[str, int] = {}
    for row in inspected:
        verdict = row["decision"]["verdict"]
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1

    summary = {
        "project_root": str(root),
        "cleanup_json": str(cleanup_path),
        "delete_candidates_total": len(inspected),
        "verdict_counts": verdict_counts,
        "approve_delete_candidate_total": verdict_counts.get("APPROVE_DELETE_CANDIDATE", 0),
        "blocked_review_total": verdict_counts.get("BLOCK_DELETE_REVIEW", 0),
        "review_delete_candidate_total": verdict_counts.get("REVIEW_DELETE_CANDIDATE", 0),
        "already_missing_total": verdict_counts.get("ALREADY_MISSING", 0),
    }

    report = {
        "schema": "v2_58_delete_candidate_inspection_v1",
        "summary": summary,
        "candidates": inspected,
    }

    output_json = root / args.output_json
    output_md = root / args.output_md
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    output_md.write_text(_build_markdown(report), encoding="utf-8")

    print("-" * 100)
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("-" * 100)
    for row in inspected:
        print(
            f"{row['decision']['verdict']:28} tracked={row['git_tracked']} "
            f"refs={row['references_count']} size={row['size_bytes']} path={row['relpath']}"
        )
    print("-" * 100)
    print(f"output_json={output_json}")
    print(f"output_md={output_md}")

    ok = len(inspected) == len(raw_candidates)
    print(f"V2.58_DELETE_CANDIDATE_INSPECTION_OK = {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
