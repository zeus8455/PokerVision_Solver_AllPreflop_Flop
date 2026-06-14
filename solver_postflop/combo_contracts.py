"""Contracts for postflop combo availability after blocker filtering.

V0.13.1 scope: JSON-safe contract objects only. This module defines
AvailableComboState metadata that later filtering modules will produce from
RangeState plus HERO and board blockers. It does not parse cards, remove combos,
refine ranges by action, compute equity, build a plan, or issue UI commands.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any, Mapping, Optional


class BlockedComboReason(str, Enum):
    """Reason assigned to a combo after blocker comparison."""

    NOT_BLOCKED = "not_blocked"
    BLOCKED_BY_HERO_CARD = "blocked_by_hero_card"
    BLOCKED_BY_BOARD_CARD = "blocked_by_board_card"
    BLOCKED_BY_HERO_AND_BOARD = "blocked_by_hero_and_board"


class ComboAvailabilityStatus(str, Enum):
    """High-level availability status for a combo state result."""

    AVAILABLE = "available"
    PARTIALLY_BLOCKED = "partially_blocked"
    FULLY_BLOCKED = "fully_blocked"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ComboBlockerResult:
    """Single combo availability result without executing filtering logic."""

    combo: str
    bucket_name: str
    combo_cards: tuple[str, ...] = field(default_factory=tuple)
    blocked_reason: BlockedComboReason = BlockedComboReason.NOT_BLOCKED
    is_available: bool = True
    blocking_hero_cards: tuple[str, ...] = field(default_factory=tuple)
    blocking_board_cards: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation."""
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class ComboGroupAvailability:
    """Per-bucket combo availability counts and retained combo lists."""

    bucket_name: str
    combo_count_before: int = 0
    combo_count_available: int = 0
    combo_count_blocked: int = 0
    available_combos: tuple[str, ...] = field(default_factory=tuple)
    blocked_combos: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation."""
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class PlayerComboState:
    """Combo availability state for one player range."""

    player_id: str
    position: Optional[str] = None
    range_name: str = "unknown_range"
    combo_count_before: int = 0
    combo_count_available: int = 0
    combo_count_blocked: int = 0
    blocked_by_hero_count: int = 0
    blocked_by_board_count: int = 0
    blocked_by_hero_and_board_count: int = 0
    available_combo_groups: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    blocked_combo_groups: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    combo_group_availability: tuple[ComboGroupAvailability, ...] = field(default_factory=tuple)
    blocker_results: tuple[ComboBlockerResult, ...] = field(default_factory=tuple)
    availability_status: ComboAvailabilityStatus = ComboAvailabilityStatus.UNKNOWN
    availability_confidence: str = "unknown"
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation."""
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class AvailableComboState:
    """Table-level combo availability result created after blocker filtering."""

    case_id: Optional[str]
    source_file: str
    spot_family: Optional[str] = None
    hero_cards_used_as_blockers: tuple[str, ...] = field(default_factory=tuple)
    board_cards_used_as_blockers: tuple[str, ...] = field(default_factory=tuple)
    player_combo_states: tuple[PlayerComboState, ...] = field(default_factory=tuple)
    total_combo_count_before: int = 0
    total_combo_count_available: int = 0
    total_combo_count_blocked: int = 0
    total_combo_count_blocked_by_hero: int = 0
    total_combo_count_blocked_by_board: int = 0
    total_combo_count_blocked_by_hero_and_board: int = 0
    availability_status: ComboAvailabilityStatus = ComboAvailabilityStatus.UNKNOWN
    range_source_info: Mapping[str, Any] = field(default_factory=dict)
    next_module: str = "flop_action_model_later"
    fields_used: tuple[str, ...] = field(default_factory=tuple)
    fields_not_provided: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation."""
        return _json_safe(asdict(self))


COMBO_CONTRACT_VERSION = "v0.13.1"
DEFAULT_COMBO_NEXT_MODULE = "flop_action_model_later"
COMBO_AVAILABILITY_STATUSES: tuple[ComboAvailabilityStatus, ...] = tuple(ComboAvailabilityStatus)
BLOCKED_COMBO_REASONS: tuple[BlockedComboReason, ...] = tuple(BlockedComboReason)

__all__ = (
    "AvailableComboState",
    "BLOCKED_COMBO_REASONS",
    "BlockedComboReason",
    "COMBO_AVAILABILITY_STATUSES",
    "COMBO_CONTRACT_VERSION",
    "ComboAvailabilityStatus",
    "ComboBlockerResult",
    "ComboGroupAvailability",
    "DEFAULT_COMBO_NEXT_MODULE",
    "PlayerComboState",
)


def _json_safe(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value
