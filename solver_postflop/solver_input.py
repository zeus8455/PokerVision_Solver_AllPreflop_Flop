"""Solver input builder backed by the versioned Clear JSON field contract."""

from __future__ import annotations

from collections.abc import Mapping as MappingABC
from typing import Any, Mapping, Optional, Sequence

from solver_postflop.engine_contracts import ClearJsonInput, SolverInput, SolverTrace
from solver_postflop.field_mapping_contract import (
    CLEAR_JSON_FIELD_MAPPINGS,
    FIELD_MAPPING_VERSION,
    FieldMappingEntry,
    assert_solver_input_fields_are_described,
)

MAPPING_VERSION = FIELD_MAPPING_VERSION
_NEXT_STEP = "solver_input_ready_for_future_branch_resolver"

_CURRENT_SOLVER_INPUT_FIELDS = (
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
)

_SEQUENCE_FIELDS = frozenset({"hero_cards", "board_cards", "players", "allowed_actions"})
_MAPPING_FIELDS = frozenset({"stacks", "committed_amounts", "positions", "blinds", "action_context"})

assert_solver_input_fields_are_described(_CURRENT_SOLVER_INPUT_FIELDS)


def build_solver_input(clear_input: ClearJsonInput) -> tuple[SolverInput, SolverTrace]:
    """Build SolverInput from a trusted Clear JSON payload using the mapping contract."""

    raw_data = clear_input.raw_data
    if not isinstance(raw_data, MappingABC):
        raise TypeError("ClearJsonInput.raw_data must be a mapping.")

    values: dict[str, Any] = {}
    fields_used: list[str] = []
    fields_not_provided: list[str] = []
    notes: list[str] = []

    for mapping_entry in CLEAR_JSON_FIELD_MAPPINGS:
        target_field = mapping_entry.solver_input_field
        value, source_key = get_mapped_value(raw_data, mapping_entry)

        if value is _MISSING:
            fallback_value = _metadata_fallback(clear_input, target_field)
            if fallback_value is _MISSING:
                fields_not_provided.append(target_field)
                if target_field in _CURRENT_SOLVER_INPUT_FIELDS:
                    values[target_field] = _default_value(target_field)
                continue
            value = fallback_value
            source_key = f"ClearJsonInput.{target_field}"

        if target_field in _CURRENT_SOLVER_INPUT_FIELDS:
            values[target_field] = _normalize_value(target_field, value)
        fields_used.append(f"{source_key}->{target_field}")

    for target_field in _CURRENT_SOLVER_INPUT_FIELDS:
        values.setdefault(target_field, _default_value(target_field))

    solver_input = SolverInput(
        table_id=_optional_str(values["table_id"]),
        hand_id=_optional_str(values["hand_id"]),
        hero_cards=_as_tuple(values["hero_cards"]),
        board_cards=_as_tuple(values["board_cards"]),
        players=_as_tuple(values["players"]),
        pot=values["pot"],
        to_call=values["to_call"],
        stacks=_as_mapping(values["stacks"]),
        committed_amounts=_as_mapping(values["committed_amounts"]),
        positions=_as_mapping(values["positions"]),
        button=values["button"],
        blinds=_as_mapping(values["blinds"]),
        allowed_actions=_as_tuple(values["allowed_actions"]),
        action_context=_as_mapping(values["action_context"]),
        raw_clear_json_ref=raw_data,
    )

    fields_used.append("raw_data->raw_clear_json_ref")
    if fields_not_provided:
        notes.append("missing Clear JSON fields were recorded without blocking input build")
    else:
        notes.append("all contract Clear JSON fields were provided")
    notes.append("SolverInput mapping is backed by FIELD_MAPPING_VERSION")

    trace = SolverTrace(
        input_file=clear_input.source_file,
        mapping_version=MAPPING_VERSION,
        fields_used=tuple(_dedupe_preserve_order(fields_used)),
        fields_not_provided=tuple(_dedupe_preserve_order(fields_not_provided)),
        module_chain_next_step=_NEXT_STEP,
        notes=tuple(notes),
    )

    return solver_input, trace


def get_mapped_value(raw_data: Mapping[str, Any], mapping_entry: FieldMappingEntry) -> tuple[Any, Optional[str]]:
    """Return the first available Clear JSON value described by one mapping entry."""

    for source_key in mapping_entry.clear_json_fields:
        if source_key in raw_data:
            return raw_data[source_key], source_key
    return _MISSING, None


class _Missing:
    pass


_MISSING = _Missing()


def _metadata_fallback(clear_input: ClearJsonInput, target_field: str) -> Any:
    if target_field == "case_id" and clear_input.case_id is not None:
        return clear_input.case_id
    if target_field == "table_id" and clear_input.table_id is not None:
        return clear_input.table_id
    if target_field == "hand_id" and clear_input.hand_id is not None:
        return clear_input.hand_id
    return _MISSING


def _default_value(target_field: str) -> Any:
    if target_field in _SEQUENCE_FIELDS:
        return ()
    if target_field in _MAPPING_FIELDS:
        return {}
    return None


def _normalize_value(target_field: str, value: Any) -> Any:
    if value is None:
        return _default_value(target_field)
    if target_field in _SEQUENCE_FIELDS:
        return _as_tuple(value)
    if target_field in _MAPPING_FIELDS:
        return _as_mapping(value)
    return value


def _as_tuple(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(value)
    return (value,)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if value is None:
        return {}
    if isinstance(value, MappingABC):
        return value
    return {"value": value}


def _optional_str(value: Any) -> Optional[str]:
    if value in (None, ""):
        return None
    return str(value)


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
