from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Iterable

from solver_postflop import (
    SolverBranch,
    SolverBranchFamily,
    SolverBranchResult,
    SolverInput,
    build_flop_context,
)


FLOP_CONTEXT_SOURCE_FILES = (
    Path("solver_postflop/flop_context.py"),
    Path("solver_postflop/flop_context_contracts.py"),
)


FORBIDDEN_SOURCE_MARKERS = (
    "Dark_JSON",
    "Pending_JSON",
    "Service JSON",
    "Runtime JSON",
    "dark_json",
    "pending_json",
    "service_json",
    "runtime_json",
    "source_discovery",
    "fallback_source",
    "display_analysis_cycle",
    "Action_Button",
    "PokerVisionFinalVersionNoSolver_snapshot",
    "solver_preflop",
    "validate_cards",
    "validate_board",
    "validate_players",
    "duplicate_cards",
    "hero_board_collision",
    "board_count_safety_gate",
    "filter_players",
    "player_filtering",
    "create_hero",
    "reconstruct_hero",
    "create_active_player",
    "active_player_reconstruction",
    "runtime_plan",
    "click_result",
    "click_sequence",
    "button_label",
)


FORBIDDEN_PAYLOAD_KEYS = {
    "final_decision",
    "recommended_action",
    "raw_action",
    "poker_decision",
    "decision_result",
    "bet_size",
    "sizing",
    "runtime_plan",
    "runtime_action_plan",
    "click_sequence",
    "click_result",
    "button_label",
    "equity",
    "range",
    "range_matrix",
}


def _source_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in FLOP_CONTEXT_SOURCE_FILES)


def _solver_input() -> SolverInput:
    raw_payload: dict[str, Any] = {
        "case_id": "flop_context_no_extra_logic_case",
        "source_file": "flop_context_no_extra_logic_case.clear.json",
        "table_id": "table_05",
        "hand_id": "hand_05",
        "hero_id": "hero",
        "hero_position": "BB",
        "hero_cards": ["Ks", "Kh"],
        "board_cards": ["Ah", "7d", "2c"],
        "players": [
            {"id": "hero", "position": "BB", "folded": False, "stack": 97.5},
            {"id": "villain", "position": "BTN", "folded": False, "stack": 101.0},
        ],
        "total_pot": 6.5,
        "to_call": 0,
        "allowed_actions": ["check", "bet"],
        "action_context": {
            "state": "check_option",
            "current_actor": "hero",
            "facing_bet": False,
            "facing_raise": False,
        },
        "pot_type": "srp",
        "preflop_context": {"pot_type": "srp", "source": "trusted_clear_json"},
        "unexpected_payload_field": {"must_remain": "read_only"},
    }
    return SolverInput(
        table_id="table_05",
        hand_id="hand_05",
        hero_cards=tuple(raw_payload["hero_cards"]),
        board_cards=tuple(raw_payload["board_cards"]),
        players=tuple(copy.deepcopy(raw_payload["players"])),
        pot=raw_payload["total_pot"],
        to_call=raw_payload["to_call"],
        positions={"hero": "BB", "villain": "BTN"},
        allowed_actions=tuple(raw_payload["allowed_actions"]),
        action_context=copy.deepcopy(raw_payload["action_context"]),
        raw_clear_json_ref=raw_payload,
    )


def _branch_result() -> SolverBranchResult:
    return SolverBranchResult(
        case_id="flop_context_no_extra_logic_case",
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/no_extra_logic.clear.json",
        branch=SolverBranch.FLOP,
        branch_family=SolverBranchFamily.POSTFLOP_FLOP,
        next_module="flop_context_builder",
        branch_reason="board_card_count_3_routes_to_flop",
        is_decision_branch_enabled=False,
        is_runtime_branch_enabled=False,
        notes=("branch_result_before_flop_context",),
    )


def _walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from _walk_keys(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk_keys(item)


def test_flop_context_source_has_no_forbidden_validation_source_or_click_markers() -> None:
    source_text = _source_text()

    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source_text


def test_build_flop_context_does_not_mutate_clear_json_or_solver_input_fields() -> None:
    solver_input = _solver_input()
    branch_result = _branch_result()

    raw_before = copy.deepcopy(solver_input.raw_clear_json_ref)
    players_before = copy.deepcopy(solver_input.players)
    board_before = copy.deepcopy(solver_input.board_cards)
    hero_cards_before = copy.deepcopy(solver_input.hero_cards)
    allowed_actions_before = copy.deepcopy(solver_input.allowed_actions)
    action_context_before = copy.deepcopy(solver_input.action_context)

    context = build_flop_context(solver_input, branch_result)

    assert context.branch == SolverBranch.FLOP.value
    assert solver_input.raw_clear_json_ref == raw_before
    assert solver_input.players == players_before
    assert solver_input.board_cards == board_before
    assert solver_input.hero_cards == hero_cards_before
    assert solver_input.allowed_actions == allowed_actions_before
    assert solver_input.action_context == action_context_before


def test_build_flop_context_does_not_mutate_branch_result() -> None:
    solver_input = _solver_input()
    branch_result = _branch_result()
    branch_before = copy.deepcopy(branch_result.to_json_dict())

    context = build_flop_context(solver_input, branch_result)

    assert context.next_module == "flop_board_texture_builder"
    assert branch_result.to_json_dict() == branch_before
    assert branch_result.is_decision_branch_enabled is False
    assert branch_result.is_runtime_branch_enabled is False


def test_build_flop_context_does_not_read_files(monkeypatch) -> None:
    def fail_file_io(*args: Any, **kwargs: Any) -> None:  # pragma: no cover - bug path only
        raise AssertionError("Flop Context Builder must not perform file I/O")

    monkeypatch.setattr("builtins.open", fail_file_io)
    monkeypatch.setattr(Path, "open", fail_file_io)
    monkeypatch.setattr(Path, "read_text", fail_file_io)
    monkeypatch.setattr(Path, "read_bytes", fail_file_io)

    context = build_flop_context(_solver_input(), _branch_result())

    assert context.case_id == "flop_context_no_extra_logic_case"
    assert context.board_cards == ("Ah", "7d", "2c")


def test_flop_context_does_not_filter_players_or_invent_missing_runtime_actors() -> None:
    solver_input = _solver_input()
    players_before = copy.deepcopy(solver_input.players)

    context = build_flop_context(solver_input, _branch_result())

    assert context.player_context.players == players_before
    assert len(context.player_context.players) == len(players_before)
    assert context.player_context.is_heads_up is True
    assert "active_player" not in solver_input.raw_clear_json_ref
    assert "created_hero" not in solver_input.raw_clear_json_ref


def test_flop_context_contains_no_decision_runtime_or_click_payload_keys() -> None:
    context = build_flop_context(_solver_input(), _branch_result())
    payload = context.to_json_dict()
    payload_keys = {key.lower() for key in _walk_keys(payload)}

    assert payload_keys.isdisjoint(FORBIDDEN_PAYLOAD_KEYS)
    assert "runtime" not in " ".join(sorted(payload_keys))
    assert "click" not in " ".join(sorted(payload_keys))


def test_flop_context_keeps_cards_as_metadata_without_repairing_or_validation_language() -> None:
    solver_input = _solver_input()
    context = build_flop_context(solver_input, _branch_result())

    assert context.hero_cards == solver_input.hero_cards
    assert context.board_cards == solver_input.board_cards
    assert "hero_cards" in context.context_fields_used
    assert "board_cards" in context.context_fields_used

    serialized_notes = " ".join(context.notes).lower()
    assert "invalid" not in serialized_notes
    assert "duplicate" not in serialized_notes
    assert "collision" not in serialized_notes
