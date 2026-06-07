from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


EXCLUDED_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
}

GENERATED_DIR_PREFIXES = (
    "_v2_",
    "_project_source_audit",
)

PROTECTED_EXTERNAL_PREFIX = "external/PokerVisionFinalVersionNoSolver_snapshot/"

CURRENT_VERSION_HINTS = [
    "v2_42", "v2_43", "v2_44", "v2_45", "v2_46", "v2_47", "v2_48",
    "v2_49", "v2_50", "v2_51", "v2_52", "v2_53", "v2_54", "v2_55",
    "v2_56", "v2_57", "v2_58", "v2_59",
]

REFERENCE_SCAN_SUFFIXES = {".py", ".ps1", ".md", ".txt", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
MAX_REFERENCE_FILE_BYTES = 900_000
MAX_JSON_PARSE_BYTES = 8_000_000


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
        out[line[3:].strip().replace("\\", "/")] = line[:2]
    return out


def _rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def _should_skip(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return True
    if any(part in EXCLUDED_DIR_NAMES for part in rel.parts):
        return True
    if any(part.startswith(GENERATED_DIR_PREFIXES) for part in rel.parts):
        return True
    return False


def _json_validity(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {"json_parse_status": "missing", "json_top_type": None, "json_error": None}
    try:
        size = path.stat().st_size
    except OSError:
        size = 0
    if size > MAX_JSON_PARSE_BYTES:
        return {"json_parse_status": "skipped_large", "json_top_type": None, "json_error": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        top_type = type(data).__name__
        return {
            "json_parse_status": "ok",
            "json_top_type": top_type,
            "json_error": None,
            "top_level_keys_sample": list(data.keys())[:40] if isinstance(data, dict) else None,
            "list_len": len(data) if isinstance(data, list) else None,
        }
    except Exception as exc:
        return {
            "json_parse_status": "error",
            "json_top_type": None,
            "json_error": f"{type(exc).__name__}: {exc}",
        }


def _should_scan_reference_file(root: Path, path: Path) -> bool:
    if not path.is_file():
        return False
    if _should_skip(path, root):
        return False
    rel = _rel(path, root)
    if rel.startswith(PROTECTED_EXTERNAL_PREFIX):
        return False
    if rel.startswith("outputs/") or rel.startswith("output/"):
        return False
    if path.suffix.lower() not in REFERENCE_SCAN_SUFFIXES:
        return False
    try:
        if path.stat().st_size > MAX_REFERENCE_FILE_BYTES:
            return False
    except OSError:
        return False
    return True


def _reference_sources(root: Path) -> list[Path]:
    return sorted(
        [path for path in root.rglob("*") if _should_scan_reference_file(root, path)],
        key=lambda p: _rel(p, root).lower(),
    )


def _scan_references_for_jsons(root: Path, json_rels: list[str]) -> dict[str, list[dict[str, Any]]]:
    # Build basename/path needles and scan small source/test/tool/config files once.
    basename_to_targets: dict[str, list[str]] = defaultdict(list)
    full_needles: dict[str, str] = {}
    for rel in json_rels:
        name = Path(rel).name
        if name:
            basename_to_targets[name].append(rel)
        full_needles[rel] = rel
        full_needles[rel.replace("/", "\\")] = rel

    refs: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for source in _reference_sources(root):
        source_rel = _rel(source, root)
        try:
            text = source.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        matched_targets: set[str] = set()

        for needle, target_rel in full_needles.items():
            if needle in text:
                matched_targets.add(target_rel)

        # Basename matching is weaker, but useful for fixture names.
        for basename, targets in basename_to_targets.items():
            if basename in text:
                for target in targets:
                    matched_targets.add(target)

        for target in matched_targets:
            refs[target].append({"source": source_rel})

    return refs


def _group_for_json(rel: str, tracked: bool, refs: list[dict[str, Any]], valid: dict[str, Any]) -> tuple[str, list[str]]:
    low = rel.lower()
    reasons: list[str] = []

    if rel.startswith(PROTECTED_EXTERNAL_PREFIX):
        return "EXTERNAL_PROTECTED_KEEP", ["external snapshot protected"]

    if rel.startswith("outputs/") or rel.startswith("output/"):
        return "GENERATED_OUTPUT_DELETE_CANDIDATE", ["generated outputs are reproducible and not source truth"]

    if valid["json_parse_status"] == "error":
        reasons.append("json_parse_error")

    if rel.startswith("tests/fixtures/") or "/fixtures/" in rel:
        if any(hint in low for hint in CURRENT_VERSION_HINTS):
            reasons.append("version-current fixture path")
            return "FIXTURE_TRUTH_SOURCE_KEEP", reasons
        if refs:
            reasons.append("fixture referenced by project tests/tools")
            return "CURRENT_REFERENCED_KEEP", reasons
        reasons.append("fixture not referenced by bounded scan")
        return "FIXTURE_REVIEW", reasons

    if refs:
        reasons.append("json referenced by project source/test/tool")
        return "CURRENT_REFERENCED_KEEP", reasons

    if not tracked:
        reasons.append("untracked json")
        if any(token in low for token in ["audit", "probe", "tmp", "temp", "output", "report"]):
            reasons.append("untracked generated/probe/report-like json")
            return "GENERATED_OUTPUT_DELETE_CANDIDATE", reasons
        return "JSON_REVIEW", reasons

    if any(hint in low for hint in CURRENT_VERSION_HINTS):
        reasons.append("version-current json")
        return "JSON_REVIEW", reasons

    reasons.append("tracked but not referenced by bounded scan")
    return "ARCHIVE_CANDIDATE_REVIEW", reasons


def _folder_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    folders: dict[str, dict[str, Any]] = {}
    for row in rows:
        folder = str(Path(row["relpath"]).parent).replace("\\", "/")
        item = folders.setdefault(
            folder,
            {
                "folder": folder,
                "json_files": 0,
                "tracked": 0,
                "referenced": 0,
                "parse_error": 0,
                "group_counts": Counter(),
                "total_size_bytes": 0,
            },
        )
        item["json_files"] += 1
        item["tracked"] += int(row["git_tracked"])
        item["referenced"] += int(row["references_count"] > 0)
        item["parse_error"] += int(row["json_parse_status"] == "error")
        item["group_counts"][row["group"]] += 1
        item["total_size_bytes"] += row["size_bytes"] or 0

    out = []
    for item in folders.values():
        group_counts = dict(item["group_counts"])
        if group_counts.get("EXTERNAL_PROTECTED_KEEP"):
            hint = "EXTERNAL_PROTECTED_KEEP"
        elif group_counts.get("FIXTURE_TRUTH_SOURCE_KEEP") or group_counts.get("CURRENT_REFERENCED_KEEP"):
            hint = "KEEP_OR_REVIEW"
        elif group_counts.get("GENERATED_OUTPUT_DELETE_CANDIDATE") == item["json_files"]:
            hint = "GENERATED_OUTPUT_DELETE_CANDIDATE"
        elif group_counts.get("ARCHIVE_CANDIDATE_REVIEW"):
            hint = "ARCHIVE_REVIEW"
        else:
            hint = "REVIEW"
        out.append(
            {
                **{k: v for k, v in item.items() if k != "group_counts"},
                "group_counts": group_counts,
                "folder_hint": hint,
            }
        )
    out.sort(key=lambda r: (r["folder_hint"], r["folder"]))
    return out


def _build_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# V2.59 Fixture / JSON Trust Review")
    lines.append("")
    lines.append("## Summary")
    for key, value in report["summary"].items():
        lines.append(f"- **{key}**: `{value}`")

    lines.append("")
    lines.append("## Policy")
    lines.append("- This report does **not** delete JSON files.")
    lines.append("- `external/PokerVisionFinalVersionNoSolver_snapshot` is protected.")
    lines.append("- Fixture JSON used by current tests is treated as truth-source.")
    lines.append("- Generated `outputs/` JSON can be regenerated and is not source truth.")

    group_order = [
        "FIXTURE_TRUTH_SOURCE_KEEP",
        "CURRENT_REFERENCED_KEEP",
        "EXTERNAL_PROTECTED_KEEP",
        "FIXTURE_REVIEW",
        "JSON_REVIEW",
        "ARCHIVE_CANDIDATE_REVIEW",
        "GENERATED_OUTPUT_DELETE_CANDIDATE",
    ]

    for group in group_order:
        rows = [row for row in report["json_files"] if row["group"] == group]
        lines.append("")
        lines.append(f"## {group}")
        if not rows:
            lines.append("- none")
            continue
        for row in rows[:220]:
            lines.append(
                f"- `{row['relpath']}` tracked=`{row['git_tracked']}` status=`{row['git_status']}` "
                f"refs=`{row['references_count']}` parse=`{row['json_parse_status']}` "
                f"size=`{row['size_bytes']}` reasons=`{'; '.join(row['reasons'])}`"
            )
        if len(rows) > 220:
            lines.append(f"- ... `{len(rows) - 220}` more")

    lines.append("")
    lines.append("## JSON folder summary")
    for folder in report["json_folder_summary"][:260]:
        lines.append(
            f"- `{folder['folder']}` files=`{folder['json_files']}` tracked=`{folder['tracked']}` "
            f"referenced=`{folder['referenced']}` parse_error=`{folder['parse_error']}` "
            f"hint=`{folder['folder_hint']}` groups=`{folder['group_counts']}`"
        )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Review fixture/JSON trust and cleanup candidates.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--output-json", default="outputs/v2_59_fixture_json_trust_review.json")
    parser.add_argument("--output-md", default="outputs/v2_59_fixture_json_trust_review.md")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    tracked = _git_tracked(root)
    status_map = _git_status_map(root)

    json_paths: list[Path] = []
    for path in root.rglob("*.json"):
        if path.is_file() and not _should_skip(path, root):
            json_paths.append(path)
    json_paths.sort(key=lambda p: _rel(p, root).lower())

    json_rels = [_rel(path, root) for path in json_paths]
    refs_by_target = _scan_references_for_jsons(root, json_rels)

    rows: list[dict[str, Any]] = []
    for path, rel in zip(json_paths, json_rels):
        refs = refs_by_target.get(rel, [])
        valid = _json_validity(path)
        group, reasons = _group_for_json(rel, rel in tracked, refs, valid)

        rows.append(
            {
                "relpath": rel,
                "group": group,
                "reasons": reasons,
                "git_tracked": rel in tracked,
                "git_status": status_map.get(rel, ""),
                "size_bytes": path.stat().st_size,
                "references_count": len(refs),
                "references_sample": refs[:20],
                "json_parse_status": valid.get("json_parse_status"),
                "json_top_type": valid.get("json_top_type"),
                "json_error": valid.get("json_error"),
                "top_level_keys_sample": valid.get("top_level_keys_sample"),
                "list_len": valid.get("list_len"),
            }
        )

    group_counts = Counter(row["group"] for row in rows)
    folder_summary = _folder_summary(rows)

    summary = {
        "project_root": str(root),
        "json_files_total": len(rows),
        "json_folders_total": len(folder_summary),
        "git_tracked_json_total": sum(1 for row in rows if row["git_tracked"]),
        "referenced_json_total": sum(1 for row in rows if row["references_count"] > 0),
        "json_parse_ok_total": sum(1 for row in rows if row["json_parse_status"] == "ok"),
        "json_parse_error_total": sum(1 for row in rows if row["json_parse_status"] == "error"),
        "external_protected_json_total": group_counts.get("EXTERNAL_PROTECTED_KEEP", 0),
        "fixture_truth_source_keep_total": group_counts.get("FIXTURE_TRUTH_SOURCE_KEEP", 0),
        "current_referenced_keep_total": group_counts.get("CURRENT_REFERENCED_KEEP", 0),
        "fixture_review_total": group_counts.get("FIXTURE_REVIEW", 0),
        "json_review_total": group_counts.get("JSON_REVIEW", 0),
        "archive_candidate_review_total": group_counts.get("ARCHIVE_CANDIDATE_REVIEW", 0),
        "generated_output_delete_candidate_total": group_counts.get("GENERATED_OUTPUT_DELETE_CANDIDATE", 0),
        "group_counts": dict(group_counts),
    }

    report = {
        "schema": "v2_59_fixture_json_trust_review_v1",
        "summary": summary,
        "json_files": rows,
        "json_folder_summary": folder_summary,
    }

    output_json = root / args.output_json
    output_md = root / args.output_md
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    output_md.write_text(_build_markdown(report), encoding="utf-8")

    print("V2.59 FIXTURE JSON TRUST REVIEW")
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("-" * 100)
    print(f"output_json={output_json}")
    print(f"output_md={output_md}")
    ok = summary["json_files_total"] > 0
    print(f"V2.59_FIXTURE_JSON_TRUST_REVIEW_OK = {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
