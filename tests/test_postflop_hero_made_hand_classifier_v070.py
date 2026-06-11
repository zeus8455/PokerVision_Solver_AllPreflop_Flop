from __future__ import annotations

import copy

from solver_postflop import (
    MadeHandClass,
    MadeHandStrengthTier,
    PairClass,
    ShowdownValueClass,
    build_board_texture_features,
    build_made_hand_features,
)
from solver_postflop.flop_context_contracts import FlopContext, FlopSpotFamily


def _flop_context(hero_cards: tuple[str, str], board_cards: tuple[str, str, str]) -> FlopContext:
    raw_payload = {
        "case_id": "made_hand_classifier_case",
        "hero_cards": list(hero_cards),
        "board_cards": list(board_cards),
        "players": [{"id": "hero"}, {"id": "villain"}],
    }
    return FlopContext(
        case_id="made_hand_classifier_case",
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/made_hand_classifier.clear.json",
        table_id="table_01",
        hand_id="hand_001",
        branch="flop",
        spot_family=FlopSpotFamily.SRP_HEADS_UP,
        hero_cards=hero_cards,
        board_cards=board_cards,
        raw_clear_json_ref=raw_payload,
        context_fields_used=("hero_cards", "board_cards", "players"),
    )


def _features(hero_cards: tuple[str, str], board_cards: tuple[str, str, str]):
    context = _flop_context(hero_cards, board_cards)
    texture = build_board_texture_features(context)
    return build_made_hand_features(context, texture), context, texture


def test_top_pair_good_kicker_matrix() -> None:
    features, _context, _texture = _features(("Ah", "Qd"), ("As", "7c", "2d"))

    assert features.made_hand_class is MadeHandClass.ONE_PAIR
    assert features.pair_class is PairClass.TOP_PAIR
    assert features.showdown_value_class is ShowdownValueClass.STRONG_SHOWDOWN
    assert features.strength_tier is MadeHandStrengthTier.STRONG_SHOWDOWN
    assert features.kicker_relevance == "high"
    assert "top_pair_good_kicker_candidate" in features.board_interaction_tags


def test_top_pair_medium_kicker_matrix() -> None:
    features, _context, _texture = _features(("Ah", "Td"), ("As", "7c", "2d"))

    assert features.pair_class is PairClass.TOP_PAIR
    assert features.kicker_relevance == "medium"
    assert "top_pair_candidate" in features.board_interaction_tags


def test_middle_pair_matrix() -> None:
    features, _context, _texture = _features(("Qh", "8d"), ("As", "Qc", "2d"))

    assert features.made_hand_class is MadeHandClass.ONE_PAIR
    assert features.pair_class is PairClass.MIDDLE_PAIR
    assert features.showdown_value_class is ShowdownValueClass.MEDIUM_SHOWDOWN
    assert features.strength_tier is MadeHandStrengthTier.MEDIUM_SHOWDOWN
    assert features.kicker_relevance == "low"


def test_bottom_pair_matrix() -> None:
    features, _context, _texture = _features(("2h", "Kd"), ("As", "Qc", "2d"))

    assert features.made_hand_class is MadeHandClass.ONE_PAIR
    assert features.pair_class is PairClass.BOTTOM_PAIR
    assert features.showdown_value_class is ShowdownValueClass.WEAK_SHOWDOWN
    assert features.strength_tier is MadeHandStrengthTier.WEAK_SHOWDOWN
    assert features.kicker_relevance == "high"


def test_overpair_matrix() -> None:
    features, _context, _texture = _features(("Kh", "Kd"), ("Qs", "7c", "2d"))

    assert features.made_hand_class is MadeHandClass.ONE_PAIR
    assert features.pair_class is PairClass.OVERPAIR
    assert features.showdown_value_class is ShowdownValueClass.STRONG_SHOWDOWN
    assert features.strength_tier is MadeHandStrengthTier.STRONG_SHOWDOWN
    assert features.kicker_relevance == "not_relevant"
    assert "overpair_candidate" in features.board_interaction_tags


def test_underpair_matrix() -> None:
    features, _context, _texture = _features(("3h", "3d"), ("Qs", "7c", "4d"))

    assert features.made_hand_class is MadeHandClass.ONE_PAIR
    assert features.pair_class is PairClass.UNDERPAIR
    assert features.showdown_value_class is ShowdownValueClass.WEAK_SHOWDOWN
    assert features.strength_tier is MadeHandStrengthTier.WEAK_SHOWDOWN
    assert features.kicker_relevance == "not_relevant"


def test_pocket_pair_below_board_matrix() -> None:
    features, _context, _texture = _features(("9h", "9d"), ("Ks", "7c", "2d"))

    assert features.made_hand_class is MadeHandClass.ONE_PAIR
    assert features.pair_class is PairClass.POCKET_PAIR_BELOW_BOARD
    assert features.showdown_value_class is ShowdownValueClass.WEAK_SHOWDOWN
    assert features.strength_tier is MadeHandStrengthTier.WEAK_SHOWDOWN


def test_high_card_matrix() -> None:
    features, _context, _texture = _features(("Ah", "Kd"), ("9s", "7c", "2d"))

    assert features.made_hand_class is MadeHandClass.HIGH_CARD
    assert features.pair_class is PairClass.NO_PAIR_CLASS
    assert features.showdown_value_class is ShowdownValueClass.AIR
    assert features.strength_tier is MadeHandStrengthTier.AIR
    assert features.kicker_relevance == "low"


def test_two_pair_matrix() -> None:
    features, _context, _texture = _features(("Ah", "Kd"), ("As", "Kc", "2d"))

    assert features.made_hand_class is MadeHandClass.TWO_PAIR
    assert features.pair_class is PairClass.NO_PAIR_CLASS
    assert features.showdown_value_class is ShowdownValueClass.VALUE_HAND
    assert features.strength_tier is MadeHandStrengthTier.VALUE_HAND
    assert features.kicker_relevance == "not_relevant"


def test_set_matrix() -> None:
    features, _context, _texture = _features(("Ah", "Ad"), ("As", "7c", "2d"))

    assert features.made_hand_class is MadeHandClass.THREE_OF_A_KIND
    assert features.pair_class is PairClass.NO_PAIR_CLASS
    assert features.strength_tier is MadeHandStrengthTier.VALUE_HAND
    assert "set_candidate" in features.board_interaction_tags
    assert "strong_made_hand" in features.board_interaction_tags


def test_trips_matrix() -> None:
    features, _context, _texture = _features(("Ah", "Kd"), ("As", "Ac", "2d"))

    assert features.made_hand_class is MadeHandClass.THREE_OF_A_KIND
    assert features.pair_class is PairClass.NO_PAIR_CLASS
    assert features.strength_tier is MadeHandStrengthTier.VALUE_HAND
    assert "trips_candidate" in features.board_interaction_tags
    assert "board_paired" in features.board_interaction_tags


def test_straight_matrix() -> None:
    features, _context, _texture = _features(("Ah", "Kd"), ("Qs", "Jc", "Td"))

    assert features.made_hand_class is MadeHandClass.STRAIGHT
    assert features.strength_tier is MadeHandStrengthTier.VERY_STRONG_VALUE
    assert features.kicker_relevance == "not_relevant"
    assert "nut_or_near_nut_candidate" in features.board_interaction_tags


def test_flush_matrix() -> None:
    features, _context, _texture = _features(("Ah", "Kh"), ("Qh", "7h", "2h"))

    assert features.made_hand_class is MadeHandClass.FLUSH
    assert features.strength_tier is MadeHandStrengthTier.VERY_STRONG_VALUE
    assert "nut_or_near_nut_candidate" in features.board_interaction_tags
    assert "board_monotone" in features.board_interaction_tags


def test_full_house_matrix() -> None:
    features, _context, _texture = _features(("Ah", "Ad"), ("As", "7c", "7d"))

    assert features.made_hand_class is MadeHandClass.FULL_HOUSE
    assert features.strength_tier is MadeHandStrengthTier.NUT_OR_NEAR_NUT
    assert "nut_or_near_nut_candidate" in features.board_interaction_tags


def test_quads_matrix() -> None:
    features, _context, _texture = _features(("Ah", "Ad"), ("As", "Ac", "7d"))

    assert features.made_hand_class is MadeHandClass.QUADS
    assert features.strength_tier is MadeHandStrengthTier.NUT_OR_NEAR_NUT
    assert "nut_or_near_nut_candidate" in features.board_interaction_tags


def test_classifier_matrix_preserves_inputs() -> None:
    context = _flop_context(("Ah", "Qd"), ("As", "7c", "2d"))
    texture = build_board_texture_features(context)
    context_before = context.to_json_dict()
    texture_before = texture.to_json_dict()
    raw_before = copy.deepcopy(context.raw_clear_json_ref)

    build_made_hand_features(context, texture)

    assert context.to_json_dict() == context_before
    assert texture.to_json_dict() == texture_before
    assert context.raw_clear_json_ref == raw_before
