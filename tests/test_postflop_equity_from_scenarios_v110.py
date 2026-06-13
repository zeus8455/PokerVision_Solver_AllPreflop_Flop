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
from solver_postflop.equity_backend_pokerkit import is_pokerkit_available
from solver_postflop.equity_contracts import (
    EquityBackendStatus,
    EquityComputationMode,
)
from solver_postflop.equity_engine import run_equity_engine
from solver_postflop.equity_input import build_equity_scenario_input
from solver_postflop.equity_input_contracts import EquityScenarioInput
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

INPUT_FIXTURE_ROOT = Path("tests") / "fixtures" / "postflop_equity_input_v0103"
INPUT_SYNTHETIC_ROOT = INPUT_FIXTURE_ROOT / "synthetic"
RESULT_FIXTURE_ROOT = Path("tests") / "fixtures" / "postflop_equity_result_v0118"
EXPECTED_ROOT = RESULT_FIXTURE_ROOT / "expected"

REQUIRED_CASE_IDS = (
    "flop_equity_input_srp_heads_up",
    "flop_equity_input_3bet_pot",
    "flop_equity_input_4bet_low_spr",
    "flop_equity_input_limp_passive",
    "flop_equity_input_multiway",
    "flop_equity_input_unknown_context",
)

NUMERIC_SAMPLE_COUNT = 256


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _case_path(case_id: str) -> Path:
    return INPUT_SYNTHETIC_ROOT / f"{case_id}.clear.json"


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
            "fixture_scope": "v0.11.8_equity_from_scenarios",
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
        features_used_by_future_modules=("equity_engine_later",),
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


def _equity_band(hero_equity: float | None) -> str:
    if hero_equity is None:
        return "no_numeric_equity"
    if hero_equity < 0.35:
        return "low_equity"
    if hero_equity < 0.65:
        return "medium_equity"
    if hero_equity < 0.85:
        return "high_equity"
    return "very_high_equity"


def test_equity_result_expected_fixture_files_are_paired_for_v0118() -> None:
    expected_case_ids = sorted(
        path.stem.removesuffix(".expected") for path in EXPECTED_ROOT.glob("*.expected.json")
    )
    assert tuple(expected_case_ids) == tuple(sorted(REQUIRED_CASE_IDS))


@pytest.mark.parametrize("case_id", REQUIRED_CASE_IDS)
def test_equity_engine_from_equity_input_fixtures_matches_expected_status(case_id: str) -> None:
    expected = _load_expected(case_id)
    scenario = _build_scenario_from_fixture(case_id)
    result = run_equity_engine(scenario, sample_count=NUMERIC_SAMPLE_COUNT)
    payload = result.to_json_dict()

    assert result.case_id == case_id
    assert result.backend_name == "pokerkit"
    assert result.opponents_count == expected["expected_opponents_count"]
    assert result.computation_mode is EquityComputationMode(expected["expected_computation_mode"])
    assert payload["backend_metadata"]["numeric_integration_version"] == "v0.11.7"
    assert payload["backend_metadata"]["scenario_case_id"] == case_id
    json.dumps(payload, sort_keys=True)

    if not is_pokerkit_available():
        assert result.backend_status is EquityBackendStatus.UNAVAILABLE
        return

    assert result.backend_status is EquityBackendStatus(expected["expected_backend_status"])


@pytest.mark.parametrize(
    "case_id",
    (
        "flop_equity_input_srp_heads_up",
        "flop_equity_input_3bet_pot",
        "flop_equity_input_4bet_low_spr",
        "flop_equity_input_limp_passive",
    ),
)
def test_heads_up_equity_input_fixtures_return_numeric_raw_equity(case_id: str) -> None:
    if not is_pokerkit_available():
        return

    expected = _load_expected(case_id)
    result = run_equity_engine(_build_scenario_from_fixture(case_id), sample_count=NUMERIC_SAMPLE_COUNT)

    assert expected["expected_result_kind"] == "numeric_heads_up_raw_equity"
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
    assert result.backend_metadata["numeric_result_integrated"] is True
    assert result.backend_metadata["backend_sample_count_used"] == result.sample_count_used
    assert result.backend_metadata["adapter_version"] == "v0.11.6"
    assert result.backend_metadata["exact_enumeration"] is False
    assert _equity_band(result.hero_equity) == expected["expected_equity_band"]
    assert result.player_equities[0].player_id == "hero"
    assert result.player_equities[0].equity == result.hero_equity


def test_multiway_equity_input_fixture_remains_structured_deferred() -> None:
    if not is_pokerkit_available():
        return

    case_id = "flop_equity_input_multiway"
    expected = _load_expected(case_id)
    result = run_equity_engine(_build_scenario_from_fixture(case_id), sample_count=NUMERIC_SAMPLE_COUNT)

    assert expected["expected_result_kind"] == "multiway_deferred"
    assert result.backend_status is EquityBackendStatus.NOT_RUN
    assert result.computation_mode is EquityComputationMode.MULTIWAY_RAW_EQUITY
    assert result.hero_equity is None
    assert result.sample_count_used is None
    assert result.backend_metadata["numeric_result_integrated"] is False
    assert result.backend_metadata["opponents_count"] == 2
    assert expected["expected_equity_band"] == "deferred"


def test_unknown_context_equity_input_fixture_remains_structured_unknown() -> None:
    if not is_pokerkit_available():
        return

    case_id = "flop_equity_input_unknown_context"
    expected = _load_expected(case_id)
    result = run_equity_engine(_build_scenario_from_fixture(case_id), sample_count=NUMERIC_SAMPLE_COUNT)

    assert expected["expected_result_kind"] == "unknown_context"
    assert result.backend_status is EquityBackendStatus.NOT_RUN
    assert result.computation_mode is EquityComputationMode.UNKNOWN_CONTEXT_EQUITY
    assert result.hero_equity is None
    assert result.sample_count_used is None
    assert result.backend_metadata["numeric_result_integrated"] is False
    assert result.backend_metadata["opponents_count"] is None
    assert expected["expected_equity_band"] == "unknown"
