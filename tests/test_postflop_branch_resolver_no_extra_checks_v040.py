from __future__ import annotations

import copy
import pathlib
from typing import Any

from solver_postflop import SolverBranch, SolverInput, SolverTrace, resolve_solver_branch


BRANCH_SOURCE_FILES = (
    pathlib.Path("solver_postflop/branch_resolver.py"),
    pathlib.Path("solver_postflop/branch_contracts.py"),
)


FORBIDDEN_SOURCE_MARKERS = (
    "Dark_JSON",
    "Pending_JSON",
    "Service JSON",
    "Runtime JSON",
    "source_discovery",
    "display_analysis_cycle",
    "Action_Button",
    "PokerVisionFinalVersionNoSolver_snapshot",
    "solver_preflop",
    "validate_cards",
    "card_validation",
    "duplicate_cards",
    "hero_board_collision",
    "hero-board collision",
    "filter_players",
    "player_filtering",
    "create_hero",
    "reconstruct_hero",
    "active_player_reconstruction",
    "runtime_plan",
    "click_result",
)


FORBIDDEN_RESULT_KEYS = {
    "action",
    "raw_action",
    "recommended_action",
    "decision",
    "poker_decision",
    "bet_size",
    "sizing",
    "runtime_plan",
    "click_sequence",
    "click_result",
    "button_label",
}


def _branch_input(*, board_cards: tuple[str, ...] = ("Ah", "7d", "2c")) -> SolverInput:
    raw_payload: dict[str, Any] = {
        "case_id": "branch_no_extra_logic_case",
        "source_file": "branch_no_extra_logic_case.clear.json",
        "board_cards": list(board_cards),
        "players": [
            {"id": "hero", "position": "BB", "folded": False, "stack": 97.5},
            {"id": "villain", "position": "BTN", "folded": False, "stack": 101.0},
        ],
        "unexpected_payload_field": {"must_remain": "read_only"},
    }
    return SolverInput(
        table_id="table_01",
        hand_id="hand_01",
        hero_cards=("Ks", "Kh"),
        board_cards=board_cards,
        players=tuple(copy.deepcopy(raw_payload["players"])),
        pot=6.5,
        to_call=0,
        allowed_actions=("check", "bet"),
        raw_clear_json_ref=raw_payload,
    )


def _trace() -> SolverTrace:
    return SolverTrace(
        input_file="branch_no_extra_logic_case.clear.json",
        mapping_version="v0.3.0",
        fields_used=("board_cards", "players", "allowed_actions"),
        fields_not_provided=(),
        module_chain_next_step="solver_input_ready_for_future_branch_resolver",
        notes=("trace_before_branch_resolver",),
    )


def test_branch_resolver_source_has_no_forbidden_external_or_validation_markers() -> None:
    combined_source = "\n".join(path.read_text(encoding="utf-8") for path in BRANCH_SOURCE_FILES)

    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in combined_source


def test_branch_resolver_does_not_mutate_clear_json_or_solver_input_fields() -> None:
    solver_input = _branch_input()
    solver_trace = _trace()

    raw_before = copy.deepcopy(solver_input.raw_clear_json_ref)
    players_before = copy.deepcopy(solver_input.players)
    board_before = copy.deepcopy(solver_input.board_cards)
    hero_cards_before = copy.deepcopy(solver_input.hero_cards)
    allowed_actions_before = copy.deepcopy(solver_input.allowed_actions)

    result = resolve_solver_branch(solver_input, solver_trace=solver_trace)

    assert result.branch == SolverBranch.FLOP
    assert solver_input.raw_clear_json_ref == raw_before
    assert solver_input.players == players_before
    assert solver_input.board_cards == board_before
    assert solver_input.hero_cards == hero_cards_before
    assert solver_input.allowed_actions == allowed_actions_before


def test_branch_resolver_does_not_read_files(monkeypatch) -> None:
    def fail_file_io(*args: Any, **kwargs: Any) -> None:  # pragma: no cover - only runs on bug
        raise AssertionError("Branch Resolver must not perform file I/O")

    monkeypatch.setattr("builtins.open", fail_file_io)
    monkeypatch.setattr(pathlib.Path, "open", fail_file_io)
    monkeypatch.setattr(pathlib.Path, "read_text", fail_file_io)
    monkeypatch.setattr(pathlib.Path, "read_bytes", fail_file_io)

    result = resolve_solver_branch(_branch_input())

    assert result.branch == SolverBranch.FLOP
    assert result.next_module == "flop_context_builder"


def test_branch_result_contains_no_poker_decision_payload_or_runtime_plan() -> None:
    result = resolve_solver_branch(_branch_input())
    result_payload = result.to_json_dict()

    assert result_payload["is_decision_branch_enabled"] is False
    assert result_payload["is_runtime_branch_enabled"] is False
    assert FORBIDDEN_RESULT_KEYS.isdisjoint(result_payload.keys())
    assert "click" not in " ".join(str(value).lower() for value in result_payload.values())


def test_branch_resolver_does_not_filter_players_or_invent_hero_or_active_player() -> None:
    solver_input = _branch_input()
    players_before = copy.deepcopy(solver_input.players)

    resolve_solver_branch(solver_input)

    assert solver_input.players == players_before
    assert len(solver_input.players) == 2
    assert all(player in solver_input.players for player in players_before)
    assert "hero_id" not in solver_input.raw_clear_json_ref
    assert "active_player" not in solver_input.raw_clear_json_ref


def test_unsupported_branch_uses_routing_language_not_validation_language() -> None:
    result = resolve_solver_branch(_branch_input(board_cards=("Ah", "7d", "2c", "Ts", "3h", "4d")))

    assert result.branch == SolverBranch.UNSUPPORTED
    assert result.branch_reason == "unsupported_board_card_count_for_branch_routing"
    assert "invalid" not in result.branch_reason.lower()
    assert "duplicate" not in result.branch_reason.lower()
    assert "collision" not in result.branch_reason.lower()
