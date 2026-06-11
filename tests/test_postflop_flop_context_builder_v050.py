from __future__ import annotations

import builtins
import copy
import json
from pathlib import Path

import pytest

from solver_postflop import (
    DEFAULT_FLOP_NEXT_MODULE,
    FlopSpotFamily,
    SolverBranch,
    build_flop_context,
    build_solver_input,
    load_clear_json_input,
    resolve_solver_branch,
)

FIXTURE_ROOT = Path("tests/fixtures/postflop_clear_json")
REAL_FLOP = FIXTURE_ROOT / "real" / "flop" / "real_flop_srp_btn_vs_bb_check_option.clear.json"
SYNTHETIC_TURN = (
    FIXTURE_ROOT / "synthetic" / "turn" / "synthetic_turn_after_flop_bet_call.clear.json"
)


def _solver_input_and_branch(fixture_path: Path = REAL_FLOP):
    clear_input = load_clear_json_input(fixture_path)
    solver_input, solver_trace = build_solver_input(clear_input)
    branch_result = resolve_solver_branch(solver_input, solver_trace)
    return clear_input, solver_input, solver_trace, branch_result


def test_build_flop_context_from_solver_input_and_flop_branch() -> None:
    clear_input, solver_input, _solver_trace, branch_result = _solver_input_and_branch()

    context = build_flop_context(solver_input, branch_result)

    assert context.case_id == clear_input.case_id
    assert context.source_file == branch_result.source_file
    assert context.table_id == solver_input.table_id
    assert context.hand_id == solver_input.hand_id
    assert context.branch == SolverBranch.FLOP.value
    assert context.spot_family == FlopSpotFamily.UNKNOWN_FLOP_SPOT
    assert context.next_module == DEFAULT_FLOP_NEXT_MODULE
    assert context.raw_clear_json_ref is solver_input.raw_clear_json_ref


def test_flop_context_requires_flop_branch() -> None:
    _clear_input, solver_input, solver_trace, branch_result = _solver_input_and_branch(SYNTHETIC_TURN)
    assert branch_result.branch == SolverBranch.TURN_NOT_IMPLEMENTED_YET

    with pytest.raises(ValueError, match="FlopContext requires flop branch"):
        build_flop_context(solver_input, branch_result)

    assert solver_trace.module_chain_next_step == branch_result.next_module


def test_cards_and_players_are_copied_without_reselection() -> None:
    _clear_input, solver_input, _solver_trace, branch_result = _solver_input_and_branch()

    context = build_flop_context(solver_input, branch_result)

    assert context.hero_cards == solver_input.hero_cards
    assert context.board_cards == solver_input.board_cards
    assert context.player_context.players == solver_input.players
    assert context.player_context.players[0] is solver_input.players[0]
    assert context.player_context.is_heads_up is True
    assert context.player_context.is_multiway is False
    assert "opponents_derivation_deferred" in context.player_context.notes


def test_pot_and_action_contexts_are_transferred_without_repair() -> None:
    _clear_input, solver_input, _solver_trace, branch_result = _solver_input_and_branch()

    context = build_flop_context(solver_input, branch_result)

    assert context.pot_context.pot == solver_input.pot
    assert context.pot_context.to_call == solver_input.to_call
    assert context.pot_context.pot_type == "srp"
    assert context.pot_context.effective_stack is None
    assert context.pot_context.spr is None
    assert "effective_stack" in context.pot_context.fields_not_provided
    assert "spr" in context.pot_context.fields_not_provided

    assert context.action_context.allowed_actions == solver_input.allowed_actions
    assert context.action_context.current_actor == "hero"
    assert context.action_context.facing_bet is False
    assert context.action_context.facing_raise is False
    assert context.action_context.can_check is True
    assert context.action_context.can_bet is True
    assert context.action_context.can_call is False
    assert context.action_context.can_raise is False


def test_missing_optional_fields_are_recorded_as_not_provided() -> None:
    payload = {
        "case_id": "minimal_flop_context_case",
        "table_id": "table_02",
        "hand_id": "hand_minimal_flop",
        "hero_cards": ["Ah", "Kd"],
        "board_cards": ["As", "7c", "2d"],
        "players": [],
    }
    clear_input = load_clear_json_input_from_payload(payload)
    solver_input, solver_trace = build_solver_input(clear_input)
    branch_result = resolve_solver_branch(solver_input, solver_trace)

    context = build_flop_context(solver_input, branch_result)

    assert context.pot_context.pot is None
    assert "pot" in context.context_fields_not_provided
    assert "to_call" in context.context_fields_not_provided
    assert "allowed_actions" in context.context_fields_not_provided
    assert "action_context" in context.context_fields_not_provided
    assert "hero_position" in context.context_fields_not_provided
    assert "pot_type" in context.context_fields_not_provided
    assert "players" in context.player_context.fields_not_provided
    assert context.action_context.can_check is None


def test_build_flop_context_does_not_mutate_clear_json_payload() -> None:
    clear_input, solver_input, _solver_trace, branch_result = _solver_input_and_branch()
    before = copy.deepcopy(clear_input.raw_data)

    context = build_flop_context(solver_input, branch_result)

    assert clear_input.raw_data == before
    assert solver_input.raw_clear_json_ref == before
    assert context.raw_clear_json_ref is solver_input.raw_clear_json_ref


def test_build_flop_context_does_not_read_files(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_input, solver_input, _solver_trace, branch_result = _solver_input_and_branch()

    def fail_open(*args, **kwargs):  # noqa: ANN002, ANN003
        raise AssertionError("build_flop_context must not read files")

    monkeypatch.setattr(builtins, "open", fail_open)

    context = build_flop_context(solver_input, branch_result)

    assert context.branch == "flop"


def test_flop_context_serializes_to_json_safe_payload() -> None:
    _clear_input, solver_input, _solver_trace, branch_result = _solver_input_and_branch()

    context = build_flop_context(solver_input, branch_result)
    payload = context.to_json_dict()

    assert payload["spot_family"] == "unknown_flop_spot"
    assert payload["next_module"] == "flop_board_texture_builder"
    assert payload["pot_context"]["pot_type"] == "srp"
    json.dumps(payload, sort_keys=True)


def test_build_flop_context_exported_from_public_package() -> None:
    import solver_postflop

    assert "build_flop_context" in solver_postflop.__all__
    assert hasattr(solver_postflop, "build_flop_context")


def load_clear_json_input_from_payload(payload: dict):
    from solver_postflop.engine_contracts import ClearJsonInput

    return ClearJsonInput(
        source_file="in_memory_minimal_flop.clear.json",
        raw_data=payload,
        loaded_at="2026-06-11T00:00:00+00:00",
        case_id=payload.get("case_id"),
        hand_id=payload.get("hand_id"),
        table_id=payload.get("table_id"),
    )
