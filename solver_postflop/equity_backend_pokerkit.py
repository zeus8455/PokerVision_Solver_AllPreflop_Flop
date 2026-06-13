"""PokerKit backend adapter skeleton for raw postflop equity.

V0.11.2 scope: backend availability and structured backend results only.
This module intentionally avoids importing PokerKit at module import time, so
postflop tests can run on machines where PokerKit is not installed yet.

Real PokerKit calculation is deferred to a later V0.11 subversion.
"""

from __future__ import annotations

import importlib.util
import time
from typing import Any, Optional

from solver_postflop.equity_contracts import (
    DEFAULT_EQUITY_BACKEND_NAME,
    EquityBackendResult,
    EquityBackendStatus,
    EquityComputationMode,
)

POKERKIT_BACKEND_ADAPTER_VERSION = "v0.11.2"
POKERKIT_PACKAGE_NAME = "pokerkit"
POKERKIT_NOT_INSTALLED_NOTE = "pokerkit_not_installed"
POKERKIT_CALCULATION_DEFERRED_NOTE = "pokerkit_backend_calculation_deferred_v0112"


def is_pokerkit_available() -> bool:
    """Return True when the local Python environment can import PokerKit.

    The function uses importlib metadata discovery instead of a direct import.
    This keeps module import safe in environments where PokerKit is absent.
    """
    return importlib.util.find_spec(POKERKIT_PACKAGE_NAME) is not None


def build_backend_unavailable_result(
    *,
    reason: str = POKERKIT_NOT_INSTALLED_NOTE,
    runtime_ms: Optional[float] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> EquityBackendResult:
    """Build a structured backend-unavailable result without raising."""
    backend_metadata = {
        "adapter_version": POKERKIT_BACKEND_ADAPTER_VERSION,
        "backend_available": False,
        "requires_local_install": True,
    }
    if metadata:
        backend_metadata.update(metadata)

    return EquityBackendResult(
        backend_name=DEFAULT_EQUITY_BACKEND_NAME,
        backend_status=EquityBackendStatus.UNAVAILABLE,
        computation_mode=EquityComputationMode.BACKEND_UNAVAILABLE,
        hero_equity=None,
        hero_win_rate=None,
        hero_tie_rate=None,
        player_results=(),
        sample_count_used=None,
        runtime_ms=runtime_ms,
        backend_metadata=backend_metadata,
        error_message=reason,
        notes=(reason,),
    )


def build_backend_error_result(
    *,
    error_message: str,
    runtime_ms: Optional[float] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> EquityBackendResult:
    """Build a structured backend-error result without breaking the pipeline."""
    backend_metadata = {
        "adapter_version": POKERKIT_BACKEND_ADAPTER_VERSION,
        "backend_available": is_pokerkit_available(),
    }
    if metadata:
        backend_metadata.update(metadata)

    return EquityBackendResult(
        backend_name=DEFAULT_EQUITY_BACKEND_NAME,
        backend_status=EquityBackendStatus.ERROR,
        computation_mode=EquityComputationMode.BACKEND_ERROR,
        hero_equity=None,
        hero_win_rate=None,
        hero_tie_rate=None,
        player_results=(),
        sample_count_used=None,
        runtime_ms=runtime_ms,
        backend_metadata=backend_metadata,
        error_message=error_message,
        notes=("pokerkit_backend_error",),
    )


def run_pokerkit_backend(
    scenario_input: Any,
    *,
    sample_count: Optional[int] = None,
) -> EquityBackendResult:
    """Run the PokerKit backend skeleton and return structured metadata.

    V0.11.2 does not compute equity. It only confirms whether the local
    PokerKit package is available and returns a safe structured backend result.
    """
    started = time.perf_counter()

    if not is_pokerkit_available():
        return build_backend_unavailable_result(
            runtime_ms=_elapsed_ms(started),
            metadata={
                "sample_count_requested": sample_count,
                "scenario_case_id": _get_attr(scenario_input, "case_id"),
            },
        )

    return EquityBackendResult(
        backend_name=DEFAULT_EQUITY_BACKEND_NAME,
        backend_status=EquityBackendStatus.NOT_RUN,
        computation_mode=EquityComputationMode.UNKNOWN_CONTEXT_EQUITY,
        hero_equity=None,
        hero_win_rate=None,
        hero_tie_rate=None,
        player_results=(),
        sample_count_used=None,
        runtime_ms=_elapsed_ms(started),
        backend_metadata={
            "adapter_version": POKERKIT_BACKEND_ADAPTER_VERSION,
            "backend_available": True,
            "sample_count_requested": sample_count,
            "scenario_case_id": _get_attr(scenario_input, "case_id"),
        },
        error_message=None,
        notes=(POKERKIT_CALCULATION_DEFERRED_NOTE,),
    )


def _elapsed_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000.0, 6)


def _get_attr(value: Any, name: str) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name, None)


__all__ = (
    "POKERKIT_BACKEND_ADAPTER_VERSION",
    "POKERKIT_CALCULATION_DEFERRED_NOTE",
    "POKERKIT_NOT_INSTALLED_NOTE",
    "POKERKIT_PACKAGE_NAME",
    "build_backend_error_result",
    "build_backend_unavailable_result",
    "is_pokerkit_available",
    "run_pokerkit_backend",
)
