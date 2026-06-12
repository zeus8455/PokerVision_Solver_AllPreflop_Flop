from __future__ import annotations

import copy
import json

from solver_postflop import (
    ComboDrawClass,
    DrawClass,
    DrawFeatures,
    DrawStrengthTier,
    FlushDrawClass,
    OvercardClass,
    StraightDrawClass,
    build_board_texture_features,
    build_draw_features,
    build_made_hand_features,
)
from solver_postflop.board_texture_contracts import BoardTextureFeatures
from solver_postflop.flop_context_contracts import FlopContext, FlopSpotFamily
from solver_postflop.hero_made_hand_contracts import MadeHandFeatures


def _flop_context(hero_cards: tuple[str, str], board_cards: tuple[str, str, str]) -> FlopContext:
    raw_payload = {
        "case_id": "draw_baseline_case",
        "hero_cards": list(hero_cards),
        "board_cards": list(board_cards),
        "players": [{"id": "hero"}, {"id": "villain"}],
    }
    return FlopContext(
        case_id="draw_baseline_case",
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/draw_baseline.clear.json",
        table_id="table_01",
        hand_id="hand_001",
        branch="flop",
        spot_family=FlopSpotFamily.SRP_HEADS_UP,
        hero_cards=hero_cards,
        board_cards=board_cards,
        raw_clear_json_ref=raw_payload,
        context_fields_used=("hero_cards", "board_cards", "players"),
    )


def _draw_features(
    hero_cards: tuple[str, str],
    board_cards: tuple[str, str, str],
) -> tuple[DrawFeatures, FlopContext, BoardTextureFeatures, MadeHandFeatures]:
    context = _flop_context(hero_cards, board_cards)
    texture = build_board_texture_features(context)
    made_hand = build_made_hand_features(context, texture)
    draw_features = build_draw_features(context, texture, made_hand)
    return draw_features, context, texture, made_hand


def test_no_draw_is_classified() -> None:
    features, _context, _texture, _made_hand = _draw_features(("8h", "4d"), ("Ks", "7c", "2d"))

    assert features.draw_class is DrawClass.NO_DRAW
    assert features.flush_draw_class is FlushDrawClass.NO_FLUSH_DRAW
    assert features.straight_draw_class is StraightDrawClass.NO_STRAIGHT_DRAW
    assert features.overcard_class is OvercardClass.NO_OVERCARDS
    assert features.combo_draw_class is ComboDrawClass.NO_COMBO_DRAW
    assert features.draw_strength_tier is DrawStrengthTier.NO_DRAW


def test_backdoor_flush_draw_is_classified() -> None:
    features, _context, _texture, _made_hand = _draw_features(("Ah", "8d"), ("Kh", "7h", "2c"))

    assert features.draw_class is DrawClass.BACKDOOR_ONLY
    assert features.flush_draw_class is FlushDrawClass.BACKDOOR_FLUSH_DRAW
    assert features.draw_strength_tier is DrawStrengthTier.BACKDOOR_ONLY
    assert "backdoor_flush_draw" in features.draw_tags


def test_standard_flush_draw_is_classified() -> None:
    features, _context, _texture, _made_hand = _draw_features(("Qh", "8h"), ("Kh", "7h", "2c"))

    assert features.draw_class is DrawClass.FLUSH_DRAW
    assert features.flush_draw_class is FlushDrawClass.STANDARD_FLUSH_DRAW
    assert features.draw_strength_tier is DrawStrengthTier.MEDIUM_DRAW
    assert "standard_flush_draw" in features.draw_tags


def test_nut_flush_draw_candidate_is_classified() -> None:
    features, _context, _texture, _made_hand = _draw_features(("Ah", "Jd"), ("Kh", "7h", "2h"))

    assert features.draw_class is DrawClass.FLUSH_DRAW
    assert features.flush_draw_class is FlushDrawClass.NUT_FLUSH_DRAW_CANDIDATE
    assert features.draw_strength_tier is DrawStrengthTier.MEDIUM_DRAW
    assert "nut_flush_draw_candidate" in features.draw_tags


def test_gutshot_is_classified() -> None:
    features, _context, _texture, _made_hand = _draw_features(("Ah", "Qd"), ("Js", "Tc", "2d"))

    assert features.draw_class is DrawClass.STRAIGHT_DRAW
    assert features.straight_draw_class is StraightDrawClass.GUTSHOT
    assert features.draw_strength_tier is DrawStrengthTier.WEAK_DRAW
    assert "gutshot" in features.draw_tags


def test_open_ended_straight_draw_is_classified() -> None:
    features, _context, _texture, _made_hand = _draw_features(("8h", "7d"), ("6s", "5c", "Kd"))

    assert features.draw_class is DrawClass.STRAIGHT_DRAW
    assert features.straight_draw_class is StraightDrawClass.OPEN_ENDED_STRAIGHT_DRAW
    assert features.draw_strength_tier is DrawStrengthTier.MEDIUM_DRAW
    assert "open_ended_straight_draw" in features.draw_tags


def test_one_overcard_is_classified() -> None:
    features, _context, _texture, _made_hand = _draw_features(("Ah", "3d"), ("Ks", "7c", "2d"))

    assert features.draw_class is DrawClass.OVERCARDS_ONLY
    assert features.overcard_class is OvercardClass.ONE_OVERCARD
    assert features.draw_strength_tier is DrawStrengthTier.WEAK_DRAW


def test_two_overcards_are_classified() -> None:
    features, _context, _texture, _made_hand = _draw_features(("Ah", "Qd"), ("Js", "7c", "2d"))

    assert features.draw_class is DrawClass.OVERCARDS_ONLY
    assert features.overcard_class is OvercardClass.TWO_OVERCARDS
    assert features.draw_strength_tier is DrawStrengthTier.WEAK_DRAW
    assert "two_overcards" in features.draw_tags


def test_draw_features_preserve_cards_and_serialize() -> None:
    features, context, _texture, _made_hand = _draw_features(("Ah", "Jd"), ("Kh", "7h", "2h"))
    payload = features.to_json_dict()

    assert isinstance(features, DrawFeatures)
    assert features.case_id == context.case_id
    assert features.source_file == context.source_file
    assert features.hero_cards == context.hero_cards
    assert features.board_cards == context.board_cards
    assert payload["hero_cards"] == ["Ah", "Jd"]
    assert payload["board_cards"] == ["Kh", "7h", "2h"]
    assert payload["flush_draw_class"] == "nut_flush_draw_candidate"
    assert payload["combo_draw_class"] == "no_combo_draw"
    assert payload["draw_tags"]
    json.dumps(payload, sort_keys=True)


def test_draw_builder_does_not_mutate_inputs_or_clear_json_reference() -> None:
    context = _flop_context(("Ah", "Jd"), ("Kh", "7h", "2h"))
    texture = build_board_texture_features(context)
    made_hand = build_made_hand_features(context, texture)
    before_context_payload = context.to_json_dict()
    before_texture_payload = texture.to_json_dict()
    before_made_hand_payload = made_hand.to_json_dict()
    before_raw_payload = copy.deepcopy(context.raw_clear_json_ref)

    build_draw_features(context, texture, made_hand)

    assert context.to_json_dict() == before_context_payload
    assert texture.to_json_dict() == before_texture_payload
    assert made_hand.to_json_dict() == before_made_hand_payload
    assert context.raw_clear_json_ref == before_raw_payload


def test_draw_builder_public_export_exists() -> None:
    import solver_postflop

    assert "build_draw_features" in solver_postflop.__all__
    assert hasattr(solver_postflop, "build_draw_features")
