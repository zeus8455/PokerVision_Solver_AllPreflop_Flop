"""Core contracts for the postflop solver engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional


@dataclass(slots=True)
class ClearJsonInput:
    """Trusted Clear JSON payload supplied explicitly to the solver layer."""

    source_file: str
    raw_data: Mapping[str, Any]
    loaded_at: str
    case_id: Optional[str] = None
    hand_id: Optional[str] = None
    table_id: Optional[str] = None


@dataclass(slots=True)
class SolverInput:
    """Internal input shape that later postflop modules will consume."""

    table_id: Optional[str] = None
    hand_id: Optional[str] = None
    hero_cards: tuple[Any, ...] = field(default_factory=tuple)
    board_cards: tuple[Any, ...] = field(default_factory=tuple)
    players: tuple[Any, ...] = field(default_factory=tuple)
    pot: Any = None
    to_call: Any = None
    stacks: Mapping[str, Any] = field(default_factory=dict)
    committed_amounts: Mapping[str, Any] = field(default_factory=dict)
    positions: Mapping[str, Any] = field(default_factory=dict)
    button: Any = None
    blinds: Mapping[str, Any] = field(default_factory=dict)
    allowed_actions: tuple[Any, ...] = field(default_factory=tuple)
    action_context: Mapping[str, Any] = field(default_factory=dict)
    raw_clear_json_ref: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SolverTrace:
    """Trace of how Clear JSON data was consumed by the solver layer."""

    input_file: str
    mapping_version: str
    input_kind: str = "clear_json"
    fields_used: tuple[str, ...] = field(default_factory=tuple)
    fields_not_provided: tuple[str, ...] = field(default_factory=tuple)
    module_chain_next_step: Optional[str] = None
    notes: tuple[str, ...] = field(default_factory=tuple)
