from __future__ import annotations

import dataclasses
import json

import pytest

from solver_postflop import (
    CLEAR_JSON_FIELD_MAPPINGS,
    FIELD_MAPPING_VERSION,
    ClearJsonFieldRequirement,
    FieldMappingEntry,
    FutureSolverModule,
    assert_solver_input_fields_are_described,
    clear_json_fields_in_contract,
    future_modules_for_solver_input_field,
    get_field_mapping_entries,
    get_mapping_for_solver_input_field,
    get_mappings_for_clear_json_field,
    solver_input_fields_in_contract,
)


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

FUTURE_CONTRACT_FIELDS = {
    "case_id",
    "source_timestamp",
    "hero_id",
    "current_actor",
    "preflop_context_raw",
    "pot_type",
    "preflop_aggressor",
    "hero_preflop_role",
}


def test_field_mapping_contract_version_and_rows_exist() -> None:
    assert FIELD_MAPPING_VERSION == "v0.3.0"
    assert len(CLEAR_JSON_FIELD_MAPPINGS) >= 20
    assert get_field_mapping_entries() == CLEAR_JSON_FIELD_MAPPINGS

    for entry in CLEAR_JSON_FIELD_MAPPINGS:
        assert isinstance(entry, FieldMappingEntry)
        assert dataclasses.is_dataclass(entry)
        assert entry.clear_json_fields
        assert entry.solver_input_field
        assert entry.data_kind
        assert isinstance(entry.requirement, ClearJsonFieldRequirement)
        assert entry.future_modules
        assert all(isinstance(module, FutureSolverModule) for module in entry.future_modules)
        assert entry.policy_note


def test_current_solver_input_fields_are_described_by_contract() -> None:
    contract_fields = set(solver_input_fields_in_contract())

    assert CURRENT_SOLVER_INPUT_FIELDS <= contract_fields
    assert FUTURE_CONTRACT_FIELDS <= contract_fields
    assert_solver_input_fields_are_described(CURRENT_SOLVER_INPUT_FIELDS)


def test_core_clear_json_source_fields_are_described() -> None:
    clear_json_fields = set(clear_json_fields_in_contract())

    required_sources = {
        "case_id",
        "table_id",
        "hand_id",
        "timestamp",
        "created_at",
        "hero_cards",
        "board_cards",
        "players",
        "hero_id",
        "hero",
        "positions",
        "total_pot",
        "pot",
        "to_call",
        "stacks",
        "chips",
        "committed",
        "committed_amounts",
        "button",
        "blinds",
        "allowed_actions",
        "action_context",
        "current_actor",
        "active_player",
        "preflop_context",
        "pot_type",
        "preflop_aggressor",
        "hero_preflop_role",
    }

    assert required_sources <= clear_json_fields


def test_get_mapping_for_solver_input_field_returns_expected_entries() -> None:
    hero_cards = get_mapping_for_solver_input_field("hero_cards")
    assert hero_cards.clear_json_fields == ("hero_cards",)
    assert FutureSolverModule.BRANCH_RESOLVER in hero_cards.future_modules
    assert FutureSolverModule.FLOP_CONTEXT_BUILDER in hero_cards.future_modules

    pot = get_mapping_for_solver_input_field("pot")
    assert pot.clear_json_fields == ("total_pot", "pot")
    assert FutureSolverModule.SPR_CALCULATION_LATER in pot.future_modules

    action_context = get_mapping_for_solver_input_field("action_context")
    assert action_context.clear_json_fields == ("action_context",)
    assert FutureSolverModule.ACTION_CONTEXT_LATER in action_context.future_modules

    with pytest.raises(KeyError):
        get_mapping_for_solver_input_field("not_a_solver_input_field")


def test_clear_json_field_reverse_lookup_supports_aliases() -> None:
    total_pot_mappings = get_mappings_for_clear_json_field("total_pot")
    pot_mappings = get_mappings_for_clear_json_field("pot")
    chips_mappings = get_mappings_for_clear_json_field("chips")

    assert total_pot_mappings
    assert pot_mappings
    assert chips_mappings
    assert total_pot_mappings[0].solver_input_field == "pot"
    assert pot_mappings[0].solver_input_field == "pot"
    assert chips_mappings[0].solver_input_field == "stacks"


def test_future_modules_are_attached_to_each_mapping_group() -> None:
    assert FutureSolverModule.TRACE_REPORT in future_modules_for_solver_input_field("case_id")
    assert FutureSolverModule.BRANCH_RESOLVER in future_modules_for_solver_input_field("board_cards")
    assert FutureSolverModule.FLOP_CONTEXT_BUILDER in future_modules_for_solver_input_field("players")
    assert FutureSolverModule.DECISION_AVAILABILITY_LATER in future_modules_for_solver_input_field("allowed_actions")
    assert FutureSolverModule.PREFLOP_CONTEXT_CONSUMER_LATER in future_modules_for_solver_input_field("preflop_context_raw")


def test_field_mapping_entries_are_json_serializable_without_behavior() -> None:
    serialized = []
    for entry in CLEAR_JSON_FIELD_MAPPINGS:
        serialized.append(
            {
                "clear_json_fields": list(entry.clear_json_fields),
                "solver_input_field": entry.solver_input_field,
                "data_kind": entry.data_kind,
                "requirement": entry.requirement.value,
                "future_modules": [module.value for module in entry.future_modules],
                "policy_note": entry.policy_note,
            }
        )

    payload = json.loads(json.dumps(serialized, sort_keys=True))
    assert len(payload) == len(CLEAR_JSON_FIELD_MAPPINGS)
    assert payload[0]["solver_input_field"] == "case_id"


def test_contract_text_does_not_reference_old_source_pipeline_markers() -> None:
    forbidden = (
        "Dark_JSON",
        "Pending_JSON",
        "Service JSON",
        "Runtime JSON",
        "source_discovery",
        "display_analysis_cycle",
        "Action_Button",
        "PokerVisionFinalVersionNoSolver_snapshot",
    )

    combined = "\n".join(
        [FIELD_MAPPING_VERSION]
        + [entry.policy_note for entry in CLEAR_JSON_FIELD_MAPPINGS]
        + [entry.solver_input_field for entry in CLEAR_JSON_FIELD_MAPPINGS]
    )

    for marker in forbidden:
        assert marker not in combined
