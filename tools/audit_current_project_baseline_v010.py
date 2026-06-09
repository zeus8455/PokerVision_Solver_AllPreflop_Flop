"""V0.1.1 project baseline audit for PokerVision_Solver_AllPreflop_Flop.

This script is intentionally read-only for the project source tree. It inspects
repository identity, Git state, expected folders, README/VERSION mismatch, the
preflop baseline, and the external PokerVision snapshot. It writes one JSON
report and one Markdown report for the V0.1.0 baseline audit block.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "v010_project_baseline_audit_1"
VERSION_LABEL = "V0.1.1"
PROJECT_REPO_NAME = "PokerVision_Solver_AllPreflop_Flop"
LEGACY_README_NAME = "PokerVision_Solver_Preflop"
DEFAULT_REPORT_DIR = Path("outputs") / "baseline_audit_v010"
DEFAULT_DOCS_DIR = Path("docs") / "reports"

EXPECTED_TOP_LEVEL_PATHS = [
    "solver_preflop",
    "external",
    "tests",
    "tools",
    "outputs",
    "ranges",
    "examples/clear_json",
    "docs",
    "docs/checkpoints",
]

EXPECTED_ROOT_FILES = [
    "README.md",
    "VERSION.md",
    "pyproject.toml",
    ".gitignore",
]

PREFLOP_BASELINE_MODULES = [
    "solver_preflop/__init__.py",
    "solver_preflop/clear_json_adapter.py",
    "solver_preflop/contracts.py",
    "solver_preflop/decision_engine.py",
    "solver_preflop/output_files.py",
    "solver_preflop/pokervision_bridge.py",
    "solver_preflop/range_engine.py",
    "solver_preflop/range_loader.py",
    "solver_preflop/range_parser.py",
    "solver_preflop/sizing_policy.py",
    "solver_preflop/spot_classifier.py",
]

POSTFLOP_CORE_CANDIDATES = [
    "solver_postflop",
    "postflop_solver",
    "solver_flop",
    "postflop",
    "normalizer",
    "player_resolver",
    "source_discovery",
    "equity",
]

EXTERNAL_SNAPSHOT_PATHS = [
    "external/PokerVisionFinalVersionNoSolver_snapshot",
    "external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2",
]


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    value: str


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _normalize_path(path: Path | str) -> str:
    return Path(path).as_posix()


def find_project_root(start: Path | None = None) -> Path:
    """Find a likely project root from the current directory or script path."""
    current = (start or Path.cwd()).resolve()
    candidates = [current, *current.parents]
    for candidate in candidates:
        if (candidate / ".git").exists() and (candidate / "pyproject.toml").exists():
            return candidate
    for candidate in candidates:
        if (candidate / "README.md").exists() and (candidate / "solver_preflop").exists():
            return candidate
    return current


def run_git(project_root: Path, args: list[str]) -> CommandResult:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=project_root,
            text=True,
            capture_output=True,
            check=False,
            timeout=15,
        )
    except Exception as exc:  # pragma: no cover - platform dependent
        return CommandResult(False, f"git command failed: {exc}")
    output = completed.stdout.strip() or completed.stderr.strip()
    return CommandResult(completed.returncode == 0, output)


def read_text_safe(path: Path, max_chars: int = 200_000) -> str:
    if not path.exists() or not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except Exception:
        return ""


def list_python_files(path: Path) -> list[str]:
    if not path.exists():
        return []
    return sorted(_normalize_path(p.relative_to(path.parent)) for p in path.rglob("*.py"))


def extract_version_headings(version_text: str, limit: int = 20) -> list[str]:
    headings: list[str] = []
    for line in version_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^#{1,6}\s+", stripped) or re.search(r"\bV\d+(?:\.\d+){1,3}\b", stripped):
            if stripped not in headings:
                headings.append(stripped)
    return headings[:limit]


def classify_readme_identity(readme_text: str) -> dict[str, Any]:
    lower = readme_text.lower()
    contains_new_name = PROJECT_REPO_NAME.lower() in lower
    contains_legacy_name = LEGACY_README_NAME.lower() in lower
    contains_legacy_path = "c:\\pokervision_solver_preflop".lower() in lower
    contains_postflop_terms = any(term in lower for term in ["postflop", "flop", "turn", "river"])
    return {
        "readme_exists": bool(readme_text),
        "contains_expected_repo_name": contains_new_name,
        "contains_legacy_preflop_name": contains_legacy_name,
        "contains_legacy_preflop_path": contains_legacy_path,
        "contains_postflop_terms": contains_postflop_terms,
        "identity_mismatch_detected": contains_legacy_name and not contains_new_name,
    }


def build_presence_map(project_root: Path, relative_paths: Iterable[str]) -> dict[str, bool]:
    return {relative: (project_root / relative).exists() for relative in relative_paths}


def build_git_state(project_root: Path) -> dict[str, Any]:
    branch = run_git(project_root, ["branch", "--show-current"])
    head = run_git(project_root, ["rev-parse", "--short", "HEAD"])
    full_head = run_git(project_root, ["rev-parse", "HEAD"])
    remote = run_git(project_root, ["remote", "get-url", "origin"])
    status = run_git(project_root, ["status", "--short"])
    log = run_git(project_root, ["log", "--oneline", "-5"])
    return {
        "git_available": all([branch.ok or head.ok or status.ok]),
        "current_branch": branch.value if branch.ok else None,
        "head_commit_short": head.value if head.ok else None,
        "head_commit_full": full_head.value if full_head.ok else None,
        "origin_url": remote.value if remote.ok else None,
        "status_short": status.value.splitlines() if status.ok and status.value else [],
        "working_tree_clean": status.ok and not bool(status.value.strip()),
        "recent_commits": log.value.splitlines() if log.ok and log.value else [],
        "errors": {
            "branch": None if branch.ok else branch.value,
            "head": None if head.ok else head.value,
            "remote": None if remote.ok else remote.value,
            "status": None if status.ok else status.value,
        },
    }


def build_risk_flags(report: dict[str, Any]) -> list[dict[str, str]]:
    flags: list[dict[str, str]] = []

    def add(code: str, severity: str, message: str) -> None:
        flags.append({"code": code, "severity": severity, "message": message})

    if report["readme_identity_check"]["identity_mismatch_detected"]:
        add(
            "README_IDENTITY_MISMATCH",
            "medium",
            "Repository is AllPreflop_Flop, but README still identifies the project as PokerVision_Solver_Preflop.",
        )
    if report["preflop_baseline_presence"]["present_count"] > 0:
        add(
            "PREFLOP_BASELINE_PRESENT",
            "info",
            "Preflop solver baseline modules are present and should be treated as source baseline, not postflop implementation.",
        )
    if report["postflop_core_presence"]["present_count"] == 0:
        add(
            "POSTFLOP_CORE_NOT_PRESENT",
            "info",
            "No dedicated postflop solver/core directories were detected yet.",
        )
    if report["external_snapshot_presence"]["present_count"] > 0:
        add(
            "EXTERNAL_SNAPSHOT_PRESENT",
            "info",
            "External PokerVision NoSolver snapshot is present; do not modify it casually during V0.1.x audit.",
        )
    missing_dirs = report["directory_presence"]["missing"]
    if missing_dirs:
        add(
            "EXPECTED_DIRS_MISSING",
            "low",
            "Some expected baseline directories are missing: " + ", ".join(missing_dirs),
        )
    if report["git_state"].get("working_tree_clean") is False:
        add(
            "WORKING_TREE_NOT_CLEAN",
            "medium",
            "Git working tree has uncommitted changes; commit/stash before development steps if needed.",
        )
    return flags


def build_report(project_root: Path) -> dict[str, Any]:
    project_root = project_root.resolve()
    readme_text = read_text_safe(project_root / "README.md")
    version_text = read_text_safe(project_root / "VERSION.md")

    dir_map = build_presence_map(project_root, EXPECTED_TOP_LEVEL_PATHS)
    root_file_map = build_presence_map(project_root, EXPECTED_ROOT_FILES)
    preflop_map = build_presence_map(project_root, PREFLOP_BASELINE_MODULES)
    postflop_map = build_presence_map(project_root, POSTFLOP_CORE_CANDIDATES)
    external_map = build_presence_map(project_root, EXTERNAL_SNAPSHOT_PATHS)

    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "version_label": VERSION_LABEL,
        "generated_at_utc": _utc_now_iso(),
        "project_root": str(project_root),
        "repo_identity": {
            "expected_repo_name": PROJECT_REPO_NAME,
            "project_root_name": project_root.name,
            "matches_expected_name": project_root.name == PROJECT_REPO_NAME,
        },
        "git_state": build_git_state(project_root),
        "root_file_presence": {
            "expected": EXPECTED_ROOT_FILES,
            "present": [p for p, ok in root_file_map.items() if ok],
            "missing": [p for p, ok in root_file_map.items() if not ok],
            "presence_map": root_file_map,
        },
        "directory_presence": {
            "expected": EXPECTED_TOP_LEVEL_PATHS,
            "present": [p for p, ok in dir_map.items() if ok],
            "missing": [p for p, ok in dir_map.items() if not ok],
            "presence_map": dir_map,
        },
        "readme_identity_check": classify_readme_identity(readme_text),
        "version_history_check": {
            "version_file_exists": bool(version_text),
            "first_detected_headings": extract_version_headings(version_text, limit=25),
            "mentions_v2_60": "V2.60" in version_text or "V2.60.0" in version_text,
            "mentions_fixture_review": "fixture" in version_text.lower(),
        },
        "preflop_baseline_presence": {
            "expected_modules": PREFLOP_BASELINE_MODULES,
            "present": [p for p, ok in preflop_map.items() if ok],
            "missing": [p for p, ok in preflop_map.items() if not ok],
            "present_count": sum(1 for ok in preflop_map.values() if ok),
            "missing_count": sum(1 for ok in preflop_map.values() if not ok),
            "presence_map": preflop_map,
        },
        "postflop_core_presence": {
            "candidate_paths": POSTFLOP_CORE_CANDIDATES,
            "present": [p for p, ok in postflop_map.items() if ok],
            "missing": [p for p, ok in postflop_map.items() if not ok],
            "present_count": sum(1 for ok in postflop_map.values() if ok),
        },
        "external_snapshot_presence": {
            "candidate_paths": EXTERNAL_SNAPSHOT_PATHS,
            "present": [p for p, ok in external_map.items() if ok],
            "missing": [p for p, ok in external_map.items() if not ok],
            "present_count": sum(1 for ok in external_map.values() if ok),
            "presence_map": external_map,
        },
        "observed_python_files": {
            "solver_preflop": list_python_files(project_root / "solver_preflop"),
            "tools_count": len(list((project_root / "tools").glob("*.py"))) if (project_root / "tools").exists() else 0,
            "tests_count": len(list((project_root / "tests").glob("test*.py"))) if (project_root / "tests").exists() else 0,
        },
        "recommended_next_action": "Run V0.1.2 Test Suite Health Audit after this baseline identity audit is committed.",
    }
    report["risk_flags"] = build_risk_flags(report)
    report["status"] = "ok"
    return report


def render_markdown(report: dict[str, Any]) -> str:
    def yes_no(value: bool) -> str:
        return "yes" if value else "no"

    risk_lines = "\n".join(
        f"- **{flag['code']}** [{flag['severity']}]: {flag['message']}" for flag in report["risk_flags"]
    ) or "- No risk flags detected."

    dir_lines = "\n".join(f"- `{p}`" for p in report["directory_presence"]["present"]) or "- none"
    missing_dir_lines = "\n".join(f"- `{p}`" for p in report["directory_presence"]["missing"]) or "- none"
    preflop_lines = "\n".join(f"- `{p}`" for p in report["preflop_baseline_presence"]["present"]) or "- none"
    postflop_lines = "\n".join(f"- `{p}`" for p in report["postflop_core_presence"]["present"]) or "- none"
    external_lines = "\n".join(f"- `{p}`" for p in report["external_snapshot_presence"]["present"]) or "- none"
    status_lines = "\n".join(f"- `{line}`" for line in report["git_state"]["status_short"]) or "- clean"
    version_lines = "\n".join(f"- {line}" for line in report["version_history_check"]["first_detected_headings"][:15]) or "- none"

    return f"""# V0.1.1 — Repo Identity / Baseline Audit

Generated at UTC: `{report['generated_at_utc']}`

## Summary

This report is the first baseline audit artifact for the V0.1.0 audit block. It does not validate postflop poker logic. It records the current repository identity, Git state, directory layout, README/VERSION identity signals, preflop baseline presence, and external snapshot presence.

## Repository identity

- Expected repo name: `{report['repo_identity']['expected_repo_name']}`
- Project root name: `{report['repo_identity']['project_root_name']}`
- Root name matches expected: **{yes_no(report['repo_identity']['matches_expected_name'])}**
- Project root: `{report['project_root']}`

## Git state

- Branch: `{report['git_state'].get('current_branch')}`
- HEAD short: `{report['git_state'].get('head_commit_short')}`
- Origin: `{report['git_state'].get('origin_url')}`
- Working tree clean: **{yes_no(report['git_state'].get('working_tree_clean'))}**

### Git status --short

{status_lines}

## README identity check

- README exists: **{yes_no(report['readme_identity_check']['readme_exists'])}**
- Contains expected repo name: **{yes_no(report['readme_identity_check']['contains_expected_repo_name'])}**
- Contains legacy preflop name: **{yes_no(report['readme_identity_check']['contains_legacy_preflop_name'])}**
- Contains legacy preflop path: **{yes_no(report['readme_identity_check']['contains_legacy_preflop_path'])}**
- Identity mismatch detected: **{yes_no(report['readme_identity_check']['identity_mismatch_detected'])}**

## Directory presence

### Present

{dir_lines}

### Missing

{missing_dir_lines}

## Preflop baseline presence

Present modules: **{report['preflop_baseline_presence']['present_count']}** / **{len(report['preflop_baseline_presence']['expected_modules'])}**

{preflop_lines}

## Postflop core presence

Dedicated postflop core candidates detected: **{report['postflop_core_presence']['present_count']}**

{postflop_lines}

## External snapshot presence

{external_lines}

## VERSION.md signals

- VERSION.md exists: **{yes_no(report['version_history_check']['version_file_exists'])}**
- Mentions V2.60: **{yes_no(report['version_history_check']['mentions_v2_60'])}**
- Mentions fixture review: **{yes_no(report['version_history_check']['mentions_fixture_review'])}**

### First detected version headings/signals

{version_lines}

## Risk flags

{risk_lines}

## V0.1.1 conclusion

Current project state should be treated as an **AllPreflop_Flop repository identity with a legacy/preflop README and preflop solver baseline still present**. This is expected for V0.1.x and should not be fixed blindly before test, JSON-source, and player-state audits are complete.

## Recommended next action

{report['recommended_next_action']}
"""


def write_reports(report: dict[str, Any], project_root: Path) -> dict[str, str]:
    json_path = project_root / DEFAULT_REPORT_DIR / "project_baseline_report.json"
    md_path = project_root / DEFAULT_DOCS_DIR / "current_project_baseline_audit_v010.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return {"json_report": str(json_path), "markdown_report": str(md_path)}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V0.1.1 project baseline audit.")
    parser.add_argument(
        "--project-root",
        default=None,
        help="Project root to audit. Defaults to auto-detection from current directory.",
    )
    parser.add_argument(
        "--print-json",
        action="store_true",
        help="Print the generated report JSON to stdout after writing files.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    project_root = find_project_root(Path(args.project_root).resolve() if args.project_root else None)
    report = build_report(project_root)
    paths = write_reports(report, project_root)
    report["written_files"] = paths

    if args.print_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"[{VERSION_LABEL}] Project baseline audit completed")
        print(f"JSON report: {paths['json_report']}")
        print(f"Markdown report: {paths['markdown_report']}")
        print(f"Risk flags: {len(report['risk_flags'])}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
