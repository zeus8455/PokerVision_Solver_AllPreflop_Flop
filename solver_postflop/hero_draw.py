"""Build HERO draw features from trusted flop feature metadata."""

from __future__ import annotations

from collections import Counter
from typing import Any

from solver_postflop.board_texture_contracts import BoardTextureFeatures
from solver_postflop.flop_context_contracts import FlopContext
from solver_postflop.hero_draw_contracts import (
    DRAW_FUTURE_MODULES,
    ComboDrawClass,
    DrawClass,
    DrawFeatures,
    DrawStrengthTier,
    FlushDrawClass,
    OvercardClass,
    StraightDrawClass,
)
from solver_postflop.hero_made_hand_contracts import MadeHandClass, MadeHandFeatures

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

_STRAIGHT_WINDOWS: tuple[tuple[int, int, int, int, int], ...] = (
    (1, 2, 3, 4, 5),
    (2, 3, 4, 5, 6),
    (3, 4, 5, 6, 7),
    (4, 5, 6, 7, 8),
    (5, 6, 7, 8, 9),
    (6, 7, 8, 9, 10),
    (7, 8, 9, 10, 11),
    (8, 9, 10, 11, 12),
    (9, 10, 11, 12, 13),
    (10, 11, 12, 13, 14),
)


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


# Internal helpers are intentionally tolerant: Clear JSON, FlopContext,
# BoardTextureFeatures, and MadeHandFeatures are treated as prepared upstream
# feature metadata. This module only derives draw labels from those objects.
def build_draw_features(
    flop_context: FlopContext,
    board_texture_features: BoardTextureFeatures,
    made_hand_features: MadeHandFeatures,
) -> DrawFeatures:
    """Build HERO draw features from flop context and upstream feature objects."""

    hero_cards = tuple(flop_context.hero_cards)
    board_cards = tuple(flop_context.board_cards)
    parsed_hero = tuple(_parse_card(card) for card in hero_cards)
    parsed_board = tuple(_parse_card(card) for card in board_cards)
    parsed_cards = (*parsed_hero, *parsed_board)

    rank_values = tuple(card.rank_value for card in parsed_cards if card.rank_value is not None)
    hero_ranks = tuple(card.rank_value for card in parsed_hero if card.rank_value is not None)
    board_ranks = tuple(card.rank_value for card in parsed_board if card.rank_value is not None)

    flush_draw_class = _classify_flush_draw(
        parsed_hero=parsed_hero,
        parsed_board=parsed_board,
        made_hand_features=made_hand_features,
    )
    straight_draw_class = _classify_straight_draw(
        rank_values=rank_values,
        made_hand_features=made_hand_features,
    )
    overcard_class = _classify_overcards(
        hero_ranks=hero_ranks,
        board_ranks=board_ranks,
    )
    combo_draw_class = _classify_combo_draw(
        flush_draw_class=flush_draw_class,
        straight_draw_class=straight_draw_class,
        overcard_class=overcard_class,
        made_hand_features=made_hand_features,
    )
    draw_class = _classify_draw_class(
        flush_draw_class=flush_draw_class,
        straight_draw_class=straight_draw_class,
        overcard_class=overcard_class,
        combo_draw_class=combo_draw_class,
    )
    draw_strength_tier = _classify_draw_strength_tier(
        draw_class=draw_class,
        flush_draw_class=flush_draw_class,
        straight_draw_class=straight_draw_class,
        overcard_class=overcard_class,
        combo_draw_class=combo_draw_class,
    )
    draw_tags = _build_draw_tags(
        draw_class=draw_class,
        flush_draw_class=flush_draw_class,
        straight_draw_class=straight_draw_class,
        overcard_class=overcard_class,
        combo_draw_class=combo_draw_class,
        draw_strength_tier=draw_strength_tier,
        board_texture_features=board_texture_features,
        made_hand_features=made_hand_features,
    )

    return DrawFeatures(
        case_id=flop_context.case_id,
        source_file=flop_context.source_file,
        hero_cards=hero_cards,
        board_cards=board_cards,
        draw_class=draw_class,
        flush_draw_class=flush_draw_class,
        straight_draw_class=straight_draw_class,
        overcard_class=overcard_class,
        combo_draw_class=combo_draw_class,
        draw_strength_tier=draw_strength_tier,
        draw_tags=draw_tags,
        features_used_by_future_modules=DRAW_FUTURE_MODULES,
        notes=(
            "hero_draw_classifier_v0.8.3",
            "flop_feature_metadata_only",
            "combo_draw_strength_matrix",
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


def _classify_flush_draw(
    *,
    parsed_hero: tuple[_ParsedCard, ...],
    parsed_board: tuple[_ParsedCard, ...],
    made_hand_features: MadeHandFeatures,
) -> FlushDrawClass:
    if made_hand_features.made_hand_class is MadeHandClass.FLUSH:
        return FlushDrawClass.NO_FLUSH_DRAW

    hero_suits = Counter(card.suit_text for card in parsed_hero if card.suit_text)
    board_suits = Counter(card.suit_text for card in parsed_board if card.suit_text)
    all_suits = hero_suits + board_suits

    for suit, count in all_suits.most_common():
        if not suit or hero_suits.get(suit, 0) == 0:
            continue
        if count >= 4:
            if any(card.rank_value == 14 and card.suit_text == suit for card in parsed_hero):
                return FlushDrawClass.NUT_FLUSH_DRAW_CANDIDATE
            return FlushDrawClass.STANDARD_FLUSH_DRAW
        if count == 3:
            return FlushDrawClass.BACKDOOR_FLUSH_DRAW
    return FlushDrawClass.NO_FLUSH_DRAW


def _classify_straight_draw(
    *,
    rank_values: tuple[int, ...],
    made_hand_features: MadeHandFeatures,
) -> StraightDrawClass:
    if made_hand_features.made_hand_class is MadeHandClass.STRAIGHT:
        return StraightDrawClass.NO_STRAIGHT_DRAW

    completions = _straight_completion_ranks(rank_values)
    if len(completions) >= 3:
        return StraightDrawClass.COMBO_STRAIGHT_DRAW
    if len(completions) >= 2:
        if _has_four_connected_ranks(rank_values):
            return StraightDrawClass.OPEN_ENDED_STRAIGHT_DRAW
        return StraightDrawClass.DOUBLE_GUTSHOT
    if len(completions) == 1:
        return StraightDrawClass.GUTSHOT
    return StraightDrawClass.NO_STRAIGHT_DRAW


def _straight_completion_ranks(rank_values: tuple[int, ...]) -> set[int]:
    ranks = set(rank_values)
    if 14 in ranks:
        ranks.add(1)

    completions: set[int] = set()
    for window in _STRAIGHT_WINDOWS:
        window_set = set(window)
        present = window_set & ranks
        if len(present) != 4:
            continue
        missing_rank = next(iter(window_set - present))
        completions.add(14 if missing_rank == 1 else missing_rank)
    return completions


def _has_four_connected_ranks(rank_values: tuple[int, ...]) -> bool:
    ranks = set(rank_values)
    if 14 in ranks:
        ranks.add(1)
    for low_rank in range(1, 12):
        if all(rank in ranks for rank in range(low_rank, low_rank + 4)):
            return True
    return False


def _classify_overcards(
    *,
    hero_ranks: tuple[int, ...],
    board_ranks: tuple[int, ...],
) -> OvercardClass:
    if not hero_ranks or not board_ranks:
        return OvercardClass.NO_OVERCARDS

    board_high = max(board_ranks)
    overcard_count = sum(1 for rank in hero_ranks if rank > board_high)
    if overcard_count >= 2:
        return OvercardClass.TWO_OVERCARDS
    if overcard_count == 1:
        return OvercardClass.ONE_OVERCARD
    return OvercardClass.NO_OVERCARDS


def _classify_combo_draw(
    *,
    flush_draw_class: FlushDrawClass,
    straight_draw_class: StraightDrawClass,
    overcard_class: OvercardClass,
    made_hand_features: MadeHandFeatures,
) -> ComboDrawClass:
    live_flush_draw = _has_live_flush_draw(flush_draw_class)
    straight_draw = _has_straight_draw(straight_draw_class)
    pair_or_better = made_hand_features.made_hand_class in {
        MadeHandClass.ONE_PAIR,
        MadeHandClass.TWO_PAIR,
        MadeHandClass.THREE_OF_A_KIND,
    }

    if live_flush_draw and straight_draw:
        if (
            flush_draw_class is FlushDrawClass.NUT_FLUSH_DRAW_CANDIDATE
            and straight_draw_class
            in {
                StraightDrawClass.OPEN_ENDED_STRAIGHT_DRAW,
                StraightDrawClass.DOUBLE_GUTSHOT,
                StraightDrawClass.COMBO_STRAIGHT_DRAW,
            }
        ):
            return ComboDrawClass.PREMIUM_COMBO_DRAW
        if pair_or_better:
            return ComboDrawClass.PAIR_PLUS_COMBO_DRAW
        if straight_draw_class is StraightDrawClass.GUTSHOT:
            return ComboDrawClass.FLUSH_PLUS_GUTSHOT
        return ComboDrawClass.FLUSH_PLUS_OESD

    if pair_or_better and live_flush_draw:
        return ComboDrawClass.PAIR_PLUS_FLUSH_DRAW
    if pair_or_better and straight_draw:
        return ComboDrawClass.PAIR_PLUS_STRAIGHT_DRAW
    if overcard_class in {OvercardClass.ONE_OVERCARD, OvercardClass.TWO_OVERCARDS} and (
        straight_draw
    ):
        return ComboDrawClass.OVERCARDS_PLUS_DRAW
    return ComboDrawClass.NO_COMBO_DRAW


def _has_live_flush_draw(flush_draw_class: FlushDrawClass) -> bool:
    return flush_draw_class in {
        FlushDrawClass.WEAK_FLUSH_DRAW,
        FlushDrawClass.STANDARD_FLUSH_DRAW,
        FlushDrawClass.NUT_FLUSH_DRAW_CANDIDATE,
    }


def _has_straight_draw(straight_draw_class: StraightDrawClass) -> bool:
    return straight_draw_class in {
        StraightDrawClass.GUTSHOT,
        StraightDrawClass.OPEN_ENDED_STRAIGHT_DRAW,
        StraightDrawClass.DOUBLE_GUTSHOT,
        StraightDrawClass.COMBO_STRAIGHT_DRAW,
    }


def _classify_draw_class(
    *,
    flush_draw_class: FlushDrawClass,
    straight_draw_class: StraightDrawClass,
    overcard_class: OvercardClass,
    combo_draw_class: ComboDrawClass,
) -> DrawClass:
    if combo_draw_class in {
        ComboDrawClass.PAIR_PLUS_FLUSH_DRAW,
        ComboDrawClass.PAIR_PLUS_STRAIGHT_DRAW,
        ComboDrawClass.PAIR_PLUS_COMBO_DRAW,
    }:
        return DrawClass.PAIR_PLUS_DRAW
    if combo_draw_class is not ComboDrawClass.NO_COMBO_DRAW:
        return DrawClass.COMBO_DRAW
    if _has_live_flush_draw(flush_draw_class):
        return DrawClass.FLUSH_DRAW
    if _has_straight_draw(straight_draw_class):
        return DrawClass.STRAIGHT_DRAW
    if flush_draw_class is FlushDrawClass.BACKDOOR_FLUSH_DRAW:
        return DrawClass.BACKDOOR_ONLY
    if overcard_class in {OvercardClass.ONE_OVERCARD, OvercardClass.TWO_OVERCARDS}:
        return DrawClass.OVERCARDS_ONLY
    return DrawClass.NO_DRAW


def _classify_draw_strength_tier(
    *,
    draw_class: DrawClass,
    flush_draw_class: FlushDrawClass,
    straight_draw_class: StraightDrawClass,
    overcard_class: OvercardClass,
    combo_draw_class: ComboDrawClass,
) -> DrawStrengthTier:
    if combo_draw_class in {
        ComboDrawClass.PREMIUM_COMBO_DRAW,
        ComboDrawClass.PAIR_PLUS_COMBO_DRAW,
    }:
        return DrawStrengthTier.PREMIUM_COMBO_DRAW
    if combo_draw_class in {
        ComboDrawClass.FLUSH_PLUS_GUTSHOT,
        ComboDrawClass.FLUSH_PLUS_OESD,
        ComboDrawClass.PAIR_PLUS_FLUSH_DRAW,
        ComboDrawClass.PAIR_PLUS_STRAIGHT_DRAW,
    }:
        return DrawStrengthTier.STRONG_DRAW
    if combo_draw_class is ComboDrawClass.OVERCARDS_PLUS_DRAW:
        return DrawStrengthTier.MEDIUM_DRAW
    if draw_class is DrawClass.NO_DRAW:
        return DrawStrengthTier.NO_DRAW
    if draw_class is DrawClass.BACKDOOR_ONLY:
        return DrawStrengthTier.BACKDOOR_ONLY
    if flush_draw_class is FlushDrawClass.NUT_FLUSH_DRAW_CANDIDATE:
        return DrawStrengthTier.MEDIUM_DRAW
    if flush_draw_class is FlushDrawClass.STANDARD_FLUSH_DRAW:
        return DrawStrengthTier.MEDIUM_DRAW
    if straight_draw_class in {
        StraightDrawClass.OPEN_ENDED_STRAIGHT_DRAW,
        StraightDrawClass.DOUBLE_GUTSHOT,
        StraightDrawClass.COMBO_STRAIGHT_DRAW,
    }:
        return DrawStrengthTier.MEDIUM_DRAW
    if straight_draw_class is StraightDrawClass.GUTSHOT:
        return DrawStrengthTier.WEAK_DRAW
    if overcard_class in {OvercardClass.ONE_OVERCARD, OvercardClass.TWO_OVERCARDS}:
        return DrawStrengthTier.WEAK_DRAW
    return DrawStrengthTier.WEAK_DRAW


def _build_draw_tags(
    *,
    draw_class: DrawClass,
    flush_draw_class: FlushDrawClass,
    straight_draw_class: StraightDrawClass,
    overcard_class: OvercardClass,
    combo_draw_class: ComboDrawClass,
    draw_strength_tier: DrawStrengthTier,
    board_texture_features: BoardTextureFeatures,
    made_hand_features: MadeHandFeatures,
) -> tuple[str, ...]:
    tags = [draw_class.value, draw_strength_tier.value]
    if flush_draw_class is not FlushDrawClass.NO_FLUSH_DRAW:
        tags.append(flush_draw_class.value)
    if straight_draw_class is not StraightDrawClass.NO_STRAIGHT_DRAW:
        tags.append(straight_draw_class.value)
    if overcard_class is not OvercardClass.NO_OVERCARDS:
        tags.append(overcard_class.value)
    if combo_draw_class is not ComboDrawClass.NO_COMBO_DRAW:
        tags.append(combo_draw_class.value)
    tags.extend(_draw_alias_tags(flush_draw_class, straight_draw_class, overcard_class, combo_draw_class))
    if board_texture_features.suit_texture.value != "unknown":
        tags.append(f"board_{board_texture_features.suit_texture.value}")
    if board_texture_features.connection_texture.value != "unknown":
        tags.append(f"board_{board_texture_features.connection_texture.value}")
    if made_hand_features.made_hand_class.value != "unknown":
        tags.append(f"made_{made_hand_features.made_hand_class.value}")
    return _dedupe(tags)


def _draw_alias_tags(
    flush_draw_class: FlushDrawClass,
    straight_draw_class: StraightDrawClass,
    overcard_class: OvercardClass,
    combo_draw_class: ComboDrawClass,
) -> tuple[str, ...]:
    tags: list[str] = []
    if flush_draw_class is FlushDrawClass.NUT_FLUSH_DRAW_CANDIDATE:
        tags.append("nut_fd_candidate")
    elif flush_draw_class is FlushDrawClass.STANDARD_FLUSH_DRAW:
        tags.append("standard_fd")
    elif flush_draw_class is FlushDrawClass.BACKDOOR_FLUSH_DRAW:
        tags.append("backdoor_fd")

    if straight_draw_class is StraightDrawClass.OPEN_ENDED_STRAIGHT_DRAW:
        tags.append("oesd")
    elif straight_draw_class is StraightDrawClass.GUTSHOT:
        tags.append("gutshot")
    elif straight_draw_class is StraightDrawClass.DOUBLE_GUTSHOT:
        tags.append("double_gutshot")
    elif straight_draw_class is StraightDrawClass.COMBO_STRAIGHT_DRAW:
        tags.append("combo_straight_draw")

    if combo_draw_class is ComboDrawClass.FLUSH_PLUS_GUTSHOT:
        tags.append("fd_plus_gutshot")
    elif combo_draw_class is ComboDrawClass.FLUSH_PLUS_OESD:
        tags.append("fd_plus_oesd")
    elif combo_draw_class is ComboDrawClass.PAIR_PLUS_FLUSH_DRAW:
        tags.append("pair_plus_fd")
    elif combo_draw_class is ComboDrawClass.PAIR_PLUS_STRAIGHT_DRAW:
        tags.append("pair_plus_straight_draw")
    elif combo_draw_class is ComboDrawClass.PAIR_PLUS_COMBO_DRAW:
        tags.append("pair_plus_combo_draw")
    elif combo_draw_class is ComboDrawClass.OVERCARDS_PLUS_DRAW:
        if overcard_class is OvercardClass.TWO_OVERCARDS:
            tags.append("two_overcards_plus_draw")
        else:
            tags.append("overcard_plus_draw")
    elif combo_draw_class is ComboDrawClass.PREMIUM_COMBO_DRAW:
        tags.append("premium_combo_draw_candidate")
    return tuple(tags)


def _dedupe(values: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return tuple(result)
