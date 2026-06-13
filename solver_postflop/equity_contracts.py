"""Contracts for the postflop raw equity result layer.

V0.11.1 scope: result metadata only. This module defines the JSON-safe
objects that a later backend/engine will return after consuming
EquityScenarioInput. It does not import or execute any backend package.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any, Mapping, Optional


class EquityComputationMode(str, Enum):
    """Mode selected by the future equity engine for raw equity snapshots."""

    HEADS_UP_RAW_EQUITY = "heads_up_raw_equity"
    MULTIWAY_RAW_EQUITY = "multiway_raw_equity"
    UNKNOWN_CONTEXT_EQUITY = "unknown_context_equity"
    BACKEND_UNAVAILABLE = "backend_unavailable"
    BACKEND_ERROR = "backend_error"


class EquityConfidenceClass(str, Enum):
    """Confidence bucket for a raw equity snapshot."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class EquityBackendStatus(str, Enum):
    """Backend execution status carried as structured metadata."""

    OK = "ok"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    NOT_RUN = "not_run"


@dataclass(frozen=True, slots=True)
class EquityPlayerResult:
    """Per-player raw equity result metadata."""

    player_id: str
    position: Optional[str] = None
    role: Optional[str] = None
    equity: Optional[float] = None
    win_rate: Optional[float] = None
    tie_rate: Optional[float] = None
    confidence: EquityConfidenceClass = EquityConfidenceClass.UNKNOWN
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation of the player result."""
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class EquityBackendResult:
    """Structured backend output before final EquityResult shaping."""

    backend_name: str = "pokerkit"
    backend_status: EquityBackendStatus = EquityBackendStatus.NOT_RUN
    computation_mode: EquityComputationMode = EquityComputationMode.UNKNOWN_CONTEXT_EQUITY
    hero_equity: Optional[float] = None
    hero_win_rate: Optional[float] = None
    hero_tie_rate: Optional[float] = None
    player_results: tuple[EquityPlayerResult, ...] = field(default_factory=tuple)
    sample_count_used: Optional[int] = None
    runtime_ms: Optional[float] = None
    backend_metadata: Mapping[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation of backend output."""
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class EquityResult:
    """Final raw equity snapshot returned by the future equity engine."""

    case_id: Optional[str]
    source_file: str
    hero_equity: Optional[float] = None
    hero_win_rate: Optional[float] = None
    hero_tie_rate: Optional[float] = None
    player_equities: tuple[EquityPlayerResult, ...] = field(default_factory=tuple)
    opponents_count: Optional[int] = None
    computation_mode: EquityComputationMode = EquityComputationMode.UNKNOWN_CONTEXT_EQUITY
    backend_name: str = "pokerkit"
    backend_status: EquityBackendStatus = EquityBackendStatus.NOT_RUN
    sample_count_used: Optional[int] = None
    equity_confidence: EquityConfidenceClass = EquityConfidenceClass.UNKNOWN
    input_features_used: tuple[str, ...] = field(default_factory=tuple)
    runtime_ms: Optional[float] = None
    backend_metadata: Mapping[str, Any] = field(default_factory=dict)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation of the equity result."""
        return _json_safe(asdict(self))


EQUITY_CONTRACT_VERSION = "v0.11.1"
DEFAULT_EQUITY_BACKEND_NAME = "pokerkit"
EQUITY_COMPUTATION_MODES: tuple[EquityComputationMode, ...] = tuple(EquityComputationMode)
EQUITY_CONFIDENCE_CLASSES: tuple[EquityConfidenceClass, ...] = tuple(EquityConfidenceClass)
EQUITY_BACKEND_STATUSES: tuple[EquityBackendStatus, ...] = tuple(EquityBackendStatus)


__all__ = (
    "DEFAULT_EQUITY_BACKEND_NAME",
    "EQUITY_BACKEND_STATUSES",
    "EQUITY_COMPUTATION_MODES",
    "EQUITY_CONFIDENCE_CLASSES",
    "EQUITY_CONTRACT_VERSION",
    "EquityBackendResult",
    "EquityBackendStatus",
    "EquityComputationMode",
    "EquityConfidenceClass",
    "EquityPlayerResult",
    "EquityResult",
)


def _json_safe(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value
