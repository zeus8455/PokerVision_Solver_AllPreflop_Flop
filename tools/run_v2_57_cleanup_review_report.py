from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


EXCLUDED_DIRS = {
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

CURRENT_VERSION_HINTS = [
    "v2_42", "v2_43", "v2_44", "v2_45", "v2_46", "v2_47", "v2_48",
    "v2_49", "v2_50", "v2_51", "v2_52", "v2_53", "v2_54", "v2_55", "v2_56", "v2_57",
]

CORE_KEEP_PREFIXES = (
    "solver_preflop/",
    "external/PokerVisionFinalVersionNoSolver_snapshot/",
)

PROTECTED_EXTERNAL_PREFIX = "external/PokerVisionFinalVersionNoSolver_snapshot/"

TEMP_NAME_PATTERNS = [
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

MODEL_SUFFIXES = {".pt", ".onnx", ".engine", ".weights"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
DATA_SUFFIXES = {".json", ".jsonl", ".txt", ".csv", ".yaml", ".yml"}


def _run(cmd: list[str], *, cwd: Path, timeout: int = 90) -> dict[str, Any]:
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
        return {"ok": False, "returncode": None, "error": str(exc), "stdout": "", "stderr": ""}


def _git_ls_files(root: Path) -> set[str]:
    result = _run(["git", "ls-files"], cwd=root, timeout=60)
    if not result["ok"]:
        return set()
    return {line.strip().replace("\\", "/") for line in result["stdout"].splitlines() if line.strip()}


def _git_status_short(root: Path) -> list[str]:
    result = _run(["git", "status", "--short"], cwd=root, timeout=60)
    if not result["ok"]:
        return []
    return [line.rstrip() for line in result["stdout"].splitlines() if line.strip()]


def _should_skip_walk(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return True
    parts = rel.parts
    if any(part in EXCLUDED_DIRS for part in parts):
        return True
    if any(part.startswith(GENERATED_DIR_PREFIXES) for part in parts):
        return True
    return False


def _rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def _is_temp_file(rel: str) -> bool:
    name = Path(rel).name
    return any(re.match(pattern, name, re.I) or re.match(pattern, rel, re.I) for pattern in TEMP_NAME_PATTERNS)


def _category(rel: str, suffix: str) -> str:
    if rel.startswith(PROTECTED_EXTERNAL_PREFIX):
        return "external_protected"
    if rel.startswith("solver_preflop/"):
        return "solver_core"
    if rel.startswith("tests/fixtures/") or "/fixtures/" in rel:
        return "fixtures"
    if rel.startswith("tests/"):
        return "tests"
    if rel.startswith("tools/"):
        return "tools"
    if rel.startswith("outputs/") or rel.startswith("output/"):
        return "generated_outputs"
    if _is_temp_file(rel):
        return "temp_scripts_or_archives"
    if suffix in MODEL_SUFFIXES:
        return "model_artifacts"
    if suffix in IMAGE_SUFFIXES:
        return "image_data"
    if suffix in DATA_SUFFIXES:
        return "data_files"
    return "other"


def _parse_py_summary(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    summary = {
        "syntax_ok": True,
        "syntax_error": None,
        "functions": [],
        "classes": [],
        "has_main": False,
        "uses_argparse": "argparse" in text,
        "uses_pytest": "pytest" in text,
        "literal_refs": [],
    }
    summary["literal_refs"] = re.findall(r"[\"']([^\"']+\.(?:json|png|jpg|jpeg|txt|py|pt|onnx|zip|yaml|yml))[\"']", text, flags=re.I)[:500]
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        summary["syntax_ok"] = False
        summary["syntax_error"] = f"{exc.__class__.__name__}: {exc}"
        return summary
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            summary["functions"].append(node.name)
        elif isinstance(node, ast.ClassDef):
            summary["classes"].append(node.name)
        elif isinstance(node, ast.If):
            dump = ast.dump(node.test)
            if "__name__" in dump and "__main__" in dump:
                summary["has_main"] = True
    return summary


def _build_reference_index(root: Path, py_files: list[Path]) -> dict[str, list[dict[str, Any]]]:
    refs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for src in py_files:
        rel_src = _rel(src, root)
        info = _parse_py_summary(src)
        for raw in info["literal_refs"]:
            if raw.startswith(("http://", "https://")):
                continue
            normalized = raw.replace("\\", "/")
            candidate_paths = [
                (src.parent / raw).resolve(),
                (root / raw).resolve(),
                (root / normalized).resolve(),
            ]
            matched = None
            for candidate in candidate_paths:
                if candidate.exists():
                    try:
                        matched = _rel(candidate, root)
                    except Exception:
                        matched = str(candidate)
                    break
            key = matched or normalized
            refs[key].append({"source": rel_src, "raw": raw, "exists": matched is not None})
    return refs


def _load_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _classify_file(
    *,
    rel: str,
    path: Path,
    category: str,
    tracked: bool,
    referenced_by: list[dict[str, Any]],
    dynamic_executed: bool,
    static_info: dict[str, Any] | None,
    merge_info: dict[str, Any],
) -> dict[str, Any]:
    suffix = path.suffix.lower()
    name = path.name
    reasons: list[str] = []
    group = "REVIEW"

    if category == "external_protected":
        group = "KEEP"
        reasons.append("external snapshot is protected; do not clean directly")
        if dynamic_executed:
            reasons.append("executed by current dynamic map")
        else:
            reasons.append("not executed by targeted dynamic map; may be live/runtime/model dependent")
    elif rel.startswith("solver_preflop/"):
        group = "KEEP"
        reasons.append("solver_preflop core source")
    elif rel in {
        "VERSION.md",
        "README.md",
        "pyproject.toml",
        "pytest.ini",
        ".gitignore",
    }:
        group = "KEEP"
        reasons.append("project metadata/config")
    elif rel.startswith("tools/run_v2_5") or rel.startswith("tests/test_v2_5"):
        group = "KEEP"
        reasons.append("current audit tooling/tests")
    elif category == "temp_scripts_or_archives":
        group = "DELETE_CANDIDATE" if not tracked else "ARCHIVE_CANDIDATE"
        reasons.append("temporary apply/repair/stage/probe/archive artifact")
    elif category == "generated_outputs":
        group = "DELETE_CANDIDATE"
        reasons.append("generated output")
    elif rel.startswith("tests/fixtures/"):
        if referenced_by or any(hint in rel.lower() for hint in CURRENT_VERSION_HINTS):
            group = "KEEP"
            reasons.append("fixture is referenced or version-current")
        else:
            group = "REVIEW"
            reasons.append("fixture is not referenced by scanned Python files")
    elif rel.startswith("tests/"):
        if any(hint in rel.lower() for hint in CURRENT_VERSION_HINTS):
            group = "KEEP"
            reasons.append("current/versioned test")
        elif referenced_by:
            group = "REVIEW"
            reasons.append("old test but referenced")
        else:
            group = "ARCHIVE_CANDIDATE"
            reasons.append("old/unreferenced test candidate")
    elif rel.startswith("tools/"):
        if name.startswith("run_v2_") and any(hint in rel.lower() for hint in CURRENT_VERSION_HINTS):
            group = "KEEP"
            reasons.append("current/versioned tool")
        elif referenced_by:
            group = "REVIEW"
            reasons.append("tool is referenced")
        else:
            group = "ARCHIVE_CANDIDATE"
            reasons.append("tool not referenced by scanned Python files")
    elif suffix in MODEL_SUFFIXES:
        group = "KEEP"
        reasons.append("model/weights artifact; do not delete automatically")
    elif suffix in IMAGE_SUFFIXES:
        group = "REVIEW"
        reasons.append("image/test data; requires manual dataset decision")
    elif suffix in DATA_SUFFIXES:
        if referenced_by:
            group = "KEEP"
            reasons.append("data file referenced by Python")
        else:
            group = "REVIEW"
            reasons.append("data file not referenced by scanned Python")

    if tracked:
        reasons.append("git tracked")
    else:
        reasons.append("untracked")

    if dynamic_executed:
        reasons.append("executed by dynamic map")

    if static_info and static_info.get("syntax_error"):
        reasons.append("syntax-error finding")

    return {
        "relpath": rel,
        "group": group,
        "category": category,
        "tracked": tracked,
        "dynamic_executed": dynamic_executed,
        "referenced_by_count": len(referenced_by),
        "referenced_by_sample": referenced_by[:8],
        "size_bytes": path.stat().st_size if path.exists() else None,
        "suffix": suffix,
        "reasons": reasons,
    }


def _build_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# V2.57 Cleanup Review Report")
    lines.append("")
    lines.append("## Summary")
    for key, value in report["summary"].items():
        lines.append(f"- **{key}**: `{value}`")

    lines.append("")
    lines.append("## Important policy")
    lines.append("- This report does **not** delete anything.")
    lines.append("- `external/PokerVisionFinalVersionNoSolver_snapshot` is treated as **KEEP / protected**.")
    lines.append("- `DELETE_CANDIDATE` still requires a separate reviewed deletion block and tests.")
    lines.append("- `ARCHIVE_CANDIDATE` means move later to archive/quarantine only after review.")

    for group in ["KEEP", "REVIEW", "ARCHIVE_CANDIDATE", "DELETE_CANDIDATE"]:
        rows = report["groups"].get(group, [])
        lines.append("")
        lines.append(f"## {group}")
        if not rows:
            lines.append("- none")
            continue
        for item in rows[:250]:
            reasons = "; ".join(item["reasons"][:5])
            lines.append(
                f"- `{item['relpath']}` — category=`{item['category']}` "
                f"tracked=`{item['tracked']}` executed=`{item['dynamic_executed']}` "
                f"refs=`{item['referenced_by_count']}` reasons=`{reasons}`"
            )
        if len(rows) > 250:
            lines.append(f"- ... `{len(rows) - 250}` more")

    lines.append("")
    lines.append("## External protected health")
    for item in report["external_protected_health"][:200]:
        reasons = "; ".join(item["reasons"][:5])
        lines.append(f"- `{item['relpath']}` — executed=`{item['dynamic_executed']}` reasons=`{reasons}`")

    lines.append("")
    lines.append("## Fixture / JSON folders")
    for row in report["json_folder_summary"][:200]:
        lines.append(
            f"- `{row['folder']}` files=`{row['json_files']}` tracked=`{row['tracked']}` "
            f"referenced=`{row['referenced']}` group_hint=`{row['group_hint']}`"
        )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build cleanup review grouping report without deleting files.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--merge-json", default="outputs/v2_56_project_logic_coverage_report_targeted.json")
    parser.add_argument("--output-json", default="outputs/v2_57_cleanup_review_report.json")
    parser.add_argument("--output-md", default="outputs/v2_57_cleanup_review_report.md")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    tracked_files = _git_ls_files(root)
    git_status = _git_status_short(root)
    merge_report = _load_optional_json(root / args.merge_json)

    dynamic_executed = set()
    for row in merge_report.get("tested_logic_chain", []):
        if row.get("relpath"):
            dynamic_executed.add(row["relpath"])

    static_files_by_rel = {}
    for section in [
        "tested_logic_chain",
        "untested_but_referenced",
        "dead_legacy_candidates",
        "runtime_only_files",
        "yolo_model_dependent_files",
        "safe_to_delete_candidates",
    ]:
        for row in merge_report.get(section, []):
            if row.get("relpath"):
                static_files_by_rel.setdefault(row["relpath"], row)

    all_files: list[Path] = []
    py_files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if _should_skip_walk(path, root):
            continue
        rel = _rel(path, root)
        all_files.append(path)
        if path.suffix.lower() == ".py":
            py_files.append(path)

    refs = _build_reference_index(root, py_files)

    classified: list[dict[str, Any]] = []
    for path in sorted(all_files, key=lambda p: _rel(p, root).lower()):
        rel = _rel(path, root)
        suffix = path.suffix.lower()
        category = _category(rel, suffix)
        info = None
        if suffix == ".py":
            parsed = _parse_py_summary(path)
            info = {"syntax_error": parsed.get("syntax_error")}
        item = _classify_file(
            rel=rel,
            path=path,
            category=category,
            tracked=rel in tracked_files,
            referenced_by=refs.get(rel, []),
            dynamic_executed=rel in dynamic_executed,
            static_info=info,
            merge_info=merge_report,
        )
        classified.append(item)

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in classified:
        groups[item["group"]].append(item)

    json_folders: dict[str, dict[str, Any]] = {}
    for item in classified:
        if item["suffix"] != ".json":
            continue
        folder = str(Path(item["relpath"]).parent).replace("\\", "/")
        row = json_folders.setdefault(folder, {"folder": folder, "json_files": 0, "tracked": 0, "referenced": 0, "group_counts": Counter()})
        row["json_files"] += 1
        row["tracked"] += int(bool(item["tracked"]))
        row["referenced"] += int(item["referenced_by_count"] > 0)
        row["group_counts"][item["group"]] += 1

    json_folder_summary = []
    for row in json_folders.values():
        group_counts = dict(row["group_counts"])
        if group_counts.get("KEEP", 0):
            hint = "KEEP_OR_REVIEW"
        elif group_counts.get("DELETE_CANDIDATE", 0) == row["json_files"]:
            hint = "DELETE_CANDIDATE"
        elif group_counts.get("ARCHIVE_CANDIDATE", 0):
            hint = "ARCHIVE_REVIEW"
        else:
            hint = "REVIEW"
        json_folder_summary.append(
            {
                "folder": row["folder"],
                "json_files": row["json_files"],
                "tracked": row["tracked"],
                "referenced": row["referenced"],
                "group_counts": group_counts,
                "group_hint": hint,
            }
        )
    json_folder_summary.sort(key=lambda r: (r["group_hint"], r["folder"]))

    external_health = [item for item in classified if item["category"] == "external_protected"]

    summary = {
        "project_root": str(root),
        "files_scanned": len(classified),
        "git_tracked_files": len(tracked_files),
        "git_status_entries": len(git_status),
        "dynamic_executed_files_from_merge": len(dynamic_executed),
        "keep_total": len(groups.get("KEEP", [])),
        "review_total": len(groups.get("REVIEW", [])),
        "archive_candidate_total": len(groups.get("ARCHIVE_CANDIDATE", [])),
        "delete_candidate_total": len(groups.get("DELETE_CANDIDATE", [])),
        "external_protected_total": len(external_health),
        "json_folders_total": len(json_folder_summary),
    }

    report = {
        "schema": "v2_57_cleanup_review_report_v1",
        "summary": summary,
        "git_status": git_status,
        "groups": {key: rows for key, rows in sorted(groups.items())},
        "external_protected_health": external_health,
        "json_folder_summary": json_folder_summary,
    }

    output_json = root / args.output_json
    output_md = root / args.output_md
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    output_md.write_text(_build_markdown(report), encoding="utf-8")

    print("V2.57 CLEANUP REVIEW REPORT")
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("-" * 100)
    print(f"output_json={output_json}")
    print(f"output_md={output_md}")

    ok = summary["files_scanned"] > 0 and summary["external_protected_total"] > 0
    print(f"V2.57_CLEANUP_REVIEW_REPORT_OK = {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
