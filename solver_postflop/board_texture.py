"""Build board texture features from trusted FlopContext board metadata."""

from __future__ import annotations

from collections import Counter
from typing import Any

from solver_postflop.board_texture_contracts import (
    BOARD_TEXTURE_FUTURE_MODULES,
    BoardConnectionTexture,
    BoardPairedTexture,
    BoardRankTexture,
    BoardSuitTexture,
    BoardTextureFeatures,
    BoardVolatilityClass,
)
from solver_postflop.flop_context_contracts import FlopContext

_RANK_VALUES: dict[str, int] = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "T": 10,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
}


class _ParsedBoardCard(tuple):
    __slots__ = ()

    @property
    def rank_text(self) -> str:
        return self[0]

    @property
    def rank_value(self) -> int | None:
        return self[1]

    @property
    def suit_text(self) -> str:
        return self[2]


# Internal helper is intentionally tolerant: Clear JSON is treated as the prepared
# input and this module only groups available board metadata into strategy-facing
# feature labels.
def build_board_texture_features(flop_context: FlopContext) -> BoardTextureFeatures:
    """Build board texture features from FlopContext board cards."""

    board_cards = tuple(flop_context.board_cards)
    parsed_cards = tuple(_parse_board_card(card) for card in board_cards)
    rank_values = tuple(card.rank_value for card in parsed_cards if card.rank_value is not None)
    suits = tuple(card.suit_text for card in parsed_cards if card.suit_text)

    suit_texture = _classify_suit_texture(suits)
    paired_texture = _classify_paired_texture(rank_values)
    rank_texture = _classify_rank_texture(rank_values)
    connection_texture = _classify_connection_texture(rank_values)
    volatility_class = _classify_volatility_class(
        suit_texture=suit_texture,
        paired_texture=paired_texture,
        rank_texture=rank_texture,
        connection_texture=connection_texture,
    )
    texture_tags = _build_texture_tags(
        suit_texture=suit_texture,
        paired_texture=paired_texture,
        rank_texture=rank_texture,
        connection_texture=connection_texture,
        volatility_class=volatility_class,
    )

    return BoardTextureFeatures(
        case_id=flop_context.case_id,
        source_file=flop_context.source_file,
        board_cards=board_cards,
        suit_texture=suit_texture,
        paired_texture=paired_texture,
        rank_texture=rank_texture,
        connection_texture=connection_texture,
        volatility_class=volatility_class,
        texture_tags=texture_tags,
        features_used_by_future_modules=BOARD_TEXTURE_FUTURE_MODULES,
        notes=(
            "board_texture_builder_v0.6.2",
            "flop_context_board_metadata_only",
            "feature_labels_only",
        ),
    )


def _parse_board_card(card: Any) -> _ParsedBoardCard:
    text = str(card).strip()
    if not text:
        return _ParsedBoardCard(("", None, ""))

    normalized = (
        text.replace("♠", "s")
        .replace("♣", "c")
        .replace("♥", "h")
        .replace("♦", "d")
    )
    suit_text = normalized[-1].lower() if normalized[-1:].lower() in {"s", "c", "h", "d"} else ""
    rank_text = normalized[:-1] if suit_text else normalized
    rank_text = rank_text.upper()
    rank_value = _RANK_VALUES.get(rank_text)
    return _ParsedBoardCard((rank_text, rank_value, suit_text))


def _classify_suit_texture(suits: tuple[str, ...]) -> BoardSuitTexture:
    if not suits:
        return BoardSuitTexture.UNKNOWN
    unique_suits = set(suits)
    if len(unique_suits) == 1:
        return BoardSuitTexture.MONOTONE
    if len(unique_suits) == 2:
        return BoardSuitTexture.TWO_TONE
    if len(unique_suits) >= 3:
        return BoardSuitTexture.RAINBOW
    return BoardSuitTexture.UNKNOWN


def _classify_paired_texture(rank_values: tuple[int, ...]) -> BoardPairedTexture:
    if not rank_values:
        return BoardPairedTexture.UNKNOWN
    rank_counts = sorted(Counter(rank_values).values(), reverse=True)
    if rank_counts == [3]:
        return BoardPairedTexture.TRIPS_BOARD
    if rank_counts == [2, 1]:
        return BoardPairedTexture.PAIRED
    if rank_counts == [1, 1, 1]:
        return BoardPairedTexture.UNPAIRED
    return BoardPairedTexture.UNKNOWN


def _classify_rank_texture(rank_values: tuple[int, ...]) -> BoardRankTexture:
    if not rank_values:
        return BoardRankTexture.UNKNOWN

    unique_ranks = sorted(set(rank_values))
    highest_rank = max(unique_ranks)
    broadway_count = sum(1 for rank in unique_ranks if rank >= 10)
    span = highest_rank - min(unique_ranks)

    if highest_rank == 14:
        return BoardRankTexture.ACE_HIGH
    if highest_rank == 13:
        return BoardRankTexture.KING_HIGH
    if broadway_count >= 2:
        return BoardRankTexture.BROADWAY_HEAVY
    if highest_rank <= 7 and len(unique_ranks) >= 2 and span <= 4:
        return BoardRankTexture.LOW_CONNECTED
    if highest_rank <= 10 and len(unique_ranks) >= 2 and span <= 4:
        return BoardRankTexture.MIDDLE_CONNECTED
    if highest_rank <= 9:
        return BoardRankTexture.LOW_STATIC
    return BoardRankTexture.UNKNOWN


def _classify_connection_texture(rank_values: tuple[int, ...]) -> BoardConnectionTexture:
    unique_ranks = sorted(set(rank_values))
    if len(unique_ranks) < 2:
        return BoardConnectionTexture.UNKNOWN

    span = unique_ranks[-1] - unique_ranks[0]
    adjacent_links = sum(1 for left, right in zip(unique_ranks, unique_ranks[1:]) if right - left == 1)

    if len(unique_ranks) == 3:
        if span <= 2:
            return BoardConnectionTexture.HIGHLY_CONNECTED
        if span <= 4 and adjacent_links >= 1:
            return BoardConnectionTexture.CONNECTED
        if span <= 5 or adjacent_links >= 1:
            return BoardConnectionTexture.SEMI_CONNECTED
        return BoardConnectionTexture.DISCONNECTED

    if span <= 2:
        return BoardConnectionTexture.SEMI_CONNECTED
    return BoardConnectionTexture.DISCONNECTED


def _classify_volatility_class(
    *,
    suit_texture: BoardSuitTexture,
    paired_texture: BoardPairedTexture,
    rank_texture: BoardRankTexture,
    connection_texture: BoardConnectionTexture,
) -> BoardVolatilityClass:
    if suit_texture is BoardSuitTexture.MONOTONE:
        return BoardVolatilityClass.DYNAMIC_BOARD
    if connection_texture in {
        BoardConnectionTexture.HIGHLY_CONNECTED,
        BoardConnectionTexture.CONNECTED,
    }:
        return BoardVolatilityClass.DYNAMIC_BOARD
    if paired_texture is BoardPairedTexture.TRIPS_BOARD:
        return BoardVolatilityClass.STATIC_BOARD
    if suit_texture is BoardSuitTexture.TWO_TONE:
        return BoardVolatilityClass.SEMI_DYNAMIC_BOARD
    if rank_texture in {
        BoardRankTexture.BROADWAY_HEAVY,
        BoardRankTexture.MIDDLE_CONNECTED,
        BoardRankTexture.LOW_CONNECTED,
    }:
        return BoardVolatilityClass.SEMI_DYNAMIC_BOARD
    if paired_texture is BoardPairedTexture.PAIRED and connection_texture is BoardConnectionTexture.SEMI_CONNECTED:
        return BoardVolatilityClass.SEMI_DYNAMIC_BOARD
    return BoardVolatilityClass.STATIC_BOARD


def _build_texture_tags(
    *,
    suit_texture: BoardSuitTexture,
    paired_texture: BoardPairedTexture,
    rank_texture: BoardRankTexture,
    connection_texture: BoardConnectionTexture,
    volatility_class: BoardVolatilityClass,
) -> tuple[str, ...]:
    tags: list[str] = []

    for value in (
        rank_texture.value,
        paired_texture.value,
        connection_texture.value,
        volatility_class.value,
        suit_texture.value,
    ):
        if value != "unknown":
            tags.append(value)

    if (
        rank_texture is BoardRankTexture.ACE_HIGH
        and volatility_class is BoardVolatilityClass.STATIC_BOARD
        and suit_texture is BoardSuitTexture.RAINBOW
    ):
        tags.append("ace_high_dry_rainbow")
    if rank_texture is BoardRankTexture.KING_HIGH and suit_texture is BoardSuitTexture.TWO_TONE:
        tags.append("king_high_two_tone")
    if suit_texture is BoardSuitTexture.MONOTONE and rank_texture is BoardRankTexture.BROADWAY_HEAVY:
        tags.append("monotone_broadway")
    if rank_texture is BoardRankTexture.LOW_CONNECTED:
        tags.append("low_connected_dynamic")

    return _dedupe(tags)


def _dedupe(values: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return tuple(result)
