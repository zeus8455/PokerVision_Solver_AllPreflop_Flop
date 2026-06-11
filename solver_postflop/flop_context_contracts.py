"""Contracts for flop context metadata used by future flop modules."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any, Mapping, Optional


class FlopSpotFamily(str, Enum):
    """Supported flop spot families for the context layer."""

    SRP_HEADS_UP = "srp_heads_up"
    THREEBET_POT_HEADS_UP = "threebet_pot_heads_up"
    FOURBET_LOW_SPR = "fourbet_low_spr"
    LIMP_OR_PASSIVE_POT = "limp_or_passive_pot"
    MULTIWAY_POT = "multiway_pot"
    UNKNOWN_FLOP_SPOT = "unknown_flop_spot"


@dataclass(frozen=True, slots=True)
class FlopPotContext:
    """Pot and stack-related context already available in SolverInput."""

    pot: Optional[float] = None
    to_call: Optional[float] = None
    effective_stack: Optional[float] = None
    spr: Optional[float] = None
    pot_type: Optional[str] = None
    fields_used: tuple[str, ...] = field(default_factory=tuple)
    fields_not_provided: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class FlopPositionContext:
    """Position context for HERO and opponents on the flop."""

    hero_id: Optional[str] = None
    hero_position: Optional[str] = None
    is_in_position: Optional[bool] = None
    position_label: Optional[str] = None
    fields_used: tuple[str, ...] = field(default_factory=tuple)
    fields_not_provided: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class FlopActionContext:
    """Action availability context already present in SolverInput."""

    allowed_actions: tuple[str, ...] = field(default_factory=tuple)
    current_actor: Optional[str] = None
    action_context_label: Optional[str] = None
    facing_bet: Optional[bool] = None
    facing_raise: Optional[bool] = None
    can_check: Optional[bool] = None
    can_call: Optional[bool] = None
    can_bet: Optional[bool] = None
    can_raise: Optional[bool] = None
    fields_used: tuple[str, ...] = field(default_factory=tuple)
    fields_not_provided: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class FlopPlayerContext:
    """Player shape context carried forward without re-selecting seats."""

    players: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    opponents: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    hero_id: Optional[str] = None
    hero_position: Optional[str] = None
    is_heads_up: Optional[bool] = None
    is_multiway: Optional[bool] = None
    fields_used: tuple[str, ...] = field(default_factory=tuple)
    fields_not_provided: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class FlopContext:
    """Structured context produced for future flop modules.

    This object is metadata and feature input only. It carries no poker action,
    sizing instruction, executable plan, or UI command.
    """

    case_id: Optional[str]
    source_file: str
    table_id: Optional[str]
    hand_id: Optional[str]
    branch: str
    spot_family: FlopSpotFamily
    hero_cards: tuple[str, ...] = field(default_factory=tuple)
    board_cards: tuple[str, ...] = field(default_factory=tuple)
    pot_context: FlopPotContext = field(default_factory=FlopPotContext)
    position_context: FlopPositionContext = field(default_factory=FlopPositionContext)
    action_context: FlopActionContext = field(default_factory=FlopActionContext)
    player_context: FlopPlayerContext = field(default_factory=FlopPlayerContext)
    next_module: str = "flop_board_texture_builder"
    context_fields_used: tuple[str, ...] = field(default_factory=tuple)
    context_fields_not_provided: tuple[str, ...] = field(default_factory=tuple)
    raw_clear_json_ref: Optional[Mapping[str, Any]] = None
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        return _json_safe(asdict(self))


DEFAULT_FLOP_NEXT_MODULE = "flop_board_texture_builder"


FLOP_SPOT_FAMILIES: tuple[FlopSpotFamily, ...] = tuple(FlopSpotFamily)


def _json_safe(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value
