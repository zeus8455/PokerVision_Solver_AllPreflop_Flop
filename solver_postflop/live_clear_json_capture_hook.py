"""Clear_JSON capture hook audit contracts for V0.9 live integration.

This module describes and audits the save-point required for postflop live
Clear_JSON artifacts. It is intentionally a read-only planning/audit layer: it
must not start main/live, change the existing project click chain, call UI
button detectors, create poker decisions, build runtime plans, or execute
physical clicks.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Optional, Union

from solver_postflop.live_clear_json_integration import (
    LIVE_CLEAR_JSON_ALLOWED_SOURCE_TYPES,
    LIVE_CLEAR_JSON_FORBIDDEN_SOURCE_TYPES,
    LiveClearJsonSourceType,
    classify_live_clear_json_source,
)
from solver_postflop.live_module_audit_report import ClearJsonCaptureStatus, RuntimeClickChainStatus

PathLike = Union[str, Path]


class ClearJsonCaptureHookMode(str, Enum):
    """How V0.9 expects postflop Clear_JSON to be captured for audit."""

    AUDIT_ONLY = "audit_only"
    EXISTING_PROJECT_SAVE_POINT = "existing_project_save_point"
    HOOK_REQUIRED = "hook_required"
    UNKNOWN = "unknown"


class ClearJsonCaptureTargetStatus(str, Enum):
    """Status of the configured Clear_JSON save target."""

    NOT_CHECKED = "not_checked"
    VALID_CLEAR_JSON_TARGET = "valid_clear_json_target"
    MISSING_CLEAR_FOLDER = "missing_clear_folder"
    INVALID_NON_CLEAR_TARGET = "invalid_non_clear_target"
    FORBIDDEN_TEMPORARY_TARGET = "forbidden_temporary_target"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ClearJsonCaptureSaveTarget:
    """Normalized target description for postflop Clear_JSON audit artifacts."""

    project_root: str
    clear_json_folder: str
    file_suffix: str = ".clear.json"
    source_type: LiveClearJsonSourceType = LiveClearJsonSourceType.CLEAR_JSON
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe target payload."""
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class ClearJsonCaptureHookAudit:
    """Audit result for the V0.9 Clear_JSON capture hook/save-point."""

    hook_version: str
    hook_mode: ClearJsonCaptureHookMode
    save_target: ClearJsonCaptureSaveTarget
    target_status: ClearJsonCaptureTargetStatus
    clear_json_capture_status: ClearJsonCaptureStatus
    runtime_click_chain_status: RuntimeClickChainStatus
    accepted_source_types: tuple[LiveClearJsonSourceType, ...] = field(default_factory=tuple)
    forbidden_source_types: tuple[LiveClearJsonSourceType, ...] = field(default_factory=tuple)
    solver_input_policy: str = "clear_json_only"
    writes_runtime_files: bool = False
    invokes_action_button: bool = False
    creates_postflop_decision: bool = False
    creates_runtime_plan: bool = False
    executes_clicks: bool = False
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe capture hook audit payload."""
        return _json_safe(asdict(self))


LIVE_CLEAR_JSON_CAPTURE_HOOK_VERSION = "v0.9.4"
DEFAULT_LIVE_CLEAR_JSON_FOLDER = "outputs/postflop_live_clear_json"
DEFAULT_LIVE_CLEAR_JSON_FILE_SUFFIX = ".clear.json"
CAPTURE_HOOK_REQUIRED_FIELDS: tuple[str, ...] = (
    "hook_version",
    "hook_mode",
    "save_target",
    "target_status",
    "clear_json_capture_status",
    "runtime_click_chain_status",
    "accepted_source_types",
    "forbidden_source_types",
    "solver_input_policy",
)
CAPTURE_HOOK_FORBIDDEN_INPUT_LABELS: tuple[str, ...] = (
    "dark_json",
    "pending_json",
    "service_json",
    "runtime_json",
    "action_decision_json",
    "action_runtime_plan_json",
    "button_detector_json",
    "temporary_json",
)
CAPTURE_HOOK_FUTURE_MODULES: tuple[str, ...] = (
    "live_audit_tool_runner_v095",
    "no_postflop_click_gate_v096",
    "main_live_audit_command_docs_v097",
)

_FORBIDDEN_CAPTURE_PATH_PARTS: tuple[str, ...] = (
    "dark_json",
    "pending_json",
    "service_json",
    "runtime_json",
    "current_cycle",
    "pending_cycle",
    "action_decision",
    "action_runtime_plan",
    "button_detector",
    "action_button",
)


def build_default_clear_json_capture_target(
    project_root: PathLike,
    *,
    clear_json_folder: PathLike = DEFAULT_LIVE_CLEAR_JSON_FOLDER,
) -> ClearJsonCaptureSaveTarget:
    """Build the V0.9 default postflop Clear_JSON save target description."""

    root = Path(project_root)
    folder = Path(clear_json_folder)
    if not folder.is_absolute():
        folder = root / folder

    return ClearJsonCaptureSaveTarget(
        project_root=str(root),
        clear_json_folder=str(folder),
        file_suffix=DEFAULT_LIVE_CLEAR_JSON_FILE_SUFFIX,
        source_type=LiveClearJsonSourceType.CLEAR_JSON,
        notes=("postflop_live_clear_json_save_target", "audit_layer_only"),
    )


def build_clear_json_capture_file_path(
    save_target: ClearJsonCaptureSaveTarget,
    *,
    table_id: str,
    hand_id: str,
    street: str = "flop",
) -> str:
    """Build a deterministic solver-readable Clear_JSON capture file path."""

    safe_table = _safe_id(table_id, fallback="table_unknown")
    safe_hand = _safe_id(hand_id, fallback="hand_unknown")
    safe_street = _safe_id(street, fallback="street_unknown")
    file_name = f"{safe_table}_{safe_hand}_{safe_street}{save_target.file_suffix}"
    return str(Path(save_target.clear_json_folder) / file_name)


def audit_clear_json_capture_target(save_target: ClearJsonCaptureSaveTarget) -> ClearJsonCaptureHookAudit:
    """Audit one save target without creating directories or touching runtime files."""

    target_path = Path(save_target.clear_json_folder)
    path_text = "/".join(part.lower() for part in target_path.parts)
    source_type = classify_live_clear_json_source(target_path / f"probe{save_target.file_suffix}")

    warnings: list[str] = []
    errors: list[str] = []
    status = ClearJsonCaptureTargetStatus.VALID_CLEAR_JSON_TARGET
    capture_status = ClearJsonCaptureStatus.CAPTURE_HOOK_AVAILABLE
    mode = ClearJsonCaptureHookMode.EXISTING_PROJECT_SAVE_POINT

    if any(part in path_text for part in _FORBIDDEN_CAPTURE_PATH_PARTS):
        status = ClearJsonCaptureTargetStatus.FORBIDDEN_TEMPORARY_TARGET
        capture_status = ClearJsonCaptureStatus.CAPTURE_HOOK_REQUIRED
        mode = ClearJsonCaptureHookMode.HOOK_REQUIRED
        errors.append("capture_target_points_to_forbidden_temporary_or_runtime_area")
    elif source_type is not LiveClearJsonSourceType.CLEAR_JSON:
        status = ClearJsonCaptureTargetStatus.INVALID_NON_CLEAR_TARGET
        capture_status = ClearJsonCaptureStatus.CAPTURE_HOOK_REQUIRED
        mode = ClearJsonCaptureHookMode.HOOK_REQUIRED
        errors.append("capture_target_does_not_classify_as_clear_json")
    elif not target_path.exists():
        status = ClearJsonCaptureTargetStatus.MISSING_CLEAR_FOLDER
        capture_status = ClearJsonCaptureStatus.CAPTURE_HOOK_REQUIRED
        mode = ClearJsonCaptureHookMode.HOOK_REQUIRED
        warnings.append("clear_json_folder_missing_capture_hook_required_before_real_live_audit")

    return ClearJsonCaptureHookAudit(
        hook_version=LIVE_CLEAR_JSON_CAPTURE_HOOK_VERSION,
        hook_mode=mode,
        save_target=save_target,
        target_status=status,
        clear_json_capture_status=capture_status,
        runtime_click_chain_status=RuntimeClickChainStatus.EXISTING_PROJECT_CHAIN_NOT_INVOKED_BY_AUDIT,
        accepted_source_types=LIVE_CLEAR_JSON_ALLOWED_SOURCE_TYPES,
        forbidden_source_types=LIVE_CLEAR_JSON_FORBIDDEN_SOURCE_TYPES,
        warnings=tuple(warnings),
        errors=tuple(errors),
        notes=(
            "capture_hook_audit_only",
            "postflop_solver_reads_clear_json_after_project_cycle",
            "existing_runtime_click_chain_not_modified",
        ),
    )


def audit_default_clear_json_capture_hook(
    project_root: PathLike,
    *,
    clear_json_folder: PathLike = DEFAULT_LIVE_CLEAR_JSON_FOLDER,
) -> ClearJsonCaptureHookAudit:
    """Build and audit the default V0.9 postflop Clear_JSON capture target."""

    target = build_default_clear_json_capture_target(project_root, clear_json_folder=clear_json_folder)
    return audit_clear_json_capture_target(target)


def is_solver_readable_clear_json_capture_path(path: PathLike) -> bool:
    """Return True only for paths accepted by the Clear-only solver input policy."""

    return classify_live_clear_json_source(path) is LiveClearJsonSourceType.CLEAR_JSON


def capture_hook_rejects_solver_input_path(path: PathLike) -> bool:
    """Return True for any non-Clear_JSON path that must not become solver input."""

    return not is_solver_readable_clear_json_capture_path(path)


def capture_hook_policy_summary() -> Mapping[str, Any]:
    """Return a stable JSON-safe summary of the V0.9.4 capture hook policy."""

    return {
        "hook_version": LIVE_CLEAR_JSON_CAPTURE_HOOK_VERSION,
        "solver_input_policy": "clear_json_only",
        "accepted_source_types": [source_type.value for source_type in LIVE_CLEAR_JSON_ALLOWED_SOURCE_TYPES],
        "forbidden_source_types": [source_type.value for source_type in LIVE_CLEAR_JSON_FORBIDDEN_SOURCE_TYPES],
        "default_clear_json_folder": DEFAULT_LIVE_CLEAR_JSON_FOLDER,
        "default_file_suffix": DEFAULT_LIVE_CLEAR_JSON_FILE_SUFFIX,
        "runtime_click_chain_policy": "existing_project_chain_not_modified",
        "postflop_solver_click_policy": "no_postflop_solver_clicks",
    }


def _safe_id(value: str, *, fallback: str) -> str:
    cleaned = "".join(character if character.isalnum() or character in {"_", "-"} else "_" for character in value)
    cleaned = cleaned.strip("_")
    return cleaned or fallback


def _json_safe(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value
