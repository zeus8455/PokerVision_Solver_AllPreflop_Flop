from __future__ import annotations

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
        "case_id": "draw_classifier_matrix_case",
        "hero_cards": list(hero_cards),
        "board_cards": list(board_cards),
        "players": [{"id": "hero"}, {"id": "villain"}],
    }
    return FlopContext(
        case_id="draw_classifier_matrix_case",
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/draw_classifier_matrix.clear.json",
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


def test_double_gutshot_is_classified() -> None:
    features, _context, _texture, _made_hand = _draw_features(("6h", "5d"), ("8s", "4c", "2d"))

    assert features.draw_class is DrawClass.STRAIGHT_DRAW
    assert features.straight_draw_class is StraightDrawClass.DOUBLE_GUTSHOT
    assert features.combo_draw_class is ComboDrawClass.NO_COMBO_DRAW
    assert features.draw_strength_tier is DrawStrengthTier.MEDIUM_DRAW
    assert "double_gutshot" in features.draw_tags


def test_flush_plus_gutshot_is_classified_as_combo_draw() -> None:
    features, _context, _texture, _made_hand = _draw_features(("Ah", "Jd"), ("Kh", "Th", "2h"))

    assert features.draw_class is DrawClass.COMBO_DRAW
    assert features.flush_draw_class is FlushDrawClass.NUT_FLUSH_DRAW_CANDIDATE
    assert features.straight_draw_class is StraightDrawClass.GUTSHOT
    assert features.overcard_class is OvercardClass.ONE_OVERCARD
    assert features.combo_draw_class is ComboDrawClass.FLUSH_PLUS_GUTSHOT
    assert features.draw_strength_tier is DrawStrengthTier.STRONG_DRAW
    assert "fd_plus_gutshot" in features.draw_tags
    assert "nut_fd_candidate" in features.draw_tags


def test_flush_plus_oesd_is_classified_as_strong_combo_draw() -> None:
    features, _context, _texture, _made_hand = _draw_features(("8h", "7h"), ("6h", "5h", "Kc"))

    assert features.draw_class is DrawClass.COMBO_DRAW
    assert features.flush_draw_class is FlushDrawClass.STANDARD_FLUSH_DRAW
    assert features.straight_draw_class is StraightDrawClass.OPEN_ENDED_STRAIGHT_DRAW
    assert features.combo_draw_class is ComboDrawClass.FLUSH_PLUS_OESD
    assert features.draw_strength_tier is DrawStrengthTier.STRONG_DRAW
    assert "fd_plus_oesd" in features.draw_tags
    assert "oesd" in features.draw_tags


def test_pair_plus_flush_draw_is_classified() -> None:
    features, _context, _texture, made_hand = _draw_features(("Ah", "Ks"), ("Kh", "7h", "2h"))

    assert made_hand.made_hand_class.value == "one_pair"
    assert features.draw_class is DrawClass.PAIR_PLUS_DRAW
    assert features.flush_draw_class is FlushDrawClass.NUT_FLUSH_DRAW_CANDIDATE
    assert features.straight_draw_class is StraightDrawClass.NO_STRAIGHT_DRAW
    assert features.combo_draw_class is ComboDrawClass.PAIR_PLUS_FLUSH_DRAW
    assert features.draw_strength_tier is DrawStrengthTier.STRONG_DRAW
    assert "pair_plus_fd" in features.draw_tags


def test_pair_plus_straight_draw_is_classified() -> None:
    features, _context, _texture, made_hand = _draw_features(("8h", "7d"), ("8s", "6c", "5d"))

    assert made_hand.made_hand_class.value == "one_pair"
    assert features.draw_class is DrawClass.PAIR_PLUS_DRAW
    assert features.flush_draw_class is FlushDrawClass.NO_FLUSH_DRAW
    assert features.straight_draw_class is StraightDrawClass.OPEN_ENDED_STRAIGHT_DRAW
    assert features.combo_draw_class is ComboDrawClass.PAIR_PLUS_STRAIGHT_DRAW
    assert features.draw_strength_tier is DrawStrengthTier.STRONG_DRAW
    assert "pair_plus_straight_draw" in features.draw_tags


def test_pair_plus_combo_draw_is_classified_as_premium_strength() -> None:
    features, _context, _texture, made_hand = _draw_features(("8h", "7h"), ("8s", "6h", "5h"))

    assert made_hand.made_hand_class.value == "one_pair"
    assert features.draw_class is DrawClass.PAIR_PLUS_DRAW
    assert features.flush_draw_class is FlushDrawClass.STANDARD_FLUSH_DRAW
    assert features.straight_draw_class is StraightDrawClass.OPEN_ENDED_STRAIGHT_DRAW
    assert features.combo_draw_class is ComboDrawClass.PAIR_PLUS_COMBO_DRAW
    assert features.draw_strength_tier is DrawStrengthTier.PREMIUM_COMBO_DRAW
    assert "pair_plus_combo_draw" in features.draw_tags


def test_overcards_plus_draw_is_classified() -> None:
    features, _context, _texture, _made_hand = _draw_features(("Ah", "Qd"), ("Js", "Tc", "2d"))

    assert features.draw_class is DrawClass.COMBO_DRAW
    assert features.straight_draw_class is StraightDrawClass.GUTSHOT
    assert features.overcard_class is OvercardClass.TWO_OVERCARDS
    assert features.combo_draw_class is ComboDrawClass.OVERCARDS_PLUS_DRAW
    assert features.draw_strength_tier is DrawStrengthTier.MEDIUM_DRAW
    assert "two_overcards_plus_draw" in features.draw_tags


def test_premium_combo_draw_is_classified() -> None:
    features, _context, _texture, made_hand = _draw_features(("Ah", "8h"), ("7h", "6h", "5c"))

    assert made_hand.made_hand_class.value == "high_card"
    assert features.draw_class is DrawClass.COMBO_DRAW
    assert features.flush_draw_class is FlushDrawClass.NUT_FLUSH_DRAW_CANDIDATE
    assert features.straight_draw_class is StraightDrawClass.OPEN_ENDED_STRAIGHT_DRAW
    assert features.combo_draw_class is ComboDrawClass.PREMIUM_COMBO_DRAW
    assert features.draw_strength_tier is DrawStrengthTier.PREMIUM_COMBO_DRAW
    assert "premium_combo_draw_candidate" in features.draw_tags


def test_combo_draw_payload_serializes_matrix_fields() -> None:
    features, context, _texture, _made_hand = _draw_features(("Ah", "Jd"), ("Kh", "Th", "2h"))
    payload = features.to_json_dict()

    assert features.case_id == context.case_id
    assert payload["draw_class"] == "combo_draw"
    assert payload["flush_draw_class"] == "nut_flush_draw_candidate"
    assert payload["straight_draw_class"] == "gutshot"
    assert payload["overcard_class"] == "one_overcard"
    assert payload["combo_draw_class"] == "flush_plus_gutshot"
    assert payload["draw_strength_tier"] == "strong_draw"
    assert "fd_plus_gutshot" in payload["draw_tags"]
    json.dumps(payload, sort_keys=True)
