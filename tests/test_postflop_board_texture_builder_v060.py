from __future__ import annotations

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
    return FlopContext(
        case_id="board_texture_builder_case",
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/board_texture.clear.json",
        table_id="table_01",
        hand_id="hand_001",
        branch="flop",
        spot_family=FlopSpotFamily.SRP_HEADS_UP,
        hero_cards=("Ah", "Kd"),
        board_cards=board_cards,
        raw_clear_json_ref={"case_id": "board_texture_builder_case", "board_cards": list(board_cards)},
    )


def test_rainbow_ace_high_dry_static_board_is_classified() -> None:
    features = build_board_texture_features(_flop_context(("Ah", "7d", "2c")))

    assert features.suit_texture is BoardSuitTexture.RAINBOW
    assert features.paired_texture is BoardPairedTexture.UNPAIRED
    assert features.rank_texture is BoardRankTexture.ACE_HIGH
    assert features.connection_texture is BoardConnectionTexture.DISCONNECTED
    assert features.volatility_class is BoardVolatilityClass.STATIC_BOARD
    assert "ace_high_dry_rainbow" in features.texture_tags


def test_two_tone_king_high_board_is_classified() -> None:
    features = build_board_texture_features(_flop_context(("Kh", "Qh", "5c")))

    assert features.suit_texture is BoardSuitTexture.TWO_TONE
    assert features.rank_texture is BoardRankTexture.KING_HIGH
    assert features.connection_texture is BoardConnectionTexture.SEMI_CONNECTED
    assert features.volatility_class is BoardVolatilityClass.SEMI_DYNAMIC_BOARD
    assert "king_high_two_tone" in features.texture_tags


def test_monotone_broadway_dynamic_board_is_classified() -> None:
    features = build_board_texture_features(_flop_context(("Qs", "Js", "Ts")))

    assert features.suit_texture is BoardSuitTexture.MONOTONE
    assert features.rank_texture is BoardRankTexture.BROADWAY_HEAVY
    assert features.connection_texture is BoardConnectionTexture.HIGHLY_CONNECTED
    assert features.volatility_class is BoardVolatilityClass.DYNAMIC_BOARD
    assert "monotone_broadway" in features.texture_tags


def test_paired_board_is_classified() -> None:
    features = build_board_texture_features(_flop_context(("9h", "9d", "2c")))

    assert features.paired_texture is BoardPairedTexture.PAIRED
    assert features.suit_texture is BoardSuitTexture.RAINBOW
    assert "paired" in features.texture_tags


def test_trips_board_is_classified() -> None:
    features = build_board_texture_features(_flop_context(("7h", "7d", "7s")))

    assert features.paired_texture is BoardPairedTexture.TRIPS_BOARD
    assert features.connection_texture is BoardConnectionTexture.UNKNOWN
    assert features.volatility_class is BoardVolatilityClass.STATIC_BOARD


def test_low_connected_dynamic_board_is_classified() -> None:
    features = build_board_texture_features(_flop_context(("6h", "5d", "4c")))

    assert features.rank_texture is BoardRankTexture.LOW_CONNECTED
    assert features.connection_texture is BoardConnectionTexture.HIGHLY_CONNECTED
    assert features.volatility_class is BoardVolatilityClass.DYNAMIC_BOARD
    assert "low_connected_dynamic" in features.texture_tags
