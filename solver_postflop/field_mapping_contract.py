"""Versioned Clear JSON to SolverInput field mapping contract.

This module is declarative. It does not read files, transform poker state,
or decide any poker action. It only describes which trusted Clear JSON fields
feed each SolverInput field and which later solver modules may consume them.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

FIELD_MAPPING_VERSION = "v0.3.0"


class ClearJsonFieldRequirement(str, Enum):
    """Requirement level for a Clear JSON source field."""

    REQUIRED_FOR_BASE_INPUT = "required_for_base_input"
    OPTIONAL_NOT_PROVIDED_ALLOWED = "optional_not_provided_allowed"
    REQUIRED_FOR_FUTURE_BRANCH = "required_for_future_branch"


class FutureSolverModule(str, Enum):
    """Future module groups that may consume mapped SolverInput fields."""

    TRACE_REPORT = "trace_report"
    BRANCH_RESOLVER = "branch_resolver"
    FLOP_CONTEXT_BUILDER = "flop_context_builder"
    TURN_BRANCH_LATER = "turn_branch_later"
    RIVER_BRANCH_LATER = "river_branch_later"
    HAND_STRENGTH_LATER = "hand_strength_later"
    DRAW_ANALYSIS_LATER = "draw_analysis_later"
    EQUITY_LATER = "equity_later"
    RANGE_ASSIGNMENT_LATER = "range_assignment_later"
    POSITION_LOGIC_LATER = "position_logic_later"
    SPR_CALCULATION_LATER = "spr_calculation_later"
    SIZE_POLICY_LATER = "size_policy_later"
    DECISION_AVAILABILITY_LATER = "decision_availability_later"
    ACTION_CONTEXT_LATER = "action_context_later"
    PREFLOP_CONTEXT_CONSUMER_LATER = "preflop_context_consumer_later"


@dataclass(frozen=True)
class FieldMappingEntry:
    """Single declarative Clear JSON to SolverInput mapping row."""

    clear_json_fields: tuple[str, ...]
    solver_input_field: str
    data_kind: str
    requirement: ClearJsonFieldRequirement
    future_modules: tuple[FutureSolverModule, ...]
    policy_note: str

    def primary_clear_json_field(self) -> str:
        """Return the preferred Clear JSON source field for this mapping."""

        return self.clear_json_fields[0]

    def includes_clear_json_field(self, field_name: str) -> bool:
        """Return True when a Clear JSON field is part of this mapping row."""

        return field_name in self.clear_json_fields


CLEAR_JSON_FIELD_MAPPINGS: tuple[FieldMappingEntry, ...] = (
    FieldMappingEntry(
        clear_json_fields=("case_id",),
        solver_input_field="case_id",
        data_kind="string | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(FutureSolverModule.TRACE_REPORT,),
        policy_note="Case metadata is used for trace/report correlation when present.",
    ),
    FieldMappingEntry(
        clear_json_fields=("table_id",),
        solver_input_field="table_id",
        data_kind="string | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(FutureSolverModule.TRACE_REPORT,),
        policy_note="Table metadata is carried forward without inference.",
    ),
    FieldMappingEntry(
        clear_json_fields=("hand_id",),
        solver_input_field="hand_id",
        data_kind="string | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(FutureSolverModule.TRACE_REPORT,),
        policy_note="Hand metadata is carried forward without inference.",
    ),
    FieldMappingEntry(
        clear_json_fields=("timestamp", "created_at"),
        solver_input_field="source_timestamp",
        data_kind="string | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(FutureSolverModule.TRACE_REPORT,),
        policy_note="Timestamp metadata is optional and never reconstructed in this layer.",
    ),
    FieldMappingEntry(
        clear_json_fields=("hero_cards",),
        solver_input_field="hero_cards",
        data_kind="sequence",
        requirement=ClearJsonFieldRequirement.REQUIRED_FOR_FUTURE_BRANCH,
        future_modules=(
            FutureSolverModule.BRANCH_RESOLVER,
            FutureSolverModule.FLOP_CONTEXT_BUILDER,
            FutureSolverModule.HAND_STRENGTH_LATER,
            FutureSolverModule.DRAW_ANALYSIS_LATER,
            FutureSolverModule.EQUITY_LATER,
            FutureSolverModule.RANGE_ASSIGNMENT_LATER,
        ),
        policy_note="Cards are mapped as provided; this contract performs no card checks.",
    ),
    FieldMappingEntry(
        clear_json_fields=("board_cards",),
        solver_input_field="board_cards",
        data_kind="sequence",
        requirement=ClearJsonFieldRequirement.REQUIRED_FOR_FUTURE_BRANCH,
        future_modules=(
            FutureSolverModule.BRANCH_RESOLVER,
            FutureSolverModule.FLOP_CONTEXT_BUILDER,
            FutureSolverModule.HAND_STRENGTH_LATER,
            FutureSolverModule.DRAW_ANALYSIS_LATER,
            FutureSolverModule.EQUITY_LATER,
        ),
        policy_note="Board cards are mapped as provided; street use happens in later modules.",
    ),
    FieldMappingEntry(
        clear_json_fields=("players",),
        solver_input_field="players",
        data_kind="sequence | mapping",
        requirement=ClearJsonFieldRequirement.REQUIRED_FOR_FUTURE_BRANCH,
        future_modules=(
            FutureSolverModule.FLOP_CONTEXT_BUILDER,
            FutureSolverModule.RANGE_ASSIGNMENT_LATER,
            FutureSolverModule.POSITION_LOGIC_LATER,
            FutureSolverModule.SPR_CALCULATION_LATER,
        ),
        policy_note="Player data is carried forward exactly as provided by Clear JSON.",
    ),
    FieldMappingEntry(
        clear_json_fields=("hero_id", "hero"),
        solver_input_field="hero_id",
        data_kind="string | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(FutureSolverModule.FLOP_CONTEXT_BUILDER, FutureSolverModule.POSITION_LOGIC_LATER),
        policy_note="Hero identity is consumed only when already present.",
    ),
    FieldMappingEntry(
        clear_json_fields=("positions",),
        solver_input_field="positions",
        data_kind="mapping | sequence | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(FutureSolverModule.FLOP_CONTEXT_BUILDER, FutureSolverModule.POSITION_LOGIC_LATER),
        policy_note="Position data is optional and is not repaired here.",
    ),
    FieldMappingEntry(
        clear_json_fields=("total_pot", "pot"),
        solver_input_field="pot",
        data_kind="number | null",
        requirement=ClearJsonFieldRequirement.REQUIRED_FOR_FUTURE_BRANCH,
        future_modules=(
            FutureSolverModule.FLOP_CONTEXT_BUILDER,
            FutureSolverModule.SPR_CALCULATION_LATER,
            FutureSolverModule.SIZE_POLICY_LATER,
        ),
        policy_note="Pot amount is copied from preferred total_pot, falling back to pot when present.",
    ),
    FieldMappingEntry(
        clear_json_fields=("to_call",),
        solver_input_field="to_call",
        data_kind="number | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(
            FutureSolverModule.FLOP_CONTEXT_BUILDER,
            FutureSolverModule.DECISION_AVAILABILITY_LATER,
            FutureSolverModule.ACTION_CONTEXT_LATER,
        ),
        policy_note="Call amount is optional and copied without action repair.",
    ),
    FieldMappingEntry(
        clear_json_fields=("stacks", "chips"),
        solver_input_field="stacks",
        data_kind="mapping | sequence | number | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(FutureSolverModule.FLOP_CONTEXT_BUILDER, FutureSolverModule.SPR_CALCULATION_LATER),
        policy_note="Stack/chip data is copied without recomputation.",
    ),
    FieldMappingEntry(
        clear_json_fields=("committed_amounts", "committed"),
        solver_input_field="committed_amounts",
        data_kind="mapping | sequence | number | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(FutureSolverModule.FLOP_CONTEXT_BUILDER, FutureSolverModule.SPR_CALCULATION_LATER),
        policy_note="Committed amounts are optional and copied without repair.",
    ),
    FieldMappingEntry(
        clear_json_fields=("button",),
        solver_input_field="button",
        data_kind="string | number | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(FutureSolverModule.POSITION_LOGIC_LATER,),
        policy_note="Button metadata is optional and never inferred here.",
    ),
    FieldMappingEntry(
        clear_json_fields=("blinds",),
        solver_input_field="blinds",
        data_kind="mapping | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(FutureSolverModule.SPR_CALCULATION_LATER, FutureSolverModule.SIZE_POLICY_LATER),
        policy_note="Blind metadata is optional and copied when present.",
    ),
    FieldMappingEntry(
        clear_json_fields=("allowed_actions",),
        solver_input_field="allowed_actions",
        data_kind="sequence | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(FutureSolverModule.DECISION_AVAILABILITY_LATER, FutureSolverModule.ACTION_CONTEXT_LATER),
        policy_note="Allowed actions are copied exactly as provided; no action is added here.",
    ),
    FieldMappingEntry(
        clear_json_fields=("action_context",),
        solver_input_field="action_context",
        data_kind="mapping | string | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(FutureSolverModule.FLOP_CONTEXT_BUILDER, FutureSolverModule.ACTION_CONTEXT_LATER),
        policy_note="Action context is copied without logical repair.",
    ),
    FieldMappingEntry(
        clear_json_fields=("current_actor", "active_player"),
        solver_input_field="current_actor",
        data_kind="string | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(FutureSolverModule.ACTION_CONTEXT_LATER,),
        policy_note="Current actor is optional and not created here.",
    ),
    FieldMappingEntry(
        clear_json_fields=("preflop_context",),
        solver_input_field="preflop_context_raw",
        data_kind="mapping | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(FutureSolverModule.PREFLOP_CONTEXT_CONSUMER_LATER,),
        policy_note="Preflop context is consumed only when Clear JSON already includes it.",
    ),
    FieldMappingEntry(
        clear_json_fields=("pot_type",),
        solver_input_field="pot_type",
        data_kind="string | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(FutureSolverModule.FLOP_CONTEXT_BUILDER, FutureSolverModule.PREFLOP_CONTEXT_CONSUMER_LATER),
        policy_note="Pot type is optional and not reconstructed here.",
    ),
    FieldMappingEntry(
        clear_json_fields=("preflop_aggressor",),
        solver_input_field="preflop_aggressor",
        data_kind="string | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(FutureSolverModule.PREFLOP_CONTEXT_CONSUMER_LATER,),
        policy_note="Preflop aggressor is optional and not reconstructed here.",
    ),
    FieldMappingEntry(
        clear_json_fields=("hero_preflop_role",),
        solver_input_field="hero_preflop_role",
        data_kind="string | null",
        requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
        future_modules=(FutureSolverModule.PREFLOP_CONTEXT_CONSUMER_LATER,),
        policy_note="Hero preflop role is optional and not reconstructed here.",
    ),
)


def get_field_mapping_entries() -> tuple[FieldMappingEntry, ...]:
    """Return the immutable mapping table."""

    return CLEAR_JSON_FIELD_MAPPINGS


def solver_input_fields_in_contract() -> tuple[str, ...]:
    """Return SolverInput target fields described by the contract."""

    return tuple(entry.solver_input_field for entry in CLEAR_JSON_FIELD_MAPPINGS)


def clear_json_fields_in_contract() -> tuple[str, ...]:
    """Return all Clear JSON source fields referenced by the contract."""

    fields: list[str] = []
    for entry in CLEAR_JSON_FIELD_MAPPINGS:
        fields.extend(entry.clear_json_fields)
    return tuple(fields)


def get_mapping_for_solver_input_field(field_name: str) -> FieldMappingEntry:
    """Return the mapping entry for a SolverInput field."""

    for entry in CLEAR_JSON_FIELD_MAPPINGS:
        if entry.solver_input_field == field_name:
            return entry
    raise KeyError(f"No mapping contract entry for SolverInput field: {field_name}")


def get_mappings_for_clear_json_field(field_name: str) -> tuple[FieldMappingEntry, ...]:
    """Return mapping rows that reference a Clear JSON field."""

    return tuple(
        entry for entry in CLEAR_JSON_FIELD_MAPPINGS if entry.includes_clear_json_field(field_name)
    )


def future_modules_for_solver_input_field(field_name: str) -> tuple[FutureSolverModule, ...]:
    """Return future module groups that may consume a SolverInput field."""

    return get_mapping_for_solver_input_field(field_name).future_modules


def assert_solver_input_fields_are_described(fields: Iterable[str]) -> None:
    """Raise KeyError when a SolverInput field is not described by the contract."""

    known_fields = set(solver_input_fields_in_contract())
    missing = [field for field in fields if field not in known_fields]
    if missing:
        raise KeyError(f"SolverInput fields missing from mapping contract: {missing}")
