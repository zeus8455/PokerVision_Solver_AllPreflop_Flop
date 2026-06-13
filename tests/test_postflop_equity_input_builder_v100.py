from __future__ import annotations

import inspect
import json

from solver_postflop.board_texture_contracts import (
    BoardConnectionTexture,
    BoardPairedTexture,
    BoardRankTexture,
    BoardSuitTexture,
    BoardTextureFeatures,
    BoardVolatilityClass,
)
from solver_postflop.equity_input import (
    EQUITY_INPUT_BUILDER_NEXT_MODULE,
    EQUITY_INPUT_BUILDER_VERSION,
    build_equity_scenario_input,
)
from solver_postflop.equity_input_contracts import EquityRunMode, EquityScenarioInput
from solver_postflop.flop_context_contracts import (
    FlopActionContext,
    FlopContext,
    FlopPlayerContext,
    FlopPositionContext,
    FlopPotContext,
    FlopSpotFamily,
)
from solver_postflop.hero_draw_contracts import (
    ComboDrawClass,
    DrawClass,
    DrawFeatures,
    DrawStrengthTier,
    FlushDrawClass,
    OvercardClass,
    StraightDrawClass,
)
from solver_postflop.hero_made_hand_contracts import (
    MadeHandClass,
    MadeHandFeatures,
    MadeHandStrengthTier,
    PairClass,
    ShowdownValueClass,
)

import solver_postflop.equity_input as equity_input


def _flop_context(
    *,
    opponents=({"player_id": "BB", "position": "BB"},),
    is_heads_up=True,
    is_multiway=False,
    spot_family=FlopSpotFamily.SRP_HEADS_UP,
) -> FlopContext:
    return FlopContext(
        case_id="equity_input_builder_case",
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/equity_input_builder.clear.json",
        table_id="table_01",
        hand_id="hand_001",
        branch="flop",
        spot_family=spot_family,
        hero_cards=("Ah", "Kh"),
        board_cards=("Qh", "Jh", "2c"),
        pot_context=FlopPotContext(
            pot=7.5,
            to_call=2.5,
            effective_stack=82.5,
            spr=11.0,
            pot_type="single_raised_pot",
        ),
        position_context=FlopPositionContext(
            hero_id="HERO",
            hero_position="BTN",
            is_in_position=True,
            position_label="ip",
        ),
        action_context=FlopActionContext(
            allowed_actions=("fold", "call", "raise"),
            current_actor="HERO",
            action_context_label="facing_bet",
            facing_bet=True,
            can_call=True,
            can_raise=True,
        ),
        player_context=FlopPlayerContext(
            players=(
                {"player_id": "HERO", "position": "BTN"},
                {"player_id": "BB", "position": "BB"},
            ),
            opponents=opponents,
            hero_id="HERO",
            hero_position="BTN",
            is_heads_up=is_heads_up,
            is_multiway=is_multiway,
        ),
        context_fields_used=("hero_cards", "board_cards", "player_context"),
        raw_clear_json_ref={"case_id": "equity_input_builder_case"},
    )


def _board_texture() -> BoardTextureFeatures:
    return BoardTextureFeatures(
        case_id="equity_input_builder_case",
        source_file="board_texture.synthetic.json",
        board_cards=("Qh", "Jh", "2c"),
        suit_texture=BoardSuitTexture.TWO_TONE,
        paired_texture=BoardPairedTexture.UNPAIRED,
        rank_texture=BoardRankTexture.BROADWAY_HEAVY,
        connection_texture=BoardConnectionTexture.SEMI_CONNECTED,
        volatility_class=BoardVolatilityClass.SEMI_DYNAMIC_BOARD,
        texture_tags=("two_tone", "broadway_heavy", "semi_connected"),
        features_used_by_future_modules=("equity_module_later",),
    )


def _made_hand() -> MadeHandFeatures:
    return MadeHandFeatures(
        case_id="equity_input_builder_case",
        source_file="made_hand.synthetic.json",
        hero_cards=("Ah", "Kh"),
        board_cards=("Qh", "Jh", "2c"),
        made_hand_class=MadeHandClass.HIGH_CARD,
        pair_class=PairClass.NO_PAIR_CLASS,
        showdown_value_class=ShowdownValueClass.AIR,
        strength_tier=MadeHandStrengthTier.AIR,
        kicker_relevance="two_overcards",
        board_interaction_tags=("two_overcards",),
        features_used_by_future_modules=("equity_module_later",),
    )


def _draw_features() -> DrawFeatures:
    return DrawFeatures(
        case_id="equity_input_builder_case",
        source_file="draw.synthetic.json",
        hero_cards=("Ah", "Kh"),
        board_cards=("Qh", "Jh", "2c"),
        draw_class=DrawClass.COMBO_DRAW,
        flush_draw_class=FlushDrawClass.NUT_FLUSH_DRAW_CANDIDATE,
        straight_draw_class=StraightDrawClass.GUTSHOT,
        overcard_class=OvercardClass.TWO_OVERCARDS,
        combo_draw_class=ComboDrawClass.PREMIUM_COMBO_DRAW,
        draw_strength_tier=DrawStrengthTier.PREMIUM_COMBO_DRAW,
        draw_tags=("nut_flush_candidate", "gutshot", "two_overcards"),
        features_used_by_future_modules=("equity_input_builder_later",),
    )


def _build(**context_kwargs) -> EquityScenarioInput:
    return build_equity_scenario_input(
        flop_context=_flop_context(**context_kwargs),
        board_texture_features=_board_texture(),
        made_hand_features=_made_hand(),
        draw_features=_draw_features(),
    )


def test_equity_input_builder_version_is_fixed_for_v0102() -> None:
    assert EQUITY_INPUT_BUILDER_VERSION == "v0.10.2"
    assert EQUITY_INPUT_BUILDER_NEXT_MODULE == "equity_engine"


def test_builds_heads_up_equity_scenario_from_flop_chain() -> None:
    scenario = _build()

    assert isinstance(scenario, EquityScenarioInput)
    assert scenario.case_id == "equity_input_builder_case"
    assert scenario.source_file.endswith("equity_input_builder.clear.json")
    assert scenario.hero.hero_cards == ("Ah", "Kh")
    assert scenario.hero.position == "BTN"
    assert scenario.hero.effective_stack == 82.5
    assert scenario.board.board_cards == ("Qh", "Jh", "2c")
    assert scenario.board.street == "flop"
    assert scenario.spot_family == "srp_heads_up"
    assert scenario.pot == 7.5
    assert scenario.to_call == 2.5
    assert scenario.effective_stack == 82.5
    assert scenario.spr == 11.0
    assert scenario.opponents.opponents_count == 1
    assert scenario.opponents.is_heads_up is True
    assert scenario.opponents.is_multiway is False
    assert scenario.opponents.opponent_positions == ("BB",)
    assert scenario.equity_run_mode is EquityRunMode.HEADS_UP_EXACT_OR_SAMPLED
    assert scenario.next_module == "equity_engine"


def test_builder_attaches_board_made_hand_and_draw_features() -> None:
    scenario = _build()

    assert scenario.board.texture_tags == (
        "two_tone",
        "broadway_heavy",
        "semi_connected",
    )
    assert scenario.board.paired_status == "unpaired"
    assert scenario.board.suit_structure == "two_tone"
    assert scenario.board.straight_structure == "semi_connected"

    assert scenario.board_texture_features["texture_tags"] == [
        "two_tone",
        "broadway_heavy",
        "semi_connected",
    ]
    assert scenario.made_hand_features["made_hand_class"] == "high_card"
    assert scenario.made_hand_features["strength_tier"] == "air"
    assert scenario.draw_features["draw_class"] == "combo_draw"
    assert scenario.draw_features["combo_draw_class"] == "premium_combo_draw"


def test_builder_selects_multiway_mode_from_existing_opponent_context() -> None:
    scenario = _build(
        opponents=(
            {"player_id": "BB", "position": "BB"},
            {"player_id": "CO", "position": "CO"},
        ),
        is_heads_up=False,
        is_multiway=True,
        spot_family=FlopSpotFamily.MULTIWAY_POT,
    )

    assert scenario.opponents.opponents_count == 2
    assert scenario.opponents.is_heads_up is False
    assert scenario.opponents.is_multiway is True
    assert scenario.opponents.opponent_positions == ("BB", "CO")
    assert scenario.equity_run_mode is EquityRunMode.MULTIWAY_SAMPLED


def test_builder_uses_unknown_mode_without_creating_opponents() -> None:
    scenario = _build(
        opponents=(),
        is_heads_up=None,
        is_multiway=None,
        spot_family=FlopSpotFamily.UNKNOWN_FLOP_SPOT,
    )

    assert scenario.opponents.opponents_count is None
    assert scenario.opponents.known_opponents == ()
    assert scenario.opponents.opponent_positions == ()
    assert scenario.opponents.range_model_status == "unknown_context"
    assert scenario.equity_run_mode is EquityRunMode.UNKNOWN_CONTEXT_MODE
    assert "opponents_count" in scenario.fields_not_provided
    assert "unknown_context_mode_selected_without_creating_opponents" in scenario.notes


def test_builder_can_select_range_based_later_by_explicit_flag() -> None:
    scenario = build_equity_scenario_input(
        flop_context=_flop_context(),
        board_texture_features=_board_texture(),
        made_hand_features=_made_hand(),
        draw_features=_draw_features(),
        force_range_based_later=True,
    )

    assert scenario.equity_run_mode is EquityRunMode.RANGE_BASED_LATER
    assert "range_based_later_selected_by_explicit_builder_flag" in scenario.notes


def test_builder_records_fields_used_and_not_provided() -> None:
    scenario = _build()

    assert "flop_context.hero_cards" in scenario.fields_used
    assert "flop_context.board_cards" in scenario.fields_used
    assert "flop_context.player_context.opponents" in scenario.fields_used
    assert "board_texture_features.texture_tags" in scenario.fields_used
    assert "hero_stack" not in scenario.fields_used
    assert "hero_stack_not_provided_by_flop_context" in scenario.hero.notes


def test_builder_payload_serializes_to_json() -> None:
    payload = _build().to_json_dict()

    assert payload["equity_run_mode"] == "heads_up_exact_or_sampled"
    assert payload["hero"]["hero_cards"] == ["Ah", "Kh"]
    assert payload["board"]["board_cards"] == ["Qh", "Jh", "2c"]
    assert payload["opponents"]["known_opponents"] == [
        {"player_id": "BB", "position": "BB"}
    ]
    assert payload["next_module"] == "equity_engine"
    json.dumps(payload, sort_keys=True)


def test_equity_input_builder_does_not_include_backend_decision_or_runtime_logic() -> None:
    source = inspect.getsource(equity_input).lower()
    forbidden_fragments = (
        "pokerkit",
        "monte_carlo",
        "calculate_equity",
        "build_range_state",
        "resolve_decision",
        "runtime_plan",
        "button_targets",
        "click_result",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source
