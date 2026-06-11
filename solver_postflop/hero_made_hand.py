"""Build HERO made-hand features from trusted flop context metadata."""

from __future__ import annotations

from collections import Counter
from typing import Any

from solver_postflop.board_texture_contracts import BoardTextureFeatures
from solver_postflop.flop_context_contracts import FlopContext
from solver_postflop.hero_made_hand_contracts import (
    MADE_HAND_FUTURE_MODULES,
    MadeHandClass,
    MadeHandFeatures,
    MadeHandStrengthTier,
    PairClass,
    ShowdownValueClass,
)

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


class _ParsedCard(tuple):
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


# This layer consumes prepared Clear_JSON-derived metadata. It classifies the
# visible HERO/board made hand and returns feature labels only.
def build_made_hand_features(
    flop_context: FlopContext,
    board_texture_features: BoardTextureFeatures,
) -> MadeHandFeatures:
    """Build baseline HERO made-hand features from FlopContext."""

    hero_cards = tuple(flop_context.hero_cards)
    board_cards = tuple(flop_context.board_cards)
    parsed_cards = tuple(_parse_card(card) for card in (*hero_cards, *board_cards))
    rank_values = tuple(card.rank_value for card in parsed_cards if card.rank_value is not None)
    suits = tuple(card.suit_text for card in parsed_cards if card.suit_text)

    made_hand_class = _classify_made_hand(rank_values=rank_values, suits=suits)
    showdown_value_class, strength_tier = _baseline_strength_for(made_hand_class)
    board_interaction_tags = _build_board_interaction_tags(
        made_hand_class=made_hand_class,
        board_texture_features=board_texture_features,
    )

    return MadeHandFeatures(
        case_id=flop_context.case_id,
        source_file=flop_context.source_file,
        hero_cards=hero_cards,
        board_cards=board_cards,
        made_hand_class=made_hand_class,
        pair_class=PairClass.NO_PAIR_CLASS,
        showdown_value_class=showdown_value_class,
        strength_tier=strength_tier,
        kicker_relevance="not_evaluated",
        board_interaction_tags=board_interaction_tags,
        features_used_by_future_modules=MADE_HAND_FUTURE_MODULES,
        notes=(
            "hero_made_hand_classifier_v0.7.2",
            "flop_context_hero_board_metadata_only",
            "baseline_made_hand_class_only",
        ),
    )


def _parse_card(card: Any) -> _ParsedCard:
    text = str(card).strip()
    if not text:
        return _ParsedCard(("", None, ""))

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
    return _ParsedCard((rank_text, rank_value, suit_text))


def _classify_made_hand(*, rank_values: tuple[int, ...], suits: tuple[str, ...]) -> MadeHandClass:
    rank_counts = Counter(rank_values)
    count_values = sorted(rank_counts.values(), reverse=True)

    if 4 in count_values:
        return MadeHandClass.QUADS
    if 3 in count_values and any(count >= 2 for count in count_values if count != 3):
        return MadeHandClass.FULL_HOUSE
    if _has_flush(suits):
        return MadeHandClass.FLUSH
    if _has_straight(rank_values):
        return MadeHandClass.STRAIGHT
    if 3 in count_values:
        return MadeHandClass.THREE_OF_A_KIND
    if sum(1 for count in count_values if count >= 2) >= 2:
        return MadeHandClass.TWO_PAIR
    if 2 in count_values:
        return MadeHandClass.ONE_PAIR
    return MadeHandClass.HIGH_CARD


def _has_flush(suits: tuple[str, ...]) -> bool:
    return any(count >= 5 for count in Counter(suits).values())


def _has_straight(rank_values: tuple[int, ...]) -> bool:
    unique_ranks = set(rank_values)
    if 14 in unique_ranks:
        unique_ranks.add(1)
    sorted_ranks = sorted(unique_ranks)
    if len(sorted_ranks) < 5:
        return False

    run_length = 1
    for left, right in zip(sorted_ranks, sorted_ranks[1:]):
        if right - left == 1:
            run_length += 1
            if run_length >= 5:
                return True
        else:
            run_length = 1
    return False


def _baseline_strength_for(
    made_hand_class: MadeHandClass,
) -> tuple[ShowdownValueClass, MadeHandStrengthTier]:
    if made_hand_class in {MadeHandClass.QUADS, MadeHandClass.FULL_HOUSE}:
        return ShowdownValueClass.VALUE_HAND, MadeHandStrengthTier.NUT_OR_NEAR_NUT
    if made_hand_class in {MadeHandClass.FLUSH, MadeHandClass.STRAIGHT}:
        return ShowdownValueClass.VALUE_HAND, MadeHandStrengthTier.VERY_STRONG_VALUE
    if made_hand_class is MadeHandClass.THREE_OF_A_KIND:
        return ShowdownValueClass.VALUE_HAND, MadeHandStrengthTier.VALUE_HAND
    if made_hand_class is MadeHandClass.TWO_PAIR:
        return ShowdownValueClass.STRONG_SHOWDOWN, MadeHandStrengthTier.STRONG_SHOWDOWN
    if made_hand_class is MadeHandClass.ONE_PAIR:
        return ShowdownValueClass.MEDIUM_SHOWDOWN, MadeHandStrengthTier.MEDIUM_SHOWDOWN
    if made_hand_class is MadeHandClass.HIGH_CARD:
        return ShowdownValueClass.AIR, MadeHandStrengthTier.AIR
    return ShowdownValueClass.UNKNOWN, MadeHandStrengthTier.UNKNOWN


def _build_board_interaction_tags(
    *,
    made_hand_class: MadeHandClass,
    board_texture_features: BoardTextureFeatures,
) -> tuple[str, ...]:
    tags = [made_hand_class.value]
    if board_texture_features.paired_texture.value != "unknown":
        tags.append(f"board_{board_texture_features.paired_texture.value}")
    if board_texture_features.suit_texture.value != "unknown":
        tags.append(f"board_{board_texture_features.suit_texture.value}")
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
