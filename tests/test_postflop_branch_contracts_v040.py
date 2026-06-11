from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass

from solver_postflop import (
    DEFAULT_FAMILY_BY_BRANCH,
    DEFAULT_NEXT_MODULE_BY_BRANCH,
    SolverBranch,
    SolverBranchFamily,
    SolverBranchResult,
    branch_family_for,
    next_module_for,
)


def test_solver_branch_labels_are_fixed() -> None:
    assert {branch.value for branch in SolverBranch} == {
        "preflop_not_handled",
        "flop",
        "turn_not_implemented_yet",
        "river_not_implemented_yet",
        "unsupported",
    }


def test_solver_branch_families_are_fixed() -> None:
    assert {family.value for family in SolverBranchFamily} == {
        "non_postflop",
        "postflop_flop",
        "postflop_turn",
        "postflop_river",
        "unsupported",
    }


def test_default_next_modules_are_defined_for_each_branch() -> None:
    assert set(DEFAULT_NEXT_MODULE_BY_BRANCH) == set(SolverBranch)
    assert next_module_for(SolverBranch.FLOP) == "flop_context_builder"
    assert next_module_for(SolverBranch.TURN_NOT_IMPLEMENTED_YET) == "turn_branch_not_implemented_yet"
    assert next_module_for(SolverBranch.RIVER_NOT_IMPLEMENTED_YET) == "river_branch_not_implemented_yet"


def test_default_branch_families_are_defined_for_each_branch() -> None:
    assert set(DEFAULT_FAMILY_BY_BRANCH) == set(SolverBranch)
    assert branch_family_for(SolverBranch.PREFLOP_NOT_HANDLED) == SolverBranchFamily.NON_POSTFLOP
    assert branch_family_for(SolverBranch.FLOP) == SolverBranchFamily.POSTFLOP_FLOP
    assert branch_family_for(SolverBranch.UNSUPPORTED) == SolverBranchFamily.UNSUPPORTED


def test_solver_branch_result_can_be_created_for_flop_branch() -> None:
    result = SolverBranchResult(
        case_id="case_flop_001",
        source_file="tests/fixtures/postflop_clear_json/real/flop/case.clear.json",
        branch=SolverBranch.FLOP,
        branch_family=SolverBranchFamily.POSTFLOP_FLOP,
        next_module="flop_context_builder",
        branch_reason="board_card_count_3_routes_to_flop",
        notes=("branch_contract_only",),
    )

    assert result.case_id == "case_flop_001"
    assert result.branch == SolverBranch.FLOP
    assert result.branch_family == SolverBranchFamily.POSTFLOP_FLOP
    assert result.next_module == "flop_context_builder"
    assert result.is_decision_branch_enabled is False
    assert result.is_runtime_branch_enabled is False


def test_solver_branch_result_serializes_to_json_safe_dict() -> None:
    result = SolverBranchResult(
        case_id="case_turn_001",
        source_file="synthetic_turn.clear.json",
        branch=SolverBranch.TURN_NOT_IMPLEMENTED_YET,
        branch_family=SolverBranchFamily.POSTFLOP_TURN,
        next_module=next_module_for(SolverBranch.TURN_NOT_IMPLEMENTED_YET),
        branch_reason="board_card_count_4_routes_to_turn_placeholder",
        notes=("no_decision_created", "routing_metadata_only"),
    )

    payload = result.to_json_dict()
    assert payload == {
        "case_id": "case_turn_001",
        "source_file": "synthetic_turn.clear.json",
        "branch": "turn_not_implemented_yet",
        "branch_family": "postflop_turn",
        "next_module": "turn_branch_not_implemented_yet",
        "branch_reason": "board_card_count_4_routes_to_turn_placeholder",
        "is_decision_branch_enabled": False,
        "is_runtime_branch_enabled": False,
        "notes": ["no_decision_created", "routing_metadata_only"],
    }
    json.dumps(payload, sort_keys=True)


def test_solver_branch_result_is_frozen_dataclass() -> None:
    result = SolverBranchResult(
        case_id=None,
        source_file="unsupported.clear.json",
        branch=SolverBranch.UNSUPPORTED,
        branch_family=SolverBranchFamily.UNSUPPORTED,
        next_module=next_module_for(SolverBranch.UNSUPPORTED),
        branch_reason="unsupported_branch_contract_case",
    )

    assert is_dataclass(result)
    assert asdict(result)["branch"] == SolverBranch.UNSUPPORTED


def test_branch_contracts_exported_from_public_package() -> None:
    import solver_postflop

    for public_name in (
        "SolverBranch",
        "SolverBranchFamily",
        "SolverBranchResult",
        "DEFAULT_NEXT_MODULE_BY_BRANCH",
        "DEFAULT_FAMILY_BY_BRANCH",
        "branch_family_for",
        "next_module_for",
    ):
        assert public_name in solver_postflop.__all__
        assert hasattr(solver_postflop, public_name)
