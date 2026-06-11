from __future__ import annotations

import ast
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Iterable

from solver_postflop import ClearJsonInput, build_solver_input
from solver_postflop.field_usage_trace import build_field_usage_trace


V030_SOURCE_FILES = (
    Path("solver_postflop/field_mapping_contract.py"),
    Path("solver_postflop/field_usage_trace.py"),
    Path("solver_postflop/solver_input.py"),
    Path("solver_postflop/clear_json_input.py"),
)


FORBIDDEN_POLICY_MARKERS = (
    "duplicate_card",
    "duplicate_cards",
    "card_duplicate",
    "card_collision",
    "hero_board_collision",
    "hero-board",
    "board_count_safety_gate",
    "board_validation",
    "validate_board",
    "validate_cards",
    "validate_players",
    "player_filter",
    "filter_players",
    "reconstruct_hero",
    "create_hero",
    "active_player_reconstruction",
    "create_active_player",
    "street_resolver",
    "source_discovery",
    "fallback_source",
    "Dark_JSON",
    "Pending_JSON",
    "Service JSON",
    "Runtime JSON",
    "dark_json",
    "pending_json",
    "service_json",
    "runtime_json",
    "display_analysis_cycle",
    "Action_Button",
    "PokerVisionFinalVersionNoSolver_snapshot",
    "solver_preflop",
)


FORBIDDEN_IMPORT_ROOTS = {
    "solver_preflop",
    "external",
    "display_analysis_cycle",
    "Action_Button",
    "source_discovery",
}


FORBIDDEN_CALLS_IN_MAPPING_LAYER = {
    "glob",
    "rglob",
    "iterdir",
    "walk",
    "validate",
    "validate_cards",
    "validate_board",
    "validate_players",
    "filter",
    "filter_players",
    "create_hero",
    "reconstruct_hero",
    "create_active_player",
}


ALLOWED_OPEN_CALL_FILES = {Path("solver_postflop/clear_json_input.py")}


def _source_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in V030_SOURCE_FILES)


def _iter_import_roots(path: Path) -> Iterable[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name.split(".", 1)[0]
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module.split(".", 1)[0]


def _iter_call_names(path: Path) -> Iterable[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            yield func.id
        elif isinstance(func, ast.Attribute):
            yield func.attr


def _json_safe(value):
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def _sample_clear_input() -> ClearJsonInput:
    payload = {
        "case_id": "v030_no_validation_policy",
        "table_id": "table_v030",
        "hand_id": "hand_v030",
        "hero_cards": ["Ah", "Kh"],
        "board_cards": ["Qs", "7d", "2c"],
        "players": [
            {"id": "hero", "position": "BB", "stack": 97.5, "folded": False},
            {"id": "villain", "position": "BTN", "stack": 103.0, "folded": False},
        ],
        "total_pot": 6.5,
        "to_call": 0,
        "allowed_actions": ["check", "bet"],
        "action_context": {"state": "check_option"},
        "unmapped_debug_payload": {"kept_for_trace_only": True},
    }
    return ClearJsonInput(
        source_file="v030_no_validation_policy.clear.json",
        raw_data=payload,
        loaded_at="2026-06-11T00:00:00+00:00",
        case_id="v030_no_validation_policy",
        hand_id="hand_v030",
        table_id="table_v030",
    )


def test_v030_mapping_layer_source_has_no_validation_or_fallback_policy_markers() -> None:
    source_text = _source_text()

    for marker in FORBIDDEN_POLICY_MARKERS:
        assert marker not in source_text


def test_v030_mapping_layer_does_not_import_external_source_or_live_chain_modules() -> None:
    imported_roots = {
        import_root
        for source_file in V030_SOURCE_FILES
        for import_root in _iter_import_roots(source_file)
    }

    assert imported_roots.isdisjoint(FORBIDDEN_IMPORT_ROOTS)


def test_v030_mapping_layer_avoids_validation_filtering_discovery_calls() -> None:
    calls_by_file = {
        source_file: set(_iter_call_names(source_file))
        for source_file in V030_SOURCE_FILES
    }

    for source_file, call_names in calls_by_file.items():
        forbidden = set(FORBIDDEN_CALLS_IN_MAPPING_LAYER)
        if source_file not in ALLOWED_OPEN_CALL_FILES:
            forbidden.add("open")
        assert call_names.isdisjoint(forbidden), f"{source_file}: {call_names & forbidden}"


def test_build_solver_input_does_not_mutate_clear_json_or_apply_safety_gate() -> None:
    clear_input = _sample_clear_input()
    before = json.loads(json.dumps(clear_input.raw_data))

    solver_input, solver_trace = build_solver_input(clear_input)

    assert clear_input.raw_data == before
    assert solver_input.raw_clear_json_ref is clear_input.raw_data
    assert tuple(solver_input.board_cards) == tuple(before["board_cards"])
    assert tuple(solver_input.hero_cards) == tuple(before["hero_cards"])
    assert solver_trace.input_kind == "clear_json"
    assert solver_trace.mapping_version == "v0.3.0"


def test_build_field_usage_trace_does_not_mutate_clear_json_or_repair_payload() -> None:
    clear_input = _sample_clear_input()
    solver_input, _ = build_solver_input(clear_input)
    before = json.loads(json.dumps(clear_input.raw_data))

    usage_trace = build_field_usage_trace(clear_input, solver_input)

    assert clear_input.raw_data == before
    assert "unmapped_debug_payload" in usage_trace.fields_ignored
    assert usage_trace.mapping_version == "v0.3.0"
    assert usage_trace.case_id == clear_input.case_id


def test_build_solver_input_and_field_usage_trace_do_not_read_files(monkeypatch) -> None:
    clear_input = _sample_clear_input()

    def blocked_open(*args, **kwargs):
        raise AssertionError("mapping and field usage trace must not open files")

    monkeypatch.setattr(Path, "open", blocked_open)

    solver_input, solver_trace = build_solver_input(clear_input)
    usage_trace = build_field_usage_trace(clear_input, solver_input)

    assert solver_trace.mapping_version == usage_trace.mapping_version
    assert usage_trace.fields_used


def test_v030_mapping_and_trace_do_not_create_decision_or_action_payloads() -> None:
    clear_input = _sample_clear_input()
    solver_input, solver_trace = build_solver_input(clear_input)
    usage_trace = build_field_usage_trace(clear_input, solver_input)

    serialized = json.dumps(
        {
            "solver_input": _json_safe(solver_input),
            "solver_trace": _json_safe(solver_trace),
            "usage_trace": usage_trace.to_json_dict(),
        },
        sort_keys=True,
    ).lower()

    forbidden_result_terms = (
        "final_decision",
        "planned_action",
        "runtime_plan",
        "click_result",
        "button_sequence",
        "bet_size_policy",
    )
    for term in forbidden_result_terms:
        assert term not in serialized
