from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass

from solver_postflop import (
    BOARD_CONNECTION_TEXTURES,
    BOARD_PAIRED_TEXTURES,
    BOARD_RANK_TEXTURES,
    BOARD_SUIT_TEXTURES,
    BOARD_TEXTURE_CONTRACT_VERSION,
    BOARD_TEXTURE_FUTURE_MODULES,
    BOARD_VOLATILITY_CLASSES,
    BoardConnectionTexture,
    BoardPairedTexture,
    BoardRankTexture,
    BoardSuitTexture,
    BoardTextureFeatures,
    BoardVolatilityClass,
)


def test_board_texture_contract_version_is_fixed_for_v060() -> None:
    assert BOARD_TEXTURE_CONTRACT_VERSION == "v0.6.0"


def test_board_suit_texture_labels_are_fixed() -> None:
    assert {texture.value for texture in BoardSuitTexture} == {
        "rainbow",
        "two_tone",
        "monotone",
        "unknown",
    }
    assert BOARD_SUIT_TEXTURES == tuple(BoardSuitTexture)


def test_board_paired_texture_labels_are_fixed() -> None:
    assert {texture.value for texture in BoardPairedTexture} == {
        "unpaired",
        "paired",
        "trips_board",
        "unknown",
    }
    assert BOARD_PAIRED_TEXTURES == tuple(BoardPairedTexture)


def test_board_rank_texture_labels_are_fixed() -> None:
    assert {texture.value for texture in BoardRankTexture} == {
        "ace_high",
        "king_high",
        "broadway_heavy",
        "middle_connected",
        "low_connected",
        "low_static",
        "unknown",
    }
    assert BOARD_RANK_TEXTURES == tuple(BoardRankTexture)


def test_board_connection_texture_labels_are_fixed() -> None:
    assert {texture.value for texture in BoardConnectionTexture} == {
        "disconnected",
        "semi_connected",
        "connected",
        "highly_connected",
        "unknown",
    }
    assert BOARD_CONNECTION_TEXTURES == tuple(BoardConnectionTexture)


def test_board_volatility_labels_are_fixed() -> None:
    assert {texture.value for texture in BoardVolatilityClass} == {
        "static_board",
        "semi_dynamic_board",
        "dynamic_board",
        "unknown",
    }
    assert BOARD_VOLATILITY_CLASSES == tuple(BoardVolatilityClass)


def test_board_texture_features_can_be_created_and_serialized() -> None:
    features = BoardTextureFeatures(
        case_id="board_texture_contract_case",
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/case.clear.json",
        board_cards=("Ah", "7d", "2c"),
        suit_texture=BoardSuitTexture.RAINBOW,
        paired_texture=BoardPairedTexture.UNPAIRED,
        rank_texture=BoardRankTexture.ACE_HIGH,
        connection_texture=BoardConnectionTexture.DISCONNECTED,
        volatility_class=BoardVolatilityClass.STATIC_BOARD,
        texture_tags=("ace_high_dry_rainbow",),
        features_used_by_future_modules=BOARD_TEXTURE_FUTURE_MODULES[:3],
        notes=("contract_only",),
    )

    assert is_dataclass(features)
    assert asdict(features)["suit_texture"] == BoardSuitTexture.RAINBOW
    payload = features.to_json_dict()
    assert payload["suit_texture"] == "rainbow"
    assert payload["paired_texture"] == "unpaired"
    assert payload["rank_texture"] == "ace_high"
    assert payload["connection_texture"] == "disconnected"
    assert payload["volatility_class"] == "static_board"
    assert payload["board_cards"] == ["Ah", "7d", "2c"]
    assert payload["texture_tags"] == ["ace_high_dry_rainbow"]
    json.dumps(payload, sort_keys=True)


def test_board_texture_features_remain_feature_metadata_only() -> None:
    features = BoardTextureFeatures(
        case_id="metadata_only_case",
        source_file="metadata_only.clear.json",
        board_cards=("Kh", "Th", "2c"),
        suit_texture=BoardSuitTexture.TWO_TONE,
        paired_texture=BoardPairedTexture.UNPAIRED,
        rank_texture=BoardRankTexture.BROADWAY_HEAVY,
        connection_texture=BoardConnectionTexture.SEMI_CONNECTED,
        volatility_class=BoardVolatilityClass.SEMI_DYNAMIC_BOARD,
        texture_tags=("king_high_two_tone", "broadway_heavy"),
    )
    payload = features.to_json_dict()

    forbidden_keys = {
        "made_hand_class",
        "draw_class",
        "equity",
        "range",
        "decision",
        "runtime_plan",
        "click_result",
    }
    assert forbidden_keys.isdisjoint(payload)


def test_board_texture_contracts_exported_from_public_package() -> None:
    import solver_postflop

    for public_name in (
        "BOARD_CONNECTION_TEXTURES",
        "BOARD_PAIRED_TEXTURES",
        "BOARD_RANK_TEXTURES",
        "BOARD_SUIT_TEXTURES",
        "BOARD_TEXTURE_CONTRACT_VERSION",
        "BOARD_TEXTURE_FUTURE_MODULES",
        "BOARD_VOLATILITY_CLASSES",
        "BoardConnectionTexture",
        "BoardPairedTexture",
        "BoardRankTexture",
        "BoardSuitTexture",
        "BoardTextureFeatures",
        "BoardVolatilityClass",
    ):
        assert public_name in solver_postflop.__all__
        assert hasattr(solver_postflop, public_name)
