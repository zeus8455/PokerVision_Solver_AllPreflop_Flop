"""Solver input builder for explicitly loaded Clear JSON payloads."""

from __future__ import annotations

from collections.abc import Mapping as MappingABC
from typing import Any, Mapping, Optional, Sequence

from solver_postflop.engine_contracts import ClearJsonInput, SolverInput, SolverTrace

MAPPING_VERSION = "v0.1.3"
_NEXT_STEP = "solver_input_ready_for_future_branch_resolver"

_FIELD_ALIASES: Mapping[str, tuple[str, ...]] = {
    "table_id": ("table_id", "tableId", "table"),
    "hand_id": ("hand_id", "handId", "hand"),
    "hero_cards": ("hero_cards", "heroCards", "hero"),
    "board_cards": ("board_cards", "boardCards", "board"),
    "players": ("players", "active_players"),
    "pot": ("total_pot", "pot"),
    "to_call": ("to_call", "toCall"),
    "stacks": ("stacks", "chips"),
    "committed_amounts": ("committed_amounts", "committed"),
    "positions": ("positions", "player_positions"),
    "button": ("button", "dealer_button", "button_position"),
    "blinds": ("blinds",),
    "allowed_actions": ("allowed_actions", "available_actions"),
    "action_context": ("action_context",),
}

_REQUIRED_TRACE_FIELDS = tuple(_FIELD_ALIASES)


def build_solver_input(clear_input: ClearJsonInput) -> tuple[SolverInput, SolverTrace]:
    """Build the first internal solver input from a trusted Clear JSON payload."""

    raw_data = clear_input.raw_data
    if not isinstance(raw_data, MappingABC):
        raise TypeError("ClearJsonInput.raw_data must be a mapping.")

    values: dict[str, Any] = {}
    fields_used: list[str] = []
    fields_not_provided: list[str] = []
    notes: list[str] = []

    for target_field in _REQUIRED_TRACE_FIELDS:
        value, source_key = _extract_value(raw_data, target_field)
        if value is _MISSING:
            fallback_value = _metadata_fallback(clear_input, target_field)
            if fallback_value is _MISSING:
                values[target_field] = _default_value(target_field)
                fields_not_provided.append(target_field)
                continue
            value = fallback_value
            source_key = f"ClearJsonInput.{target_field}"

        values[target_field] = _normalize_value(target_field, value)
        fields_used.append(f"{source_key}->{target_field}")

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
        notes.append("missing optional Clear JSON fields were recorded without blocking input build")
    else:
        notes.append("all baseline Clear JSON fields were provided")

    trace = SolverTrace(
        input_file=clear_input.source_file,
        mapping_version=MAPPING_VERSION,
        fields_used=tuple(fields_used),
        fields_not_provided=tuple(fields_not_provided),
        module_chain_next_step=_NEXT_STEP,
        notes=tuple(notes),
    )

    return solver_input, trace


class _Missing:
    pass


_MISSING = _Missing()


def _extract_value(raw_data: Mapping[str, Any], target_field: str) -> tuple[Any, Optional[str]]:
    for source_key in _FIELD_ALIASES[target_field]:
        if source_key in raw_data:
            return raw_data[source_key], source_key
    return _MISSING, None


def _metadata_fallback(clear_input: ClearJsonInput, target_field: str) -> Any:
    if target_field == "table_id" and clear_input.table_id is not None:
        return clear_input.table_id
    if target_field == "hand_id" and clear_input.hand_id is not None:
        return clear_input.hand_id
    return _MISSING


def _default_value(target_field: str) -> Any:
    if target_field in {"hero_cards", "board_cards", "players", "allowed_actions"}:
        return ()
    if target_field in {"stacks", "committed_amounts", "positions", "blinds", "action_context"}:
        return {}
    return None


def _normalize_value(target_field: str, value: Any) -> Any:
    if value is None:
        return _default_value(target_field)
    if target_field in {"hero_cards", "board_cards", "players", "allowed_actions"}:
        return _as_tuple(value)
    if target_field in {"stacks", "committed_amounts", "positions", "blinds", "action_context"}:
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
