from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Iterable

from solver_postflop import (
    BoardSuitTexture,
    BoardTextureFeatures,
    build_board_texture_features,
)
from solver_postflop.flop_context_contracts import (
    FlopActionContext,
    FlopContext,
    FlopPlayerContext,
    FlopPotContext,
    FlopPositionContext,
    FlopSpotFamily,
)


BOARD_TEXTURE_SOURCE_FILES = (
    Path("solver_postflop/board_texture.py"),
)


FORBIDDEN_SOURCE_MARKERS = (
    "Dark_JSON",
    "Pending_JSON",
    "Service JSON",
    "Runtime JSON",
    "dark_json",
    "pending_json",
    "service_json",
    "runtime_json",
    "source_discovery",
    "fallback_source",
    "display_analysis_cycle",
    "Action_Button",
    "PokerVisionFinalVersionNoSolver_snapshot",
    "solver_preflop",
    "validate_cards",
    "validate_board",
    "validate_players",
    "card_validation",
    "duplicate_cards",
    "hero_board_collision",
    "hero-board collision",
    "board_count_safety_gate",
    "filter_players",
    "player_filtering",
    "create_hero",
    "reconstruct_hero",
    "create_active_player",
    "active_player_reconstruction",
    "made_hand_class",
    "hero_made_hand",
    "draw_class",
    "hero_draw",
    "equity_value",
    "range_matrix",
    "runtime_plan",
    "click_result",
    "click_sequence",
    "button_label",
)


FORBIDDEN_PAYLOAD_KEYS = {
    "made_hand_class",
    "pair_class",
    "strength_tier",
    "showdown_value",
    "kicker_relevance",
    "draw_class",
    "flush_draw_class",
    "straight_draw_class",
    "overcard_class",
    "combo_draw_class",
    "draw_strength_tier",
    "equity",
    "equity_value",
    "range",
    "ranges",
    "range_matrix",
    "final_decision",
    "recommended_action",
    "raw_action",
    "poker_decision",
    "decision_result",
    "bet_size",
    "sizing",
    "runtime_plan",
    "runtime_action_plan",
    "click_sequence",
    "click_result",
    "button_label",
}


def _source_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in BOARD_TEXTURE_SOURCE_FILES)


def _flop_context() -> FlopContext:
    raw_payload: dict[str, Any] = {
        "case_id": "board_texture_no_extra_logic_case",
        "source_file": "tests/fixtures/postflop_clear_json/synthetic/flop/board_texture_no_extra_logic.clear.json",
        "table_id": "table_06",
        "hand_id": "hand_06",
        "hero_id": "hero",
        "hero_position": "BB",
        "hero_cards": ["Ks", "Kh"],
        "board_cards": ["Ah", "7d", "2c"],
        "players": [
            {"id": "hero", "position": "BB", "folded": False, "stack": 97.5},
            {"id": "villain", "position": "BTN", "folded": False, "stack": 101.0},
        ],
        "total_pot": 6.5,
        "to_call": 0,
        "allowed_actions": ["check", "bet"],
        "action_context": {"state": "check_option", "current_actor": "hero"},
        "unexpected_payload_field": {"must_remain": "read_only"},
    }
    players = tuple(copy.deepcopy(raw_payload["players"]))
    return FlopContext(
        case_id="board_texture_no_extra_logic_case",
        source_file=raw_payload["source_file"],
        table_id="table_06",
        hand_id="hand_06",
        branch="flop",
        spot_family=FlopSpotFamily.SRP_HEADS_UP,
        hero_cards=tuple(raw_payload["hero_cards"]),
        board_cards=tuple(raw_payload["board_cards"]),
        pot_context=FlopPotContext(pot=6.5, to_call=0, pot_type="srp", fields_used=("pot", "to_call", "pot_type")),
        position_context=FlopPositionContext(hero_id="hero", hero_position="BB", fields_used=("hero_id", "hero_position")),
        action_context=FlopActionContext(
            allowed_actions=tuple(raw_payload["allowed_actions"]),
            current_actor="hero",
            action_context_label="check_option",
            can_check=True,
            can_bet=True,
            fields_used=("allowed_actions", "action_context"),
        ),
        player_context=FlopPlayerContext(
            players=players,
            opponents=(players[1],),
            hero_id="hero",
            hero_position="BB",
            is_heads_up=True,
            is_multiway=False,
            fields_used=("players", "hero_id", "hero_position"),
        ),
        context_fields_used=("board_cards", "hero_cards", "players", "allowed_actions", "pot", "to_call"),
        context_fields_not_provided=("effective_stack", "spr"),
        raw_clear_json_ref=raw_payload,
        notes=("flop_context_before_board_texture",),
    )


def _walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from _walk_keys(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk_keys(item)


def test_board_texture_source_has_no_forbidden_validation_hand_draw_equity_or_click_markers() -> None:
    source_text = _source_text()

    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source_text


def test_build_board_texture_features_does_not_mutate_flop_context_or_clear_json_reference() -> None:
    context = _flop_context()
    context_before = copy.deepcopy(context.to_json_dict())
    raw_before = copy.deepcopy(context.raw_clear_json_ref)

    features = build_board_texture_features(context)

    assert isinstance(features, BoardTextureFeatures)
    assert features.suit_texture is BoardSuitTexture.RAINBOW
    assert context.to_json_dict() == context_before
    assert context.raw_clear_json_ref == raw_before


def test_build_board_texture_features_does_not_mutate_context_cards_players_or_actions() -> None:
    context = _flop_context()
    board_before = copy.deepcopy(context.board_cards)
    hero_cards_before = copy.deepcopy(context.hero_cards)
    players_before = copy.deepcopy(context.player_context.players)
    allowed_actions_before = copy.deepcopy(context.action_context.allowed_actions)

    features = build_board_texture_features(context)

    assert features.board_cards == board_before
    assert context.board_cards == board_before
    assert context.hero_cards == hero_cards_before
    assert context.player_context.players == players_before
    assert context.action_context.allowed_actions == allowed_actions_before


def test_build_board_texture_features_does_not_read_files(monkeypatch) -> None:
    def fail_file_io(*args: Any, **kwargs: Any) -> None:  # pragma: no cover - bug path only
        raise AssertionError("Board Texture Builder must not perform file I/O")

    monkeypatch.setattr("builtins.open", fail_file_io)
    monkeypatch.setattr(Path, "open", fail_file_io)
    monkeypatch.setattr(Path, "read_text", fail_file_io)
    monkeypatch.setattr(Path, "read_bytes", fail_file_io)

    features = build_board_texture_features(_flop_context())

    assert features.case_id == "board_texture_no_extra_logic_case"
    assert features.board_cards == ("Ah", "7d", "2c")


def test_board_texture_features_contain_no_decision_runtime_click_made_hand_draw_or_equity_keys() -> None:
    features = build_board_texture_features(_flop_context())
    payload = features.to_json_dict()
    payload_keys = {key.lower() for key in _walk_keys(payload)}

    assert payload_keys.isdisjoint(FORBIDDEN_PAYLOAD_KEYS)
    assert "runtime" not in " ".join(sorted(payload_keys))
    assert "click" not in " ".join(sorted(payload_keys))


def test_board_texture_does_not_filter_players_or_invent_hero_state() -> None:
    context = _flop_context()
    players_before = copy.deepcopy(context.player_context.players)

    build_board_texture_features(context)

    assert context.player_context.players == players_before
    assert len(context.player_context.players) == 2
    assert context.player_context.hero_id == "hero"
    assert "created_hero" not in context.raw_clear_json_ref
    assert "active_player" not in context.raw_clear_json_ref


def test_board_texture_keeps_cards_as_board_metadata_without_validation_or_repair_language() -> None:
    context = _flop_context()
    features = build_board_texture_features(context)

    assert features.board_cards == context.board_cards
    assert "ace_high" in features.texture_tags
    assert "rainbow" in features.texture_tags

    serialized_notes = " ".join(features.notes).lower()
    assert "invalid" not in serialized_notes
    assert "duplicate" not in serialized_notes
    assert "collision" not in serialized_notes
    assert "repair" not in serialized_notes
