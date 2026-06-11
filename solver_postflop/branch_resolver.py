"""Branch routing for trusted postflop SolverInput objects."""

from __future__ import annotations

from typing import Any, Optional

from solver_postflop.branch_contracts import (
    SolverBranch,
    SolverBranchResult,
    branch_family_for,
    next_module_for,
)
from solver_postflop.engine_contracts import SolverInput, SolverTrace


def resolve_solver_branch(
    solver_input: SolverInput,
    solver_trace: Optional[SolverTrace] = None,
) -> SolverBranchResult:
    """Route a trusted SolverInput to the next solver branch.

    Routing is metadata-only. It uses the board-card count already present in
    SolverInput and does not repair or reinterpret the Clear JSON payload.
    """

    board_cards = solver_input.board_cards
    board_count = len(board_cards) if board_cards is not None else None
    branch, reason = _branch_for_board_count(board_count)
    next_module = next_module_for(branch)

    result = SolverBranchResult(
        case_id=_case_id_from_solver_input(solver_input),
        source_file=solver_trace.input_file if solver_trace is not None else _source_file_from_solver_input(solver_input),
        branch=branch,
        branch_family=branch_family_for(branch),
        next_module=next_module,
        branch_reason=reason,
        is_decision_branch_enabled=False,
        is_runtime_branch_enabled=False,
        notes=(
            "branch_routing_metadata_only",
            f"board_card_count={board_count if board_count is not None else 'not_provided'}",
        ),
    )

    if solver_trace is not None:
        _append_branch_note_to_trace(solver_trace, result)

    return result


def _branch_for_board_count(board_count: Optional[int]) -> tuple[SolverBranch, str]:
    if board_count is None:
        return SolverBranch.UNSUPPORTED, "board_cards_not_provided_for_branch_routing"
    if board_count == 0:
        return SolverBranch.PREFLOP_NOT_HANDLED, "board_card_count_0_routes_to_preflop_not_handled"
    if board_count == 3:
        return SolverBranch.FLOP, "board_card_count_3_routes_to_flop"
    if board_count == 4:
        return SolverBranch.TURN_NOT_IMPLEMENTED_YET, "board_card_count_4_routes_to_turn_placeholder"
    if board_count == 5:
        return SolverBranch.RIVER_NOT_IMPLEMENTED_YET, "board_card_count_5_routes_to_river_placeholder"
    return SolverBranch.UNSUPPORTED, "unsupported_board_card_count_for_branch_routing"


def _case_id_from_solver_input(solver_input: SolverInput) -> Optional[str]:
    raw_payload = solver_input.raw_clear_json_ref
    if isinstance(raw_payload, dict):
        case_id = raw_payload.get("case_id")
        if case_id not in (None, ""):
            return str(case_id)
    return None


def _source_file_from_solver_input(solver_input: SolverInput) -> str:
    raw_payload: Any = solver_input.raw_clear_json_ref
    if isinstance(raw_payload, dict):
        for key in ("source_file", "clear_json_file"):
            source_file = raw_payload.get(key)
            if source_file not in (None, ""):
                return str(source_file)
    return ""


def _append_branch_note_to_trace(solver_trace: SolverTrace, result: SolverBranchResult) -> None:
    solver_trace.module_chain_next_step = result.next_module
    solver_trace.notes = tuple(
        list(solver_trace.notes)
        + [
            f"branch={result.branch.value}",
            f"branch_reason={result.branch_reason}",
            "branch_resolver_completed_without_poker_decision",
        ]
    )
