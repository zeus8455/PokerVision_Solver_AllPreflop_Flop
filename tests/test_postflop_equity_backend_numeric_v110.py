from __future__ import annotations

import ast
import json
from pathlib import Path

from solver_postflop.equity_backend_pokerkit import (
    POKERKIT_INPUT_NOT_READY_NOTE,
    POKERKIT_MULTIWAY_DEFERRED_NOTE,
    POKERKIT_NUMERIC_HEADS_UP_NOTE,
    is_pokerkit_available,
    run_pokerkit_backend,
)
from solver_postflop.equity_contracts import (
    EquityBackendStatus,
    EquityComputationMode,
)
from solver_postflop.equity_input_contracts import (
    EquityBoardInput,
    EquityHeroInput,
    EquityOpponentModelInput,
    EquityRunMode,
    EquityScenarioInput,
)

BACKEND_SOURCE = Path("solver_postflop/equity_backend_pokerkit.py")


def _heads_up_scenario(
    *,
    board_cards: tuple[str, ...] = (
        "Q_diamonds",
        "J_clubs",
        "10_spades",
        "2_clubs",
        "3_diamonds",
    ),
) -> EquityScenarioInput:
    return EquityScenarioInput(
        case_id="numeric_heads_up_case_v0116",
        source_file="synthetic://numeric_heads_up_case_v0116.clear.json",
        hero=EquityHeroInput(
            hero_cards=("A_spades", "K_hearts"),
            position="BTN",
            effective_stack=80.0,
        ),
        board=EquityBoardInput(board_cards=board_cards, street="river"),
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
        equity_run_mode=EquityRunMode.HEADS_UP_EXACT_OR_SAMPLED,
        fields_used=("hero.hero_cards", "board.board_cards", "opponents.opponents_count"),
    )


def _multiway_scenario() -> EquityScenarioInput:
    scenario = _heads_up_scenario()
    return EquityScenarioInput(
        case_id="numeric_multiway_deferred_case_v0116",
        source_file=scenario.source_file,
        hero=scenario.hero,
        board=scenario.board,
        opponents=EquityOpponentModelInput(
            opponents_count=2,
            is_heads_up=False,
            is_multiway=True,
            opponent_positions=("BB", "SB"),
        ),
        spot_family=scenario.spot_family,
        pot=scenario.pot,
        to_call=scenario.to_call,
        effective_stack=scenario.effective_stack,
        spr=scenario.spr,
        equity_run_mode=EquityRunMode.MULTIWAY_SAMPLED,
        fields_used=scenario.fields_used,
    )


def _unknown_context_scenario() -> EquityScenarioInput:
    return EquityScenarioInput(
        case_id="numeric_unknown_context_case_v0116",
        source_file="synthetic://numeric_unknown_context_case_v0116.clear.json",
        hero=EquityHeroInput(hero_cards=(), position="BTN"),
        board=EquityBoardInput(board_cards=("Q_diamonds", "J_clubs", "10_spades"), street="flop"),
        opponents=EquityOpponentModelInput(opponents_count=None),
        equity_run_mode=EquityRunMode.UNKNOWN_CONTEXT_MODE,
    )


def test_numeric_backend_returns_structured_result_without_pokerkit_requirement() -> None:
    result = run_pokerkit_backend(_heads_up_scenario(), sample_count=64)
    payload = result.to_json_dict()

    assert payload["backend_name"] == "pokerkit"
    assert payload["backend_status"] in {"ok", "unavailable", "error"}
    assert payload["computation_mode"] in {
        "heads_up_raw_equity",
        "backend_unavailable",
        "backend_error",
    }
    json.dumps(payload, sort_keys=True)


def test_numeric_backend_heads_up_result_when_pokerkit_available() -> None:
    if not is_pokerkit_available():
        return

    result = run_pokerkit_backend(_heads_up_scenario(), sample_count=128)

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
    assert result.backend_metadata["adapter_version"] == "v0.11.6"
    assert result.backend_metadata["hero_compact"] == "AsKh"
    assert result.backend_metadata["board_compact"] == "QdJcTs2c3d"
    assert result.player_results[0].player_id == "hero"
    assert POKERKIT_NUMERIC_HEADS_UP_NOTE in result.notes


def test_numeric_backend_supports_flop_board_with_limited_sample_when_available() -> None:
    if not is_pokerkit_available():
        return

    scenario = _heads_up_scenario(board_cards=("Q_diamonds", "J_clubs", "10_spades"))
    result = run_pokerkit_backend(scenario, sample_count=32)

    assert result.backend_status is EquityBackendStatus.OK
    assert result.sample_count_used is not None
    assert result.sample_count_used <= 32
    assert result.backend_metadata["missing_board_cards"] == 2
    assert result.backend_metadata["exact_enumeration"] is False
    assert result.hero_equity is not None


def test_numeric_backend_multiway_is_deferred_without_crash() -> None:
    result = run_pokerkit_backend(_multiway_scenario(), sample_count=64)

    if result.backend_status is EquityBackendStatus.UNAVAILABLE:
        return

    assert result.backend_status is EquityBackendStatus.NOT_RUN
    assert result.computation_mode is EquityComputationMode.MULTIWAY_RAW_EQUITY
    assert result.hero_equity is None
    assert POKERKIT_MULTIWAY_DEFERRED_NOTE in result.notes
    assert result.backend_metadata["opponents_count"] == 2


def test_numeric_backend_unknown_context_is_not_pipeline_breaking() -> None:
    result = run_pokerkit_backend(_unknown_context_scenario(), sample_count=64)

    if result.backend_status is EquityBackendStatus.UNAVAILABLE:
        return

    assert result.backend_status is EquityBackendStatus.NOT_RUN
    assert result.computation_mode is EquityComputationMode.UNKNOWN_CONTEXT_EQUITY
    assert result.hero_equity is None
    assert POKERKIT_INPUT_NOT_READY_NOTE in result.notes
    assert result.backend_metadata["opponents_count"] is None


def test_numeric_backend_source_has_no_strategy_runtime_or_live_source_logic() -> None:
    source = BACKEND_SOURCE.read_text(encoding="utf-8").lower()
    forbidden_terms = [
        "build_range(",
        "narrow_range(",
        "blocker_filter(",
        "decision_engine(",
        "runtime_plan(",
        "click(",
        "mouse",
        "clear_json_pending",
        "dark_json",
        "current_cycle",
        "solver_preflop",
        "display_analysis_cycle",
    ]

    for forbidden in forbidden_terms:
        assert forbidden not in source


def test_numeric_backend_imports_do_not_pull_live_or_preflop_modules() -> None:
    tree = ast.parse(BACKEND_SOURCE.read_text(encoding="utf-8"))
    imported_roots: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert "solver_preflop" not in imported_roots
    assert "display_analysis_cycle" not in imported_roots
    assert "Action_Button" not in imported_roots
