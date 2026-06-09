#!/usr/bin/env python3
"""Build final V0.1.0 baseline audit report for PokerVision_Solver_AllPreflop_Flop.

This tool merges the four V0.1 audit outputs:
- project_baseline_report.json
- test_suite_health_report.json
- json_source_map_report.json
- player_state_filtering_report.json

It does not modify runtime, tests, source JSON, click chain, solver logic, or postflop logic.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

REPORT_DIR = Path("outputs") / "baseline_audit_v010"
DOCS_REPORT_DIR = Path("docs") / "reports"
FINAL_JSON_NAME = "v010_final_report.json"
FINAL_MD_NAME = "v010_final_baseline_audit_report.md"
PLAN_MD_NAME = "v010_plan_to_v020.md"

REQUIRED_SOURCE_REPORTS = {
    "project_baseline": "project_baseline_report.json",
    "test_suite_health": "test_suite_health_report.json",
    "json_source_map": "json_source_map_report.json",
    "player_state_filtering": "player_state_filtering_report.json",
}

V020_SOURCE_TYPES = [
    "dark_json",
    "pending_json",
    "service_json",
    "current_cycle_json",
    "runtime_json",
    "solver_payload_json",
    "final_clear_json",
    "manual_live_like_json",
    "unknown",
]


@dataclass(frozen=True)
class SourceReportLoad:
    key: str
    path: str
    exists: bool
    loaded: bool
    error: Optional[str]
    data: Dict[str, Any]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_git_command(project_root: Path, args: List[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(project_root),
            check=False,
            text=True,
            capture_output=True,
            timeout=10,
        )
    except Exception as exc:  # pragma: no cover - environment dependent
        return f"ERROR: {exc}"
    out = (completed.stdout or "").strip()
    err = (completed.stderr or "").strip()
    if completed.returncode != 0:
        return f"ERROR rc={completed.returncode}: {err or out}"
    return out


def load_json_file(path: Path) -> SourceReportLoad:
    key = path.stem
    if not path.exists():
        return SourceReportLoad(key=key, path=str(path), exists=False, loaded=False, error="missing", data={})
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return SourceReportLoad(key=key, path=str(path), exists=True, loaded=False, error="root is not object", data={})
        return SourceReportLoad(key=key, path=str(path), exists=True, loaded=True, error=None, data=data)
    except Exception as exc:
        return SourceReportLoad(key=key, path=str(path), exists=True, loaded=False, error=str(exc), data={})


def load_source_reports(project_root: Path) -> Dict[str, SourceReportLoad]:
    loaded: Dict[str, SourceReportLoad] = {}
    for key, name in REQUIRED_SOURCE_REPORTS.items():
        item = load_json_file(project_root / REPORT_DIR / name)
        loaded[key] = SourceReportLoad(
            key=key,
            path=item.path,
            exists=item.exists,
            loaded=item.loaded,
            error=item.error,
            data=item.data,
        )
    return loaded


def get_nested(data: Mapping[str, Any], candidates: Iterable[str], default: Any = None) -> Any:
    for key in candidates:
        if key in data:
            return data[key]
    return default


def summarize_project_baseline(data: Mapping[str, Any]) -> Dict[str, Any]:
    risk_flags = get_nested(data, ["risk_flags", "risks"], []) or []
    repo_identity = get_nested(data, ["repo_identity", "project_identity"], {}) or {}
    directory_presence = get_nested(data, ["directory_presence", "directories"], {}) or {}
    preflop = get_nested(data, ["preflop_baseline_presence", "preflop_baseline"], {}) or {}
    external = get_nested(data, ["external_snapshot_presence", "external_snapshot"], {}) or {}
    return {
        "summary": "AllPreflop_Flop repository currently behaves as a preflop baseline plus external snapshot and audit/history tail.",
        "repo_identity": repo_identity,
        "directory_presence": directory_presence,
        "preflop_baseline_presence": preflop,
        "external_snapshot_presence": external,
        "risk_flags_count": len(risk_flags) if isinstance(risk_flags, list) else None,
        "risk_flags": risk_flags,
    }


def summarize_test_suite(data: Mapping[str, Any]) -> Dict[str, Any]:
    total = get_nested(data, ["total_test_files", "total_files"], None)
    by_category = get_nested(data, ["by_category", "category_counts"], {}) or {}
    by_action = get_nested(data, ["by_recommended_action", "recommended_action_counts"], {}) or {}
    return {
        "summary": "Test suite is mixed; legacy/live-only tests must not automatically block postflop development.",
        "total_test_files": total,
        "by_category": by_category,
        "by_recommended_action": by_action,
        "postflop_gate_rule": "Use core/postflop-specific tests as blockers; keep legacy/live-only tests as non-blocking evidence unless explicitly promoted.",
    }


def summarize_json_sources(data: Mapping[str, Any]) -> Dict[str, Any]:
    total = get_nested(data, ["total_json_files", "total_files"], None)
    by_type = get_nested(data, ["by_source_type", "source_type_counts"], {}) or {}
    before_click = get_nested(data, ["before_click", "available_before_click_count"], None)
    after_click = get_nested(data, ["after_click", "available_after_click_count"], None)
    return {
        "summary": "Project has pre-click and post-click JSON sources; Final Clear_JSON must remain optional for postflop source discovery.",
        "total_json_files": total,
        "by_source_type": by_type,
        "available_before_click_count": before_click,
        "available_after_click_count": after_click,
        "final_clear_json_optional": True,
        "recommended_v020_source_types": V020_SOURCE_TYPES,
    }


def summarize_player_state(data: Mapping[str, Any]) -> Dict[str, Any]:
    total_files = get_nested(data, ["total_files_scanned", "files_scanned"], None)
    mechanisms = get_nested(data, ["mechanisms_found", "total_mechanisms"], None)
    by_logic = get_nested(data, ["by_logic_type", "logic_type_counts"], {}) or {}
    should_not_duplicate = get_nested(data, ["should_not_duplicate", "should_not_duplicate_count"], None)
    return {
        "summary": "Existing project contains substantial player-state/filtering logic; postflop resolver must adapt rather than duplicate it.",
        "total_files_scanned": total_files,
        "mechanisms_found": mechanisms,
        "by_logic_type": by_logic,
        "should_not_duplicate_count": should_not_duplicate,
        "postflop_rule": "Do not re-implement HERO/sitout/all-in/active/clear-state filtering without explicit adapter contract.",
    }


def build_final_report(project_root: Path) -> Dict[str, Any]:
    source_reports = load_source_reports(project_root)
    missing_or_failed = [
        {"key": key, "path": item.path, "error": item.error}
        for key, item in source_reports.items()
        if not item.loaded
    ]
    project = source_reports["project_baseline"].data
    tests = source_reports["test_suite_health"].data
    json_sources = source_reports["json_source_map"].data
    player_state = source_reports["player_state_filtering"].data

    git = {
        "branch": run_git_command(project_root, ["branch", "--show-current"]),
        "head": run_git_command(project_root, ["rev-parse", "--short", "HEAD"]),
        "status_short": run_git_command(project_root, ["status", "--short"]),
        "recent_commits": run_git_command(project_root, ["log", "--oneline", "-6"]),
    }

    report = {
        "schema_version": "v010_final_report.1",
        "version": "V0.1.5",
        "title": "Final V0.1 Baseline Audit Report / Plan to V0.2",
        "generated_at_utc": utc_now_iso(),
        "project_root": str(project_root),
        "git": git,
        "source_report_status": {
            key: {
                "path": item.path,
                "exists": item.exists,
                "loaded": item.loaded,
                "error": item.error,
            }
            for key, item in source_reports.items()
        },
        "missing_or_failed_source_reports": missing_or_failed,
        "v010_findings": {
            "project_identity": summarize_project_baseline(project),
            "test_suite": summarize_test_suite(tests),
            "json_source_map": summarize_json_sources(json_sources),
            "player_state_filtering": summarize_player_state(player_state),
        },
        "postflop_development_rules": [
            "Do not build postflop only on Final Clear_JSON; support intermediate pre-click source JSON.",
            "Do not duplicate existing player-state filtering; adapt/check already cleaned PokerVision data.",
            "Do not make legacy/live-only tests automatic postflop blockers.",
            "V0.2 must create fixture lab and manifest only, not solver logic.",
            "manual_live_like_json must be explicitly separated from real project source JSON.",
        ],
        "v020_plan": {
            "version": "V0.2.0",
            "title": "Source-Based Postflop Fixture Lab",
            "must_create": [
                "docs/POSTFLOP_FIXTURE_STRATEGY.md",
                "docs/POSTFLOP_SOURCE_TYPES.md",
                "docs/POSTFLOP_FIXTURE_MANIFEST_RULES.md",
                "tests/fixtures/postflop/manifest.json",
                "tests/fixtures/postflop/source_json/",
                "tests/fixtures/postflop/live_like_tree/",
                "tests/fixtures/postflop/normalized/",
                "tests/fixtures/postflop/expected/",
                "tests/test_postflop_fixture_manifest_v020.py",
                "tests/test_postflop_fixture_structure_v020.py",
                "tests/test_postflop_source_fixture_types_v020.py",
            ],
            "allowed_source_types": V020_SOURCE_TYPES,
            "final_clear_json_required": False,
            "manual_live_like_json_rule": "Must be marked as manual and never presented as real-source.",
            "must_not_do": [
                "postflop solver",
                "normalizer",
                "source discovery",
                "player resolver",
                "equity",
                "ranges",
                "poker decisions",
                "runtime click plan",
                "clicking",
                "runtime changes",
            ],
        },
        "readiness_decision": {
            "v010_closed_when_reports_loaded": len(missing_or_failed) == 0,
            "ready_for_v020_design": len(missing_or_failed) == 0,
            "notes": "V0.1 closes baseline/test/source/player-state audit. V0.2 can start fixture lab if all four source reports are loaded.",
        },
    }
    return report


def markdown_table_from_mapping(mapping: Mapping[str, Any]) -> str:
    if not mapping:
        return "_No data._"
    lines = ["| Key | Value |", "|---|---:|"]
    for key in sorted(mapping):
        lines.append(f"| `{key}` | {mapping[key]} |")
    return "\n".join(lines)


def render_final_markdown(report: Mapping[str, Any]) -> str:
    findings = report["v010_findings"]
    project = findings["project_identity"]
    tests = findings["test_suite"]
    json_map = findings["json_source_map"]
    player = findings["player_state_filtering"]
    rules = report["postflop_development_rules"]
    readiness = report["readiness_decision"]

    return f"""# V0.1.5 — Final V0.1 Baseline Audit Report

## Status

**Version:** {report['version']}  
**Generated:** {report['generated_at_utc']}  
**Git HEAD:** `{report['git']['head']}`  
**Branch:** `{report['git']['branch']}`

## Executive Summary

V0.1.0 closed the initial baseline/test/source audit block for **PokerVision_Solver_AllPreflop_Flop**.
The project is ready to plan **V0.2.0 — Source-Based Postflop Fixture Lab** only as a fixture/documentation/test-structure version, not as solver logic.

## Project Identity Findings

{project['summary']}

**Risk flags count:** {project.get('risk_flags_count')}

## Test Suite Findings

{tests['summary']}

**Total test files:** {tests.get('total_test_files')}

### By category

{markdown_table_from_mapping(tests.get('by_category', {}))}

### By recommended action

{markdown_table_from_mapping(tests.get('by_recommended_action', {}))}

## JSON Source Map Findings

{json_map['summary']}

**Total JSON files:** {json_map.get('total_json_files')}  
**Before click:** {json_map.get('available_before_click_count')}  
**After click:** {json_map.get('available_after_click_count')}  
**Final Clear_JSON optional:** {json_map.get('final_clear_json_optional')}

### By source type

{markdown_table_from_mapping(json_map.get('by_source_type', {}))}

## Player-State / Filtering Findings

{player['summary']}

**Files scanned:** {player.get('total_files_scanned')}  
**Mechanisms found:** {player.get('mechanisms_found')}  
**Should not duplicate:** {player.get('should_not_duplicate_count')}

### By logic type

{markdown_table_from_mapping(player.get('by_logic_type', {}))}

## Postflop Development Rules

""" + "\n".join(f"- **{rule}**" for rule in rules) + f"""

## Key Risks

- Building postflop only from Final Clear_JSON would be unsafe because pre-click JSON sources already exist and Final Clear_JSON may depend on click-cycle.
- Duplicating HERO/sitout/all-in/player filtering may conflict with existing PokerVision logic.
- Treating legacy/live-only tests as strict blockers may freeze development incorrectly.
- Manual live-like fixtures must never be mixed with real project source files without explicit metadata.

## Readiness Decision

**V0.1 reports loaded:** {readiness['v010_closed_when_reports_loaded']}  
**Ready for V0.2 design:** {readiness['ready_for_v020_design']}

## Next Version

**V0.2.0 — Source-Based Postflop Fixture Lab**
"""


def render_v020_plan_markdown(report: Mapping[str, Any]) -> str:
    plan = report["v020_plan"]
    return "# V0.2.0 — Source-Based Postflop Fixture Lab Plan\n\n" + f"""
## Goal

Create a source-based postflop fixture lab connected to real PokerVision JSON source types.
This version must not implement solver logic, normalizer, source discovery, player resolver, equity, ranges, poker decisions, runtime click plans, clicking, or runtime changes.

## Required files / folders

""" + "\n".join(f"- `{item}`" for item in plan["must_create"]) + "\n\n## Allowed source_type values\n\n" + "\n".join(f"- `{item}`" for item in plan["allowed_source_types"]) + f"""

## Mandatory rules

- **Final Clear_JSON is not required:** `{plan['final_clear_json_required']}`.
- **manual_live_like_json rule:** {plan['manual_live_like_json_rule']}
- Each fixture case must have `case_id`, `source_type`, `source_file`, `expected_file`, `status`, and source truth metadata.
- `manual_live_like_json` must use `is_manual_live_like_source = true`.
- Real project source JSON must use `is_real_project_source = true` only when it actually comes from project outputs.

## Must not do in V0.2

""" + "\n".join(f"- {item}" for item in plan["must_not_do"]) + "\n"


def write_outputs(project_root: Path, report: Mapping[str, Any]) -> Dict[str, str]:
    out_dir = project_root / REPORT_DIR
    docs_dir = project_root / DOCS_REPORT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    final_json = out_dir / FINAL_JSON_NAME
    final_md = docs_dir / FINAL_MD_NAME
    plan_md = docs_dir / PLAN_MD_NAME

    final_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    final_md.write_text(render_final_markdown(report), encoding="utf-8")
    plan_md.write_text(render_v020_plan_markdown(report), encoding="utf-8")

    return {
        "final_json": str(final_json),
        "final_markdown": str(final_md),
        "v020_plan_markdown": str(plan_md),
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build final V0.1 report and V0.2 plan.")
    parser.add_argument("--project-root", default=".", help="Project root. Default: current directory")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    report = build_final_report(project_root)
    paths = write_outputs(project_root, report)

    print("[V0.1.5] Final V0.1 report completed")
    print(f"JSON report: {paths['final_json']}")
    print(f"Markdown report: {paths['final_markdown']}")
    print(f"V0.2 plan: {paths['v020_plan_markdown']}")
    print(f"Ready for V0.2 design: {report['readiness_decision']['ready_for_v020_design']}")
    return 0 if report["readiness_decision"]["v010_closed_when_reports_loaded"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
