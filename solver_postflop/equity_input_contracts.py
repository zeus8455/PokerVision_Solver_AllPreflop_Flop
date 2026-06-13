"""Contracts for the postflop equity input scenario layer."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any, Mapping, Optional


class EquityRunMode(str, Enum):
    """Future equity computation mode selected from already-built flop context."""

    HEADS_UP_EXACT_OR_SAMPLED = "heads_up_exact_or_sampled"
    MULTIWAY_SAMPLED = "multiway_sampled"
    RANGE_BASED_LATER = "range_based_later"
    UNKNOWN_CONTEXT_MODE = "unknown_context_mode"


@dataclass(frozen=True, slots=True)
class EquityHeroInput:
    """HERO card and stack metadata for a future equity scenario."""

    hero_cards: tuple[str, ...] = field(default_factory=tuple)
    position: Optional[str] = None
    stack: Optional[float] = None
    effective_stack: Optional[float] = None
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation of HERO input."""
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class EquityBoardInput:
    """Board metadata for a future equity scenario."""

    board_cards: tuple[str, ...] = field(default_factory=tuple)
    street: str = "flop"
    texture_tags: tuple[str, ...] = field(default_factory=tuple)
    paired_status: Optional[str] = None
    suit_structure: Optional[str] = None
    straight_structure: Optional[str] = None
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation of board input."""
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class EquityOpponentModelInput:
    """Opponent-count metadata carried from existing player context."""

    opponents_count: Optional[int] = None
    is_heads_up: Optional[bool] = None
    is_multiway: Optional[bool] = None
    known_opponents: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    opponent_positions: tuple[str, ...] = field(default_factory=tuple)
    range_model_status: str = "range_based_later"
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation of opponent input."""
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class EquityScenarioInput:
    """Prepared scenario metadata consumed by the later equity engine."""

    case_id: Optional[str]
    source_file: str
    hero: EquityHeroInput = field(default_factory=EquityHeroInput)
    board: EquityBoardInput = field(default_factory=EquityBoardInput)
    opponents: EquityOpponentModelInput = field(default_factory=EquityOpponentModelInput)
    spot_family: Optional[str] = None
    pot: Optional[float] = None
    to_call: Optional[float] = None
    effective_stack: Optional[float] = None
    spr: Optional[float] = None
    position_context: Mapping[str, Any] = field(default_factory=dict)
    action_context: Mapping[str, Any] = field(default_factory=dict)
    board_texture_features: Mapping[str, Any] = field(default_factory=dict)
    made_hand_features: Mapping[str, Any] = field(default_factory=dict)
    draw_features: Mapping[str, Any] = field(default_factory=dict)
    equity_run_mode: EquityRunMode = EquityRunMode.UNKNOWN_CONTEXT_MODE
    next_module: str = "equity_engine"
    fields_used: tuple[str, ...] = field(default_factory=tuple)
    fields_not_provided: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation of the scenario input."""
        return _json_safe(asdict(self))


EQUITY_INPUT_CONTRACT_VERSION = "v0.10.1"
DEFAULT_EQUITY_INPUT_NEXT_MODULE = "equity_engine"
EQUITY_RUN_MODES: tuple[EquityRunMode, ...] = tuple(EquityRunMode)
EQUITY_RANGE_MODEL_STATUSES: tuple[str, ...] = (
    "range_based_later",
    "unknown_context",
)


__all__ = (
    "DEFAULT_EQUITY_INPUT_NEXT_MODULE",
    "EQUITY_INPUT_CONTRACT_VERSION",
    "EQUITY_RANGE_MODEL_STATUSES",
    "EQUITY_RUN_MODES",
    "EquityBoardInput",
    "EquityHeroInput",
    "EquityOpponentModelInput",
    "EquityRunMode",
    "EquityScenarioInput",
)


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
