"""Contracts for board texture features used by future flop modules."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any, Optional


class BoardSuitTexture(str, Enum):
    """Suit distribution classes for a trusted flop board."""

    RAINBOW = "rainbow"
    TWO_TONE = "two_tone"
    MONOTONE = "monotone"
    UNKNOWN = "unknown"


class BoardPairedTexture(str, Enum):
    """Pairing classes for a trusted flop board."""

    UNPAIRED = "unpaired"
    PAIRED = "paired"
    TRIPS_BOARD = "trips_board"
    UNKNOWN = "unknown"


class BoardRankTexture(str, Enum):
    """Rank-shape classes for future flop strategy modules."""

    ACE_HIGH = "ace_high"
    KING_HIGH = "king_high"
    BROADWAY_HEAVY = "broadway_heavy"
    MIDDLE_CONNECTED = "middle_connected"
    LOW_CONNECTED = "low_connected"
    LOW_STATIC = "low_static"
    UNKNOWN = "unknown"


class BoardConnectionTexture(str, Enum):
    """Connectivity classes for future draw and range interaction modules."""

    DISCONNECTED = "disconnected"
    SEMI_CONNECTED = "semi_connected"
    CONNECTED = "connected"
    HIGHLY_CONNECTED = "highly_connected"
    UNKNOWN = "unknown"


class BoardVolatilityClass(str, Enum):
    """High-level board volatility classes for later sizing/barrel logic."""

    STATIC_BOARD = "static_board"
    SEMI_DYNAMIC_BOARD = "semi_dynamic_board"
    DYNAMIC_BOARD = "dynamic_board"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class BoardTextureFeatures:
    """Board texture features produced from FlopContext board metadata.

    This object is feature metadata only. It carries no HERO made-hand class,
    draw class, equity value, poker action, executable plan, or UI command.
    """

    case_id: Optional[str]
    source_file: str
    board_cards: tuple[str, ...]
    suit_texture: BoardSuitTexture
    paired_texture: BoardPairedTexture
    rank_texture: BoardRankTexture
    connection_texture: BoardConnectionTexture
    volatility_class: BoardVolatilityClass
    texture_tags: tuple[str, ...] = field(default_factory=tuple)
    features_used_by_future_modules: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation of board texture features."""
        return _json_safe(asdict(self))


BOARD_TEXTURE_CONTRACT_VERSION = "v0.6.0"

BOARD_SUIT_TEXTURES: tuple[BoardSuitTexture, ...] = tuple(BoardSuitTexture)
BOARD_PAIRED_TEXTURES: tuple[BoardPairedTexture, ...] = tuple(BoardPairedTexture)
BOARD_RANK_TEXTURES: tuple[BoardRankTexture, ...] = tuple(BoardRankTexture)
BOARD_CONNECTION_TEXTURES: tuple[BoardConnectionTexture, ...] = tuple(BoardConnectionTexture)
BOARD_VOLATILITY_CLASSES: tuple[BoardVolatilityClass, ...] = tuple(BoardVolatilityClass)

BOARD_TEXTURE_FUTURE_MODULES: tuple[str, ...] = (
    "hero_made_hand_classifier_later",
    "hero_draw_classifier_later",
    "range_interaction_later",
    "equity_module_later",
    "decision_engine_later",
    "bet_sizing_policy_later",
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
