from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from solver_postflop.board_texture_contracts import (
    BoardConnectionTexture,
    BoardPairedTexture,
    BoardRankTexture,
    BoardSuitTexture,
    BoardTextureFeatures,
    BoardVolatilityClass,
)
from solver_postflop.equity_input import build_equity_scenario_input
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

FIXTURE_ROOT = Path("tests") / "fixtures" / "postflop_equity_input_v0103"
SYNTHETIC_ROOT = FIXTURE_ROOT / "synthetic"
EXPECTED_ROOT = FIXTURE_ROOT / "expected"

REQUIRED_CASE_IDS = (
    "flop_equity_input_srp_heads_up",
    "flop_equity_input_3bet_pot",
    "flop_equity_input_4bet_low_spr",
    "flop_equity_input_limp_passive",
    "flop_equity_input_multiway",
    "flop_equity_input_unknown_context",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _case_path(case_id: str) -> Path:
    return SYNTHETIC_ROOT / f"{case_id}.clear.json"


def _expected_path(case_id: str) -> Path:
    return EXPECTED_ROOT / f"{case_id}.expected.json"


def _load_case(case_id: str) -> dict[str, Any]:
    return _load_json(_case_path(case_id))


def _load_expected(case_id: str) -> dict[str, Any]:
    return _load_json(_expected_path(case_id))


def _tuple_dicts(items: list[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    return tuple(dict(item) for item in items)


def _build_flop_context(payload: dict[str, Any]) -> FlopContext:
    action_context = dict(payload["action_context"])
    action_context["allowed_actions"] = tuple(action_context.get("allowed_actions", ()))

    player_context = dict(payload["player_context"])
    player_context["players"] = _tuple_dicts(player_context.get("players", []))
    player_context["opponents"] = _tuple_dicts(player_context.get("opponents", []))

    return FlopContext(
        case_id=payload["case_id"],
        source_file=payload["source_file"],
        table_id=payload["table_id"],
        hand_id=payload["hand_id"],
        branch="flop",
        spot_family=FlopSpotFamily(payload["spot_family"]),
        hero_cards=tuple(payload["hero_cards"]),
        board_cards=tuple(payload["board_cards"]),
        pot_context=FlopPotContext(**payload["pot_context"]),
        position_context=FlopPositionContext(**payload["position_context"]),
        action_context=FlopActionContext(**action_context),
        player_context=FlopPlayerContext(**player_context),
        context_fields_used=("hero_cards", "board_cards", "player_context"),
        raw_clear_json_ref={
            "case_id": payload["case_id"],
            "fixture_scope": "v0.10.3_equity_input_fixture_coverage",
        },
        notes=("synthetic_fixture_context_only",),
    )


def _build_board_texture(payload: dict[str, Any]) -> BoardTextureFeatures:
    texture = payload["board_texture"]
    return BoardTextureFeatures(
        case_id=payload["case_id"],
        source_file=payload["source_file"],
        board_cards=tuple(payload["board_cards"]),
        suit_texture=BoardSuitTexture(texture["suit_texture"]),
        paired_texture=BoardPairedTexture(texture["paired_texture"]),
        rank_texture=BoardRankTexture(texture["rank_texture"]),
        connection_texture=BoardConnectionTexture(texture["connection_texture"]),
        volatility_class=BoardVolatilityClass(texture["volatility_class"]),
        texture_tags=tuple(texture["texture_tags"]),
        features_used_by_future_modules=("equity_input_builder_later",),
        notes=("synthetic_fixture_board_texture",),
    )


def _build_made_hand(payload: dict[str, Any]) -> MadeHandFeatures:
    made_hand = payload["made_hand"]
    return MadeHandFeatures(
        case_id=payload["case_id"],
        source_file=payload["source_file"],
        hero_cards=tuple(payload["hero_cards"]),
        board_cards=tuple(payload["board_cards"]),
        made_hand_class=MadeHandClass(made_hand["made_hand_class"]),
        pair_class=PairClass(made_hand["pair_class"]),
        showdown_value_class=ShowdownValueClass(made_hand["showdown_value_class"]),
        strength_tier=MadeHandStrengthTier(made_hand["strength_tier"]),
        kicker_relevance=made_hand["kicker_relevance"],
        board_interaction_tags=tuple(made_hand["board_interaction_tags"]),
        features_used_by_future_modules=("equity_module_later",),
        notes=("synthetic_fixture_made_hand",),
    )


def _build_draw_features(payload: dict[str, Any]) -> DrawFeatures:
    draw = payload["draw"]
    return DrawFeatures(
        case_id=payload["case_id"],
        source_file=payload["source_file"],
        hero_cards=tuple(payload["hero_cards"]),
        board_cards=tuple(payload["board_cards"]),
        draw_class=DrawClass(draw["draw_class"]),
        flush_draw_class=FlushDrawClass(draw["flush_draw_class"]),
        straight_draw_class=StraightDrawClass(draw["straight_draw_class"]),
        overcard_class=OvercardClass(draw["overcard_class"]),
        combo_draw_class=ComboDrawClass(draw["combo_draw_class"]),
        draw_strength_tier=DrawStrengthTier(draw["draw_strength_tier"]),
        draw_tags=tuple(draw["draw_tags"]),
        features_used_by_future_modules=("equity_module_later",),
        notes=("synthetic_fixture_draw_features",),
    )


def _build_scenario_from_fixture(case_id: str) -> EquityScenarioInput:
    payload = _load_case(case_id)
    return build_equity_scenario_input(
        flop_context=_build_flop_context(payload),
        board_texture_features=_build_board_texture(payload),
        made_hand_features=_build_made_hand(payload),
        draw_features=_build_draw_features(payload),
    )


def test_equity_input_fixture_files_are_paired_for_v0103() -> None:
    source_case_ids = sorted(path.stem.removesuffix(".clear") for path in SYNTHETIC_ROOT.glob("*.clear.json"))
    expected_case_ids = sorted(path.stem.removesuffix(".expected") for path in EXPECTED_ROOT.glob("*.expected.json"))

    assert tuple(source_case_ids) == tuple(sorted(REQUIRED_CASE_IDS))
    assert source_case_ids == expected_case_ids


@pytest.mark.parametrize("case_id", REQUIRED_CASE_IDS)
def test_equity_input_builder_matches_expected_fixture_output(case_id: str) -> None:
    expected = _load_expected(case_id)
    scenario = _build_scenario_from_fixture(case_id)

    assert scenario.case_id == case_id
    assert scenario.spot_family == expected["expected_spot_family"]
    assert scenario.equity_run_mode is EquityRunMode(expected["expected_equity_run_mode"])
    assert scenario.opponents.opponents_count == expected["expected_opponents_count"]
    assert scenario.next_module == expected["expected_next_module"]

    for expected_field in expected["expected_features_used"]:
        assert expected_field in scenario.fields_used


@pytest.mark.parametrize("case_id", REQUIRED_CASE_IDS)
def test_equity_input_fixture_preserves_cards_and_feature_payloads(case_id: str) -> None:
    payload = _load_case(case_id)
    scenario = _build_scenario_from_fixture(case_id)

    assert scenario.hero.hero_cards == tuple(payload["hero_cards"])
    assert scenario.board.board_cards == tuple(payload["board_cards"])
    assert scenario.board.texture_tags == tuple(payload["board_texture"]["texture_tags"])
    assert scenario.board_texture_features["texture_tags"] == payload["board_texture"]["texture_tags"]
    assert scenario.made_hand_features["made_hand_class"] == payload["made_hand"]["made_hand_class"]
    assert scenario.draw_features["draw_class"] == payload["draw"]["draw_class"]


@pytest.mark.parametrize("case_id", REQUIRED_CASE_IDS)
def test_equity_input_fixture_result_is_json_serializable(case_id: str) -> None:
    scenario = _build_scenario_from_fixture(case_id)
    payload = scenario.to_json_dict()

    assert payload["case_id"] == case_id
    assert payload["next_module"] == "equity_engine"
    json.dumps(payload, sort_keys=True)


def test_unknown_context_fixture_does_not_create_opponents() -> None:
    scenario = _build_scenario_from_fixture("flop_equity_input_unknown_context")

    assert scenario.equity_run_mode is EquityRunMode.UNKNOWN_CONTEXT_MODE
    assert scenario.opponents.opponents_count is None
    assert scenario.opponents.known_opponents == ()
    assert scenario.opponents.opponent_positions == ()
    assert "opponents_count" in scenario.fields_not_provided
    assert "unknown_context_mode_selected_without_creating_opponents" in scenario.notes


def test_equity_input_fixture_coverage_contains_required_spot_families() -> None:
    observed = {_load_expected(case_id)["expected_spot_family"] for case_id in REQUIRED_CASE_IDS}

    assert observed == {
        "srp_heads_up",
        "threebet_pot_heads_up",
        "fourbet_low_spr",
        "limp_or_passive_pot",
        "multiway_pot",
        "unknown_flop_spot",
    }
