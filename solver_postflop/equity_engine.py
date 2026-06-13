"""Raw postflop equity engine wrapper.

V0.11.4 scope: convert EquityScenarioInput into a structured EquityResult
by selecting the raw computation mode and delegating backend metadata to the
PokerKit adapter. This module does not implement card enumeration, sampling,
range logic, poker decisions, runtime planning, or clicks.
"""

from __future__ import annotations

import time
from typing import Callable, Optional

from solver_postflop.equity_backend_pokerkit import run_pokerkit_backend
from solver_postflop.equity_contracts import (
    DEFAULT_EQUITY_BACKEND_NAME,
    EquityBackendResult,
    EquityBackendStatus,
    EquityComputationMode,
    EquityConfidenceClass,
    EquityResult,
)
from solver_postflop.equity_input_contracts import EquityRunMode, EquityScenarioInput

EQUITY_ENGINE_VERSION = "v0.11.4"
EQUITY_ENGINE_DEFAULT_BACKEND = DEFAULT_EQUITY_BACKEND_NAME
EQUITY_ENGINE_WRAPPER_NOTE = "equity_engine_wrapper_v0114"
RAW_NUMERIC_BACKEND_DEFERRED_NOTE = "raw_numeric_backend_result_deferred"

BackendRunner = Callable[[EquityScenarioInput], EquityBackendResult]


def run_equity_engine(
    scenario_input: EquityScenarioInput,
    *,
    backend_runner: Optional[Callable[..., EquityBackendResult]] = None,
    sample_count: Optional[int] = None,
) -> EquityResult:
    """Run the raw equity wrapper and return a JSON-safe EquityResult.

    The selected computation mode is derived only from the prepared
    EquityScenarioInput. Backend availability/errors are represented as data,
    not as pipeline-breaking exceptions.
    """
    started = time.perf_counter()
    selected_mode = select_equity_computation_mode(scenario_input)
    runner = backend_runner or run_pokerkit_backend

    try:
        backend_result = runner(scenario_input, sample_count=sample_count)
    except TypeError:
        backend_result = runner(scenario_input)
    except Exception as exc:  # pragma: no cover - intentionally defensive wrapper
        backend_result = EquityBackendResult(
            backend_name=EQUITY_ENGINE_DEFAULT_BACKEND,
            backend_status=EquityBackendStatus.ERROR,
            computation_mode=EquityComputationMode.BACKEND_ERROR,
            runtime_ms=_elapsed_ms(started),
            backend_metadata={
                "engine_version": EQUITY_ENGINE_VERSION,
                "selected_computation_mode": selected_mode.value,
            },
            error_message=f"{type(exc).__name__}: {exc}",
            notes=("backend_runner_exception",),
        )

    return build_equity_result_from_backend(
        scenario_input=scenario_input,
        backend_result=backend_result,
        selected_mode=selected_mode,
        engine_runtime_ms=_elapsed_ms(started),
    )


def select_equity_computation_mode(
    scenario_input: EquityScenarioInput,
) -> EquityComputationMode:
    """Map EquityRunMode to the raw equity computation-mode contract."""
    run_mode = scenario_input.equity_run_mode
    if run_mode == EquityRunMode.HEADS_UP_EXACT_OR_SAMPLED:
        return EquityComputationMode.HEADS_UP_RAW_EQUITY
    if run_mode == EquityRunMode.MULTIWAY_SAMPLED:
        return EquityComputationMode.MULTIWAY_RAW_EQUITY
    return EquityComputationMode.UNKNOWN_CONTEXT_EQUITY


def build_equity_result_from_backend(
    *,
    scenario_input: EquityScenarioInput,
    backend_result: EquityBackendResult,
    selected_mode: EquityComputationMode,
    engine_runtime_ms: Optional[float] = None,
) -> EquityResult:
    """Shape backend metadata into the public EquityResult contract."""
    final_mode = _resolve_final_mode(
        backend_result=backend_result,
        selected_mode=selected_mode,
    )
    notes = _merge_notes(
        (EQUITY_ENGINE_WRAPPER_NOTE,),
        backend_result.notes,
        _mode_notes(scenario_input=scenario_input, backend_result=backend_result),
    )

    runtime_ms = backend_result.runtime_ms
    if runtime_ms is None:
        runtime_ms = engine_runtime_ms

    backend_metadata = dict(backend_result.backend_metadata)
    backend_metadata.update(
        {
            "engine_version": EQUITY_ENGINE_VERSION,
            "selected_computation_mode": selected_mode.value,
            "scenario_equity_run_mode": _enum_value(scenario_input.equity_run_mode),
        }
    )

    return EquityResult(
        case_id=scenario_input.case_id,
        source_file=scenario_input.source_file,
        hero_equity=backend_result.hero_equity,
        hero_win_rate=backend_result.hero_win_rate,
        hero_tie_rate=backend_result.hero_tie_rate,
        player_equities=tuple(backend_result.player_results),
        opponents_count=scenario_input.opponents.opponents_count,
        computation_mode=final_mode,
        backend_name=backend_result.backend_name or EQUITY_ENGINE_DEFAULT_BACKEND,
        backend_status=backend_result.backend_status,
        sample_count_used=backend_result.sample_count_used,
        equity_confidence=_derive_confidence(backend_result),
        input_features_used=tuple(scenario_input.fields_used),
        runtime_ms=runtime_ms,
        backend_metadata=backend_metadata,
        notes=notes,
    )


def _resolve_final_mode(
    *,
    backend_result: EquityBackendResult,
    selected_mode: EquityComputationMode,
) -> EquityComputationMode:
    if backend_result.backend_status == EquityBackendStatus.UNAVAILABLE:
        return EquityComputationMode.BACKEND_UNAVAILABLE
    if backend_result.backend_status == EquityBackendStatus.ERROR:
        return EquityComputationMode.BACKEND_ERROR
    if backend_result.computation_mode in {
        EquityComputationMode.BACKEND_UNAVAILABLE,
        EquityComputationMode.BACKEND_ERROR,
    }:
        return backend_result.computation_mode
    return selected_mode


def _derive_confidence(backend_result: EquityBackendResult) -> EquityConfidenceClass:
    if backend_result.backend_status != EquityBackendStatus.OK:
        return EquityConfidenceClass.UNKNOWN
    if backend_result.hero_equity is None:
        return EquityConfidenceClass.UNKNOWN
    if backend_result.sample_count_used is not None and backend_result.sample_count_used < 1000:
        return EquityConfidenceClass.LOW
    return EquityConfidenceClass.MEDIUM


def _mode_notes(
    *,
    scenario_input: EquityScenarioInput,
    backend_result: EquityBackendResult,
) -> tuple[str, ...]:
    notes: list[str] = []
    if backend_result.hero_equity is None:
        notes.append(RAW_NUMERIC_BACKEND_DEFERRED_NOTE)
    if scenario_input.equity_run_mode == EquityRunMode.UNKNOWN_CONTEXT_MODE:
        notes.append("unknown_context_equity_result")
    if scenario_input.equity_run_mode == EquityRunMode.RANGE_BASED_LATER:
        notes.append("range_based_input_deferred_to_future_module")
    return tuple(notes)


def _merge_notes(*groups: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    output: list[str] = []
    for group in groups:
        for item in group:
            if item not in seen:
                seen.add(item)
                output.append(item)
    return tuple(output)


def _elapsed_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000.0, 6)


def _enum_value(value: object) -> object:
    return getattr(value, "value", value)


__all__ = (
    "EQUITY_ENGINE_DEFAULT_BACKEND",
    "EQUITY_ENGINE_VERSION",
    "EQUITY_ENGINE_WRAPPER_NOTE",
    "RAW_NUMERIC_BACKEND_DEFERRED_NOTE",
    "build_equity_result_from_backend",
    "run_equity_engine",
    "select_equity_computation_mode",
)
