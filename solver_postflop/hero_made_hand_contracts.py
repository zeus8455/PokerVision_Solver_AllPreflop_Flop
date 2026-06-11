"""Contracts for HERO made-hand features used by future flop modules."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any, Optional


class MadeHandClass(str, Enum):
    """Primary made-hand classes for a trusted HERO/board flop state."""

    NO_MADE_HAND = "no_made_hand"
    HIGH_CARD = "high_card"
    ONE_PAIR = "one_pair"
    TWO_PAIR = "two_pair"
    THREE_OF_A_KIND = "three_of_a_kind"
    STRAIGHT = "straight"
    FLUSH = "flush"
    FULL_HOUSE = "full_house"
    QUADS = "quads"
    UNKNOWN = "unknown"


class PairClass(str, Enum):
    """Pair subclasses for later value/bluff-catch policy modules."""

    TOP_PAIR = "top_pair"
    SECOND_PAIR = "second_pair"
    MIDDLE_PAIR = "middle_pair"
    BOTTOM_PAIR = "bottom_pair"
    OVERPAIR = "overpair"
    UNDERPAIR = "underpair"
    POCKET_PAIR_BELOW_BOARD = "pocket_pair_below_board"
    NO_PAIR_CLASS = "no_pair_class"
    UNKNOWN = "unknown"


class ShowdownValueClass(str, Enum):
    """Coarse showdown bucket for future strategy modules."""

    AIR = "air"
    WEAK_SHOWDOWN = "weak_showdown"
    MEDIUM_SHOWDOWN = "medium_showdown"
    STRONG_SHOWDOWN = "strong_showdown"
    VALUE_HAND = "value_hand"
    UNKNOWN = "unknown"


class MadeHandStrengthTier(str, Enum):
    """Strength tier used by later equity/range/decision layers."""

    AIR = "air"
    WEAK_SHOWDOWN = "weak_showdown"
    MEDIUM_SHOWDOWN = "medium_showdown"
    STRONG_SHOWDOWN = "strong_showdown"
    VALUE_HAND = "value_hand"
    VERY_STRONG_VALUE = "very_strong_value"
    NUT_OR_NEAR_NUT = "nut_or_near_nut"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class MadeHandFeatures:
    """HERO made-hand feature metadata produced after board texture.

    This object is feature metadata only. It carries no draw class, equity value,
    range assignment, poker action, executable runtime plan, or UI command.
    """

    case_id: Optional[str]
    source_file: str
    hero_cards: tuple[str, ...]
    board_cards: tuple[str, ...]
    made_hand_class: MadeHandClass
    pair_class: PairClass
    showdown_value_class: ShowdownValueClass
    strength_tier: MadeHandStrengthTier
    kicker_relevance: str = "not_provided"
    board_interaction_tags: tuple[str, ...] = field(default_factory=tuple)
    features_used_by_future_modules: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation of made-hand features."""
        return _json_safe(asdict(self))


MADE_HAND_CONTRACT_VERSION = "v0.7.0"

MADE_HAND_CLASSES: tuple[MadeHandClass, ...] = tuple(MadeHandClass)
PAIR_CLASSES: tuple[PairClass, ...] = tuple(PairClass)
SHOWDOWN_VALUE_CLASSES: tuple[ShowdownValueClass, ...] = tuple(ShowdownValueClass)
MADE_HAND_STRENGTH_TIERS: tuple[MadeHandStrengthTier, ...] = tuple(MadeHandStrengthTier)

MADE_HAND_FUTURE_MODULES: tuple[str, ...] = (
    "hero_draw_classifier_later",
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
