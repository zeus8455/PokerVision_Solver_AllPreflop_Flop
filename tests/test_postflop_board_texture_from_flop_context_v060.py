from __future__ import annotations

import copy
import json

from solver_postflop import (
    BoardSuitTexture,
    BoardTextureFeatures,
    build_board_texture_features,
)
from solver_postflop.flop_context_contracts import FlopContext, FlopSpotFamily


def _context_with_raw_payload() -> FlopContext:
    raw_payload = {
        "case_id": "texture_from_context_case",
        "hero_cards": ["Ah", "Kd"],
        "board_cards": ["Ah", "7d", "2c"],
        "players": [{"id": "hero", "position": "BB"}, {"id": "villain", "position": "BTN"}],
    }
    return FlopContext(
        case_id="texture_from_context_case",
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/texture_from_context.clear.json",
        table_id="table_01",
        hand_id="hand_001",
        branch="flop",
        spot_family=FlopSpotFamily.SRP_HEADS_UP,
        hero_cards=("Ah", "Kd"),
        board_cards=("Ah", "7d", "2c"),
        raw_clear_json_ref=raw_payload,
        context_fields_used=("board_cards", "hero_cards", "players"),
    )


def test_board_texture_builds_from_flop_context_and_preserves_board_cards() -> None:
    context = _context_with_raw_payload()
    features = build_board_texture_features(context)

    assert isinstance(features, BoardTextureFeatures)
    assert features.case_id == context.case_id
    assert features.source_file == context.source_file
    assert features.board_cards == context.board_cards
    assert features.suit_texture is BoardSuitTexture.RAINBOW


def test_board_texture_does_not_mutate_flop_context_or_clear_json_reference() -> None:
    context = _context_with_raw_payload()
    before_context_payload = context.to_json_dict()
    before_raw_payload = copy.deepcopy(context.raw_clear_json_ref)

    build_board_texture_features(context)

    assert context.to_json_dict() == before_context_payload
    assert context.raw_clear_json_ref == before_raw_payload


def test_board_texture_result_serializes_to_json() -> None:
    context = _context_with_raw_payload()
    features = build_board_texture_features(context)
    payload = features.to_json_dict()

    assert payload["board_cards"] == ["Ah", "7d", "2c"]
    assert payload["suit_texture"] == "rainbow"
    assert payload["texture_tags"]
    json.dumps(payload, sort_keys=True)


def test_board_texture_public_export_exists() -> None:
    import solver_postflop

    assert "build_board_texture_features" in solver_postflop.__all__
    assert hasattr(solver_postflop, "build_board_texture_features")
