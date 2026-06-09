"""Postflop contract primitives for PokerVision_Solver_AllPreflop_Flop.

V0.3.1 scope:
- create the isolated ``solver_postflop`` module;
- define stable source type vocabulary shared with the V0.2 fixture lab;
- define reusable warning/error payloads for future source discovery,
  normalizer, street detector, and trace modules.

This file intentionally does not search files, normalize JSON, infer streets,
make poker decisions, or interact with runtime/click-chain code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Mapping


class ContractValidationError(ValueError):
    """Raised when a postflop contract receives invalid structural data."""


class PostflopSourceType(str, Enum):
    """Allowed source types for postflop source/fixture data.

    The values must stay aligned with:
    ``tests/fixtures/postflop/manifest.json`` -> ``allowed_source_types``.
    """

    DARK_JSON = "dark_json"
    PENDING_JSON = "pending_json"
    SERVICE_JSON = "service_json"
    CURRENT_CYCLE_JSON = "current_cycle_json"
    RUNTIME_JSON = "runtime_json"
    SOLVER_PAYLOAD_JSON = "solver_payload_json"
    FINAL_CLEAR_JSON = "final_clear_json"
    MANUAL_LIVE_LIKE_JSON = "manual_live_like_json"
    UNKNOWN = "unknown"

    @classmethod
    def values(cls) -> list[str]:
        """Return source type values in declaration order."""

        return [source_type.value for source_type in cls]

    @classmethod
    def from_value(cls, value: "PostflopSourceType | str") -> "PostflopSourceType":
        """Convert a string/enum value to ``PostflopSourceType``.

        Unknown textual input is not silently mapped to ``UNKNOWN`` because that
        would hide schema mistakes. Use explicit ``"unknown"`` when the source
        type is intentionally unknown.
        """

        if isinstance(value, cls):
            return value

        normalized = str(value).strip()
        for source_type in cls:
            if source_type.value == normalized:
                return source_type

        raise ContractValidationError(f"Unsupported postflop source_type: {value!r}")

    @property
    def is_manual_live_like(self) -> bool:
        """True only for manually-created live-like fixtures."""

        return self is PostflopSourceType.MANUAL_LIVE_LIKE_JSON

    @property
    def can_be_real_project_source(self) -> bool:
        """Whether the type may represent a real PokerVision-produced JSON."""

        return self not in {
            PostflopSourceType.MANUAL_LIVE_LIKE_JSON,
            PostflopSourceType.UNKNOWN,
        }

    @property
    def requires_click_cycle_by_type(self) -> bool:
        """Whether this source type normally implies post-click/final data."""

        return self is PostflopSourceType.FINAL_CLEAR_JSON


class ContractSeverity(str, Enum):
    """Shared warning/error severity vocabulary."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

    @classmethod
    def from_value(cls, value: "ContractSeverity | str") -> "ContractSeverity":
        if isinstance(value, cls):
            return value

        normalized = str(value).strip().lower()
        for severity in cls:
            if severity.value == normalized:
                return severity

        raise ContractValidationError(f"Unsupported severity: {value!r}")


def _validate_non_empty_text(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ContractValidationError(f"{field_name} must be a non-empty string")
    return normalized


def _normalize_context(context: Mapping[str, Any] | None) -> dict[str, Any]:
    if context is None:
        return {}
    if not isinstance(context, Mapping):
        raise ContractValidationError("context must be a mapping/dict")
    return dict(context)


@dataclass(frozen=True)
class ModuleWarning:
    """Non-fatal structured warning emitted by future postflop modules."""

    code: str
    message: str
    severity: ContractSeverity | str = ContractSeverity.WARNING
    source_file: str | None = None
    field_name: str | None = None
    context: Mapping[str, Any] | None = field(default_factory=dict)

    ALLOWED_SEVERITIES: ClassVar[set[ContractSeverity]] = {
        ContractSeverity.INFO,
        ContractSeverity.WARNING,
    }

    def __post_init__(self) -> None:
        code = _validate_non_empty_text(self.code, "warning.code")
        message = _validate_non_empty_text(self.message, "warning.message")
        severity = ContractSeverity.from_value(self.severity)
        if severity not in self.ALLOWED_SEVERITIES:
            raise ContractValidationError("ModuleWarning severity must be info or warning")

        object.__setattr__(self, "code", code)
        object.__setattr__(self, "message", message)
        object.__setattr__(self, "severity", severity)
        object.__setattr__(self, "source_file", _normalize_optional_path(self.source_file))
        object.__setattr__(self, "field_name", _normalize_optional_text(self.field_name))
        object.__setattr__(self, "context", _normalize_context(self.context))

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""

        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "source_file": self.source_file,
            "field_name": self.field_name,
            "context": dict(self.context or {}),
        }


@dataclass(frozen=True)
class ModuleError:
    """Structured error emitted by future postflop modules."""

    code: str
    message: str
    severity: ContractSeverity | str = ContractSeverity.ERROR
    is_fatal: bool = True
    source_file: str | None = None
    field_name: str | None = None
    context: Mapping[str, Any] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        code = _validate_non_empty_text(self.code, "error.code")
        message = _validate_non_empty_text(self.message, "error.message")
        severity = ContractSeverity.from_value(self.severity)
        if severity is not ContractSeverity.ERROR:
            raise ContractValidationError("ModuleError severity must be error")

        object.__setattr__(self, "code", code)
        object.__setattr__(self, "message", message)
        object.__setattr__(self, "severity", severity)
        object.__setattr__(self, "is_fatal", bool(self.is_fatal))
        object.__setattr__(self, "source_file", _normalize_optional_path(self.source_file))
        object.__setattr__(self, "field_name", _normalize_optional_text(self.field_name))
        object.__setattr__(self, "context", _normalize_context(self.context))

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""

        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "is_fatal": self.is_fatal,
            "source_file": self.source_file,
            "field_name": self.field_name,
            "context": dict(self.context or {}),
        }


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _normalize_optional_path(value: str | Path | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


__all__ = [
    "ContractSeverity",
    "ContractValidationError",
    "ModuleError",
    "ModuleWarning",
    "PostflopSourceType",
]
