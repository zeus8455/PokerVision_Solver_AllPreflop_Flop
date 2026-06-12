"""Contracts for HERO draw features used by future flop modules."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any, Optional


class DrawClass(str, Enum):
    """Primary draw bucket for trusted HERO/board flop metadata."""

    NO_DRAW = "no_draw"
    BACKDOOR_ONLY = "backdoor_only"
    FLUSH_DRAW = "flush_draw"
    STRAIGHT_DRAW = "straight_draw"
    COMBO_DRAW = "combo_draw"
    OVERCARDS_ONLY = "overcards_only"
    PAIR_PLUS_DRAW = "pair_plus_draw"
    UNKNOWN = "unknown"


class FlushDrawClass(str, Enum):
    """Flush-draw subclasses for later equity/range/decision layers."""

    NO_FLUSH_DRAW = "no_flush_draw"
    BACKDOOR_FLUSH_DRAW = "backdoor_flush_draw"
    WEAK_FLUSH_DRAW = "weak_flush_draw"
    STANDARD_FLUSH_DRAW = "standard_flush_draw"
    NUT_FLUSH_DRAW_CANDIDATE = "nut_flush_draw_candidate"
    UNKNOWN = "unknown"


class StraightDrawClass(str, Enum):
    """Straight-draw subclasses for later equity/range/decision layers."""

    NO_STRAIGHT_DRAW = "no_straight_draw"
    GUTSHOT = "gutshot"
    OPEN_ENDED_STRAIGHT_DRAW = "open_ended_straight_draw"
    DOUBLE_GUTSHOT = "double_gutshot"
    COMBO_STRAIGHT_DRAW = "combo_straight_draw"
    UNKNOWN = "unknown"


class OvercardClass(str, Enum):
    """Overcard feature bucket for later float/call equity modules."""

    NO_OVERCARDS = "no_overcards"
    ONE_OVERCARD = "one_overcard"
    TWO_OVERCARDS = "two_overcards"
    UNKNOWN = "unknown"


class ComboDrawClass(str, Enum):
    """Combined draw class for later aggression/equity policies."""

    NO_COMBO_DRAW = "no_combo_draw"
    FLUSH_PLUS_GUTSHOT = "flush_plus_gutshot"
    FLUSH_PLUS_OESD = "flush_plus_oesd"
    PAIR_PLUS_FLUSH_DRAW = "pair_plus_flush_draw"
    PAIR_PLUS_STRAIGHT_DRAW = "pair_plus_straight_draw"
    PAIR_PLUS_COMBO_DRAW = "pair_plus_combo_draw"
    OVERCARDS_PLUS_DRAW = "overcards_plus_draw"
    PREMIUM_COMBO_DRAW = "premium_combo_draw"
    UNKNOWN = "unknown"


class DrawStrengthTier(str, Enum):
    """Coarse draw-strength tier for future equity/range/decision layers."""

    NO_DRAW = "no_draw"
    BACKDOOR_ONLY = "backdoor_only"
    WEAK_DRAW = "weak_draw"
    MEDIUM_DRAW = "medium_draw"
    STRONG_DRAW = "strong_draw"
    PREMIUM_COMBO_DRAW = "premium_combo_draw"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class DrawFeatures:
    """HERO draw feature metadata produced after made-hand features.

    This object is feature metadata only. It carries no equity value, opponent
    range assignment, poker action, executable runtime plan, or UI command.
    """

    case_id: Optional[str]
    source_file: str
    hero_cards: tuple[str, ...]
    board_cards: tuple[str, ...]
    draw_class: DrawClass
    flush_draw_class: FlushDrawClass
    straight_draw_class: StraightDrawClass
    overcard_class: OvercardClass
    combo_draw_class: ComboDrawClass
    draw_strength_tier: DrawStrengthTier
    draw_tags: tuple[str, ...] = field(default_factory=tuple)
    features_used_by_future_modules: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation of draw features."""
        return _json_safe(asdict(self))


DRAW_CONTRACT_VERSION = "v0.8.0"

DRAW_CLASSES: tuple[DrawClass, ...] = tuple(DrawClass)
FLUSH_DRAW_CLASSES: tuple[FlushDrawClass, ...] = tuple(FlushDrawClass)
STRAIGHT_DRAW_CLASSES: tuple[StraightDrawClass, ...] = tuple(StraightDrawClass)
OVERCARD_CLASSES: tuple[OvercardClass, ...] = tuple(OvercardClass)
COMBO_DRAW_CLASSES: tuple[ComboDrawClass, ...] = tuple(ComboDrawClass)
DRAW_STRENGTH_TIERS: tuple[DrawStrengthTier, ...] = tuple(DrawStrengthTier)

DRAW_FUTURE_MODULES: tuple[str, ...] = (
    "equity_input_builder_later",
    "equity_module_later",
    "range_interaction_later",
    "decision_engine_later",
    "bet_sizing_policy_later",
    "runtime_plan_later",
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
