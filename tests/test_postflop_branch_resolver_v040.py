from __future__ import annotations

import copy

from solver_postflop import (
    SolverBranch,
    SolverBranchFamily,
    SolverInput,
    SolverTrace,
    resolve_solver_branch,
)


def _solver_input_with_board(board_cards, *, case_id: str = "branch_case") -> SolverInput:
    return SolverInput(
        table_id="table_01",
        hand_id="hand_01",
        hero_cards=("Ah", "Kh"),
        board_cards=tuple(board_cards),
        players=({"id": "hero", "position": "BB"}, {"id": "villain", "position": "BTN"}),
        raw_clear_json_ref={"case_id": case_id, "source_file": f"{case_id}.clear.json"},
    )


def _trace() -> SolverTrace:
    return SolverTrace(
        input_file="branch_case.clear.json",
        mapping_version="v0.3.0",
        fields_used=("board_cards",),
        fields_not_provided=(),
        module_chain_next_step="solver_input_ready_for_future_branch_resolver",
        notes=("solver_input_ready",),
    )


def test_board_count_zero_routes_to_preflop_not_handled() -> None:
    result = resolve_solver_branch(_solver_input_with_board(()))

    assert result.branch == SolverBranch.PREFLOP_NOT_HANDLED
    assert result.branch_family == SolverBranchFamily.NON_POSTFLOP
    assert result.next_module == "preflop_solver_external_or_skip"
    assert result.branch_reason == "board_card_count_0_routes_to_preflop_not_handled"
    assert result.is_decision_branch_enabled is False
    assert result.is_runtime_branch_enabled is False


def test_board_count_three_routes_to_flop_branch() -> None:
    result = resolve_solver_branch(_solver_input_with_board(("Ah", "7d", "2c"), case_id="flop_case"))

    assert result.case_id == "flop_case"
    assert result.source_file == "flop_case.clear.json"
    assert result.branch == SolverBranch.FLOP
    assert result.branch_family == SolverBranchFamily.POSTFLOP_FLOP
    assert result.next_module == "flop_context_builder"
    assert result.branch_reason == "board_card_count_3_routes_to_flop"


def test_board_count_four_routes_to_turn_placeholder_branch() -> None:
    result = resolve_solver_branch(_solver_input_with_board(("Ah", "7d", "2c", "Ts")))

    assert result.branch == SolverBranch.TURN_NOT_IMPLEMENTED_YET
    assert result.branch_family == SolverBranchFamily.POSTFLOP_TURN
    assert result.next_module == "turn_branch_not_implemented_yet"
    assert result.branch_reason == "board_card_count_4_routes_to_turn_placeholder"


def test_board_count_five_routes_to_river_placeholder_branch() -> None:
    result = resolve_solver_branch(_solver_input_with_board(("Ah", "7d", "2c", "Ts", "3h")))

    assert result.branch == SolverBranch.RIVER_NOT_IMPLEMENTED_YET
    assert result.branch_family == SolverBranchFamily.POSTFLOP_RIVER
    assert result.next_module == "river_branch_not_implemented_yet"
    assert result.branch_reason == "board_card_count_5_routes_to_river_placeholder"


def test_missing_board_cards_routes_to_unsupported_without_validation_language() -> None:
    solver_input = SolverInput(board_cards=None, raw_clear_json_ref={"case_id": "missing_board"})
    result = resolve_solver_branch(solver_input)

    assert result.branch == SolverBranch.UNSUPPORTED
    assert result.branch_reason == "board_cards_not_provided_for_branch_routing"
    assert "invalid" not in result.branch_reason


def test_unsupported_board_counts_route_to_unsupported_without_invalid_wording() -> None:
    for board_cards in (("Ah",), ("Ah", "7d"), ("Ah", "7d", "2c", "Ts", "3h", "4d")):
        result = resolve_solver_branch(_solver_input_with_board(board_cards))

        assert result.branch == SolverBranch.UNSUPPORTED
        assert result.branch_family == SolverBranchFamily.UNSUPPORTED
        assert result.next_module == "unsupported_branch_report"
        assert result.branch_reason == "unsupported_board_card_count_for_branch_routing"
        assert "invalid" not in result.branch_reason


def test_solver_trace_can_be_supplied_and_is_advanced_to_next_module() -> None:
    solver_trace = _trace()
    result = resolve_solver_branch(_solver_input_with_board(("Ah", "7d", "2c")), solver_trace=solver_trace)

    assert result.source_file == "branch_case.clear.json"
    assert result.next_module == "flop_context_builder"
    assert solver_trace.module_chain_next_step == "flop_context_builder"
    assert "branch=flop" in solver_trace.notes
    assert "branch_reason=board_card_count_3_routes_to_flop" in solver_trace.notes


def test_clear_json_payload_is_not_mutated_by_branch_resolver() -> None:
    solver_input = _solver_input_with_board(("Ah", "7d", "2c"), case_id="read_only_branch")
    before = copy.deepcopy(solver_input.raw_clear_json_ref)

    resolve_solver_branch(solver_input, solver_trace=_trace())

    assert solver_input.raw_clear_json_ref == before


def test_branch_result_serializes_after_resolver() -> None:
    result = resolve_solver_branch(_solver_input_with_board(("Ah", "7d", "2c")))

    assert result.to_json_dict() == {
        "case_id": "branch_case",
        "source_file": "branch_case.clear.json",
        "branch": "flop",
        "branch_family": "postflop_flop",
        "next_module": "flop_context_builder",
        "branch_reason": "board_card_count_3_routes_to_flop",
        "is_decision_branch_enabled": False,
        "is_runtime_branch_enabled": False,
        "notes": [
            "branch_routing_metadata_only",
            "board_card_count=3",
        ],
    }
