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
    """Build HERO made-hand features from FlopContext and BoardTextureFeatures."""

    hero_cards = tuple(flop_context.hero_cards)
    board_cards = tuple(flop_context.board_cards)
    parsed_hero = tuple(_parse_card(card) for card in hero_cards)
    parsed_board = tuple(_parse_card(card) for card in board_cards)
    parsed_cards = (*parsed_hero, *parsed_board)
    rank_values = tuple(card.rank_value for card in parsed_cards if card.rank_value is not None)
    suits = tuple(card.suit_text for card in parsed_cards if card.suit_text)

    made_hand_class = _classify_made_hand(rank_values=rank_values, suits=suits)
    pair_class = _classify_pair_class(
        made_hand_class=made_hand_class,
        hero_ranks=tuple(card.rank_value for card in parsed_hero if card.rank_value is not None),
        board_ranks=tuple(card.rank_value for card in parsed_board if card.rank_value is not None),
    )
    showdown_value_class, strength_tier = _strength_for(
        made_hand_class=made_hand_class,
        pair_class=pair_class,
    )
    kicker_relevance = _kicker_relevance(
        made_hand_class=made_hand_class,
        pair_class=pair_class,
        hero_ranks=tuple(card.rank_value for card in parsed_hero if card.rank_value is not None),
        board_ranks=tuple(card.rank_value for card in parsed_board if card.rank_value is not None),
    )
    board_interaction_tags = _build_board_interaction_tags(
        made_hand_class=made_hand_class,
        pair_class=pair_class,
        strength_tier=strength_tier,
        kicker_relevance=kicker_relevance,
        hero_ranks=tuple(card.rank_value for card in parsed_hero if card.rank_value is not None),
        board_ranks=tuple(card.rank_value for card in parsed_board if card.rank_value is not None),
        board_texture_features=board_texture_features,
    )

    return MadeHandFeatures(
        case_id=flop_context.case_id,
        source_file=flop_context.source_file,
        hero_cards=hero_cards,
        board_cards=board_cards,
        made_hand_class=made_hand_class,
        pair_class=pair_class,
        showdown_value_class=showdown_value_class,
        strength_tier=strength_tier,
        kicker_relevance=kicker_relevance,
        board_interaction_tags=board_interaction_tags,
        features_used_by_future_modules=MADE_HAND_FUTURE_MODULES,
        notes=(
            "hero_made_hand_classifier_v0.7.3",
            "flop_context_hero_board_metadata_only",
            "pair_class_strength_tier_matrix",
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


def _classify_pair_class(
    *,
    made_hand_class: MadeHandClass,
    hero_ranks: tuple[int, ...],
    board_ranks: tuple[int, ...],
) -> PairClass:
    if not hero_ranks or not board_ranks:
        return PairClass.NO_PAIR_CLASS

    board_unique_desc = tuple(sorted(set(board_ranks), reverse=True))
    hero_counts = Counter(hero_ranks)
    board_counts = Counter(board_ranks)
    hero_pair_rank = next((rank for rank, count in hero_counts.items() if count == 2), None)
    board_high = board_unique_desc[0]
    board_low = board_unique_desc[-1]

    if hero_pair_rank is not None and made_hand_class is MadeHandClass.ONE_PAIR:
        if hero_pair_rank > board_high:
            return PairClass.OVERPAIR
        if hero_pair_rank < board_low:
            return PairClass.UNDERPAIR
        return PairClass.POCKET_PAIR_BELOW_BOARD

    if made_hand_class is not MadeHandClass.ONE_PAIR:
        return PairClass.NO_PAIR_CLASS

    hero_board_pair_ranks = tuple(
        rank for rank in hero_ranks if board_counts.get(rank, 0) == 1
    )
    if not hero_board_pair_ranks:
        return PairClass.NO_PAIR_CLASS

    paired_rank = max(hero_board_pair_ranks)
    if paired_rank == board_unique_desc[0]:
        return PairClass.TOP_PAIR
    if paired_rank == board_unique_desc[-1]:
        return PairClass.BOTTOM_PAIR
    if len(board_unique_desc) >= 3 and paired_rank == board_unique_desc[1]:
        return PairClass.MIDDLE_PAIR
    return PairClass.SECOND_PAIR


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


def _strength_for(
    *,
    made_hand_class: MadeHandClass,
    pair_class: PairClass,
) -> tuple[ShowdownValueClass, MadeHandStrengthTier]:
    if made_hand_class in {MadeHandClass.QUADS, MadeHandClass.FULL_HOUSE}:
        return ShowdownValueClass.VALUE_HAND, MadeHandStrengthTier.NUT_OR_NEAR_NUT
    if made_hand_class in {MadeHandClass.FLUSH, MadeHandClass.STRAIGHT}:
        return ShowdownValueClass.VALUE_HAND, MadeHandStrengthTier.VERY_STRONG_VALUE
    if made_hand_class is MadeHandClass.THREE_OF_A_KIND:
        return ShowdownValueClass.VALUE_HAND, MadeHandStrengthTier.VALUE_HAND
    if made_hand_class is MadeHandClass.TWO_PAIR:
        return ShowdownValueClass.VALUE_HAND, MadeHandStrengthTier.VALUE_HAND
    if made_hand_class is MadeHandClass.ONE_PAIR:
        if pair_class in {PairClass.OVERPAIR, PairClass.TOP_PAIR}:
            return ShowdownValueClass.STRONG_SHOWDOWN, MadeHandStrengthTier.STRONG_SHOWDOWN
        if pair_class in {PairClass.MIDDLE_PAIR, PairClass.SECOND_PAIR}:
            return ShowdownValueClass.MEDIUM_SHOWDOWN, MadeHandStrengthTier.MEDIUM_SHOWDOWN
        if pair_class in {
            PairClass.BOTTOM_PAIR,
            PairClass.UNDERPAIR,
            PairClass.POCKET_PAIR_BELOW_BOARD,
            PairClass.NO_PAIR_CLASS,
        }:
            return ShowdownValueClass.WEAK_SHOWDOWN, MadeHandStrengthTier.WEAK_SHOWDOWN
        return ShowdownValueClass.MEDIUM_SHOWDOWN, MadeHandStrengthTier.MEDIUM_SHOWDOWN
    if made_hand_class is MadeHandClass.HIGH_CARD:
        return ShowdownValueClass.AIR, MadeHandStrengthTier.AIR
    return ShowdownValueClass.UNKNOWN, MadeHandStrengthTier.UNKNOWN


def _kicker_relevance(
    *,
    made_hand_class: MadeHandClass,
    pair_class: PairClass,
    hero_ranks: tuple[int, ...],
    board_ranks: tuple[int, ...],
) -> str:
    if made_hand_class is MadeHandClass.HIGH_CARD:
        return "low"
    if made_hand_class is not MadeHandClass.ONE_PAIR:
        return "not_relevant"
    if pair_class in {
        PairClass.OVERPAIR,
        PairClass.UNDERPAIR,
        PairClass.POCKET_PAIR_BELOW_BOARD,
        PairClass.NO_PAIR_CLASS,
    }:
        return "not_relevant"

    board_rank_set = set(board_ranks)
    kicker_candidates = tuple(rank for rank in hero_ranks if rank not in board_rank_set)
    if not kicker_candidates:
        return "not_evaluated"
    kicker = max(kicker_candidates)
    if kicker >= 12:
        return "high"
    if kicker >= 10:
        return "medium"
    return "low"


def _build_board_interaction_tags(
    *,
    made_hand_class: MadeHandClass,
    pair_class: PairClass,
    strength_tier: MadeHandStrengthTier,
    kicker_relevance: str,
    hero_ranks: tuple[int, ...],
    board_ranks: tuple[int, ...],
    board_texture_features: BoardTextureFeatures,
) -> tuple[str, ...]:
    tags = [made_hand_class.value]
    if pair_class is not PairClass.NO_PAIR_CLASS:
        tags.append(pair_class.value)

    if made_hand_class is MadeHandClass.ONE_PAIR and pair_class is PairClass.TOP_PAIR:
        if kicker_relevance == "high":
            tags.append("top_pair_good_kicker_candidate")
        else:
            tags.append("top_pair_candidate")
    if pair_class is PairClass.OVERPAIR:
        tags.append("overpair_candidate")
    if made_hand_class is MadeHandClass.THREE_OF_A_KIND:
        tags.append(_three_kind_tag(hero_ranks=hero_ranks, board_ranks=board_ranks))
    if made_hand_class in {MadeHandClass.STRAIGHT, MadeHandClass.FLUSH, MadeHandClass.FULL_HOUSE, MadeHandClass.QUADS}:
        tags.append("nut_or_near_nut_candidate")
    if strength_tier in {
        MadeHandStrengthTier.VALUE_HAND,
        MadeHandStrengthTier.VERY_STRONG_VALUE,
        MadeHandStrengthTier.NUT_OR_NEAR_NUT,
    }:
        tags.append("strong_made_hand")

    if board_texture_features.paired_texture.value != "unknown":
        tags.append(f"board_{board_texture_features.paired_texture.value}")
    if board_texture_features.suit_texture.value != "unknown":
        tags.append(f"board_{board_texture_features.suit_texture.value}")
    return _dedupe(tags)


def _three_kind_tag(*, hero_ranks: tuple[int, ...], board_ranks: tuple[int, ...]) -> str:
    hero_counts = Counter(hero_ranks)
    board_counts = Counter(board_ranks)
    if any(hero_counts.get(rank, 0) == 2 and board_counts.get(rank, 0) == 1 for rank in hero_counts):
        return "set_candidate"
    if any(hero_counts.get(rank, 0) == 1 and board_counts.get(rank, 0) == 2 for rank in hero_counts):
        return "trips_candidate"
    return "three_of_a_kind_candidate"


def _dedupe(values: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return tuple(result)
