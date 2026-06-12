"""Architecture gate for HERO made-hand classifier scope discipline."""

from __future__ import annotations

import ast
import copy
import inspect
from dataclasses import asdict
from pathlib import Path

from solver_postflop.board_texture_contracts import (
    BoardConnectionTexture,
    BoardPairedTexture,
    BoardRankTexture,
    BoardSuitTexture,
    BoardTextureFeatures,
    BoardVolatilityClass,
)
from solver_postflop.flop_context_contracts import (
    FlopActionContext,
    FlopContext,
    FlopPlayerContext,
    FlopPotContext,
    FlopPositionContext,
    FlopSpotFamily,
)
from solver_postflop.hero_made_hand import build_made_hand_features
from solver_postflop.hero_made_hand_contracts import MadeHandClass


_ALLOWED_MADE_HAND_OUTPUT_KEYS = {
    "case_id",
    "source_file",
    "hero_cards",
    "board_cards",
    "made_hand_class",
    "pair_class",
    "showdown_value_class",
    "strength_tier",
    "kicker_relevance",
    "board_interaction_tags",
    "features_used_by_future_modules",
    "notes",
}


_FORBIDDEN_SOURCE_MARKERS = {
    # Clear_JSON trust boundary / validation is owned by earlier project layers.
    "validate_",
    "validation",
    "validator",
    "duplicate",
    "collision",
    "dirty_source",
    "dirty-json",
    "dirty_json",
    "malformed",
    "invalid_card",
    # No source discovery or temporary JSON fallback in made-hand classification.
    "dark_json",
    "pending_json",
    "service_json",
    "runtime_json",
    "source_discovery",
    "latest_source",
    "glob(",
    "rglob(",
    "open(",
    "path(",
    "json.load",
    # No player filtering, hero creation, or active-state selection.
    "filter_players",
    "player_filter",
    "active_player",
    "create_hero",
    "hero_created",
    "select_hero",
    "seat_filter",
    "opponent_filter",
    # No draw/equity/range/decision/runtime/click implementation here.
    "drawfeatures",
    "build_draw",
    "hero_draw",
    "equity",
    "range_engine",
    "opponent_range",
    "decision",
    "runtime_plan",
    "action_button",
    "pyautogui",
    "mouse",
    "click(",
}


_FORBIDDEN_CALL_NAMES = {
    "open",
    "glob",
    "rglob",
    "read_text",
    "read_bytes",
    "load",
    "loads",
    "dump",
    "dumps",
}


_FORBIDDEN_OUTPUT_KEYS = {
    "draw_class",
    "flush_draw_class",
    "straight_draw_class",
    "equity",
    "range",
    "decision",
    "runtime_plan",
    "action_sequence",
    "button_sequence",
    "click_result",
}


def test_hero_made_hand_source_contains_no_out_of_scope_markers() -> None:
    source = inspect.getsource(__import__("solver_postflop.hero_made_hand", fromlist=["dummy"]))
    normalized = source.lower()

    missing_scope_violations = {
        marker for marker in _FORBIDDEN_SOURCE_MARKERS if marker in normalized
    }

    assert missing_scope_violations == set()


def test_hero_made_hand_module_does_not_perform_file_or_json_io() -> None:
    import solver_postflop.hero_made_hand as hero_made_hand

    source_path = Path(inspect.getsourcefile(hero_made_hand) or "")
    tree = ast.parse(source_path.read_text(encoding="utf-8"))

    forbidden_calls: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        call_name = _call_name(node.func)
        if call_name in _FORBIDDEN_CALL_NAMES:
            forbidden_calls.append(call_name)

    assert forbidden_calls == []


def test_made_hand_features_contract_has_no_draw_equity_decision_runtime_fields() -> None:
    result = _build_sample_result()
    json_dict = result.to_json_dict()

    assert set(json_dict) == _ALLOWED_MADE_HAND_OUTPUT_KEYS
    assert not (_FORBIDDEN_OUTPUT_KEYS & set(json_dict))
    assert result.made_hand_class is MadeHandClass.ONE_PAIR


def test_build_made_hand_features_does_not_mutate_flop_context_or_clear_json() -> None:
    raw_clear_json = _sample_raw_clear_json()
    flop_context = _sample_flop_context(raw_clear_json=raw_clear_json)
    board_texture = _sample_board_texture()

    before_raw = copy.deepcopy(raw_clear_json)
    before_flop_context = copy.deepcopy(flop_context.to_json_dict())
    before_board_texture = copy.deepcopy(board_texture.to_json_dict())
    before_hero_cards = tuple(flop_context.hero_cards)
    before_board_cards = tuple(flop_context.board_cards)
    before_players = copy.deepcopy(tuple(flop_context.player_context.players))
    before_allowed_actions = tuple(flop_context.action_context.allowed_actions)

    _ = build_made_hand_features(flop_context, board_texture)

    assert raw_clear_json == before_raw
    assert flop_context.to_json_dict() == before_flop_context
    assert board_texture.to_json_dict() == before_board_texture
    assert tuple(flop_context.hero_cards) == before_hero_cards
    assert tuple(flop_context.board_cards) == before_board_cards
    assert tuple(flop_context.player_context.players) == before_players
    assert tuple(flop_context.action_context.allowed_actions) == before_allowed_actions


def test_build_made_hand_features_preserves_input_card_order_without_repair() -> None:
    raw_clear_json = _sample_raw_clear_json()
    flop_context = _sample_flop_context(raw_clear_json=raw_clear_json)
    board_texture = _sample_board_texture()

    result = build_made_hand_features(flop_context, board_texture)

    assert result.hero_cards == ("Ah", "Qh")
    assert result.board_cards == ("As", "7d", "2c")
    assert raw_clear_json["hero_cards"] == ["Ah", "Qh"]
    assert raw_clear_json["board_cards"] == ["As", "7d", "2c"]


def test_made_hand_output_remains_feature_metadata_not_action_payload() -> None:
    result = _build_sample_result()
    json_dict = result.to_json_dict()

    serialized_keys = set(_flatten_keys(json_dict))
    assert "made_hand_class" in serialized_keys
    assert "board_interaction_tags" in serialized_keys
    assert not (_FORBIDDEN_OUTPUT_KEYS & serialized_keys)
    assert "one_pair" == json_dict["made_hand_class"]


def _build_sample_result():
    raw_clear_json = _sample_raw_clear_json()
    return build_made_hand_features(
        _sample_flop_context(raw_clear_json=raw_clear_json),
        _sample_board_texture(),
    )


def _sample_raw_clear_json() -> dict:
    return {
        "case_id": "made_hand_no_extra_logic_case",
        "table_id": "table_01",
        "hand_id": "hand_01",
        "hero_id": "hero",
        "hero_cards": ["Ah", "Qh"],
        "board_cards": ["As", "7d", "2c"],
        "players": [
            {"id": "hero", "position": "BTN", "stack": 100.0},
            {"id": "villain", "position": "BB", "stack": 100.0},
        ],
        "allowed_actions": ["check", "bet"],
    }


def _sample_flop_context(*, raw_clear_json: dict) -> FlopContext:
    return FlopContext(
        case_id="made_hand_no_extra_logic_case",
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/made_hand_no_extra_logic.clear.json",
        table_id="table_01",
        hand_id="hand_01",
        branch="flop",
        spot_family=FlopSpotFamily.SRP_HEADS_UP,
        hero_cards=("Ah", "Qh"),
        board_cards=("As", "7d", "2c"),
        pot_context=FlopPotContext(pot=5.5, to_call=0.0, pot_type="srp"),
        position_context=FlopPositionContext(hero_id="hero", hero_position="BTN"),
        action_context=FlopActionContext(allowed_actions=("check", "bet"), can_check=True, can_bet=True),
        player_context=FlopPlayerContext(
            players=tuple(raw_clear_json["players"]),
            hero_id="hero",
            hero_position="BTN",
            is_heads_up=True,
            is_multiway=False,
        ),
        raw_clear_json_ref=raw_clear_json,
        notes=("no_extra_logic_fixture",),
    )


def _sample_board_texture() -> BoardTextureFeatures:
    return BoardTextureFeatures(
        case_id="made_hand_no_extra_logic_case",
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/made_hand_no_extra_logic.clear.json",
        board_cards=("As", "7d", "2c"),
        suit_texture=BoardSuitTexture.RAINBOW,
        paired_texture=BoardPairedTexture.UNPAIRED,
        rank_texture=BoardRankTexture.ACE_HIGH,
        connection_texture=BoardConnectionTexture.DISCONNECTED,
        volatility_class=BoardVolatilityClass.STATIC_BOARD,
        texture_tags=("ace_high_dry_rainbow",),
        notes=("sample_board_texture_no_extra_logic",),
    )


def _call_name(func: ast.AST) -> str:
    if isinstance(func, ast.Name):
        return func.id.lower()
    if isinstance(func, ast.Attribute):
        return func.attr.lower()
    return ""


def _flatten_keys(value) -> tuple[str, ...]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            keys.append(str(key))
            keys.extend(_flatten_keys(item))
    elif isinstance(value, list):
        for item in value:
            keys.extend(_flatten_keys(item))
    return tuple(keys)
