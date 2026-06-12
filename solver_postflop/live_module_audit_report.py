"""Contracts for live Clear_JSON postflop module audit reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any, Mapping, Optional


class LiveAuditModuleStatus(str, Enum):
    """Status of one postflop module inside the live Clear_JSON audit chain."""

    NOT_RUN = "not_run"
    PASSED = "passed"
    SKIPPED = "skipped"
    FAILED = "failed"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class ModuleChainStatus(str, Enum):
    """Overall status for a Clear_JSON → feature-chain audit pass."""

    NOT_STARTED = "not_started"
    CLEAR_JSON_LOADED = "clear_json_loaded"
    BRANCH_RESOLVED = "branch_resolved"
    NON_FLOP_SKIPPED = "non_flop_skipped"
    FLOP_FEATURES_COMPLETED = "flop_features_completed"
    MODULE_ERROR = "module_error"
    UNKNOWN = "unknown"


class RuntimeClickChainStatus(str, Enum):
    """Observed status of the existing project click chain from audit metadata.

    These values are report metadata only. The postflop solver is not allowed to
    create a runtime plan, call Action_Button, or execute clicks from this layer.
    """

    NOT_CHECKED = "not_checked"
    EXISTING_PROJECT_CHAIN_NOT_INVOKED_BY_AUDIT = "existing_project_chain_not_invoked_by_audit"
    EXISTING_PROJECT_CHAIN_OBSERVED = "existing_project_chain_observed"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class ClearJsonCaptureStatus(str, Enum):
    """Capture status for postflop Clear_JSON availability in live audit."""

    NOT_CHECKED = "not_checked"
    CLEAR_JSON_CAPTURED = "clear_json_captured"
    CLEAR_JSON_MISSING = "clear_json_missing"
    CAPTURE_HOOK_REQUIRED = "capture_hook_required"
    CAPTURE_HOOK_AVAILABLE = "capture_hook_available"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class LiveModuleResult:
    """One module's audit payload for a single Clear_JSON source.

    The payload is metadata emitted by already-built feature modules. It should
    not contain poker decisions, executable runtime plans, or UI click commands.
    """

    module_name: str
    status: LiveAuditModuleStatus
    payload: Mapping[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation of a module result."""
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class LiveModuleAuditReport:
    """Audit report for one live or live-like Clear_JSON file.

    This report records the postflop read-only feature chain. It does not create
    a poker action, runtime plan, Action_Button command, or physical click.
    """

    source_file: str
    table_id: Optional[str]
    hand_id: Optional[str]
    branch: str
    spot_family: Optional[str]
    board_texture_result: LiveModuleResult
    made_hand_result: LiveModuleResult
    draw_result: LiveModuleResult
    fields_used: tuple[str, ...] = field(default_factory=tuple)
    fields_not_provided: tuple[str, ...] = field(default_factory=tuple)
    module_chain_status: ModuleChainStatus = ModuleChainStatus.NOT_STARTED
    runtime_click_chain_status: RuntimeClickChainStatus = RuntimeClickChainStatus.NOT_CHECKED
    clear_json_capture_status: ClearJsonCaptureStatus = ClearJsonCaptureStatus.NOT_CHECKED
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation of one audit report."""
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class LiveClearJsonAuditReport:
    """Envelope for the full V0.9 live Clear_JSON module audit output."""

    report_version: str
    generated_at: str
    source_root: str
    reports: tuple[LiveModuleAuditReport, ...] = field(default_factory=tuple)
    total_files_seen: int = 0
    total_clear_json_processed: int = 0
    module_chain_status: ModuleChainStatus = ModuleChainStatus.NOT_STARTED
    runtime_click_chain_status: RuntimeClickChainStatus = RuntimeClickChainStatus.NOT_CHECKED
    clear_json_capture_status: ClearJsonCaptureStatus = ClearJsonCaptureStatus.NOT_CHECKED
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation of the full report."""
        return _json_safe(asdict(self))


LIVE_AUDIT_REPORT_CONTRACT_VERSION = "v0.9.0"
LIVE_AUDIT_MODULE_STATUSES: tuple[LiveAuditModuleStatus, ...] = tuple(LiveAuditModuleStatus)
MODULE_CHAIN_STATUSES: tuple[ModuleChainStatus, ...] = tuple(ModuleChainStatus)
RUNTIME_CLICK_CHAIN_STATUSES: tuple[RuntimeClickChainStatus, ...] = tuple(RuntimeClickChainStatus)
CLEAR_JSON_CAPTURE_STATUSES: tuple[ClearJsonCaptureStatus, ...] = tuple(ClearJsonCaptureStatus)

LIVE_AUDIT_REPORT_FUTURE_MODULES: tuple[str, ...] = (
    "live_clear_json_discovery_v092",
    "full_module_pipeline_runner_v093",
    "clear_json_capture_hook_audit_v094",
    "live_audit_tool_runner_v095",
    "no_postflop_click_gate_v096",
    "equity_input_builder_later",
)


LIVE_AUDIT_REQUIRED_REPORT_FIELDS: tuple[str, ...] = (
    "source_file",
    "table_id",
    "hand_id",
    "branch",
    "spot_family",
    "board_texture_result",
    "made_hand_result",
    "draw_result",
    "fields_used",
    "fields_not_provided",
    "module_chain_status",
    "runtime_click_chain_status",
    "clear_json_capture_status",
)


def build_not_run_module_result(module_name: str, note: str = "not_run_yet") -> LiveModuleResult:
    """Create a stable not-run placeholder for later V0.9 audit stages."""
    return LiveModuleResult(
        module_name=module_name,
        status=LiveAuditModuleStatus.NOT_RUN,
        notes=(note,),
    )


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
