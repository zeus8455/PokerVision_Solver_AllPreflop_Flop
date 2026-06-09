from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "v0.1.4-player-state-filtering"
REPORT_DIR = Path("outputs") / "baseline_audit_v010"
DOCS_DIR = Path("docs") / "reports"
JSON_REPORT_NAME = "player_state_filtering_report.json"
MARKDOWN_REPORT_NAME = "current_player_state_filtering_audit_v010.md"

AUDIT_ONLY_POLICY = {
    "version": "V0.1.4",
    "audit_only": True,
    "postflop_solver_must_not_duplicate_existing_player_state_filtering": True,
    "runtime_and_click_chain_must_not_be_modified": True,
    "player_resolver_is_not_implemented_in_this_version": True,
}

SCAN_SUFFIXES = {".py", ".json", ".md", ".txt", ".yaml", ".yml"}
SKIP_DIR_PARTS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    "venv",
    ".venv",
    "env",
    "node_modules",
}

LOGIC_KEYWORDS: dict[str, list[str]] = {
    "sitout_filtering": [
        "sitout",
        "sit_out",
        "sitting_out",
        "sitting out",
        "logical_sitout",
        "remove_table",
        "remove_game",
    ],
    "all_in_state": [
        "all_in",
        "all-in",
        "allin",
        "is_all_in",
        "player_all_in",
    ],
    "hero_detection": [
        "hero",
        "hero_cards",
        "is_hero",
        "hero_seat",
        "hero_position",
    ],
    "active_player_state": [
        "active_player",
        "active seat",
        "active_spot",
        "player_to_act",
        "to_act",
        "acting_player",
        "active_confirmed",
        "active_cycle",
    ],
    "trigger_service_state": [
        "trigger_ui",
        "trigger ui",
        "service_json",
        "service state",
        "table_status",
        "no_active_confirmed",
        "service diagnostic",
        "trigger_ui_block",
    ],
    "clear_json_filtering": [
        "clear_json_pending",
        "clear json pending",
        "clear_json",
        "clear state",
        "before clear_json",
        "dark_json",
    ],
    "final_clear_json_filtering": [
        "final_clear_json",
        "final clear_json",
        "json_complete",
        "click_result",
        "finalize",
        "finalized",
    ],
    "player_exclusion_logic": [
        "ignored",
        "ignore_player",
        "excluded",
        "exclude_player",
        "removed_player",
        "remove_player",
        "filter_players",
        "players_to_ignore",
    ],
    "fold_filtering": [
        "folded",
        "is_folded",
        "fold:false",
        "fold true",
        "folded_players",
        "player_folded",
        "fold_status",
    ],
    "unknown_player_state_logic": [
        "player_state",
        "players_state",
        "player status",
        "state_filter",
        "table player",
    ],
}

LOGIC_PRIORITY = [
    "sitout_filtering",
    "all_in_state",
    "hero_detection",
    "active_player_state",
    "trigger_service_state",
    "clear_json_filtering",
    "final_clear_json_filtering",
    "player_exclusion_logic",
    "fold_filtering",
    "unknown_player_state_logic",
]

LOGIC_DESCRIPTIONS = {
    "fold_filtering": "Detects or filters players based on folded state.",
    "sitout_filtering": "Detects or filters players based on sitout/sitting-out state.",
    "all_in_state": "Tracks all-in state; these players must not be treated as folded automatically.",
    "hero_detection": "Detects HERO identity, cards, seat, or position.",
    "active_player_state": "Tracks active player/active spot/table-to-act state.",
    "trigger_service_state": "Tracks Trigger_UI/service/table status state used before analysis or click-cycle.",
    "clear_json_filtering": "Touches player/table state before or while producing Clear_JSON/Clear_JSON_Pending/Dark_JSON.",
    "final_clear_json_filtering": "Touches finalization, JSON_Complete, or click_result after click-cycle/final clear generation.",
    "player_exclusion_logic": "Excludes, ignores, removes, or filters players from further processing.",
    "unknown_player_state_logic": "Contains player-state markers but needs manual review.",
}

SOURCE_OF_TRUTH_HINTS = [
    "clear_json",
    "final_clear_json",
    "json_complete",
    "trigger_ui",
    "table_status",
    "player_state",
    "service_json",
]

OUTPUT_HINTS = [
    "write_text",
    "json.dump",
    "json.dumps",
    "open(",
    "save_json",
    "output",
    "outputs",
]

INPUT_HINTS = [
    "json.load",
    "json.loads",
    "read_text",
    "open(",
    "load_json",
    "input",
    "source",
]


def normalize_text(text: str) -> str:
    return text.replace("-", "_").lower()


def _keyword_hits(text: str, keywords: list[str]) -> list[str]:
    low = normalize_text(text)
    hits: list[str] = []
    for keyword in keywords:
        needle = normalize_text(keyword)
        if needle in low:
            hits.append(keyword)
    return sorted(set(hits))


def classify_logic_types(path: str | Path, text: str) -> list[str]:
    joined = f"{Path(path).as_posix()}\n{text}"
    matched = [logic_type for logic_type in LOGIC_PRIORITY if _keyword_hits(joined, LOGIC_KEYWORDS[logic_type])]
    return matched or []


def matched_keywords_for_logic(path: str | Path, text: str, logic_type: str) -> list[str]:
    joined = f"{Path(path).as_posix()}\n{text}"
    return _keyword_hits(joined, LOGIC_KEYWORDS.get(logic_type, []))


def primary_logic_type(path: str | Path, text: str) -> str | None:
    matches = classify_logic_types(path, text)
    return matches[0] if matches else None


def infer_io_hints(text: str) -> tuple[list[str], list[str]]:
    low = text.lower()
    input_hints = sorted({hint for hint in INPUT_HINTS if hint.lower() in low})
    output_hints = sorted({hint for hint in OUTPUT_HINTS if hint.lower() in low})
    json_names = sorted(
        {
            name
            for name in [
                "Dark_JSON",
                "Clear_JSON",
                "Clear_JSON_Pending",
                "Final Clear_JSON",
                "JSON_Complete",
                "service JSON",
                "current_cycle JSON",
                "solver payload JSON",
                "click_result",
            ]
            if name.lower().replace(" ", "_") in low.replace(" ", "_")
        }
    )
    return input_hints + json_names, output_hints + json_names


def risk_for_logic(logic_type: str, text: str) -> str:
    low = text.lower()
    if logic_type in {"sitout_filtering", "all_in_state", "hero_detection", "final_clear_json_filtering"}:
        return "high"
    if "click_result" in low or "json_complete" in low or "final_clear" in low:
        return "high"
    if logic_type in {"trigger_service_state", "active_player_state", "clear_json_filtering", "player_exclusion_logic"}:
        return "medium"
    return "medium" if logic_type != "unknown_player_state_logic" else "needs_manual_review"


def is_source_of_truth_candidate(path: str | Path, logic_type: str, text: str) -> bool:
    low = f"{Path(path).as_posix()}\n{text}".lower()
    if logic_type in {"clear_json_filtering", "final_clear_json_filtering", "trigger_service_state"}:
        return True
    return any(hint in low for hint in SOURCE_OF_TRUTH_HINTS)


def should_reuse_by_postflop(logic_type: str) -> bool:
    return logic_type in {
        "sitout_filtering",
        "all_in_state",
        "hero_detection",
        "active_player_state",
        "trigger_service_state",
        "clear_json_filtering",
        "final_clear_json_filtering",
        "player_exclusion_logic",
        "fold_filtering",
    }


def should_not_duplicate(logic_type: str) -> bool:
    return logic_type in {
        "sitout_filtering",
        "all_in_state",
        "hero_detection",
        "active_player_state",
        "trigger_service_state",
        "clear_json_filtering",
        "final_clear_json_filtering",
        "player_exclusion_logic",
    }


def _line_span(source: str, node: ast.AST) -> tuple[int | None, int | None]:
    return getattr(node, "lineno", None), getattr(node, "end_lineno", None)


def _source_segment(source: str, node: ast.AST) -> str:
    try:
        return ast.get_source_segment(source, node) or ""
    except Exception:
        return ""


def mechanism_record(
    *,
    root: Path,
    file_path: Path,
    function_or_class_name: str,
    object_type: str,
    logic_type: str,
    text: str,
    line_start: int | None = None,
    line_end: int | None = None,
) -> dict[str, Any]:
    relative = file_path.relative_to(root).as_posix() if file_path.is_relative_to(root) else file_path.as_posix()
    input_hints, output_hints = infer_io_hints(text)
    return {
        "file_path": relative,
        "function_or_class_name": function_or_class_name,
        "object_type": object_type,
        "logic_type": logic_type,
        "matched_logic_types": classify_logic_types(relative, text),
        "matched_keywords": matched_keywords_for_logic(relative, text, logic_type),
        "what_it_does": LOGIC_DESCRIPTIONS.get(logic_type, LOGIC_DESCRIPTIONS["unknown_player_state_logic"]),
        "input_files_or_json": input_hints,
        "output_files_or_json": output_hints,
        "is_source_of_truth": is_source_of_truth_candidate(relative, logic_type, text),
        "can_be_reused_by_postflop": should_reuse_by_postflop(logic_type),
        "should_not_be_duplicated": should_not_duplicate(logic_type),
        "risk_if_modified": risk_for_logic(logic_type, text),
        "line_start": line_start,
        "line_end": line_end,
        "notes": build_notes(logic_type, text),
    }


def build_notes(logic_type: str, text: str) -> str:
    notes: list[str] = []
    low = text.lower()
    if logic_type == "all_in_state":
        notes.append("All-in state should be preserved; do not treat it as fold state.")
    if logic_type == "sitout_filtering":
        notes.append("Sitout filtering is a core player-state mechanism and should not be duplicated blindly.")
    if logic_type == "hero_detection":
        notes.append("HERO identity/cards should be imported or verified, not invented by postflop code.")
    if "click_result" in low:
        notes.append("This mechanism appears to be post-click/finalization related.")
    if "clear_json_pending" in low or "dark_json" in low:
        notes.append("This mechanism may affect pre-click sources used by future source discovery.")
    if not notes:
        notes.append("Needs review before postflop module reuses or bypasses this logic.")
    return " ".join(notes)


def should_scan_path(path: Path) -> bool:
    if any(part in SKIP_DIR_PARTS for part in path.parts):
        return False
    if path.suffix.lower() not in SCAN_SUFFIXES:
        return False
    if path.name == JSON_REPORT_NAME or path.name == MARKDOWN_REPORT_NAME:
        return False
    return True


def scan_python_file(path: Path, root: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    mechanisms: list[dict[str, Any]] = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        logic_type = primary_logic_type(path, text)
        if logic_type:
            mechanisms.append(
                mechanism_record(
                    root=root,
                    file_path=path,
                    function_or_class_name="<syntax_error_file_level>",
                    object_type="file",
                    logic_type=logic_type,
                    text=text,
                )
            )
        return mechanisms

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            segment = _source_segment(text, node)
            logic_type = primary_logic_type(path, segment)
            if not logic_type:
                continue
            start, end = _line_span(text, node)
            mechanisms.append(
                mechanism_record(
                    root=root,
                    file_path=path,
                    function_or_class_name=getattr(node, "name", "<unknown>"),
                    object_type="class" if isinstance(node, ast.ClassDef) else "function",
                    logic_type=logic_type,
                    text=segment,
                    line_start=start,
                    line_end=end,
                )
            )

    if not mechanisms:
        logic_type = primary_logic_type(path, text)
        if logic_type:
            mechanisms.append(
                mechanism_record(
                    root=root,
                    file_path=path,
                    function_or_class_name="<file_level>",
                    object_type="file",
                    logic_type=logic_type,
                    text=text,
                )
            )
    return mechanisms


def scan_text_or_json_file(path: Path, root: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    logic_type = primary_logic_type(path, text)
    if not logic_type:
        return []
    return [
        mechanism_record(
            root=root,
            file_path=path,
            function_or_class_name="<file_level>",
            object_type="file",
            logic_type=logic_type,
            text=text,
        )
    ]


def scan_file(path: Path, root: Path) -> list[dict[str, Any]]:
    try:
        if path.suffix.lower() == ".py":
            return scan_python_file(path, root)
        return scan_text_or_json_file(path, root)
    except OSError:
        return []


def git_value(root: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
        if result.returncode != 0:
            return result.stderr.strip() or result.stdout.strip() or "unavailable"
        return result.stdout.strip()
    except Exception as exc:  # pragma: no cover - defensive for machines without git
        return f"unavailable: {exc}"


def summarize(mechanisms: list[dict[str, Any]], scanned_files: int) -> dict[str, Any]:
    by_logic_type = Counter(item["logic_type"] for item in mechanisms)
    by_risk = Counter(item["risk_if_modified"] for item in mechanisms)
    source_of_truth = sum(1 for item in mechanisms if item["is_source_of_truth"])
    reusable = sum(1 for item in mechanisms if item["can_be_reused_by_postflop"])
    do_not_duplicate = sum(1 for item in mechanisms if item["should_not_be_duplicated"])
    return {
        "total_files_scanned": scanned_files,
        "total_mechanisms_found": len(mechanisms),
        "by_logic_type": dict(sorted(by_logic_type.items())),
        "by_risk_if_modified": dict(sorted(by_risk.items())),
        "source_of_truth_candidates": source_of_truth,
        "can_be_reused_by_postflop_candidates": reusable,
        "should_not_be_duplicated_candidates": do_not_duplicate,
    }


def build_report(root: str | Path) -> dict[str, Any]:
    root = Path(root).resolve()
    mechanisms: list[dict[str, Any]] = []
    scanned_files = 0

    for path in sorted(root.rglob("*")):
        if not path.is_file() or not should_scan_path(path):
            continue
        scanned_files += 1
        mechanisms.extend(scan_file(path, root))

    mechanisms = sorted(
        mechanisms,
        key=lambda item: (
            item["file_path"],
            item["line_start"] if item["line_start"] is not None else 0,
            item["function_or_class_name"],
        ),
    )

    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "project_root": str(root),
        "git": {
            "branch": git_value(root, ["rev-parse", "--abbrev-ref", "HEAD"]),
            "head": git_value(root, ["rev-parse", "--short", "HEAD"]),
            "status_short": git_value(root, ["status", "--short"]),
        },
        "policy": AUDIT_ONLY_POLICY,
        "summary": summarize(mechanisms, scanned_files),
        "mechanisms": mechanisms,
    }
    return report


def markdown_escape(value: Any) -> str:
    text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    summary = report["summary"]
    lines.append("# V0.1.4 — Player-State / Filtering Audit")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append(
        "This report maps existing folded/sitout/all-in/HERO/active/trigger/service/Clear_JSON/finalization player-state logic before postflop development."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Schema: `{report['schema_version']}`")
    lines.append(f"- Project root: `{report['project_root']}`")
    lines.append(f"- Git branch: `{report['git']['branch']}`")
    lines.append(f"- Git HEAD: `{report['git']['head']}`")
    lines.append(f"- Total files scanned: **{summary['total_files_scanned']}**")
    lines.append(f"- Total mechanisms found: **{summary['total_mechanisms_found']}**")
    lines.append(f"- Source-of-truth candidates: **{summary['source_of_truth_candidates']}**")
    lines.append(f"- Reusable by postflop candidates: **{summary['can_be_reused_by_postflop_candidates']}**")
    lines.append(f"- Should-not-duplicate candidates: **{summary['should_not_be_duplicated_candidates']}**")
    lines.append("")
    lines.append("## By logic type")
    lines.append("")
    for logic_type, count in summary["by_logic_type"].items():
        lines.append(f"- **{logic_type}**: {count}")
    lines.append("")
    lines.append("## Policy")
    lines.append("")
    lines.append("- V0.1.4 is audit-only.")
    lines.append("- Postflop solver must not duplicate existing player-state filtering blindly.")
    lines.append("- Runtime and click-chain are not modified in this version.")
    lines.append("- Player resolver is not implemented in this version.")
    lines.append("")
    lines.append("## Mechanism map")
    lines.append("")
    lines.append(
        "| file_path | function_or_class_name | logic_type | source_of_truth | reuse_by_postflop | should_not_duplicate | risk | keywords | notes |"
    )
    lines.append("|---|---|---:|---:|---:|---:|---|---|---|")
    for item in report["mechanisms"][:500]:
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_escape(item["file_path"]),
                    markdown_escape(item["function_or_class_name"]),
                    markdown_escape(item["logic_type"]),
                    markdown_escape(item["is_source_of_truth"]),
                    markdown_escape(item["can_be_reused_by_postflop"]),
                    markdown_escape(item["should_not_be_duplicated"]),
                    markdown_escape(item["risk_if_modified"]),
                    markdown_escape(", ".join(item["matched_keywords"][:8])),
                    markdown_escape(item["notes"]),
                ]
            )
            + " |"
        )
    if len(report["mechanisms"]) > 500:
        lines.append("")
        lines.append(f"_Table truncated to 500 rows out of {len(report['mechanisms'])}; full data is in JSON report._")
    lines.append("")
    lines.append("## Next step")
    lines.append("")
    lines.append("Use this report in V0.1.5 to decide what player-state logic can be reused and what must not be duplicated before V0.2.0 Fixture Lab.")
    lines.append("")
    return "\n".join(lines)


def write_reports(root: str | Path, report: dict[str, Any]) -> tuple[Path, Path]:
    root = Path(root).resolve()
    report_dir = root / REPORT_DIR
    docs_dir = root / DOCS_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    json_path = report_dir / JSON_REPORT_NAME
    markdown_path = docs_dir / MARKDOWN_REPORT_NAME
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, markdown_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit current player-state/filtering mechanisms for V0.1.4.")
    parser.add_argument("--root", default=".", help="Project root. Defaults to current directory.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    report = build_report(root)
    json_path, markdown_path = write_reports(root, report)
    summary = report["summary"]

    print("[V0.1.4] Player-state/filtering audit completed")
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {markdown_path}")
    print(f"Total files scanned: {summary['total_files_scanned']}")
    print(f"Mechanisms found: {summary['total_mechanisms_found']}")
    print(f"By logic type: {summary['by_logic_type']}")
    print(f"Should not duplicate: {summary['should_not_be_duplicated_candidates']}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
