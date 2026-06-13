from __future__ import annotations

import json

from solver_postflop.equity_backend_pokerkit import is_pokerkit_available
from solver_postflop.equity_contracts import (
    EquityBackendStatus,
    EquityComputationMode,
    EquityConfidenceClass,
)
from solver_postflop.equity_engine import (
    NUMERIC_BACKEND_INTEGRATION_NOTE,
    RAW_NUMERIC_BACKEND_DEFERRED_NOTE,
    run_equity_engine,
)
from solver_postflop.equity_input_contracts import (
    EquityBoardInput,
    EquityHeroInput,
    EquityOpponentModelInput,
    EquityRunMode,
    EquityScenarioInput,
)


def _heads_up_numeric_scenario(
    *,
    board_cards: tuple[str, ...] = ("Q_diamonds", "J_clubs", "10_spades"),
) -> EquityScenarioInput:
    return EquityScenarioInput(
        case_id="engine_numeric_heads_up_case_v0117",
        source_file="synthetic://engine_numeric_heads_up_case_v0117.clear.json",
        hero=EquityHeroInput(
            hero_cards=("A_spades", "K_hearts"),
            position="BTN",
            effective_stack=80.0,
        ),
        board=EquityBoardInput(
            board_cards=board_cards,
            street="flop" if len(board_cards) == 3 else "river",
            texture_tags=("broadway_connected",),
            straight_structure="highly_connected",
        ),
        opponents=EquityOpponentModelInput(
            opponents_count=1,
            is_heads_up=True,
            is_multiway=False,
            opponent_positions=("BB",),
        ),
        spot_family="srp_heads_up",
        pot=12.5,
        to_call=0.0,
        effective_stack=80.0,
        spr=6.4,
        position_context={"hero_position": "BTN", "villain_position": "BB"},
        action_context={"flop_action_context": "checked_to_hero"},
        board_texture_features={"texture_tags": ["broadway_connected"]},
        made_hand_features={"made_hand_class": "straight"},
        draw_features={"draw_class": "made_hand_no_draw_needed"},
        equity_run_mode=EquityRunMode.HEADS_UP_EXACT_OR_SAMPLED,
        fields_used=(
            "hero.hero_cards",
            "board.board_cards",
            "opponents.opponents_count",
            "board_texture_features.texture_tags",
            "made_hand_features.made_hand_class",
            "draw_features.draw_class",
        ),
    )


def _multiway_deferred_scenario() -> EquityScenarioInput:
    scenario = _heads_up_numeric_scenario()
    return EquityScenarioInput(
        case_id="engine_numeric_multiway_deferred_case_v0117",
        source_file=scenario.source_file,
        hero=scenario.hero,
        board=scenario.board,
        opponents=EquityOpponentModelInput(
            opponents_count=2,
            is_heads_up=False,
            is_multiway=True,
            opponent_positions=("BB", "SB"),
        ),
        spot_family="srp_multiway",
        pot=scenario.pot,
        to_call=scenario.to_call,
        effective_stack=scenario.effective_stack,
        spr=scenario.spr,
        equity_run_mode=EquityRunMode.MULTIWAY_SAMPLED,
        fields_used=scenario.fields_used,
    )


def _unknown_context_scenario() -> EquityScenarioInput:
    return EquityScenarioInput(
        case_id="engine_numeric_unknown_context_case_v0117",
        source_file="synthetic://engine_numeric_unknown_context_case_v0117.clear.json",
        hero=EquityHeroInput(hero_cards=(), position="BTN"),
        board=EquityBoardInput(
            board_cards=("Q_diamonds", "J_clubs", "10_spades"),
            street="flop",
        ),
        opponents=EquityOpponentModelInput(opponents_count=None),
        equity_run_mode=EquityRunMode.UNKNOWN_CONTEXT_MODE,
        fields_not_provided=("hero.hero_cards", "opponents.opponents_count"),
    )


def test_equity_engine_returns_structured_result_without_backend_requirement() -> None:
    result = run_equity_engine(_heads_up_numeric_scenario(), sample_count=64)
    payload = result.to_json_dict()

    assert payload["backend_name"] == "pokerkit"
    assert payload["backend_status"] in {"ok", "unavailable", "error"}
    assert payload["computation_mode"] in {
        "heads_up_raw_equity",
        "backend_unavailable",
        "backend_error",
    }
    assert payload["backend_metadata"]["numeric_integration_version"] == "v0.11.7"
    json.dumps(payload, sort_keys=True)


def test_equity_engine_integrates_numeric_heads_up_backend_result_when_available() -> None:
    if not is_pokerkit_available():
        return

    result = run_equity_engine(_heads_up_numeric_scenario(), sample_count=256)

    assert result.backend_status is EquityBackendStatus.OK
    assert result.computation_mode is EquityComputationMode.HEADS_UP_RAW_EQUITY
    assert result.hero_equity is not None
    assert result.hero_win_rate is not None
    assert result.hero_tie_rate is not None
    assert 0.0 <= result.hero_equity <= 1.0
    assert 0.0 <= result.hero_win_rate <= 1.0
    assert 0.0 <= result.hero_tie_rate <= 1.0
    assert abs(result.hero_equity - (result.hero_win_rate + result.hero_tie_rate / 2.0)) <= 1e-6
    assert result.sample_count_used is not None
    assert result.sample_count_used > 0
    assert result.backend_name == "pokerkit"
    assert result.equity_confidence is EquityConfidenceClass.MEDIUM
    assert result.opponents_count == 1
    assert result.input_features_used == (
        "hero.hero_cards",
        "board.board_cards",
        "opponents.opponents_count",
        "board_texture_features.texture_tags",
        "made_hand_features.made_hand_class",
        "draw_features.draw_class",
    )
    assert result.backend_metadata["numeric_result_integrated"] is True
    assert result.backend_metadata["backend_sample_count_used"] == result.sample_count_used
    assert result.backend_metadata["hero_compact"] == "AsKh"
    assert result.backend_metadata["board_compact"] == "QdJcTs"
    assert NUMERIC_BACKEND_INTEGRATION_NOTE in result.notes
    assert RAW_NUMERIC_BACKEND_DEFERRED_NOTE not in result.notes
    assert result.player_equities[0].player_id == "hero"
    assert result.player_equities[0].equity == result.hero_equity


def test_equity_engine_numeric_integration_supports_complete_board_when_available() -> None:
    if not is_pokerkit_available():
        return

    result = run_equity_engine(
        _heads_up_numeric_scenario(
            board_cards=("Q_diamonds", "J_clubs", "10_spades", "2_clubs", "3_diamonds")
        ),
        sample_count=256,
    )

    assert result.backend_status is EquityBackendStatus.OK
    assert result.computation_mode is EquityComputationMode.HEADS_UP_RAW_EQUITY
    assert result.hero_equity is not None
    assert result.backend_metadata["board_compact"] == "QdJcTs2c3d"
    assert result.backend_metadata["missing_board_cards"] == 0
    assert result.backend_metadata["numeric_result_integrated"] is True


def test_equity_engine_multiway_stays_structured_deferred() -> None:
    result = run_equity_engine(_multiway_deferred_scenario(), sample_count=64)

    if result.backend_status is EquityBackendStatus.UNAVAILABLE:
        return

    assert result.backend_status is EquityBackendStatus.NOT_RUN
    assert result.computation_mode is EquityComputationMode.MULTIWAY_RAW_EQUITY
    assert result.hero_equity is None
    assert result.backend_metadata["numeric_result_integrated"] is False
    assert RAW_NUMERIC_BACKEND_DEFERRED_NOTE in result.notes


def test_equity_engine_unknown_context_does_not_crash() -> None:
    result = run_equity_engine(_unknown_context_scenario(), sample_count=64)

    if result.backend_status is EquityBackendStatus.UNAVAILABLE:
        return

    assert result.backend_status is EquityBackendStatus.NOT_RUN
    assert result.computation_mode is EquityComputationMode.UNKNOWN_CONTEXT_EQUITY
    assert result.hero_equity is None
    assert result.equity_confidence is EquityConfidenceClass.UNKNOWN
    assert result.backend_metadata["numeric_result_integrated"] is False
    assert RAW_NUMERIC_BACKEND_DEFERRED_NOTE in result.notes
