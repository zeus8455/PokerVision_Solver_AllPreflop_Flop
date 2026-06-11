from __future__ import annotations

import copy
import json

from solver_postflop import (
    MadeHandClass,
    MadeHandFeatures,
    MadeHandStrengthTier,
    PairClass,
    ShowdownValueClass,
    build_board_texture_features,
    build_made_hand_features,
)
from solver_postflop.board_texture_contracts import BoardTextureFeatures
from solver_postflop.flop_context_contracts import FlopContext, FlopSpotFamily


def _flop_context(hero_cards: tuple[str, str], board_cards: tuple[str, str, str]) -> FlopContext:
    raw_payload = {
        "case_id": "made_hand_baseline_case",
        "hero_cards": list(hero_cards),
        "board_cards": list(board_cards),
        "players": [{"id": "hero"}, {"id": "villain"}],
    }
    return FlopContext(
        case_id="made_hand_baseline_case",
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/made_hand_baseline.clear.json",
        table_id="table_01",
        hand_id="hand_001",
        branch="flop",
        spot_family=FlopSpotFamily.SRP_HEADS_UP,
        hero_cards=hero_cards,
        board_cards=board_cards,
        raw_clear_json_ref=raw_payload,
        context_fields_used=("hero_cards", "board_cards", "players"),
    )


def _made_hand(hero_cards: tuple[str, str], board_cards: tuple[str, str, str]) -> tuple[MadeHandFeatures, FlopContext, BoardTextureFeatures]:
    context = _flop_context(hero_cards, board_cards)
    texture = build_board_texture_features(context)
    features = build_made_hand_features(context, texture)
    return features, context, texture


def test_high_card_is_classified() -> None:
    features, _context, _texture = _made_hand(("Ah", "Kd"), ("9s", "7d", "2c"))

    assert features.made_hand_class is MadeHandClass.HIGH_CARD
    assert features.showdown_value_class is ShowdownValueClass.AIR
    assert features.strength_tier is MadeHandStrengthTier.AIR
    assert features.pair_class is PairClass.NO_PAIR_CLASS


def test_one_pair_is_classified() -> None:
    features, _context, _texture = _made_hand(("Ah", "Kd"), ("As", "7d", "2c"))

    assert features.made_hand_class is MadeHandClass.ONE_PAIR
    assert features.showdown_value_class is ShowdownValueClass.STRONG_SHOWDOWN
    assert features.strength_tier is MadeHandStrengthTier.STRONG_SHOWDOWN
    assert features.pair_class is PairClass.TOP_PAIR
    assert features.kicker_relevance == "high"


def test_two_pair_is_classified() -> None:
    features, _context, _texture = _made_hand(("Ah", "Kd"), ("As", "Kc", "2d"))

    assert features.made_hand_class is MadeHandClass.TWO_PAIR
    assert features.strength_tier is MadeHandStrengthTier.VALUE_HAND


def test_three_of_a_kind_is_classified() -> None:
    features, _context, _texture = _made_hand(("Ah", "Ad"), ("As", "7c", "2d"))

    assert features.made_hand_class is MadeHandClass.THREE_OF_A_KIND
    assert features.strength_tier is MadeHandStrengthTier.VALUE_HAND


def test_straight_is_classified() -> None:
    features, _context, _texture = _made_hand(("Ah", "Kd"), ("Qs", "Jc", "Td"))

    assert features.made_hand_class is MadeHandClass.STRAIGHT
    assert features.strength_tier is MadeHandStrengthTier.VERY_STRONG_VALUE


def test_wheel_straight_is_classified() -> None:
    features, _context, _texture = _made_hand(("Ah", "5d"), ("4s", "3c", "2d"))

    assert features.made_hand_class is MadeHandClass.STRAIGHT


def test_flush_is_classified() -> None:
    features, _context, _texture = _made_hand(("Ah", "Kh"), ("Qh", "7h", "2h"))

    assert features.made_hand_class is MadeHandClass.FLUSH
    assert features.strength_tier is MadeHandStrengthTier.VERY_STRONG_VALUE


def test_full_house_is_classified() -> None:
    features, _context, _texture = _made_hand(("Ah", "Ad"), ("As", "7c", "7d"))

    assert features.made_hand_class is MadeHandClass.FULL_HOUSE
    assert features.strength_tier is MadeHandStrengthTier.NUT_OR_NEAR_NUT


def test_quads_is_classified() -> None:
    features, _context, _texture = _made_hand(("Ah", "Ad"), ("As", "Ac", "7d"))

    assert features.made_hand_class is MadeHandClass.QUADS
    assert features.strength_tier is MadeHandStrengthTier.NUT_OR_NEAR_NUT


def test_made_hand_preserves_cards_and_serializes() -> None:
    features, context, _texture = _made_hand(("Ah", "Kd"), ("As", "7d", "2c"))
    payload = features.to_json_dict()

    assert isinstance(features, MadeHandFeatures)
    assert features.case_id == context.case_id
    assert features.source_file == context.source_file
    assert features.hero_cards == context.hero_cards
    assert features.board_cards == context.board_cards
    assert payload["hero_cards"] == ["Ah", "Kd"]
    assert payload["board_cards"] == ["As", "7d", "2c"]
    assert payload["made_hand_class"] == "one_pair"
    assert payload["board_interaction_tags"]
    json.dumps(payload, sort_keys=True)


def test_made_hand_builder_does_not_mutate_inputs_or_clear_json_reference() -> None:
    context = _flop_context(("Ah", "Kd"), ("As", "7d", "2c"))
    texture = build_board_texture_features(context)
    before_context_payload = context.to_json_dict()
    before_texture_payload = texture.to_json_dict()
    before_raw_payload = copy.deepcopy(context.raw_clear_json_ref)

    build_made_hand_features(context, texture)

    assert context.to_json_dict() == before_context_payload
    assert texture.to_json_dict() == before_texture_payload
    assert context.raw_clear_json_ref == before_raw_payload


def test_made_hand_public_export_exists() -> None:
    import solver_postflop

    assert "build_made_hand_features" in solver_postflop.__all__
    assert hasattr(solver_postflop, "build_made_hand_features")
