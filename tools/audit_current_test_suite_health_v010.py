#!/usr/bin/env python3
"""V0.1.2 — Test Suite Health Audit for PokerVision_Solver_AllPreflop_Flop.

This tool intentionally does not change project code. It inventories the current
pytest suite, classifies test files, performs guarded collection/run checks, and
writes both machine-readable JSON and human-readable Markdown reports.

Default mode is safe: collect every test file, but run only files that do not
look live/external/old-output dependent. Use --run-mode all only when you
explicitly want every file executed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Literal

SCHEMA_VERSION = "v0.1.2-test-suite-health"
REPORT_DIR = Path("outputs") / "baseline_audit_v010"
DOCS_REPORT_DIR = Path("docs") / "reports"
JSON_REPORT_NAME = "test_suite_health_report.json"
MARKDOWN_REPORT_NAME = "current_test_suite_health_audit_v010.md"

Category = Literal[
    "core_baseline",
    "legacy_old_audit",
    "live_dry_run",
    "static_dynamic_map",
    "future_postflop",
    "unknown",
]
RecommendedAction = Literal[
    "keep_as_required_baseline",
    "keep_but_not_blocking",
    "mark_legacy",
    "quarantine_temporarily",
    "fix_before_postflop",
    "needs_manual_review",
]
RunMode = Literal["collect-only", "safe", "all"]

CORE_PATTERNS = (
    "adapter",
    "clear_json",
    "contract",
    "decision",
    "engine",
    "output_files",
    "preflop",
    "range",
    "sizing",
    "spot_classifier",
    "solver",
)

LIVE_PATTERNS = (
    "action_button",
    "click",
    "controlled_live",
    "current_cycle",
    "dry_run",
    "live",
    "mss",
    "pyautogui",
    "real_click",
    "runtime",
    "screen",
    "ui_display_cycle",
    "win32",
)

EXTERNAL_PATTERNS = (
    "external",
    "pokervisionfinalversionnosolver_snapshot",
    "pokervision v1_2",
    "snapshot",
)

OLD_OUTPUT_PATTERNS = (
    "outputs",
    "current_cycle",
    "fixture",
    "fixtures",
    "json_complete",
    "solver_payloads",
    "ui_display_cycle",
    "v2_",
)

STATIC_MAP_PATTERNS = (
    "audit_tools",
    "baseline_audit",
    "module_map",
    "source_map",
    "static",
    "structure",
)

LEGACY_FILE_RE = re.compile(r"(^|/|\\)test_v\d+[_\d]*", re.IGNORECASE)
VERSIONED_AUDIT_RE = re.compile(r"v\d+[_\d]*", re.IGNORECASE)


@dataclass(frozen=True)
class CommandResult:
    status: str
    returncode: int | None
    duration_seconds: float
    stdout_tail: str
    stderr_tail: str


@dataclass(frozen=True)
class TestFileHealth:
    test_file: str
    category: Category
    collect_status: str
    run_status: str
    requires_live_environment: bool
    requires_external_snapshot: bool
    requires_old_outputs: bool
    is_blocking_for_postflop_dev: bool
    failure_reason: str
    recommended_action: RecommendedAction
    notes: list[str]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_text_safe(path: Path, limit_chars: int = 300_000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return text[:limit_chars]


def normalize_for_match(value: str) -> str:
    return value.replace("\\", "/").lower()


def contains_any(haystack: str, patterns: Iterable[str]) -> bool:
    lowered = haystack.lower()
    return any(pattern.lower() in lowered for pattern in patterns)


def tail(text: str, max_chars: int = 1600) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return "..." + text[-max_chars:]


def discover_test_files(project_root: Path) -> list[Path]:
    tests_dir = project_root / "tests"
    if not tests_dir.exists():
        return []
    return sorted(
        path for path in tests_dir.rglob("test_*.py") if path.is_file() and "__pycache__" not in path.parts
    )


def detect_requirements(relative_path: str, content: str) -> tuple[bool, bool, bool, list[str]]:
    haystack = normalize_for_match(relative_path + "\n" + content)
    notes: list[str] = []

    requires_live = contains_any(haystack, LIVE_PATTERNS) or "pokervision_controlled_live" in haystack
    requires_external = contains_any(haystack, EXTERNAL_PATTERNS)
    requires_old_outputs = contains_any(haystack, OLD_OUTPUT_PATTERNS)

    # Avoid marking the new audit test as old-output dependent just because it
    # validates the output report path.
    if "test_baseline_audit_tools_v010.py" in normalize_for_match(relative_path):
        requires_old_outputs = False
        requires_live = False

    if requires_live:
        notes.append("contains live/runtime/click/screen related references")
    if requires_external:
        notes.append("contains external snapshot references")
    if requires_old_outputs:
        notes.append("contains outputs/fixture/current_cycle related references")

    return requires_live, requires_external, requires_old_outputs, notes


def classify_test_file(relative_path: str, content: str) -> Category:
    path_key = normalize_for_match(relative_path)
    haystack = normalize_for_match(relative_path + "\n" + content)

    if "postflop" in haystack or "flop" in path_key:
        return "future_postflop"
    if contains_any(haystack, LIVE_PATTERNS):
        return "live_dry_run"
    if contains_any(haystack, STATIC_MAP_PATTERNS):
        return "static_dynamic_map"
    if LEGACY_FILE_RE.search(path_key) or ("audit" in haystack and VERSIONED_AUDIT_RE.search(path_key)):
        return "legacy_old_audit"
    if contains_any(haystack, CORE_PATTERNS):
        return "core_baseline"
    return "unknown"


def should_run_file(
    *,
    category: Category,
    run_mode: RunMode,
    requires_live_environment: bool,
    requires_external_snapshot: bool,
    requires_old_outputs: bool,
) -> bool:
    if run_mode == "collect-only":
        return False
    if run_mode == "all":
        return True
    if requires_live_environment or requires_external_snapshot or requires_old_outputs:
        return False
    if category in {"legacy_old_audit", "unknown"}:
        return False
    return True


def run_pytest_for_file(project_root: Path, test_file: Path, *, collect_only: bool, timeout_seconds: int) -> CommandResult:
    import time

    cmd = [sys.executable, "-m", "pytest", str(test_file.relative_to(project_root)), "-q"]
    if collect_only:
        cmd.insert(-1, "--collect-only")

    started = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(project_root),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
        )
        duration = time.monotonic() - started
        status = "passed" if proc.returncode == 0 else "failed"
        return CommandResult(
            status=status,
            returncode=proc.returncode,
            duration_seconds=round(duration, 3),
            stdout_tail=tail(proc.stdout),
            stderr_tail=tail(proc.stderr),
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.monotonic() - started
        return CommandResult(
            status="timeout",
            returncode=None,
            duration_seconds=round(duration, 3),
            stdout_tail=tail(exc.stdout or ""),
            stderr_tail=tail(exc.stderr or ""),
        )


def choose_recommended_action(
    *,
    category: Category,
    collect_status: str,
    run_status: str,
    requires_live_environment: bool,
    requires_external_snapshot: bool,
    requires_old_outputs: bool,
) -> RecommendedAction:
    failed = collect_status not in {"passed", "no_tests_collected"} or run_status in {"failed", "timeout"}

    if category == "core_baseline":
        return "fix_before_postflop" if failed else "keep_as_required_baseline"
    if category == "legacy_old_audit":
        return "quarantine_temporarily" if failed else "mark_legacy"
    if category == "live_dry_run":
        return "keep_but_not_blocking"
    if category == "static_dynamic_map":
        return "fix_before_postflop" if failed else "keep_but_not_blocking"
    if category == "future_postflop":
        return "needs_manual_review" if failed else "keep_but_not_blocking"
    if requires_live_environment or requires_external_snapshot or requires_old_outputs:
        return "keep_but_not_blocking"
    return "needs_manual_review"


def build_failure_reason(collect: CommandResult, run: CommandResult | None, skipped_reason: str) -> str:
    if collect.status not in {"passed", "no_tests_collected"}:
        return f"collect_{collect.status}: {collect.stderr_tail or collect.stdout_tail}".strip()
    if run is not None and run.status not in {"passed", "no_tests_collected"}:
        return f"run_{run.status}: {run.stderr_tail or run.stdout_tail}".strip()
    if skipped_reason:
        return skipped_reason
    return ""


def analyse_test_file(project_root: Path, test_file: Path, *, run_mode: RunMode, timeout_seconds: int) -> TestFileHealth:
    relative_path = test_file.relative_to(project_root).as_posix()
    content = read_text_safe(test_file)
    category = classify_test_file(relative_path, content)
    requires_live, requires_external, requires_old_outputs, notes = detect_requirements(relative_path, content)

    collect = run_pytest_for_file(project_root, test_file, collect_only=True, timeout_seconds=timeout_seconds)

    run_result: CommandResult | None = None
    skipped_reason = ""
    if should_run_file(
        category=category,
        run_mode=run_mode,
        requires_live_environment=requires_live,
        requires_external_snapshot=requires_external,
        requires_old_outputs=requires_old_outputs,
    ):
        run_result = run_pytest_for_file(project_root, test_file, collect_only=False, timeout_seconds=timeout_seconds)
        run_status = run_result.status
    else:
        if run_mode == "collect-only":
            skipped_reason = "run skipped because run_mode=collect-only"
            run_status = "not_run_collect_only"
        else:
            skipped_reason = "run skipped by safe audit guard"
            run_status = "not_run_guarded"

    action = choose_recommended_action(
        category=category,
        collect_status=collect.status,
        run_status=run_status,
        requires_live_environment=requires_live,
        requires_external_snapshot=requires_external,
        requires_old_outputs=requires_old_outputs,
    )
    is_blocking = action in {"keep_as_required_baseline", "fix_before_postflop"}

    if category == "unknown":
        notes.append("classification requires manual review")
    if run_status == "not_run_guarded":
        notes.append("safe mode avoided executing this file")

    return TestFileHealth(
        test_file=relative_path,
        category=category,
        collect_status=collect.status,
        run_status=run_status,
        requires_live_environment=requires_live,
        requires_external_snapshot=requires_external,
        requires_old_outputs=requires_old_outputs,
        is_blocking_for_postflop_dev=is_blocking,
        failure_reason=build_failure_reason(collect, run_result, skipped_reason),
        recommended_action=action,
        notes=notes,
    )


def summarise(items: list[TestFileHealth]) -> dict[str, object]:
    return {
        "total_test_files": len(items),
        "by_category": dict(Counter(item.category for item in items)),
        "by_collect_status": dict(Counter(item.collect_status for item in items)),
        "by_run_status": dict(Counter(item.run_status for item in items)),
        "by_recommended_action": dict(Counter(item.recommended_action for item in items)),
        "requires_live_environment": sum(1 for item in items if item.requires_live_environment),
        "requires_external_snapshot": sum(1 for item in items if item.requires_external_snapshot),
        "requires_old_outputs": sum(1 for item in items if item.requires_old_outputs),
        "blocking_for_postflop_dev": sum(1 for item in items if item.is_blocking_for_postflop_dev),
    }


def build_report(project_root: Path, *, run_mode: RunMode = "safe", timeout_seconds: int = 35) -> dict[str, object]:
    test_files = discover_test_files(project_root)
    items = [
        analyse_test_file(project_root, test_file, run_mode=run_mode, timeout_seconds=timeout_seconds)
        for test_file in test_files
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": utc_now_iso(),
        "project_root": str(project_root),
        "run_mode": run_mode,
        "timeout_seconds_per_pytest_call": timeout_seconds,
        "purpose": "Classify current tests before postflop development; do not delete or rewrite tests in this audit.",
        "summary": summarise(items),
        "test_files": [asdict(item) for item in items],
        "next_step": "V0.1.3 JSON Source Map Audit",
    }


def markdown_bool(value: bool) -> str:
    return "yes" if value else "no"


def render_markdown(report: dict[str, object]) -> str:
    summary = report["summary"]
    assert isinstance(summary, dict)
    test_files = report["test_files"]
    assert isinstance(test_files, list)

    lines: list[str] = []
    lines.append("# V0.1.2 — Test Suite Health Audit")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append(
        "This report classifies the current pytest suite before any postflop solver, normalizer, "
        "player resolver, ranges, equity, runtime, or click-chain changes."
    )
    lines.append("")
    lines.append("The audit is intentionally conservative: legacy, live, external snapshot, and old-output tests are not deleted or treated as automatic blockers for postflop development.")
    lines.append("")
    lines.append("## Run Metadata")
    lines.append("")
    lines.append(f"- Schema version: `{report['schema_version']}`")
    lines.append(f"- Generated at UTC: `{report['generated_at_utc']}`")
    lines.append(f"- Project root: `{report['project_root']}`")
    lines.append(f"- Run mode: `{report['run_mode']}`")
    lines.append(f"- Timeout per pytest call: `{report['timeout_seconds_per_pytest_call']}s`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for key, value in summary.items():
        lines.append(f"- **{key}**: `{value}`")
    lines.append("")
    lines.append("## Test File Classification")
    lines.append("")
    lines.append("| test_file | category | collect | run | live | external | old_outputs | blocking | action |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for item in test_files:
        assert isinstance(item, dict)
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{item['test_file']}`",
                    str(item["category"]),
                    str(item["collect_status"]),
                    str(item["run_status"]),
                    markdown_bool(bool(item["requires_live_environment"])),
                    markdown_bool(bool(item["requires_external_snapshot"])),
                    markdown_bool(bool(item["requires_old_outputs"])),
                    markdown_bool(bool(item["is_blocking_for_postflop_dev"])),
                    str(item["recommended_action"]),
                ]
            )
            + " |"
        )
    lines.append("")
    lines.append("## Failure / Guard Notes")
    lines.append("")
    for item in test_files:
        assert isinstance(item, dict)
        failure_reason = str(item.get("failure_reason") or "")
        notes = item.get("notes") or []
        if failure_reason or notes:
            lines.append(f"### `{item['test_file']}`")
            if failure_reason:
                lines.append(f"- Failure / guard reason: `{failure_reason}`")
            if notes:
                for note in notes:
                    lines.append(f"- Note: {note}")
            lines.append("")
    lines.append("## V0.1.2 Conclusion")
    lines.append("")
    lines.append("This report is the test-suite baseline for the new postflop direction. The next version should continue with JSON source mapping, not with direct postflop decision logic.")
    lines.append("")
    lines.append("Next step: **V0.1.3 — JSON Source Map Audit**.")
    lines.append("")
    return "\n".join(lines)


def write_reports(project_root: Path, report: dict[str, object]) -> tuple[Path, Path]:
    json_dir = project_root / REPORT_DIR
    docs_dir = project_root / DOCS_REPORT_DIR
    json_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    json_path = json_dir / JSON_REPORT_NAME
    markdown_path = docs_dir / MARKDOWN_REPORT_NAME

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, markdown_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="V0.1.2 test suite health audit")
    parser.add_argument("--project-root", default=".", help="Project root path. Defaults to current directory.")
    parser.add_argument(
        "--run-mode",
        choices=["collect-only", "safe", "all"],
        default="safe",
        help="collect-only: no test execution; safe: run only non-live/non-external files; all: run every test file.",
    )
    parser.add_argument("--timeout-seconds", type=int, default=35, help="Timeout per pytest file call.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    project_root = Path(args.project_root).resolve()
    report = build_report(project_root, run_mode=args.run_mode, timeout_seconds=args.timeout_seconds)
    json_path, markdown_path = write_reports(project_root, report)

    summary = report["summary"]
    assert isinstance(summary, dict)
    print("[V0.1.2] Test suite health audit completed")
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {markdown_path}")
    print(f"Total test files: {summary.get('total_test_files')}")
    print(f"By category: {summary.get('by_category')}")
    print(f"By recommended action: {summary.get('by_recommended_action')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
