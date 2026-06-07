from __future__ import annotations

import argparse
import json
import os
import runpy
import sys
import time
import traceback
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


EXCLUDED_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "outputs",
    "output",
    "temp",
    "tmp",
    ".venv",
    "venv",
    "env",
    "node_modules",
}

DEFAULT_PYTEST_TARGETS = [
    "tests/test_v2_42_full_preflop_spot_matrix_e2e.py",
    "tests/test_v2_43_allin_semantic_cleanup_audit.py",
    "tests/test_v2_44_premium_fold_guard_e2e.py",
    "tests/test_v2_45_allin_taxonomy_audit.py",
    "tests/test_v2_46_clear_json_allin_propagation_audit.py",
    "tests/test_v2_47_allin_stack_policy_audit.py",
    "tests/test_v2_48_unknown_amount_allin_audit.py",
    "tests/test_v2_49_dark_clear_solver_runtime_chain.py",
    "tests/test_v2_50_remove_game_service_policy_audit.py",
    "tests/test_v2_51_postflop_runtime_fallback_audit.py",
    "tests/test_v2_52_invalid_hero_runtime_fallback_audit.py",
    "tests/test_v2_53_bridge_payload_fallback_audit.py",
    "tests/test_v2_54_project_static_logic_map.py",
]

DEFAULT_TOOL_SCRIPTS = [
    "tools/run_v2_42_full_preflop_spot_matrix_e2e.py",
    "tools/run_v2_43_allin_semantic_cleanup_audit.py",
    "tools/run_v2_45_allin_taxonomy_audit.py",
    "tools/run_v2_46_clear_json_allin_propagation_audit.py",
    "tools/run_v2_47_allin_stack_policy_audit.py",
    "tools/run_v2_48_unknown_amount_allin_audit.py",
    "tools/run_v2_49_dark_clear_solver_runtime_chain.py",
    "tools/run_v2_50_remove_game_service_policy_audit.py",
    "tools/run_v2_51_postflop_runtime_fallback_audit.py",
    "tools/run_v2_52_invalid_hero_runtime_fallback_audit.py",
    "tools/run_v2_53_bridge_payload_fallback_audit.py",
    "tools/run_v2_54_project_static_logic_map.py",
]


@dataclass
class FileExecStats:
    relpath: str
    lines: set[int] = field(default_factory=set)
    function_calls: Counter[str] = field(default_factory=Counter)

    def to_json(self) -> dict[str, Any]:
        return {
            "relpath": self.relpath,
            "executed_lines_count": len(self.lines),
            "executed_lines_sample": sorted(self.lines)[:80],
            "function_calls_total": int(sum(self.function_calls.values())),
            "functions_called_count": len(self.function_calls),
            "top_functions": self.function_calls.most_common(40),
        }


class DynamicTracer:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root.resolve()
        self.project_root_key = os.path.normcase(os.path.abspath(str(self.project_root)))
        self._filename_rel_cache: dict[str, str | None] = {}
        self.stats: dict[str, FileExecStats] = {}
        self.enabled = False

    def _relpath(self, filename: str) -> str | None:
        cached = self._filename_rel_cache.get(filename)
        if filename in self._filename_rel_cache:
            return cached

        try:
            if not filename or filename.startswith("<"):
                self._filename_rel_cache[filename] = None
                return None

            abs_name = os.path.abspath(filename)
            key = os.path.normcase(abs_name)
            root_key = self.project_root_key

            # Hot-path guard: reject stdlib/site-packages/pytest frames before
            # Path work. Path.resolve() here makes pytest startup look frozen.
            if key != root_key and not key.startswith(root_key + os.sep):
                self._filename_rel_cache[filename] = None
                return None

            path = Path(abs_name)
            if path.suffix != ".py":
                self._filename_rel_cache[filename] = None
                return None

            try:
                rel = path.relative_to(self.project_root)
            except ValueError:
                self._filename_rel_cache[filename] = None
                return None

            if any(part in EXCLUDED_DIR_NAMES for part in rel.parts):
                self._filename_rel_cache[filename] = None
                return None

            result = str(rel).replace("\\", "/")
            self._filename_rel_cache[filename] = result
            return result
        except Exception:
            self._filename_rel_cache[filename] = None
            return None

    def _get_stats(self, rel: str) -> FileExecStats:
        if rel not in self.stats:
            self.stats[rel] = FileExecStats(relpath=rel)
        return self.stats[rel]

    def tracer(self, frame, event: str, arg):
        if not self.enabled:
            return self.tracer

        rel = self._relpath(frame.f_code.co_filename)
        if rel is None:
            return self.tracer

        stats = self._get_stats(rel)
        if event == "line":
            stats.lines.add(int(frame.f_lineno))
        elif event == "call":
            qual = frame.f_code.co_name
            if "self" in frame.f_locals:
                try:
                    qual = f"{frame.f_locals['self'].__class__.__name__}.{qual}"
                except Exception:
                    pass
            stats.function_calls[qual] += 1
        return self.tracer

    def start(self) -> None:
        self.enabled = True
        sys.settrace(self.tracer)

    def stop(self) -> None:
        sys.settrace(None)
        self.enabled = False


def should_skip_static(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return True
    if any(part in EXCLUDED_DIR_NAMES for part in rel.parts):
        return True
    if any(part.startswith("_v2_") or part.startswith("_project_source_audit") for part in rel.parts):
        return True
    return False


def static_py_files(root: Path) -> list[str]:
    files = [
        str(path.relative_to(root)).replace("\\", "/")
        for path in root.rglob("*.py")
        if path.is_file() and not should_skip_static(path, root)
    ]
    return sorted(files)


def tool_args_for(script: Path, output_dir: Path) -> list[str]:
    text = script.read_text(encoding="utf-8", errors="ignore")
    args: list[str] = []
    stem = script.stem

    if "--report-json" in text:
        args += ["--report-json", str(output_dir / f"{stem}.json")]

    if script.name == "run_v2_54_project_static_logic_map.py":
        args += [
            "--project-root",
            ".",
            "--output-json",
            str(output_dir / "v2_54_static_from_dynamic.json"),
            "--output-md",
            str(output_dir / "v2_54_static_from_dynamic.md"),
            "--skip-pytest-collect",
        ]

    return args


def run_tool_under_trace(root: Path, tracer: DynamicTracer, rel_script: str, output_dir: Path) -> dict[str, Any]:
    print(f"[v2.55] running tool: {rel_script}", flush=True)
    script = root / rel_script
    result: dict[str, Any] = {
        "kind": "tool",
        "script": rel_script,
        "exists": script.exists(),
        "ok": False,
        "returncode": None,
        "duration_sec": None,
        "error": None,
    }
    if not script.exists():
        result["error"] = "missing_script"
        return result

    old_argv = sys.argv[:]
    old_cwd = Path.cwd()
    started = time.perf_counter()
    try:
        sys.argv = [str(script)] + tool_args_for(script, output_dir)
        os.chdir(root)
        tracer.start()
        try:
            runpy.run_path(str(script), run_name="__main__")
            result["returncode"] = 0
            result["ok"] = True
        except SystemExit as exc:
            code = exc.code
            if code is None:
                code = 0
            if not isinstance(code, int):
                code = 1
            result["returncode"] = code
            result["ok"] = code == 0
        finally:
            tracer.stop()
    except Exception as exc:
        tracer.stop()
        result["returncode"] = 1
        result["ok"] = False
        result["error"] = "".join(traceback.format_exception_only(type(exc), exc)).strip()
        result["traceback_tail"] = traceback.format_exc()[-4000:]
    finally:
        os.chdir(old_cwd)
        sys.argv = old_argv
        result["duration_sec"] = round(time.perf_counter() - started, 3)

    return result


def run_pytest_under_trace(root: Path, tracer: DynamicTracer, targets: list[str]) -> dict[str, Any]:
    existing = [target for target in targets if (root / target).exists()]
    result: dict[str, Any] = {
        "kind": "pytest",
        "targets_requested": targets,
        "targets_existing": existing,
        "ok": False,
        "returncode": None,
        "duration_sec": None,
        "error": None,
    }
    if not existing:
        result["error"] = "no_existing_pytest_targets"
        return result

    print(f"[v2.55] running pytest targets: {len(existing)}", flush=True)
    started = time.perf_counter()
    old_cwd = Path.cwd()
    try:
        import pytest

        os.chdir(root)
        tracer.start()
        try:
            code = pytest.main(existing + ["-q"])
        finally:
            tracer.stop()
        result["returncode"] = int(code)
        result["ok"] = int(code) == 0
    except Exception as exc:
        tracer.stop()
        result["returncode"] = 1
        result["ok"] = False
        result["error"] = "".join(traceback.format_exception_only(type(exc), exc)).strip()
        result["traceback_tail"] = traceback.format_exc()[-4000:]
    finally:
        os.chdir(old_cwd)
        result["duration_sec"] = round(time.perf_counter() - started, 3)

    return result


def self_smoke_target() -> int:
    # Small deterministic workload used by the unit test to prove tracer output.
    total = 0
    for i in range(5):
        total += i * 2
    return total


def run_self_smoke(tracer: DynamicTracer) -> dict[str, Any]:
    started = time.perf_counter()
    tracer.start()
    try:
        value = self_smoke_target()
    finally:
        tracer.stop()
    return {
        "kind": "self_smoke",
        "ok": value == 20,
        "returncode": 0 if value == 20 else 1,
        "duration_sec": round(time.perf_counter() - started, 3),
        "value": value,
    }


def build_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    summary = report["summary"]

    lines.append("# V2.55 Project Dynamic Execution Map")
    lines.append("")
    lines.append("## Summary")
    for key, value in summary.items():
        lines.append(f"- **{key}**: `{value}`")

    lines.append("")
    lines.append("## Command results")
    for row in report["command_results"]:
        lines.append(
            f"- `{row.get('kind')}` `{row.get('script', '')}` "
            f"ok=`{row.get('ok')}` returncode=`{row.get('returncode')}` duration=`{row.get('duration_sec')}` "
            f"error=`{row.get('error')}`"
        )

    lines.append("")
    lines.append("## Executed files")
    for row in report["executed_files"][:220]:
        lines.append(
            f"- `{row['relpath']}` lines=`{row['executed_lines_count']}` "
            f"calls=`{row['function_calls_total']}` functions=`{row['functions_called_count']}` "
            f"top={row['top_functions'][:5]}"
        )

    lines.append("")
    lines.append("## Not executed Python files")
    for rel in report["not_executed_py_files"][:300]:
        lines.append(f"- `{rel}`")
    if len(report["not_executed_py_files"]) > 300:
        lines.append(f"- ... `{len(report['not_executed_py_files']) - 300}` more")

    lines.append("")
    lines.append("## Suspicious legacy candidates not executed")
    lines.append("Candidates only. Do not delete without manual review.")
    for rel in report["suspicious_legacy_not_executed"][:300]:
        lines.append(f"- `{rel}`")

    lines.append("")
    lines.append("## Runtime / solver / test execution buckets")
    for name, rows in report["buckets"].items():
        lines.append(f"### {name}")
        for rel in rows[:120]:
            lines.append(f"- `{rel}`")
        if len(rows) > 120:
            lines.append(f"- ... `{len(rows) - 120}` more")

    return "\n".join(lines)


def classify_legacy(rel: str) -> bool:
    low = rel.lower()
    return any(token in low for token in ["legacy", "old", "backup", "stub", "deprecated", "archive", "audit", "probe", "tmp"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build dynamic execution map for PokerVision_Solver_Preflop.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--output-json", default="outputs/v2_55_project_dynamic_execution_map.json")
    parser.add_argument("--output-md", default="outputs/v2_55_project_dynamic_execution_map.md")
    parser.add_argument("--profile", choices=["smoke", "default"], default="default")
    parser.add_argument("--skip-pytest", action="store_true")
    parser.add_argument("--skip-tools", action="store_true")
    parser.add_argument("--self-smoke", action="store_true")
    parser.add_argument("--pytest-target", action="append", default=[])
    parser.add_argument("--tool-script", action="append", default=[])
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    out_json = root / args.output_json
    out_md = root / args.output_md
    out_json.parent.mkdir(parents=True, exist_ok=True)
    dynamic_tmp = out_json.parent / "v2_55_dynamic_tmp"
    dynamic_tmp.mkdir(parents=True, exist_ok=True)

    tracer = DynamicTracer(root)
    command_results: list[dict[str, Any]] = []

    if args.self_smoke or args.profile == "smoke":
        command_results.append(run_self_smoke(tracer))

    pytest_targets = args.pytest_target or DEFAULT_PYTEST_TARGETS
    tool_scripts = args.tool_script or DEFAULT_TOOL_SCRIPTS

    if args.profile == "smoke" and not args.tool_script and not args.pytest_target:
        # Smoke keeps the apply/test phase fast and deterministic.
        pytest_targets = []
        tool_scripts = []

    if not args.skip_tools:
        for script in tool_scripts:
            command_results.append(run_tool_under_trace(root, tracer, script, dynamic_tmp))

    if not args.skip_pytest:
        command_results.append(run_pytest_under_trace(root, tracer, pytest_targets))

    all_py = static_py_files(root)
    executed = sorted((stats.to_json() for stats in tracer.stats.values()), key=lambda row: row["relpath"])
    executed_set = {row["relpath"] for row in executed}
    not_executed = [rel for rel in all_py if rel not in executed_set]

    buckets = {
        "executed_solver_preflop": [rel for rel in sorted(executed_set) if rel.startswith("solver_preflop/")],
        "executed_external_runtime": [rel for rel in sorted(executed_set) if "external/PokerVisionFinalVersionNoSolver_snapshot/" in rel and "/runtime/" in rel],
        "executed_external_logic": [rel for rel in sorted(executed_set) if "external/PokerVisionFinalVersionNoSolver_snapshot/" in rel and "/logic/" in rel],
        "executed_tools": [rel for rel in sorted(executed_set) if rel.startswith("tools/")],
        "executed_tests": [rel for rel in sorted(executed_set) if rel.startswith("tests/")],
        "not_executed_solver_preflop": [rel for rel in not_executed if rel.startswith("solver_preflop/")],
        "not_executed_external_snapshot": [rel for rel in not_executed if rel.startswith("external/PokerVisionFinalVersionNoSolver_snapshot/")],
        "not_executed_tools": [rel for rel in not_executed if rel.startswith("tools/")],
        "not_executed_tests": [rel for rel in not_executed if rel.startswith("tests/")],
    }

    suspicious_legacy = [rel for rel in not_executed if classify_legacy(rel)]

    summary = {
        "project_root": str(root),
        "profile": args.profile,
        "commands_total": len(command_results),
        "commands_ok": sum(1 for row in command_results if row.get("ok") is True),
        "commands_failed": sum(1 for row in command_results if row.get("ok") is not True),
        "python_files_total": len(all_py),
        "executed_files_total": len(executed_set),
        "not_executed_files_total": len(not_executed),
        "executed_functions_total": sum(row["functions_called_count"] for row in executed),
        "function_calls_total": sum(row["function_calls_total"] for row in executed),
        "suspicious_legacy_not_executed_total": len(suspicious_legacy),
    }

    report = {
        "schema": "v2_55_project_dynamic_execution_map_v1",
        "summary": summary,
        "command_results": command_results,
        "executed_files": executed,
        "not_executed_py_files": not_executed,
        "suspicious_legacy_not_executed": suspicious_legacy,
        "buckets": buckets,
    }

    out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    out_md.write_text(build_markdown(report), encoding="utf-8")

    print("V2.55 PROJECT DYNAMIC EXECUTION MAP")
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("-" * 100)
    print(f"output_json={out_json}")
    print(f"output_md={out_md}")

    ok = summary["commands_total"] > 0 and summary["executed_files_total"] > 0
    print(f"V2.55_PROJECT_DYNAMIC_EXECUTION_MAP_OK = {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
