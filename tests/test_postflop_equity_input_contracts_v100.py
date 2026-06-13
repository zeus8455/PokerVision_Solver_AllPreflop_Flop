from __future__ import annotations

import inspect
import json
from dataclasses import asdict, is_dataclass

from solver_postflop.equity_input_contracts import (
    DEFAULT_EQUITY_INPUT_NEXT_MODULE,
    EQUITY_INPUT_CONTRACT_VERSION,
    EQUITY_RANGE_MODEL_STATUSES,
    EQUITY_RUN_MODES,
    EquityBoardInput,
    EquityHeroInput,
    EquityOpponentModelInput,
    EquityRunMode,
    EquityScenarioInput,
)
import solver_postflop.equity_input_contracts as equity_input_contracts


def test_equity_input_contract_version_is_fixed_for_v0101() -> None:
    assert EQUITY_INPUT_CONTRACT_VERSION == "v0.10.1"


def test_equity_run_modes_are_fixed_for_future_engine_selection() -> None:
    assert {mode.value for mode in EquityRunMode} == {
        "heads_up_exact_or_sampled",
        "multiway_sampled",
        "range_based_later",
        "unknown_context_mode",
    }
    assert EQUITY_RUN_MODES == tuple(EquityRunMode)


def test_equity_range_model_statuses_are_metadata_only() -> None:
    assert EQUITY_RANGE_MODEL_STATUSES == (
        "range_based_later",
        "unknown_context",
    )


def test_equity_hero_input_can_be_created_and_serialized() -> None:
    hero = EquityHeroInput(
        hero_cards=("Ah", "Kh"),
        position="BTN",
        stack=100.0,
        effective_stack=82.5,
        notes=("contract_only",),
    )

    assert is_dataclass(hero)
    assert asdict(hero)["hero_cards"] == ("Ah", "Kh")

    payload = hero.to_json_dict()
    assert payload == {
        "hero_cards": ["Ah", "Kh"],
        "position": "BTN",
        "stack": 100.0,
        "effective_stack": 82.5,
        "notes": ["contract_only"],
    }
    json.dumps(payload, sort_keys=True)


def test_equity_board_input_can_be_created_and_serialized() -> None:
    board = EquityBoardInput(
        board_cards=("Qh", "Jh", "2c"),
        street="flop",
        texture_tags=("two_tone", "broadway_heavy"),
        paired_status="unpaired",
        suit_structure="two_tone",
        straight_structure="semi_connected",
        notes=("from_board_texture_features",),
    )

    payload = board.to_json_dict()
    assert payload["board_cards"] == ["Qh", "Jh", "2c"]
    assert payload["street"] == "flop"
    assert payload["texture_tags"] == ["two_tone", "broadway_heavy"]
    assert payload["paired_status"] == "unpaired"
    assert payload["suit_structure"] == "two_tone"
    assert payload["straight_structure"] == "semi_connected"
    json.dumps(payload, sort_keys=True)


def test_equity_opponent_model_input_can_be_created_and_serialized() -> None:
    opponents = EquityOpponentModelInput(
        opponents_count=1,
        is_heads_up=True,
        is_multiway=False,
        known_opponents=({"player_id": "BB", "position": "BB"},),
        opponent_positions=("BB",),
        range_model_status="range_based_later",
        notes=("opponents_are_carried_from_existing_context",),
    )

    payload = opponents.to_json_dict()
    assert payload["opponents_count"] == 1
    assert payload["is_heads_up"] is True
    assert payload["is_multiway"] is False
    assert payload["known_opponents"] == [{"player_id": "BB", "position": "BB"}]
    assert payload["opponent_positions"] == ["BB"]
    assert payload["range_model_status"] == "range_based_later"
    json.dumps(payload, sort_keys=True)


def test_equity_scenario_input_can_be_created_and_serialized() -> None:
    scenario = EquityScenarioInput(
        case_id="equity_input_contract_case",
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/equity_input_contract.clear.json",
        hero=EquityHeroInput(hero_cards=("Ah", "Kh"), position="BTN", effective_stack=82.5),
        board=EquityBoardInput(
            board_cards=("Qh", "Jh", "2c"),
            texture_tags=("two_tone", "broadway_heavy"),
            paired_status="unpaired",
            suit_structure="two_tone",
            straight_structure="semi_connected",
        ),
        opponents=EquityOpponentModelInput(
            opponents_count=1,
            is_heads_up=True,
            is_multiway=False,
            opponent_positions=("BB",),
        ),
        spot_family="srp_heads_up",
        pot=7.5,
        to_call=2.5,
        effective_stack=82.5,
        spr=11.0,
        position_context={"hero_position": "BTN", "is_in_position": True},
        action_context={"can_call": True, "can_raise": True},
        board_texture_features={"texture_tags": ["two_tone", "broadway_heavy"]},
        made_hand_features={"made_hand_class": "high_card"},
        draw_features={"draw_class": "combo_draw"},
        equity_run_mode=EquityRunMode.HEADS_UP_EXACT_OR_SAMPLED,
        fields_used=("hero_cards", "board_cards", "spot_family", "player_context"),
        fields_not_provided=("range_state",),
        notes=("contract_only_no_builder",),
    )

    assert is_dataclass(scenario)
    payload = scenario.to_json_dict()

    assert payload["case_id"] == "equity_input_contract_case"
    assert payload["source_file"].endswith("equity_input_contract.clear.json")
    assert payload["hero"]["hero_cards"] == ["Ah", "Kh"]
    assert payload["board"]["board_cards"] == ["Qh", "Jh", "2c"]
    assert payload["opponents"]["opponents_count"] == 1
    assert payload["spot_family"] == "srp_heads_up"
    assert payload["pot"] == 7.5
    assert payload["to_call"] == 2.5
    assert payload["effective_stack"] == 82.5
    assert payload["spr"] == 11.0
    assert payload["equity_run_mode"] == "heads_up_exact_or_sampled"
    assert payload["next_module"] == DEFAULT_EQUITY_INPUT_NEXT_MODULE
    assert payload["fields_used"] == ["hero_cards", "board_cards", "spot_family", "player_context"]
    assert payload["fields_not_provided"] == ["range_state"]
    json.dumps(payload, sort_keys=True)


def test_equity_scenario_input_remains_prepared_metadata_only() -> None:
    scenario = EquityScenarioInput(
        case_id="metadata_only_case",
        source_file="metadata_only.clear.json",
        hero=EquityHeroInput(hero_cards=("As", "Kd")),
        board=EquityBoardInput(board_cards=("Qh", "7d", "2c")),
        opponents=EquityOpponentModelInput(opponents_count=None),
        equity_run_mode=EquityRunMode.UNKNOWN_CONTEXT_MODE,
    )

    payload = scenario.to_json_dict()
    forbidden_keys = {
        "hero_equity",
        "hero_win_rate",
        "hero_tie_rate",
        "player_equities",
        "range_state",
        "action_plan",
        "button_targets",
        "click_result",
    }
    assert forbidden_keys.isdisjoint(payload)
    assert payload["next_module"] == "equity_engine"


def test_equity_input_contracts_define_module_exports() -> None:
    assert set(equity_input_contracts.__all__) == {
        "DEFAULT_EQUITY_INPUT_NEXT_MODULE",
        "EQUITY_INPUT_CONTRACT_VERSION",
        "EQUITY_RANGE_MODEL_STATUSES",
        "EQUITY_RUN_MODES",
        "EquityBoardInput",
        "EquityHeroInput",
        "EquityOpponentModelInput",
        "EquityRunMode",
        "EquityScenarioInput",
    }


def test_equity_input_contracts_do_not_include_backend_or_action_logic() -> None:
    source = inspect.getsource(equity_input_contracts).lower()
    forbidden_fragments = (
        "pokerkit",
        "monte_carlo",
        "simulation",
        "calculate_equity",
        "build_range_state",
        "resolve_decision",
        "runtime_plan",
        "button_targets",
        "click_result",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source
