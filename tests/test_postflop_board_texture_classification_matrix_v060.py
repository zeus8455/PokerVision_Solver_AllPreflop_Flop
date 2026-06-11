from __future__ import annotations

from copy import deepcopy

from solver_postflop import (
    BoardConnectionTexture,
    BoardPairedTexture,
    BoardRankTexture,
    BoardSuitTexture,
    BoardVolatilityClass,
    build_board_texture_features,
)
from solver_postflop.flop_context_contracts import FlopContext, FlopSpotFamily


def _flop_context(board_cards: tuple[str, str, str]) -> FlopContext:
    raw_ref = {
        "case_id": "board_texture_matrix_case",
        "table_id": "table_01",
        "hand_id": "hand_001",
        "hero_cards": ["Ah", "Kd"],
        "board_cards": list(board_cards),
        "players": [
            {"id": "hero", "position": "BTN", "folded": False},
            {"id": "villain", "position": "BB", "folded": False},
        ],
    }
    return FlopContext(
        case_id="board_texture_matrix_case",
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/board_texture_matrix.clear.json",
        table_id="table_01",
        hand_id="hand_001",
        branch="flop",
        spot_family=FlopSpotFamily.SRP_HEADS_UP,
        hero_cards=("Ah", "Kd"),
        board_cards=board_cards,
        raw_clear_json_ref=raw_ref,
    )


def _features(board_cards: tuple[str, str, str]):
    return build_board_texture_features(_flop_context(board_cards))


def test_matrix_rainbow_ace_high_dry_static_board() -> None:
    features = _features(("Ah", "7d", "2c"))

    assert features.suit_texture is BoardSuitTexture.RAINBOW
    assert features.paired_texture is BoardPairedTexture.UNPAIRED
    assert features.rank_texture is BoardRankTexture.ACE_HIGH
    assert features.connection_texture is BoardConnectionTexture.DISCONNECTED
    assert features.volatility_class is BoardVolatilityClass.STATIC_BOARD
    assert "ace_high_dry_rainbow" in features.texture_tags


def test_matrix_king_high_two_tone_semi_dynamic_board() -> None:
    features = _features(("Kh", "Qh", "5c"))

    assert features.suit_texture is BoardSuitTexture.TWO_TONE
    assert features.rank_texture is BoardRankTexture.KING_HIGH
    assert features.connection_texture is BoardConnectionTexture.SEMI_CONNECTED
    assert features.volatility_class is BoardVolatilityClass.SEMI_DYNAMIC_BOARD
    assert "king_high_two_tone" in features.texture_tags


def test_matrix_monotone_broadway_highly_connected_dynamic_board() -> None:
    features = _features(("Qs", "Js", "Ts"))

    assert features.suit_texture is BoardSuitTexture.MONOTONE
    assert features.rank_texture is BoardRankTexture.BROADWAY_HEAVY
    assert features.connection_texture is BoardConnectionTexture.HIGHLY_CONNECTED
    assert features.volatility_class is BoardVolatilityClass.DYNAMIC_BOARD
    assert "monotone_broadway" in features.texture_tags
    assert "very_wet_connected" in features.texture_tags


def test_matrix_low_connected_highly_connected_dynamic_board() -> None:
    features = _features(("6h", "5d", "4c"))

    assert features.suit_texture is BoardSuitTexture.RAINBOW
    assert features.rank_texture is BoardRankTexture.LOW_CONNECTED
    assert features.connection_texture is BoardConnectionTexture.HIGHLY_CONNECTED
    assert features.volatility_class is BoardVolatilityClass.DYNAMIC_BOARD
    assert "low_connected_dynamic" in features.texture_tags


def test_matrix_middle_connected_two_tone_dynamic_board() -> None:
    features = _features(("9h", "8h", "7c"))

    assert features.suit_texture is BoardSuitTexture.TWO_TONE
    assert features.rank_texture is BoardRankTexture.MIDDLE_CONNECTED
    assert features.connection_texture is BoardConnectionTexture.HIGHLY_CONNECTED
    assert features.volatility_class is BoardVolatilityClass.DYNAMIC_BOARD
    assert "very_wet_connected" in features.texture_tags


def test_matrix_paired_dry_static_board() -> None:
    features = _features(("9h", "9d", "2c"))

    assert features.suit_texture is BoardSuitTexture.RAINBOW
    assert features.paired_texture is BoardPairedTexture.PAIRED
    assert features.connection_texture is BoardConnectionTexture.DISCONNECTED
    assert features.volatility_class is BoardVolatilityClass.STATIC_BOARD
    assert "paired_dry" in features.texture_tags


def test_matrix_paired_dynamic_board_keeps_pair_and_volatility() -> None:
    features = _features(("9h", "9d", "8h"))

    assert features.suit_texture is BoardSuitTexture.TWO_TONE
    assert features.paired_texture is BoardPairedTexture.PAIRED
    assert features.connection_texture is BoardConnectionTexture.SEMI_CONNECTED
    assert features.volatility_class is BoardVolatilityClass.SEMI_DYNAMIC_BOARD
    assert "paired" in features.texture_tags


def test_matrix_trips_board_is_static_and_not_connection_driven() -> None:
    features = _features(("7h", "7d", "7s"))

    assert features.suit_texture is BoardSuitTexture.RAINBOW
    assert features.paired_texture is BoardPairedTexture.TRIPS_BOARD
    assert features.connection_texture is BoardConnectionTexture.UNKNOWN
    assert features.volatility_class is BoardVolatilityClass.STATIC_BOARD


def test_matrix_low_static_disconnected_board() -> None:
    features = _features(("9h", "5d", "2c"))

    assert features.suit_texture is BoardSuitTexture.RAINBOW
    assert features.rank_texture is BoardRankTexture.LOW_STATIC
    assert features.connection_texture is BoardConnectionTexture.DISCONNECTED
    assert features.volatility_class is BoardVolatilityClass.STATIC_BOARD


def test_matrix_texture_builder_does_not_mutate_flop_context_or_clear_json_ref() -> None:
    context = _flop_context(("Ah", "7d", "2c"))
    raw_before = deepcopy(context.raw_clear_json_ref)
    board_before = context.board_cards
    hero_before = context.hero_cards

    features = build_board_texture_features(context)

    assert context.raw_clear_json_ref == raw_before
    assert context.board_cards == board_before
    assert context.hero_cards == hero_before
    assert features.board_cards == board_before
