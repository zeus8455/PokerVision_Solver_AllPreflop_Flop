from __future__ import annotations

import ast
from pathlib import Path

from solver_postflop.equity_contracts import (
    EquityBackendResult,
    EquityBackendStatus,
    EquityComputationMode,
    EquityConfidenceClass,
    EquityPlayerResult,
)
from solver_postflop.equity_engine import (
    EQUITY_ENGINE_WRAPPER_NOTE,
    RAW_NUMERIC_BACKEND_DEFERRED_NOTE,
    build_equity_result_from_backend,
    run_equity_engine,
    select_equity_computation_mode,
)
from solver_postflop.equity_input_contracts import (
    EquityBoardInput,
    EquityHeroInput,
    EquityOpponentModelInput,
    EquityRunMode,
    EquityScenarioInput,
)

ENGINE_SOURCE = Path("solver_postflop/equity_engine.py")


def _scenario(
    *,
    run_mode: EquityRunMode = EquityRunMode.HEADS_UP_EXACT_OR_SAMPLED,
    opponents_count: int | None = 1,
) -> EquityScenarioInput:
    return EquityScenarioInput(
        case_id="engine_case_001",
        source_file="tests/fixtures/postflop_equity_input_v0103/synthetic/flop_equity_input_srp_heads_up.clear.json",
        hero=EquityHeroInput(hero_cards=("Ah", "Kd"), position="BTN", effective_stack=80.0),
        board=EquityBoardInput(board_cards=("As", "7d", "2c"), street="flop"),
        opponents=EquityOpponentModelInput(
            opponents_count=opponents_count,
            is_heads_up=opponents_count == 1 if opponents_count is not None else None,
            is_multiway=opponents_count > 1 if opponents_count is not None else None,
            opponent_positions=("BB",) if opponents_count == 1 else ("BB", "SB"),
        ),
        spot_family="srp_heads_up",
        pot=6.5,
        to_call=2.0,
        effective_stack=80.0,
        spr=12.3,
        equity_run_mode=run_mode,
        fields_used=("flop_context.hero_cards", "flop_context.board_cards"),
    )


def _ok_backend(*args, **kwargs) -> EquityBackendResult:
    player = EquityPlayerResult(
        player_id="hero",
        position="BTN",
        equity=0.64,
        win_rate=0.61,
        tie_rate=0.03,
    )
    return EquityBackendResult(
        backend_status=EquityBackendStatus.OK,
        computation_mode=EquityComputationMode.HEADS_UP_RAW_EQUITY,
        hero_equity=0.64,
        hero_win_rate=0.61,
        hero_tie_rate=0.03,
        player_results=(player,),
        sample_count_used=5000,
        runtime_ms=1.25,
        backend_metadata={"fake_backend": True},
        notes=("fake_backend_ok",),
    )


def _not_run_backend(*args, **kwargs) -> EquityBackendResult:
    return EquityBackendResult(
        backend_status=EquityBackendStatus.NOT_RUN,
        computation_mode=EquityComputationMode.UNKNOWN_CONTEXT_EQUITY,
        runtime_ms=0.5,
        backend_metadata={"fake_backend": True},
        notes=("backend_deferred",),
    )


def _unavailable_backend(*args, **kwargs) -> EquityBackendResult:
    return EquityBackendResult(
        backend_status=EquityBackendStatus.UNAVAILABLE,
        computation_mode=EquityComputationMode.BACKEND_UNAVAILABLE,
        runtime_ms=0.4,
        error_message="pokerkit_not_installed",
        notes=("pokerkit_not_installed",),
    )


def _error_backend(*args, **kwargs) -> EquityBackendResult:
    return EquityBackendResult(
        backend_status=EquityBackendStatus.ERROR,
        computation_mode=EquityComputationMode.BACKEND_ERROR,
        runtime_ms=0.7,
        error_message="backend_error_fixture",
        notes=("backend_error_fixture",),
    )


def test_select_equity_computation_mode_maps_heads_up_and_multiway() -> None:
    assert (
        select_equity_computation_mode(_scenario())
        == EquityComputationMode.HEADS_UP_RAW_EQUITY
    )
    assert (
        select_equity_computation_mode(
            _scenario(run_mode=EquityRunMode.MULTIWAY_SAMPLED, opponents_count=2)
        )
        == EquityComputationMode.MULTIWAY_RAW_EQUITY
    )


def test_select_equity_computation_mode_maps_unknown_context() -> None:
    scenario = _scenario(
        run_mode=EquityRunMode.UNKNOWN_CONTEXT_MODE,
        opponents_count=None,
    )

    assert select_equity_computation_mode(scenario) == EquityComputationMode.UNKNOWN_CONTEXT_EQUITY


def test_run_equity_engine_shapes_ok_backend_result() -> None:
    result = run_equity_engine(_scenario(), backend_runner=_ok_backend, sample_count=5000)

    assert result.case_id == "engine_case_001"
    assert result.computation_mode == EquityComputationMode.HEADS_UP_RAW_EQUITY
    assert result.backend_status == EquityBackendStatus.OK
    assert result.hero_equity == 0.64
    assert result.hero_win_rate == 0.61
    assert result.hero_tie_rate == 0.03
    assert result.sample_count_used == 5000
    assert result.equity_confidence == EquityConfidenceClass.MEDIUM
    assert result.player_equities[0].player_id == "hero"
    assert result.input_features_used == (
        "flop_context.hero_cards",
        "flop_context.board_cards",
    )
    assert result.backend_metadata["engine_version"] == "v0.11.4"


def test_run_equity_engine_preserves_multiway_selected_mode_when_backend_deferred() -> None:
    scenario = _scenario(run_mode=EquityRunMode.MULTIWAY_SAMPLED, opponents_count=2)

    result = run_equity_engine(scenario, backend_runner=_not_run_backend)

    assert result.computation_mode == EquityComputationMode.MULTIWAY_RAW_EQUITY
    assert result.backend_status == EquityBackendStatus.NOT_RUN
    assert result.hero_equity is None
    assert result.opponents_count == 2
    assert RAW_NUMERIC_BACKEND_DEFERRED_NOTE in result.notes


def test_run_equity_engine_handles_backend_unavailable_as_structured_result() -> None:
    result = run_equity_engine(_scenario(), backend_runner=_unavailable_backend)

    assert result.computation_mode == EquityComputationMode.BACKEND_UNAVAILABLE
    assert result.backend_status == EquityBackendStatus.UNAVAILABLE
    assert result.hero_equity is None
    assert result.equity_confidence == EquityConfidenceClass.UNKNOWN
    assert "pokerkit_not_installed" in result.notes


def test_run_equity_engine_handles_backend_error_as_structured_result() -> None:
    result = run_equity_engine(_scenario(), backend_runner=_error_backend)

    assert result.computation_mode == EquityComputationMode.BACKEND_ERROR
    assert result.backend_status == EquityBackendStatus.ERROR
    assert result.hero_equity is None
    assert result.equity_confidence == EquityConfidenceClass.UNKNOWN
    assert "backend_error_fixture" in result.notes


def test_build_equity_result_from_backend_serializes_to_json() -> None:
    scenario = _scenario()
    backend = _ok_backend(scenario)
    result = build_equity_result_from_backend(
        scenario_input=scenario,
        backend_result=backend,
        selected_mode=EquityComputationMode.HEADS_UP_RAW_EQUITY,
        engine_runtime_ms=2.0,
    )

    payload = result.to_json_dict()

    assert payload["computation_mode"] == "heads_up_raw_equity"
    assert payload["backend_status"] == "ok"
    assert payload["hero_equity"] == 0.64
    assert payload["player_equities"][0]["player_id"] == "hero"
    assert EQUITY_ENGINE_WRAPPER_NOTE in payload["notes"]


def test_run_equity_engine_default_backend_returns_structured_result() -> None:
    result = run_equity_engine(_scenario())
    payload = result.to_json_dict()

    assert payload["backend_name"] == "pokerkit"
    assert payload["backend_status"] in {"not_run", "unavailable", "error", "ok"}
    assert payload["computation_mode"] in {
        "heads_up_raw_equity",
        "backend_unavailable",
        "backend_error",
    }
    assert payload["backend_metadata"]["engine_version"] == "v0.11.4"


def test_equity_engine_source_has_no_forbidden_runtime_or_strategy_logic() -> None:
    source = ENGINE_SOURCE.read_text(encoding="utf-8").lower()
    forbidden_terms = [
        "monte_carlo(",
        "run_simulation(",
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
    ]

    for forbidden in forbidden_terms:
        assert forbidden not in source


def test_equity_engine_imports_do_not_pull_live_or_preflop_modules() -> None:
    tree = ast.parse(ENGINE_SOURCE.read_text(encoding="utf-8"))
    imported_roots: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert "solver_preflop" not in imported_roots
    assert "display_analysis_cycle" not in imported_roots
    assert "Action_Button" not in imported_roots
