from __future__ import annotations

import copy
from pathlib import Path

from solver_postflop import ClearJsonInput, SolverInput, SolverTrace, build_solver_input


def _clear_input(payload: dict) -> ClearJsonInput:
    return ClearJsonInput(
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/case.clear.json",
        raw_data=payload,
        loaded_at="2026-06-11T00:00:00+00:00",
        case_id=payload.get("case_id"),
        hand_id=payload.get("hand_id"),
        table_id=payload.get("table_id"),
    )


def test_build_solver_input_maps_baseline_clear_json_fields() -> None:
    payload = {
        "case_id": "flop_case_001",
        "table_id": "table_02",
        "hand_id": "hand_99",
        "hero_cards": ["As", "Kd"],
        "board_cards": ["Ah", "7c", "2d"],
        "players": [{"id": "hero"}, {"id": "bb"}],
        "total_pot": 7.5,
        "to_call": 2.0,
        "stacks": {"hero": 93.0, "bb": 88.5},
        "committed": {"hero": 2.5, "bb": 5.0},
        "positions": {"hero": "BTN", "bb": "BB"},
        "button": "BTN",
        "blinds": {"sb": 0.5, "bb": 1.0},
        "allowed_actions": ["fold", "call", "raise"],
        "action_context": {"facing_bet": True},
    }

    solver_input, trace = build_solver_input(_clear_input(payload))

    assert isinstance(solver_input, SolverInput)
    assert isinstance(trace, SolverTrace)
    assert solver_input.table_id == "table_02"
    assert solver_input.hand_id == "hand_99"
    assert solver_input.hero_cards == ("As", "Kd")
    assert solver_input.board_cards == ("Ah", "7c", "2d")
    assert solver_input.players == ({"id": "hero"}, {"id": "bb"})
    assert solver_input.pot == 7.5
    assert solver_input.to_call == 2.0
    assert solver_input.stacks == {"hero": 93.0, "bb": 88.5}
    assert solver_input.committed_amounts == {"hero": 2.5, "bb": 5.0}
    assert solver_input.positions == {"hero": "BTN", "bb": "BB"}
    assert solver_input.button == "BTN"
    assert solver_input.blinds == {"sb": 0.5, "bb": 1.0}
    assert solver_input.allowed_actions == ("fold", "call", "raise")
    assert solver_input.action_context == {"facing_bet": True}
    assert solver_input.raw_clear_json_ref is payload


def test_build_solver_input_records_trace_used_fields() -> None:
    payload = {
        "table_id": "table_01",
        "hand_id": "hand_10",
        "hero_cards": ["Qs", "Qh"],
        "board_cards": ["Qd", "7s", "3c"],
        "players": [],
        "pot": 4.5,
        "allowed_actions": ["check", "bet"],
    }

    _, trace = build_solver_input(_clear_input(payload))

    assert trace.input_kind == "clear_json"
    assert trace.input_file.endswith("case.clear.json")
    assert trace.mapping_version == "v0.3.0"
    assert trace.module_chain_next_step == "solver_input_ready_for_future_branch_resolver"
    assert "table_id->table_id" in trace.fields_used
    assert "hand_id->hand_id" in trace.fields_used
    assert "hero_cards->hero_cards" in trace.fields_used
    assert "board_cards->board_cards" in trace.fields_used
    assert "pot->pot" in trace.fields_used
    assert "allowed_actions->allowed_actions" in trace.fields_used
    assert "raw_data->raw_clear_json_ref" in trace.fields_used


def test_missing_optional_fields_are_recorded_without_blocking() -> None:
    payload = {
        "table_id": "table_04",
        "hand_id": "hand_minimal",
        "hero_cards": ["9c", "9d"],
    }

    solver_input, trace = build_solver_input(_clear_input(payload))

    assert solver_input.table_id == "table_04"
    assert solver_input.hand_id == "hand_minimal"
    assert solver_input.hero_cards == ("9c", "9d")
    assert solver_input.board_cards == ()
    assert solver_input.players == ()
    assert solver_input.pot is None
    assert solver_input.to_call is None
    assert solver_input.stacks == {}
    assert solver_input.committed_amounts == {}
    assert solver_input.positions == {}
    assert solver_input.allowed_actions == ()
    assert "board_cards" in trace.fields_not_provided
    assert "players" in trace.fields_not_provided
    assert "pot" in trace.fields_not_provided
    assert "to_call" in trace.fields_not_provided
    assert "allowed_actions" in trace.fields_not_provided


def test_solver_input_uses_clear_input_metadata_for_ids_when_needed() -> None:
    clear_input = ClearJsonInput(
        source_file="metadata_only.clear.json",
        raw_data={"hero_cards": ["Ac", "Ad"]},
        loaded_at="2026-06-11T00:00:00+00:00",
        case_id="metadata_case",
        hand_id="metadata_hand",
        table_id="metadata_table",
    )

    solver_input, trace = build_solver_input(clear_input)

    assert solver_input.table_id == "metadata_table"
    assert solver_input.hand_id == "metadata_hand"
    assert "ClearJsonInput.table_id->table_id" in trace.fields_used
    assert "ClearJsonInput.hand_id->hand_id" in trace.fields_used


def test_build_solver_input_does_not_mutate_clear_json_payload() -> None:
    payload = {
        "table_id": "table_05",
        "hand_id": "hand_read_only",
        "players": [{"id": "hero", "stack": 100.0}],
        "action_context": {"street": "flop"},
    }
    before = copy.deepcopy(payload)

    solver_input, _ = build_solver_input(_clear_input(payload))

    assert payload == before
    solver_input.players[0]["stack"] = 55.0
    assert payload["players"][0]["stack"] == 55.0
    assert set(payload) == set(before)


def test_solver_input_mapping_has_no_extra_source_or_decision_code() -> None:
    source_text = Path("solver_postflop/solver_input.py").read_text(encoding="utf-8")

    forbidden_markers = (
        "glob(",
        "rglob(",
        "os.walk",
        "solver_preflop",
        "external.",
        "display_analysis_cycle",
        "Action_Button",
        "Dark_JSON",
        "Pending_JSON",
        "Service JSON",
        "Runtime JSON",
        "duplicate",
        "collision",
        "equity",
        "range_engine",
        "click",
    )

    for marker in forbidden_markers:
        assert marker not in source_text
