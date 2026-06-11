from __future__ import annotations

import copy
from pathlib import Path

from solver_postflop import (
    CLEAR_JSON_FIELD_MAPPINGS,
    FIELD_MAPPING_VERSION,
    ClearJsonInput,
    build_field_usage_trace,
    build_solver_input,
    get_mapping_for_solver_input_field,
    solver_input_fields_in_contract,
)
from solver_postflop.solver_input import MAPPING_VERSION, get_mapped_value


CURRENT_SOLVER_INPUT_FIELDS = {
    "table_id",
    "hand_id",
    "hero_cards",
    "board_cards",
    "players",
    "pot",
    "to_call",
    "stacks",
    "committed_amounts",
    "positions",
    "button",
    "blinds",
    "allowed_actions",
    "action_context",
}


def _clear_input(payload: dict) -> ClearJsonInput:
    return ClearJsonInput(
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/contract_backed.clear.json",
        raw_data=payload,
        loaded_at="2026-06-11T00:00:00+00:00",
        case_id=payload.get("case_id"),
        hand_id=payload.get("hand_id"),
        table_id=payload.get("table_id"),
    )


def _rich_payload() -> dict:
    return {
        "case_id": "contract_backed_case_001",
        "table_id": "table_03",
        "hand_id": "hand_303",
        "hero_cards": ["As", "Kd"],
        "board_cards": ["Ah", "7c", "2d"],
        "players": [{"id": "hero"}, {"id": "villain"}],
        "total_pot": 8.5,
        "to_call": 1.5,
        "chips": {"hero": 91.5, "villain": 88.0},
        "committed": {"hero": 3.5, "villain": 5.0},
        "positions": {"hero": "BTN", "villain": "BB"},
        "button": "BTN",
        "blinds": {"sb": 0.5, "bb": 1.0},
        "allowed_actions": ["fold", "call", "raise"],
        "action_context": {"facing_bet": True},
        "current_actor": "hero",
        "pot_type": "srp",
    }


def _target_from_trace_entry(trace_entry: str) -> str:
    if "->" not in trace_entry:
        return trace_entry
    return trace_entry.rsplit("->", 1)[1]


def test_build_solver_input_uses_field_mapping_contract_version() -> None:
    solver_input, trace = build_solver_input(_clear_input(_rich_payload()))

    assert MAPPING_VERSION == FIELD_MAPPING_VERSION == "v0.3.0"
    assert trace.mapping_version == FIELD_MAPPING_VERSION
    assert solver_input.raw_clear_json_ref["case_id"] == "contract_backed_case_001"
    assert "SolverInput mapping is backed by FIELD_MAPPING_VERSION" in trace.notes


def test_current_solver_input_fields_remain_described_by_contract() -> None:
    contract_fields = set(solver_input_fields_in_contract())

    assert CURRENT_SOLVER_INPUT_FIELDS <= contract_fields
    for field_name in CURRENT_SOLVER_INPUT_FIELDS:
        assert get_mapping_for_solver_input_field(field_name).solver_input_field == field_name


def test_trace_used_and_missing_targets_are_contract_described() -> None:
    payload = {
        "table_id": "table_07",
        "hand_id": "hand_007",
        "hero_cards": ["Qc", "Qd"],
        "board_cards": ["Qs", "8h", "3c"],
        "players": [],
        "pot": 5.0,
    }

    _solver_input, trace = build_solver_input(_clear_input(payload))
    contract_targets = set(solver_input_fields_in_contract())

    used_targets = {_target_from_trace_entry(entry) for entry in trace.fields_used}
    used_targets.discard("raw_clear_json_ref")

    assert used_targets <= contract_targets
    assert set(trace.fields_not_provided) <= contract_targets
    assert "allowed_actions" in trace.fields_not_provided
    assert "action_context" in trace.fields_not_provided


def test_contract_aliases_drive_solver_input_mapping() -> None:
    payload = _rich_payload()
    solver_input, trace = build_solver_input(_clear_input(payload))

    assert solver_input.pot == 8.5
    assert solver_input.stacks == {"hero": 91.5, "villain": 88.0}
    assert solver_input.committed_amounts == {"hero": 3.5, "villain": 5.0}
    assert "total_pot->pot" in trace.fields_used
    assert "chips->stacks" in trace.fields_used
    assert "committed->committed_amounts" in trace.fields_used


def test_get_mapped_value_prefers_first_available_contract_source_field() -> None:
    pot_entry = get_mapping_for_solver_input_field("pot")
    stack_entry = get_mapping_for_solver_input_field("stacks")

    assert get_mapped_value({"total_pot": 10, "pot": 5}, pot_entry) == (10, "total_pot")
    assert get_mapped_value({"pot": 5}, pot_entry) == (5, "pot")
    assert get_mapped_value({"chips": {"hero": 100}}, stack_entry) == ({"hero": 100}, "chips")


def test_fixture_library_cases_build_solver_input_with_contract_trace() -> None:
    manifest_path = Path("tests/fixtures/postflop_clear_json/manifest.json")
    import json

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["cases"]

    for case in manifest["cases"]:
        import solver_postflop

        clear_input = solver_postflop.load_clear_json_input(case["clear_json_file"])
        solver_input, solver_trace = build_solver_input(clear_input)
        field_usage_trace = build_field_usage_trace(clear_input, solver_input)

        assert solver_input.raw_clear_json_ref is clear_input.raw_data
        assert solver_trace.mapping_version == FIELD_MAPPING_VERSION
        assert field_usage_trace.mapping_version == FIELD_MAPPING_VERSION
        assert "board_cards" in field_usage_trace.fields_used


def test_contract_backed_mapping_keeps_clear_json_read_only() -> None:
    payload = _rich_payload()
    before = copy.deepcopy(payload)

    solver_input, solver_trace = build_solver_input(_clear_input(payload))

    assert payload == before
    assert solver_input.raw_clear_json_ref is payload
    assert solver_trace.input_kind == "clear_json"


def test_solver_input_source_keeps_public_api_and_no_extra_markers() -> None:
    source_text = Path("solver_postflop/solver_input.py").read_text(encoding="utf-8")

    assert "def build_solver_input(clear_input: ClearJsonInput) -> tuple[SolverInput, SolverTrace]:" in source_text
    assert "CLEAR_JSON_FIELD_MAPPINGS" in source_text
    assert "FIELD_MAPPING_VERSION" in source_text

    forbidden_markers = (
        "Dark_JSON",
        "Pending_JSON",
        "Service JSON",
        "Runtime JSON",
        "source_discovery",
        "display_analysis_cycle",
        "Action_Button",
        "PokerVisionFinalVersionNoSolver_snapshot",
        "duplicate",
        "collision",
        "range_engine",
    )

    for marker in forbidden_markers:
        assert marker not in source_text


def test_every_contract_entry_remains_available_for_trace_linking() -> None:
    payload = _rich_payload()
    solver_input, _solver_trace = build_solver_input(_clear_input(payload))
    usage_trace = build_field_usage_trace(_clear_input(payload), solver_input)
    record_targets = {record.solver_input_field for record in usage_trace.records if record.solver_input_field}
    contract_targets = {entry.solver_input_field for entry in CLEAR_JSON_FIELD_MAPPINGS}

    assert contract_targets <= record_targets
