#!/usr/bin/env python3
"""V0.1.3 — JSON Source Map Audit for PokerVision_Solver_AllPreflop_Flop.

This tool maps JSON sources that already exist in the project and code locations
that appear to create/read/write JSON artifacts. It does not normalize data, does
not build postflop fixtures, does not make poker decisions, and does not change
runtime/click-chain code.

The output is designed to feed the next roadmap stages:
- V0.2.0 Source-Based Postflop Fixture Lab
- V0.3.0 Postflop Source Contracts
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "v0.1.3-json-source-map"
REPORT_DIR = Path("outputs") / "baseline_audit_v010"
DOCS_REPORT_DIR = Path("docs") / "reports"
JSON_REPORT_NAME = "json_source_map_report.json"
MARKDOWN_REPORT_NAME = "current_json_source_map_v010.md"

ALLOWED_SOURCE_TYPES = (
    "dark_json",
    "pending_json",
    "service_json",
    "current_cycle_json",
    "runtime_json",
    "solver_payload_json",
    "final_clear_json",
    "manual_live_like_json",
    "unknown",
)

SEARCH_DIRS = (
    "outputs",
    "examples",
    "external",
    "tests/fixtures",
    "tests",
)

SKIP_DIR_NAMES = {
    ".git",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
}

PY_JSON_TOKENS = (
    "json.dump",
    "json.dumps",
    "json.load",
    "json.loads",
    "write_text",
    "read_text",
    "open(",
    "save_json",
    "load_json",
    "Clear_JSON",
    "Dark_JSON",
    "JSON_Complete",
    "Clear_JSON_Pending",
    "solver_payload",
    "solver_payloads",
    "Action_Decision_JSON",
    "Action_Runtime_Plan_JSON",
    "current_cycle",
    "click_result",
)

BOARD_KEYS = {
    "board",
    "board_cards",
    "community_cards",
    "flop",
    "turn",
    "river",
    "Board",
    "Board_Cards",
}
HERO_KEYS = {
    "hero_cards",
    "Hero_cards",
    "hero_hand",
    "Hero_hand",
    "hole_cards",
    "cards_hero",
}
PLAYER_KEYS = {
    "players",
    "Players",
    "seats",
    "Seats",
    "player_states",
    "Player_State",
    "player_state",
}
ACTION_KEYS = {
    "actions",
    "Actions",
    "action_history",
    "available_actions",
    "allowed_actions",
    "Action_Decision_JSON",
    "Action_Runtime_Plan_JSON",
    "planned_action",
    "raw_action",
}
CLICK_KEYS = {
    "click_result",
    "Click_Result",
    "clicked",
    "click_status",
    "physical_click",
    "real_click_enabled",
}
STREET_VALUES = {"preflop", "flop", "turn", "river", "showdown"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_path(value: str) -> str:
    return value.replace("\\", "/").lower()


def relative_to_root(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


def is_under_skipped_dir(path: Path) -> bool:
    return any(part in SKIP_DIR_NAMES for part in path.parts)


def read_text_safe(path: Path, *, limit_chars: int = 500_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit_chars]
    except OSError:
        return ""


def load_json_safe(path: Path, *, limit_bytes: int = 2_000_000) -> tuple[bool, Any, str]:
    try:
        if path.stat().st_size > limit_bytes:
            return False, None, f"file larger than scan limit {limit_bytes} bytes"
        return True, json.loads(path.read_text(encoding="utf-8", errors="replace")), ""
    except Exception as exc:  # noqa: BLE001 - audit must never crash on a bad source file.
        return False, None, f"failed to parse JSON: {type(exc).__name__}: {exc}"


def walk_values(value: Any, *, max_nodes: int = 20_000) -> Iterable[Any]:
    stack = [value]
    seen = 0
    while stack and seen < max_nodes:
        current = stack.pop()
        seen += 1
        yield current
        if isinstance(current, dict):
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)


def collect_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    for node in walk_values(value):
        if isinstance(node, dict):
            keys.update(str(k) for k in node.keys())
    return keys


def find_street_candidate(path_key: str, payload: Any) -> str:
    for street in ("river", "turn", "flop", "preflop", "showdown"):
        if street in path_key:
            return street

    for node in walk_values(payload):
        if isinstance(node, dict):
            for key, val in node.items():
                key_l = str(key).lower()
                if key_l in {"street", "stage", "street_candidate", "current_street"}:
                    val_l = str(val).lower()
                    for street in STREET_VALUES:
                        if street in val_l:
                            return street
        elif isinstance(node, str):
            val_l = node.lower()
            for street in STREET_VALUES:
                if val_l == street:
                    return street
    return "unknown"


def list_has_card_like_items(value: Any) -> bool:
    if not isinstance(value, list):
        return False
    if len(value) == 0:
        return False
    if all(isinstance(item, str) for item in value):
        # Accept both short forms (As, Kh) and verbose card labels used by OCR/CV outputs.
        return True
    if all(isinstance(item, dict) for item in value):
        return any({"rank", "suit", "card", "value"} & {str(k).lower() for k in item.keys()} for item in value)
    return False


def has_key_or_card_list(payload: Any, candidate_keys: set[str]) -> bool:
    for node in walk_values(payload):
        if not isinstance(node, dict):
            continue
        for key, val in node.items():
            if str(key) in candidate_keys:
                return True
            if str(key).lower() in {k.lower() for k in candidate_keys} and list_has_card_like_items(val):
                return True
    return False


def detect_json_features(payload: Any) -> dict[str, Any]:
    keys = collect_keys(payload)
    contains_board = bool(keys & BOARD_KEYS) or has_key_or_card_list(payload, BOARD_KEYS)
    contains_hero = bool(keys & HERO_KEYS) or has_key_or_card_list(payload, HERO_KEYS)
    contains_players = bool(keys & PLAYER_KEYS)
    contains_actions = bool(keys & ACTION_KEYS)
    contains_click_result = bool(keys & CLICK_KEYS)
    return {
        "keys_sample": sorted(keys)[:120],
        "contains_board_cards": contains_board,
        "contains_hero_cards": contains_hero,
        "contains_players": contains_players,
        "contains_actions": contains_actions,
        "contains_click_result": contains_click_result,
    }


def infer_source_type_from_path_and_payload(relative_path: str, payload: Any | None) -> str:
    key = normalize_path(relative_path)
    compact_keys = ""
    if payload is not None:
        compact_keys = " ".join(k.lower() for k in list(collect_keys(payload))[:400])
    haystack = f"{key} {compact_keys}"

    if "manual_live_like" in haystack or "manual-live-like" in haystack:
        return "manual_live_like_json"
    if "solver_payload" in haystack or "solver_payloads" in haystack or "payload_json" in haystack:
        return "solver_payload_json"
    if "json_complete" in haystack or "final_clear" in haystack or "final clear" in haystack:
        return "final_clear_json"
    if "clear_json_pending" in haystack or "pending_json" in haystack or "pending" in key:
        return "pending_json"
    if "dark_json" in haystack or "/dark_json/" in haystack or ".dark.json" in key:
        return "dark_json"
    if "current_cycle" in haystack or "current-cycle" in haystack:
        return "current_cycle_json"
    if "service" in haystack or "trigger_ui" in haystack or "table_status" in haystack:
        return "service_json"
    if "runtime" in haystack or "action_runtime_plan" in haystack or "runtime_plan" in haystack:
        return "runtime_json"
    return "unknown"


def source_kind_for(source_type: str) -> str:
    if source_type in {"dark_json", "pending_json", "service_json", "current_cycle_json", "runtime_json", "solver_payload_json"}:
        return "pre_click_or_intermediate_source"
    if source_type == "final_clear_json":
        return "post_click_or_final_source"
    if source_type == "manual_live_like_json":
        return "manual_live_like_source"
    return "unknown_json"


def classify_click_availability(source_type: str, contains_click_result: bool) -> tuple[bool, bool, bool]:
    """Return available_before_click, available_after_click, requires_click_cycle."""
    if source_type == "final_clear_json":
        return False, True, True
    if contains_click_result:
        return False, True, True
    if source_type in {
        "dark_json",
        "pending_json",
        "service_json",
        "current_cycle_json",
        "runtime_json",
        "solver_payload_json",
        "manual_live_like_json",
        "unknown",
    }:
        return True, False, False
    return False, False, False


def is_real_project_source(relative_path: str, source_type: str) -> bool:
    key = normalize_path(relative_path)
    if source_type == "manual_live_like_json":
        return False
    if key.startswith("outputs/") or key.startswith("examples/") or key.startswith("external/"):
        return True
    return False


def is_manual_live_like_source(relative_path: str, source_type: str) -> bool:
    return source_type == "manual_live_like_json" or "manual_live_like" in normalize_path(relative_path)


def can_be_used_for_fixture_lab(source_type: str, features: dict[str, Any], parse_ok: bool) -> bool:
    if not parse_ok:
        return False
    if source_type in {"dark_json", "pending_json", "service_json", "current_cycle_json", "runtime_json", "solver_payload_json", "final_clear_json", "manual_live_like_json"}:
        return True
    return any(
        bool(features.get(flag))
        for flag in (
            "contains_board_cards",
            "contains_hero_cards",
            "contains_players",
            "contains_actions",
        )
    )


def scan_json_file(path: Path, project_root: Path) -> dict[str, Any]:
    rel = relative_to_root(path, project_root)
    parse_ok, payload, parse_error = load_json_safe(path)
    features = detect_json_features(payload) if parse_ok else {
        "keys_sample": [],
        "contains_board_cards": False,
        "contains_hero_cards": False,
        "contains_players": False,
        "contains_actions": False,
        "contains_click_result": False,
    }
    source_type = infer_source_type_from_path_and_payload(rel, payload if parse_ok else None)
    before_click, after_click, requires_click = classify_click_availability(
        source_type, bool(features["contains_click_result"])
    )
    manual = is_manual_live_like_source(rel, source_type)
    real = is_real_project_source(rel, source_type) and not manual
    street_candidate = find_street_candidate(normalize_path(rel), payload if parse_ok else None)

    risk_notes: list[str] = []
    if source_type == "unknown":
        risk_notes.append("source_type could not be inferred; requires manual review before V0.2 fixture use")
    if source_type == "final_clear_json":
        risk_notes.append("final_clear_json should not be treated as mandatory for postflop; it may require click-cycle")
    if manual:
        risk_notes.append("manual_live_like_json must stay explicitly separated from real project source")
    if parse_error:
        risk_notes.append(parse_error)

    return {
        "source_file": rel,
        "source_type": source_type,
        "source_kind": source_kind_for(source_type),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "parse_status": "parsed" if parse_ok else "not_parsed",
        "parse_error": parse_error,
        "is_real_project_source": real,
        "is_manual_live_like_source": manual,
        "contains_board_cards": bool(features["contains_board_cards"]),
        "contains_hero_cards": bool(features["contains_hero_cards"]),
        "contains_players": bool(features["contains_players"]),
        "contains_actions": bool(features["contains_actions"]),
        "contains_click_result": bool(features["contains_click_result"]),
        "street_candidate": street_candidate,
        "available_before_click": before_click,
        "available_after_click": after_click,
        "requires_click_cycle": requires_click,
        "can_be_used_for_fixture_lab_v020": can_be_used_for_fixture_lab(source_type, features, parse_ok),
        "can_become_source_candidate_v030": parse_ok and source_type in ALLOWED_SOURCE_TYPES,
        "keys_sample": features["keys_sample"],
        "risk_notes": risk_notes,
    }


def discover_json_files(project_root: Path, *, max_files: int = 1500) -> list[Path]:
    results: list[Path] = []
    for rel_dir in SEARCH_DIRS:
        root = project_root / rel_dir
        if not root.exists():
            continue
        for path in root.rglob("*.json"):
            if len(results) >= max_files:
                return sorted(results)
            if path.is_file() and not is_under_skipped_dir(path):
                results.append(path)
    return sorted(set(results))


def discover_python_files(project_root: Path, *, max_files: int = 2500) -> list[Path]:
    results: list[Path] = []
    for path in project_root.rglob("*.py"):
        if len(results) >= max_files:
            break
        if path.is_file() and not is_under_skipped_dir(path):
            results.append(path)
    return sorted(results)


def classify_py_json_operation(line: str) -> str:
    line_l = line.lower()
    if "json.dump" in line_l or "json.dumps" in line_l or "write_text" in line_l or "open(" in line_l and "w" in line_l:
        return "write_or_create_reference"
    if "json.load" in line_l or "json.loads" in line_l or "read_text" in line_l or "open(" in line_l and "r" in line_l:
        return "read_reference"
    return "path_or_symbol_reference"


def infer_function_or_class_at_line(source: str, line_no: int) -> str:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return "unknown"

    best_name = "module_scope"
    best_line = -1
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = getattr(node, "lineno", -1)
            end = getattr(node, "end_lineno", start)
            if start <= line_no <= end and start > best_line:
                best_name = node.name
                best_line = start
    return best_name


def scan_py_json_references(path: Path, project_root: Path) -> list[dict[str, Any]]:
    rel = relative_to_root(path, project_root)
    source = read_text_safe(path)
    if not source:
        return []
    references: list[dict[str, Any]] = []
    for idx, line in enumerate(source.splitlines(), start=1):
        if not any(token.lower() in line.lower() for token in PY_JSON_TOKENS):
            continue
        source_type = infer_source_type_from_path_and_payload(rel + " " + line, None)
        references.append(
            {
                "file_path": rel,
                "line_no": idx,
                "function_or_class_name": infer_function_or_class_at_line(source, idx),
                "operation_kind": classify_py_json_operation(line),
                "source_type_hint": source_type,
                "evidence": line.strip()[:240],
            }
        )
    return references


def build_report(project_root: Path) -> dict[str, Any]:
    project_root = project_root.resolve()
    json_files = discover_json_files(project_root)
    json_sources = [scan_json_file(path, project_root) for path in json_files]

    code_refs: list[dict[str, Any]] = []
    for py_file in discover_python_files(project_root):
        code_refs.extend(scan_py_json_references(py_file, project_root))

    by_type = Counter(src["source_type"] for src in json_sources)
    by_kind = Counter(src["source_kind"] for src in json_sources)
    source_candidates_v020 = [src for src in json_sources if src["can_be_used_for_fixture_lab_v020"]]
    source_candidates_v030 = [src for src in json_sources if src["can_become_source_candidate_v030"]]
    before_click = [src for src in json_sources if src["available_before_click"]]
    after_click = [src for src in json_sources if src["available_after_click"]]
    manual_sources = [src for src in json_sources if src["is_manual_live_like_source"]]
    final_clear_sources = [src for src in json_sources if src["source_type"] == "final_clear_json"]

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "project_root": str(project_root),
        "fixture_lab_v020_policy": {
            "allowed_source_types": list(ALLOWED_SOURCE_TYPES),
            "final_clear_json_is_optional": True,
            "manual_live_like_json_must_be_explicit": True,
            "postflop_source_discovery_must_not_depend_only_on_final_clear_json": True,
        },
        "summary": {
            "total_json_files_scanned": len(json_sources),
            "total_code_references": len(code_refs),
            "by_source_type": dict(sorted(by_type.items())),
            "by_source_kind": dict(sorted(by_kind.items())),
            "available_before_click_count": len(before_click),
            "available_after_click_count": len(after_click),
            "requires_click_cycle_count": sum(1 for src in json_sources if src["requires_click_cycle"]),
            "v020_fixture_candidate_count": len(source_candidates_v020),
            "v030_source_candidate_count": len(source_candidates_v030),
            "manual_live_like_count": len(manual_sources),
            "final_clear_json_count": len(final_clear_sources),
            "final_clear_json_optional_confirmed": True,
        },
        "json_sources": json_sources,
        "code_references": code_refs,
        "next_step_notes": [
            "Use V0.2.0 to copy or author selected source-based postflop fixtures with manifest metadata.",
            "Use V0.3.0 to formalize these source records into PostflopSourceCandidate and related contracts.",
            "Do not make Final Clear_JSON the only supported source because postflop final output may require click-cycle.",
        ],
    }


def write_reports(project_root: Path, report: dict[str, Any]) -> tuple[Path, Path]:
    json_dir = project_root / REPORT_DIR
    md_dir = project_root / DOCS_REPORT_DIR
    json_dir.mkdir(parents=True, exist_ok=True)
    md_dir.mkdir(parents=True, exist_ok=True)

    json_path = json_dir / JSON_REPORT_NAME
    md_path = md_dir / MARKDOWN_REPORT_NAME
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    policy = report["fixture_lab_v020_policy"]
    lines: list[str] = []
    lines.append("# V0.1.3 — JSON Source Map Audit")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This report maps existing JSON artifacts and JSON-related code references before building "
        "the V0.2 source-based postflop fixture lab and V0.3 postflop source contracts."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Schema version: `{report['schema_version']}`")
    lines.append(f"- Total JSON files scanned: **{summary['total_json_files_scanned']}**")
    lines.append(f"- Total code references: **{summary['total_code_references']}**")
    lines.append(f"- Available before click: **{summary['available_before_click_count']}**")
    lines.append(f"- Available after click: **{summary['available_after_click_count']}**")
    lines.append(f"- Requires click-cycle: **{summary['requires_click_cycle_count']}**")
    lines.append(f"- V0.2 fixture candidates: **{summary['v020_fixture_candidate_count']}**")
    lines.append(f"- V0.3 source candidates: **{summary['v030_source_candidate_count']}**")
    lines.append(f"- Manual live-like sources: **{summary['manual_live_like_count']}**")
    lines.append(f"- Final Clear JSON count: **{summary['final_clear_json_count']}**")
    lines.append("")
    lines.append("## Source Type Policy")
    lines.append("")
    lines.append("Allowed source types:")
    for source_type in policy["allowed_source_types"]:
        lines.append(f"- `{source_type}`")
    lines.append("")
    lines.append(f"- Final Clear JSON is optional: **{policy['final_clear_json_is_optional']}**")
    lines.append(f"- Manual live-like JSON must be explicit: **{policy['manual_live_like_json_must_be_explicit']}**")
    lines.append(
        f"- Source discovery must not depend only on Final Clear JSON: "
        f"**{policy['postflop_source_discovery_must_not_depend_only_on_final_clear_json']}**"
    )
    lines.append("")
    lines.append("## Source Type Counts")
    lines.append("")
    lines.append("| source_type | count |")
    lines.append("|---|---:|")
    for source_type, count in summary["by_source_type"].items():
        lines.append(f"| `{source_type}` | {count} |")
    lines.append("")
    lines.append("## Candidate JSON Sources")
    lines.append("")
    lines.append("| source_file | source_type | before_click | after_click | v020_candidate | street | notes |")
    lines.append("|---|---|---:|---:|---:|---|---|")
    for src in report["json_sources"][:120]:
        notes = "; ".join(src.get("risk_notes", []))[:180]
        lines.append(
            f"| `{src['source_file']}` | `{src['source_type']}` | "
            f"{src['available_before_click']} | {src['available_after_click']} | "
            f"{src['can_be_used_for_fixture_lab_v020']} | `{src['street_candidate']}` | {notes} |"
        )
    if len(report["json_sources"]) > 120:
        lines.append(f"| ... | ... | ... | ... | ... | ... | {len(report['json_sources']) - 120} more JSON sources in JSON report |")
    lines.append("")
    lines.append("## Key Audit Conclusion")
    lines.append("")
    lines.append(
        "V0.2 fixtures and V0.3 contracts must support intermediate source JSON. "
        "Final Clear_JSON must remain optional because postflop final output may be available only after click-cycle."
    )
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V0.1.3 JSON source map audit.")
    parser.add_argument("--project-root", default=".", help="Project root. Defaults to current directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    report = build_report(project_root)
    json_path, markdown_path = write_reports(project_root, report)
    summary = report["summary"]
    print("[V0.1.3] JSON source map audit completed")
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {markdown_path}")
    print(f"Total JSON files: {summary['total_json_files_scanned']}")
    print(f"By source type: {summary['by_source_type']}")
    print(f"Before click: {summary['available_before_click_count']}")
    print(f"After click: {summary['available_after_click_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
