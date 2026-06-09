"""Postflop source contracts.

V0.3.x contract layer for PokerVision_Solver_AllPreflop_Flop.

This module intentionally contains data contracts only:
- no file discovery;
- no JSON folder scanning;
- no real JSON normalization;
- no poker decisions;
- no runtime/click-chain changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class ContractValidationError(ValueError):
    """Raised when a contract receives invalid input."""


class _StringEnum(str, Enum):
    """Enum helper with stable string conversion."""

    @classmethod
    def values(cls) -> list[str]:
        return [item.value for item in cls]

    @classmethod
    def from_value(cls, value: str | "_StringEnum") -> "_StringEnum":
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value))
        except ValueError as exc:
            allowed = ", ".join(cls.values())
            raise ContractValidationError(
                f"Unsupported {cls.__name__}: {value!r}. Allowed values: {allowed}"
            ) from exc

    def __str__(self) -> str:
        return self.value


class PostflopSourceType(_StringEnum):
    """Allowed source JSON types used by V0.2 fixture lab and V0.3 contracts."""

    DARK_JSON = "dark_json"
    PENDING_JSON = "pending_json"
    SERVICE_JSON = "service_json"
    CURRENT_CYCLE_JSON = "current_cycle_json"
    RUNTIME_JSON = "runtime_json"
    SOLVER_PAYLOAD_JSON = "solver_payload_json"
    FINAL_CLEAR_JSON = "final_clear_json"
    MANUAL_LIVE_LIKE_JSON = "manual_live_like_json"
    UNKNOWN = "unknown"

    @property
    def is_manual_live_like(self) -> bool:
        return self is PostflopSourceType.MANUAL_LIVE_LIKE_JSON

    @property
    def can_be_real_project_source(self) -> bool:
        return self not in {
            PostflopSourceType.MANUAL_LIVE_LIKE_JSON,
            PostflopSourceType.UNKNOWN,
        }

    @property
    def is_final_clear_json(self) -> bool:
        return self is PostflopSourceType.FINAL_CLEAR_JSON

    @property
    def requires_click_cycle_by_type(self) -> bool:
        return self is PostflopSourceType.FINAL_CLEAR_JSON


class ContractSeverity(_StringEnum):
    """Common structured severity for warnings/errors."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class PostflopConfidence(_StringEnum):
    """Confidence of source-candidate classification."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class RawSourceLoadStatus(_StringEnum):
    """Status for a raw source payload after a future loader reads it."""

    LOADED = "loaded"
    INVALID_JSON = "invalid_json"
    MISSING_FILE = "missing_file"
    UNREADABLE = "unreadable"
    EMPTY = "empty"


class DiscoveryStatus(_StringEnum):
    """Status for a future source-discovery result."""

    OK = "ok"
    PARTIAL = "partial"
    FAILED = "failed"
    EMPTY = "empty"


def _require_non_empty_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractValidationError(f"{field_name} must be a non-empty string.")
    return value.strip()


def _coerce_context(context: Mapping[str, Any] | None) -> dict[str, Any]:
    if context is None:
        return {}
    if not isinstance(context, Mapping):
        raise ContractValidationError("context must be a mapping/dict.")
    return dict(context)


def _serialize_warnings(warnings: list["ModuleWarning"]) -> list[dict[str, Any]]:
    return [warning.to_dict() for warning in warnings]


def _serialize_errors(errors: list["ModuleError"]) -> list[dict[str, Any]]:
    return [error.to_dict() for error in errors]


@dataclass(frozen=True)
class ModuleWarning:
    """Structured non-fatal contract/module warning."""

    code: str
    message: str
    severity: ContractSeverity | str = ContractSeverity.WARNING
    source_file: str | None = None
    field_name: str | None = None
    context: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", _require_non_empty_text(self.code, "code"))
        object.__setattr__(self, "message", _require_non_empty_text(self.message, "message"))
        severity = ContractSeverity.from_value(self.severity)
        if severity is ContractSeverity.ERROR:
            raise ContractValidationError("ModuleWarning severity cannot be 'error'.")
        object.__setattr__(self, "severity", severity)
        object.__setattr__(self, "context", _coerce_context(self.context))
        if self.source_file is not None:
            object.__setattr__(
                self, "source_file", _require_non_empty_text(self.source_file, "source_file")
            )
        if self.field_name is not None:
            object.__setattr__(
                self, "field_name", _require_non_empty_text(self.field_name, "field_name")
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "source_file": self.source_file,
            "field_name": self.field_name,
            "context": dict(self.context),
        }


@dataclass(frozen=True)
class ModuleError:
    """Structured fatal/non-recoverable contract/module error."""

    code: str
    message: str
    severity: ContractSeverity | str = ContractSeverity.ERROR
    source_file: str | None = None
    field_name: str | None = None
    context: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", _require_non_empty_text(self.code, "code"))
        object.__setattr__(self, "message", _require_non_empty_text(self.message, "message"))
        severity = ContractSeverity.from_value(self.severity)
        if severity is not ContractSeverity.ERROR:
            raise ContractValidationError("ModuleError severity must be 'error'.")
        object.__setattr__(self, "severity", severity)
        object.__setattr__(self, "context", _coerce_context(self.context))
        if self.source_file is not None:
            object.__setattr__(
                self, "source_file", _require_non_empty_text(self.source_file, "source_file")
            )
        if self.field_name is not None:
            object.__setattr__(
                self, "field_name", _require_non_empty_text(self.field_name, "field_name")
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "source_file": self.source_file,
            "field_name": self.field_name,
            "context": dict(self.context),
            "is_fatal": True,
        }


@dataclass(frozen=True)
class PostflopSourceCandidate:
    """Metadata contract for one discovered postflop source JSON candidate.

    This is only a contract. It does not scan folders and does not load the JSON file.
    """

    source_file: str
    source_type: PostflopSourceType | str
    table_id: str = "unknown"
    hand_id: str = "unknown"
    detected_at: str = "unknown"
    has_board_cards: bool = False
    has_hero_cards: bool = False
    has_players: bool = False
    has_actions: bool = False
    can_be_normalized: bool = False
    confidence: PostflopConfidence | str = PostflopConfidence.UNKNOWN
    warnings: list[ModuleWarning] = field(default_factory=list)
    is_real_project_source: bool = False
    is_manual_live_like_source: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "source_file", _require_non_empty_text(self.source_file, "source_file")
        )
        source_type = PostflopSourceType.from_value(self.source_type)
        object.__setattr__(self, "source_type", source_type)
        confidence = PostflopConfidence.from_value(self.confidence)
        object.__setattr__(self, "confidence", confidence)

        if not isinstance(self.is_real_project_source, bool):
            raise ContractValidationError("is_real_project_source must be bool.")
        if not isinstance(self.is_manual_live_like_source, bool):
            raise ContractValidationError("is_manual_live_like_source must be bool.")

        manual_flag = self.is_manual_live_like_source or source_type.is_manual_live_like
        object.__setattr__(self, "is_manual_live_like_source", manual_flag)

        if manual_flag and self.is_real_project_source:
            raise ContractValidationError(
                "manual_live_like_json cannot be marked as real project source."
            )

        if self.is_real_project_source and not source_type.can_be_real_project_source:
            raise ContractValidationError(
                f"{source_type.value} cannot be marked as real project source."
            )

        table_id = self.table_id if self.table_id else "unknown"
        hand_id = self.hand_id if self.hand_id else "unknown"
        detected_at = self.detected_at if self.detected_at else "unknown"
        object.__setattr__(self, "table_id", str(table_id))
        object.__setattr__(self, "hand_id", str(hand_id))
        object.__setattr__(self, "detected_at", str(detected_at))

        for field_name in (
            "has_board_cards",
            "has_hero_cards",
            "has_players",
            "has_actions",
            "can_be_normalized",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise ContractValidationError(f"{field_name} must be bool.")

        warnings: list[ModuleWarning] = list(self.warnings or [])
        if self.table_id == "unknown":
            warnings.append(
                ModuleWarning(
                    code="missing_table_id",
                    message="table_id is unknown for source candidate.",
                    field_name="table_id",
                    source_file=self.source_file,
                    context={"source_type": source_type.value},
                )
            )
        if self.hand_id == "unknown":
            warnings.append(
                ModuleWarning(
                    code="missing_hand_id",
                    message="hand_id is unknown for source candidate.",
                    field_name="hand_id",
                    source_file=self.source_file,
                    context={"source_type": source_type.value},
                )
            )
        object.__setattr__(self, "warnings", warnings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_file": self.source_file,
            "source_type": self.source_type.value,
            "table_id": self.table_id,
            "hand_id": self.hand_id,
            "detected_at": self.detected_at,
            "has_board_cards": self.has_board_cards,
            "has_hero_cards": self.has_hero_cards,
            "has_players": self.has_players,
            "has_actions": self.has_actions,
            "can_be_normalized": self.can_be_normalized,
            "confidence": self.confidence.value,
            "warnings": _serialize_warnings(self.warnings),
            "is_real_project_source": self.is_real_project_source,
            "is_manual_live_like_source": self.is_manual_live_like_source,
        }


@dataclass(frozen=True)
class PostflopRawSource:
    """Raw JSON payload wrapper for a discovered candidate.

    This contract intentionally preserves raw_data as-is and performs no normalization.
    """

    candidate: PostflopSourceCandidate
    raw_data: Mapping[str, Any] | None = field(default_factory=dict)
    load_status: RawSourceLoadStatus | str = RawSourceLoadStatus.LOADED
    warnings: list[ModuleWarning] = field(default_factory=list)
    errors: list[ModuleError] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.candidate, PostflopSourceCandidate):
            raise ContractValidationError("candidate must be PostflopSourceCandidate.")
        object.__setattr__(
            self,
            "load_status",
            RawSourceLoadStatus.from_value(self.load_status),
        )
        if self.raw_data is None:
            object.__setattr__(self, "raw_data", {})
        elif not isinstance(self.raw_data, Mapping):
            raise ContractValidationError("raw_data must be a mapping/dict or None.")
        else:
            object.__setattr__(self, "raw_data", dict(self.raw_data))
        object.__setattr__(self, "warnings", list(self.warnings or []))
        object.__setattr__(self, "errors", list(self.errors or []))

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate": self.candidate.to_dict(),
            "raw_data": dict(self.raw_data or {}),
            "load_status": self.load_status.value,
            "warnings": _serialize_warnings(self.warnings),
            "errors": _serialize_errors(self.errors),
        }


@dataclass(frozen=True)
class PostflopSourceDiscoveryResult:
    """Future source-discovery result contract.

    V0.3.2 only defines this shape. V0.4 will implement actual discovery.
    """

    input_root: str
    candidates: list[PostflopSourceCandidate] = field(default_factory=list)
    raw_sources: list[PostflopRawSource] = field(default_factory=list)
    warnings: list[ModuleWarning] = field(default_factory=list)
    errors: list[ModuleError] = field(default_factory=list)
    status: DiscoveryStatus | str = DiscoveryStatus.OK

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "input_root", _require_non_empty_text(self.input_root, "input_root")
        )
        object.__setattr__(self, "status", DiscoveryStatus.from_value(self.status))
        object.__setattr__(self, "candidates", list(self.candidates or []))
        object.__setattr__(self, "raw_sources", list(self.raw_sources or []))
        object.__setattr__(self, "warnings", list(self.warnings or []))
        object.__setattr__(self, "errors", list(self.errors or []))

        for candidate in self.candidates:
            if not isinstance(candidate, PostflopSourceCandidate):
                raise ContractValidationError("candidates must contain PostflopSourceCandidate.")
        for raw_source in self.raw_sources:
            if not isinstance(raw_source, PostflopRawSource):
                raise ContractValidationError("raw_sources must contain PostflopRawSource.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_root": self.input_root,
            "status": self.status.value,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "raw_sources": [raw_source.to_dict() for raw_source in self.raw_sources],
            "warnings": _serialize_warnings(self.warnings),
            "errors": _serialize_errors(self.errors),
        }
