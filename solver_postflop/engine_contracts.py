"""Baseline contracts for the postflop solver engine.

This module contains only passive data contracts for trusted Clear JSON input
and the future solver input pipeline. It performs no file search, no state
repair, no poker decision making, and no UI action work.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

MappingVersion = str


def utc_now() -> datetime:
    """Return an aware UTC timestamp for contract creation."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class ClearJsonInput:
    """Trusted Clear JSON input wrapper.

    The object keeps an immutable reference to the loaded data and basic
    metadata discovered from the already prepared Clear JSON document.
    """

    source_file: Path | str
    raw_data: Mapping[str, Any]
    loaded_at: datetime = field(default_factory=utc_now)
    case_id: str | None = None
    hand_id: str | None = None
    table_id: str | None = None


@dataclass(frozen=True, slots=True)
class SolverInput:
    """Internal input contract for future postflop solver modules."""

    table_id: str | None = None
    hand_id: str | None = None
    hero_cards: Sequence[str] = field(default_factory=tuple)
    board_cards: Sequence[str] = field(default_factory=tuple)
    players: Sequence[Mapping[str, Any]] = field(default_factory=tuple)
    pot: float | int | None = None
    to_call: float | int | None = None
    stacks: Mapping[str, float | int | None] = field(default_factory=dict)
    committed_amounts: Mapping[str, float | int | None] = field(default_factory=dict)
    positions: Mapping[str, str | None] = field(default_factory=dict)
    button: str | None = None
    blinds: Mapping[str, float | int | None] = field(default_factory=dict)
    allowed_actions: Sequence[str] = field(default_factory=tuple)
    action_context: Mapping[str, Any] = field(default_factory=dict)
    raw_clear_json_ref: Mapping[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class SolverTrace:
    """Trace contract for mapping observability."""

    input_file: Path | str
    input_kind: str = "clear_json"
    mapping_version: MappingVersion = "v0.1.1"
    fields_used: Sequence[str] = field(default_factory=tuple)
    fields_not_provided: Sequence[str] = field(default_factory=tuple)
    module_chain_next_step: str | None = None
    notes: Sequence[str] = field(default_factory=tuple)
