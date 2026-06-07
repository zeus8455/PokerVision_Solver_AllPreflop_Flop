from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CURRENT_TEST_HINTS = [
    "v2_42", "v2_43", "v2_44", "v2_45", "v2_46", "v2_47", "v2_48",
    "v2_49", "v2_50", "v2_51", "v2_52", "v2_53", "v2_54", "v2_55", "v2_56",
]

YOLO_HINTS = [
    "yolo", "ultralytics", "cv2", "opencv", "model_path", "weights",
    "detector", "predict(", "best.pt", "onnx",
]

RUNTIME_HINTS = [
    "runtime", "v11_stage1_runtime", "action_runtime", "trigger_ui", "click", "autoclick",
]

SOLVER_HINTS = [
    "solver_preflop", "spot_classifier", "range_engine", "decision_engine",
    "clear_json_adapter", "contracts",
]


def _run(cmd: list[str], *, cwd: Path, timeout: int = 120, keep_full_stdout: bool = False) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(cwd),
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        result = {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "cmd": cmd,
            "stdout_tail": completed.stdout[-6000:],
            "stderr_tail": completed.stderr[-6000:],
        }
        if keep_full_stdout:
            result["stdout"] = completed.stdout
        return result
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return {
            "ok": False,
            "returncode": None,
            "cmd": cmd,
            "error": f"timeout after {timeout}s",
            "stdout_tail": stdout[-6000:],
            "stderr_tail": stderr[-6000:],
            "stdout": stdout if keep_full_stdout else "",
        }
    except Exception as exc:
        return {
            "ok": False,
            "returncode": None,
            "cmd": cmd,
            "error": str(exc),
        }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def _git_tracked(root: Path) -> set[str]:
    # Do not use stdout_tail here: git ls-files can exceed 6000 chars.
    result = _run(["git", "ls-files"], cwd=root, timeout=60, keep_full_stdout=True)
    if not result.get("ok"):
        return set()
    return {
        line.strip().replace("\\", "/")
        for line in (result.get("stdout") or "").splitlines()
        if line.strip()
    }


def _pytest_collect(root: Path, timeout: int = 120) -> dict[str, Any]:
    result = _run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=root,
        timeout=timeout,
        keep_full_stdout=True,
    )
    stdout = result.get("stdout", "") or result.get("stdout_tail", "") or ""
    items = [
        line.strip()
        for line in stdout.splitlines()
        if line.strip() and ("::" in line or line.strip().endswith(".py"))
    ]
    result["collected_items_estimate"] = len(items)
    result["items_sample"] = items[:300]
    result.pop("stdout", None)
    return result


def _ensure_static_report(root: Path, output_json: Path, output_md: Path) -> dict[str, Any]:
    cmd = [
        sys.executable,
        "tools/run_v2_54_project_static_logic_map.py",
        "--project-root",
        str(root),
        "--output-json",
        str(output_json),
        "--output-md",
        str(output_md),
        "--skip-pytest-collect",
    ]
    return _run(cmd, cwd=root, timeout=180)


def _ensure_dynamic_report(
    root: Path,
    output_json: Path,
    output_md: Path,
    *,
    profile: str,
    pytest_targets: list[str],
    skip_tools: bool,
    skip_pytest: bool,
) -> dict[str, Any]:
    cmd = [
        sys.executable,
        "tools/run_v2_55_project_dynamic_execution_map.py",
        "--project-root",
        str(root),
        "--output-json",
        str(output_json),
        "--output-md",
        str(output_md),
        "--profile",
        profile,
    ]
    if skip_tools:
        cmd.append("--skip-tools")
    if skip_pytest:
        cmd.append("--skip-pytest")
    for target in pytest_targets:
        cmd.extend(["--pytest-target", target])
    if profile == "smoke":
        cmd.extend(["--skip-tools", "--skip-pytest", "--self-smoke"])
    return _run(cmd, cwd=root, timeout=240)


def _read_text_safe(path: Path, max_chars: int = 200_000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return text[:max_chars]
    except Exception:
        return ""


def _file_by_rel(static_files: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["relpath"]: row for row in static_files}


def _is_current_test(rel: str) -> bool:
    low = rel.lower()
    return rel.startswith("tests/") and any(hint in low for hint in CURRENT_TEST_HINTS)


def _has_any(text: str, hints: list[str]) -> bool:
    low = text.lower()
    return any(hint.lower() in low for hint in hints)


def _path_category(rel: str) -> str:
    if rel.startswith("solver_preflop/"):
        return "solver_preflop"
    if rel.startswith("tests/"):
        return "tests"
    if rel.startswith("tools/"):
        return "tools"
    if rel.startswith("external/PokerVisionFinalVersionNoSolver_snapshot/") and "/runtime/" in rel:
        return "external_runtime"
    if rel.startswith("external/PokerVisionFinalVersionNoSolver_snapshot/") and "/logic/" in rel:
        return "external_logic"
    if rel.startswith("external/PokerVisionFinalVersionNoSolver_snapshot/"):
        return "external_snapshot_other"
    return "other"


def _extract_literal_path_refs(root: Path, rel: str) -> list[dict[str, Any]]:
    path = root / rel
    text = _read_text_safe(path)
    refs: list[dict[str, Any]] = []
    candidates = re.findall(r"[\"']([^\"']+\.(?:json|png|jpg|jpeg|txt|py|pt|onnx|zip))[\"']", text, flags=re.I)
    for raw in candidates[:400]:
        if raw.startswith(("http://", "https://")):
            continue
        normalized = raw.replace("\\", "/")
        possible = (path.parent / raw).resolve()
        refs.append(
            {
                "source": rel,
                "raw": raw,
                "normalized": normalized,
                "exists_relative_to_source": possible.exists(),
            }
        )
    return refs


def _build_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    summary = report["summary"]

    lines.append("# V2.56 Project Logic Coverage Merge Report")
    lines.append("")
    lines.append("## Summary")
    for key, value in summary.items():
        lines.append(f"- **{key}**: `{value}`")

    lines.append("")
    lines.append("## Source reports")
    for key, value in report["source_reports"].items():
        lines.append(f"- **{key}**: `{value}`")

    def add_section(title: str, rows: list[Any], limit: int = 120) -> None:
        lines.append("")
        lines.append(f"## {title}")
        if not rows:
            lines.append("- none")
            return
        for row in rows[:limit]:
            if isinstance(row, dict):
                rel = row.get("relpath") or row.get("path") or row.get("source") or str(row)
                extra = []
                for key in ["category", "reason", "status", "executed_lines_count", "function_calls_total"]:
                    if key in row:
                        extra.append(f"{key}=`{row[key]}`")
                lines.append(f"- `{rel}`" + (f" — {' '.join(extra)}" if extra else ""))
            else:
                lines.append(f"- `{row}`")
        if len(rows) > limit:
            lines.append(f"- ... `{len(rows) - limit}` more")

    add_section("1. Active logic chain", report["active_logic_chain"])
    add_section("2. Tested logic chain", report["tested_logic_chain"])
    add_section("3. Untested but referenced / likely active", report["untested_but_referenced"])
    add_section("4. Dead / legacy candidates", report["dead_legacy_candidates"])
    add_section("5. Missing fixture dependencies", report["missing_fixture_dependencies"])
    add_section("6. Old tests needing rewrite candidates", report["old_tests_needing_rewrite"])
    add_section("7. Runtime-only files", report["runtime_only_files"])
    add_section("8. YOLO / model-dependent files", report["yolo_model_dependent_files"])
    add_section("9. Safe-to-delete candidates", report["safe_to_delete_candidates"])

    lines.append("")
    lines.append("## Notes")
    lines.append("- Safe-to-delete entries are candidates only. Do not delete until reviewed manually.")
    lines.append("- Dynamic coverage depends on which profile/pytest targets were run.")
    lines.append("- Live-only code cannot be proven by unit tests alone.")

    return "\n".join(lines)


def build_report(
    *,
    root: Path,
    static_report: dict[str, Any],
    dynamic_report: dict[str, Any],
    pytest_collect: dict[str, Any],
    git_tracked: set[str],
    static_path: Path,
    dynamic_path: Path,
) -> dict[str, Any]:
    static_files = static_report.get("files", [])
    dynamic_executed = dynamic_report.get("executed_files", [])
    executed_by_rel = {row["relpath"]: row for row in dynamic_executed}
    executed_set = set(executed_by_rel)

    active_logic_chain: list[dict[str, Any]] = []
    tested_logic_chain: list[dict[str, Any]] = []

    for rel, dyn in sorted(executed_by_rel.items()):
        category = _path_category(rel)
        entry = {
            "relpath": rel,
            "category": category,
            "executed_lines_count": dyn.get("executed_lines_count"),
            "function_calls_total": dyn.get("function_calls_total"),
            "reason": "executed by dynamic trace",
        }
        tested_logic_chain.append(entry)
        if category in {"solver_preflop", "external_runtime", "external_logic", "tools"} or _has_any(rel, RUNTIME_HINTS + SOLVER_HINTS):
            active_logic_chain.append(entry)

    untested_but_referenced: list[dict[str, Any]] = []
    for row in static_files:
        rel = row["relpath"]
        if rel in executed_set:
            continue
        if row.get("likely_active") or _has_any(rel, RUNTIME_HINTS + SOLVER_HINTS):
            untested_but_referenced.append(
                {
                    "relpath": rel,
                    "category": row.get("category"),
                    "reason": "static likely_active/runtime/solver but not executed by current dynamic profile",
                }
            )

    dead_legacy_candidates: list[dict[str, Any]] = []
    for row in static_files:
        rel = row["relpath"]
        if rel in executed_set:
            continue
        if row.get("likely_legacy"):
            dead_legacy_candidates.append(
                {
                    "relpath": rel,
                    "category": row.get("category"),
                    "reason": "static likely_legacy and not executed by current dynamic profile",
                }
            )

    missing_refs: list[dict[str, Any]] = []
    for row in static_files:
        rel = row["relpath"]
        if not (rel.startswith("tests/") or rel.startswith("tools/")):
            continue
        for ref in _extract_literal_path_refs(root, rel):
            raw = ref["raw"]
            if raw.startswith(("outputs/", ".\\outputs", "./outputs")):
                continue
            if not ref["exists_relative_to_source"]:
                missing_refs.append(ref)

    old_tests_needing_rewrite: list[dict[str, Any]] = []
    for row in static_files:
        rel = row["relpath"]
        if not rel.startswith("tests/"):
            continue
        if rel not in executed_set and (row.get("likely_legacy") or not _is_current_test(rel)):
            old_tests_needing_rewrite.append(
                {
                    "relpath": rel,
                    "category": row.get("category"),
                    "reason": "test not executed by current profile and likely old/non-current",
                }
            )

    runtime_only_files: list[dict[str, Any]] = []
    for row in static_files:
        rel = row["relpath"]
        if _path_category(rel) == "external_runtime" or row.get("is_runtime_module"):
            runtime_only_files.append(
                {
                    "relpath": rel,
                    "category": row.get("category"),
                    "status": "executed" if rel in executed_set else "not_executed",
                    "reason": "runtime module",
                }
            )

    yolo_model_files: list[dict[str, Any]] = []
    for row in static_files:
        rel = row["relpath"]
        text = _read_text_safe(root / rel, max_chars=80_000)
        if _has_any(text, YOLO_HINTS) or _has_any(rel, YOLO_HINTS):
            yolo_model_files.append(
                {
                    "relpath": rel,
                    "category": row.get("category"),
                    "status": "executed" if rel in executed_set else "not_executed",
                    "reason": "contains YOLO/model/detector hints",
                }
            )

    safe_to_delete_candidates: list[dict[str, Any]] = []
    protected_prefixes = (
        "solver_preflop/",
        "external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/runtime/",
        "external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/logic/",
    )
    for item in dead_legacy_candidates:
        rel = item["relpath"]
        if rel.startswith(protected_prefixes):
            continue
        if _is_current_test(rel):
            continue
        safe_to_delete_candidates.append(
            {
                "relpath": rel,
                "category": item.get("category"),
                "reason": "legacy/not executed/non-protected candidate; manual review required",
            }
        )

    category_counts = Counter(_path_category(row["relpath"]) for row in static_files)
    executed_category_counts = Counter(_path_category(rel) for rel in executed_set)

    summary = {
        "project_root": str(root),
        "static_python_files_total": len(static_files),
        "dynamic_executed_files_total": len(executed_set),
        "dynamic_not_executed_files_total": len(dynamic_report.get("not_executed_py_files", [])),
        "git_tracked_files_total": len(git_tracked),
        "pytest_collect_ok": pytest_collect.get("ok"),
        "pytest_collect_items_estimate": pytest_collect.get("collected_items_estimate"),
        "active_logic_chain_total": len(active_logic_chain),
        "tested_logic_chain_total": len(tested_logic_chain),
        "untested_but_referenced_total": len(untested_but_referenced),
        "dead_legacy_candidates_total": len(dead_legacy_candidates),
        "missing_fixture_dependencies_total": len(missing_refs),
        "old_tests_needing_rewrite_total": len(old_tests_needing_rewrite),
        "runtime_only_files_total": len(runtime_only_files),
        "yolo_model_dependent_files_total": len(yolo_model_files),
        "safe_to_delete_candidates_total": len(safe_to_delete_candidates),
        "static_category_counts": dict(category_counts),
        "executed_category_counts": dict(executed_category_counts),
    }

    return {
        "schema": "v2_56_project_logic_coverage_report_v1",
        "summary": summary,
        "source_reports": {
            "static_json": str(static_path),
            "dynamic_json": str(dynamic_path),
            "static_schema": static_report.get("schema"),
            "dynamic_schema": dynamic_report.get("schema"),
        },
        "pytest_collect": pytest_collect,
        "active_logic_chain": active_logic_chain,
        "tested_logic_chain": tested_logic_chain,
        "untested_but_referenced": untested_but_referenced,
        "dead_legacy_candidates": dead_legacy_candidates,
        "missing_fixture_dependencies": missing_refs[:1000],
        "old_tests_needing_rewrite": old_tests_needing_rewrite,
        "runtime_only_files": runtime_only_files,
        "yolo_model_dependent_files": yolo_model_files,
        "safe_to_delete_candidates": safe_to_delete_candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge static and dynamic project maps into a logic coverage report.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--static-json", default="outputs/v2_54_project_static_logic_map.json")
    parser.add_argument("--dynamic-json", default="outputs/v2_55_project_dynamic_execution_map.json")
    parser.add_argument("--output-json", default="outputs/v2_56_project_logic_coverage_report.json")
    parser.add_argument("--output-md", default="outputs/v2_56_project_logic_coverage_report.md")
    parser.add_argument("--refresh-static", action="store_true")
    parser.add_argument("--refresh-dynamic", action="store_true")
    parser.add_argument("--dynamic-profile", choices=["smoke", "default"], default="smoke")
    parser.add_argument("--skip-pytest-collect", action="store_true")
    parser.add_argument("--pytest-target", action="append", default=[])
    parser.add_argument("--dynamic-skip-tools", action="store_true")
    parser.add_argument("--dynamic-skip-pytest", action="store_true")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    static_json = (root / args.static_json).resolve()
    dynamic_json = (root / args.dynamic_json).resolve()
    output_json = (root / args.output_json).resolve()
    output_md = (root / args.output_md).resolve()

    run_results: dict[str, Any] = {}

    if args.refresh_static or not static_json.exists():
        run_results["static_refresh"] = _ensure_static_report(
            root,
            static_json,
            static_json.with_suffix(".md"),
        )

    if args.refresh_dynamic or not dynamic_json.exists():
        run_results["dynamic_refresh"] = _ensure_dynamic_report(
            root,
            dynamic_json,
            dynamic_json.with_suffix(".md"),
            profile=args.dynamic_profile,
            pytest_targets=args.pytest_target,
            skip_tools=args.dynamic_skip_tools,
            skip_pytest=args.dynamic_skip_pytest,
        )

    static_report = _load_json(static_json)
    dynamic_report = _load_json(dynamic_json)
    pytest_collect = {} if args.skip_pytest_collect else _pytest_collect(root)
    tracked = _git_tracked(root)

    report = build_report(
        root=root,
        static_report=static_report,
        dynamic_report=dynamic_report,
        pytest_collect=pytest_collect,
        git_tracked=tracked,
        static_path=static_json,
        dynamic_path=dynamic_json,
    )
    report["run_results"] = run_results

    _write_json(output_json, report)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(_build_markdown(report), encoding="utf-8")

    print("V2.56 PROJECT LOGIC COVERAGE MERGE REPORT")
    for key, value in report["summary"].items():
        print(f"{key}: {value}")
    print("-" * 100)
    print(f"output_json={output_json}")
    print(f"output_md={output_md}")

    ok = (
        report["summary"]["static_python_files_total"] > 0
        and report["summary"]["dynamic_executed_files_total"] > 0
    )
    print(f"V2.56_PROJECT_LOGIC_COVERAGE_REPORT_OK = {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
