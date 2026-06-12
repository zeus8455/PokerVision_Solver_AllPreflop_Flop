"""Clear_JSON discovery and V0.9.3 module pipeline audit layer.

This module keeps V0.9 Clear_JSON discovery strict: only Clear_JSON files may
be accepted as solver input. V0.9.3 adds a read-only pipeline runner over those
accepted Clear_JSON files: ClearJsonInput -> SolverInput -> FieldUsageTrace ->
Branch Resolver -> FlopContext -> BoardTextureFeatures -> MadeHandFeatures ->
DrawFeatures -> LiveModuleAuditReport.

It does not run main/live, install a capture hook, create poker decisions, build
postflop runtime plans, call UI button detectors, or execute clicks.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Optional, Union

from solver_postflop.board_texture import build_board_texture_features
from solver_postflop.branch_contracts import SolverBranch
from solver_postflop.branch_resolver import resolve_solver_branch
from solver_postflop.clear_json_input import load_clear_json_input
from solver_postflop.field_usage_trace import build_field_usage_trace
from solver_postflop.flop_context import build_flop_context
from solver_postflop.hero_draw import build_draw_features
from solver_postflop.hero_made_hand import build_made_hand_features
from solver_postflop.solver_input import build_solver_input
from solver_postflop.live_module_audit_report import (
    ClearJsonCaptureStatus,
    LiveAuditModuleStatus,
    LiveClearJsonAuditReport,
    LiveModuleAuditReport,
    LiveModuleResult,
    ModuleChainStatus,
    RuntimeClickChainStatus,
)

PathLike = Union[str, Path]


class LiveClearJsonSourceType(str, Enum):
    """Source type detected during V0.9 Clear_JSON discovery."""

    CLEAR_JSON = "clear_json"
    DARK_JSON = "dark_json"
    PENDING_JSON = "pending_json"
    SERVICE_JSON = "service_json"
    RUNTIME_JSON = "runtime_json"
    ACTION_DECISION_JSON = "action_decision_json"
    ACTION_RUNTIME_PLAN_JSON = "action_runtime_plan_json"
    BUTTON_DETECTOR_JSON = "button_detector_json"
    TEMPORARY_JSON = "temporary_json"
    UNKNOWN_JSON = "unknown_json"
    NON_JSON = "non_json"


class LiveClearJsonScanStatus(str, Enum):
    """Overall discovery status for a source root."""

    NOT_STARTED = "not_started"
    SOURCE_ROOT_MISSING = "source_root_missing"
    NO_FILES_FOUND = "no_files_found"
    CLEAR_JSON_FOUND = "clear_json_found"
    NO_CLEAR_JSON_FOUND = "no_clear_json_found"
    UNKNOWN = "unknown"


class LiveClearJsonSkipReason(str, Enum):
    """Reason a discovered file was not accepted as Clear_JSON solver input."""

    NOT_JSON = "not_json"
    FORBIDDEN_SOURCE_TYPE = "forbidden_source_type"
    UNKNOWN_JSON_SHAPE = "unknown_json_shape"
    SOURCE_ROOT_MISSING = "source_root_missing"


@dataclass(frozen=True, slots=True)
class LiveClearJsonCandidate:
    """One accepted Clear_JSON candidate for later V0.9 pipeline stages."""

    source_file: str
    file_name: str
    source_type: LiveClearJsonSourceType = LiveClearJsonSourceType.CLEAR_JSON
    table_id: Optional[str] = None
    hand_id: Optional[str] = None
    case_id: Optional[str] = None
    size_bytes: int = 0
    modified_at: Optional[str] = None
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary for report output."""
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class LiveClearJsonSkippedFile:
    """One file rejected by the Clear-only discovery policy."""

    source_file: str
    file_name: str
    detected_source_type: LiveClearJsonSourceType
    skip_reason: LiveClearJsonSkipReason
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary for report output."""
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class LiveClearJsonScanResult:
    """Discovery result for a root that may contain live Clear_JSON files."""

    source_root: str
    status: LiveClearJsonScanStatus
    candidates: tuple[LiveClearJsonCandidate, ...] = field(default_factory=tuple)
    skipped_files: tuple[LiveClearJsonSkippedFile, ...] = field(default_factory=tuple)
    total_files_seen: int = 0
    total_clear_json_candidates: int = 0
    clear_only_policy: str = "accept_clear_json_only"
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary for report output."""
        return _json_safe(asdict(self))


LIVE_CLEAR_JSON_SCAN_VERSION = "v0.9.2"
LIVE_CLEAR_JSON_PIPELINE_VERSION = "v0.9.3"
LIVE_CLEAR_JSON_PIPELINE_MODULE_CHAIN: tuple[str, ...] = (
    "clear_json_input",
    "solver_input_mapping",
    "field_usage_trace",
    "branch_resolver",
    "flop_context_builder",
    "board_texture_features",
    "made_hand_features",
    "draw_features",
    "live_module_audit_report",
)
LIVE_CLEAR_JSON_ALLOWED_SOURCE_TYPES: tuple[LiveClearJsonSourceType, ...] = (
    LiveClearJsonSourceType.CLEAR_JSON,
)
LIVE_CLEAR_JSON_FORBIDDEN_SOURCE_TYPES: tuple[LiveClearJsonSourceType, ...] = (
    LiveClearJsonSourceType.DARK_JSON,
    LiveClearJsonSourceType.PENDING_JSON,
    LiveClearJsonSourceType.SERVICE_JSON,
    LiveClearJsonSourceType.RUNTIME_JSON,
    LiveClearJsonSourceType.ACTION_DECISION_JSON,
    LiveClearJsonSourceType.ACTION_RUNTIME_PLAN_JSON,
    LiveClearJsonSourceType.BUTTON_DETECTOR_JSON,
    LiveClearJsonSourceType.TEMPORARY_JSON,
)
LIVE_CLEAR_JSON_SCAN_FUTURE_MODULES: tuple[str, ...] = (
    "full_module_pipeline_runner_v093",
    "clear_json_capture_hook_audit_v094",
    "live_audit_tool_runner_v095",
    "no_postflop_click_gate_v096",
)

_CLEAR_MARKERS: tuple[str, ...] = (
    ".clear.json",
    "clear_json",
    "final_clear_json",
    "clear-json",
)
_CLEAR_PATH_PARTS: frozenset[str] = frozenset({"clear", "clear_json", "final_clear_json"})
_FORBIDDEN_MARKERS: tuple[tuple[LiveClearJsonSourceType, tuple[str, ...]], ...] = (
    (LiveClearJsonSourceType.DARK_JSON, ("dark_json", ".dark.json", "dark-json")),
    (LiveClearJsonSourceType.PENDING_JSON, ("pending_json", ".pending.json", "pending-json")),
    (LiveClearJsonSourceType.SERVICE_JSON, ("service_json", ".service.json", "service-json")),
    (LiveClearJsonSourceType.RUNTIME_JSON, ("runtime_json", ".runtime.json", "runtime-json")),
    (LiveClearJsonSourceType.ACTION_DECISION_JSON, ("action_decision", "action_decision_json")),
    (LiveClearJsonSourceType.ACTION_RUNTIME_PLAN_JSON, ("action_runtime_plan", "runtime_plan_json")),
    (LiveClearJsonSourceType.BUTTON_DETECTOR_JSON, ("button_detector", "action_button", "button-detect")),
    (LiveClearJsonSourceType.TEMPORARY_JSON, ("current_cycle", "pending_cycle")),
)


def discover_live_clear_json_files(
    source_root: PathLike,
    *,
    recursive: bool = True,
    include_non_json_skips: bool = True,
    max_files: Optional[int] = None,
) -> LiveClearJsonScanResult:
    """Discover candidate Clear_JSON files under a root.

    V0.9.2 scope is discovery only. The returned candidates are not loaded into
    SolverInput and no feature modules are executed here.
    """

    root = Path(source_root)
    if not root.exists():
        skipped = LiveClearJsonSkippedFile(
            source_file=str(root),
            file_name=root.name,
            detected_source_type=LiveClearJsonSourceType.UNKNOWN_JSON,
            skip_reason=LiveClearJsonSkipReason.SOURCE_ROOT_MISSING,
            notes=("source_root_missing",),
        )
        return LiveClearJsonScanResult(
            source_root=str(root),
            status=LiveClearJsonScanStatus.SOURCE_ROOT_MISSING,
            skipped_files=(skipped,),
            total_files_seen=0,
            total_clear_json_candidates=0,
            notes=("source_root_missing",),
        )

    files = _iter_files(root, recursive=recursive)
    if max_files is not None:
        files = tuple(files[:max_files])

    candidates: list[LiveClearJsonCandidate] = []
    skipped_files: list[LiveClearJsonSkippedFile] = []

    for file_path in files:
        source_type = classify_live_clear_json_source(file_path)
        if source_type is LiveClearJsonSourceType.CLEAR_JSON:
            candidates.append(_build_candidate(file_path))
            continue

        if source_type is LiveClearJsonSourceType.NON_JSON and not include_non_json_skips:
            continue

        skipped_files.append(
            LiveClearJsonSkippedFile(
                source_file=str(file_path),
                file_name=file_path.name,
                detected_source_type=source_type,
                skip_reason=_skip_reason_for(source_type),
                notes=("not_accepted_as_solver_input",),
            )
        )

    status = _status_for(files_seen=len(files), candidates_count=len(candidates))
    return LiveClearJsonScanResult(
        source_root=str(root),
        status=status,
        candidates=tuple(candidates),
        skipped_files=tuple(skipped_files),
        total_files_seen=len(files),
        total_clear_json_candidates=len(candidates),
    )


def audit_live_clear_json_root(
    source_root: PathLike,
    *,
    recursive: bool = True,
    include_non_json_skips: bool = True,
    max_files: Optional[int] = None,
) -> LiveClearJsonAuditReport:
    """Discover Clear_JSON files under a root and run the V0.9.3 audit pipeline.

    This is still an offline audit runner. It does not start main/live and does
    not interact with the existing project click chain.
    """

    scan_result = discover_live_clear_json_files(
        source_root,
        recursive=recursive,
        include_non_json_skips=include_non_json_skips,
        max_files=max_files,
    )
    return audit_live_clear_json_scan_result(scan_result)


def audit_live_clear_json_scan_result(scan_result: LiveClearJsonScanResult) -> LiveClearJsonAuditReport:
    """Run the V0.9.3 module pipeline for accepted Clear_JSON candidates only."""

    reports = tuple(audit_live_clear_json_candidate(candidate) for candidate in scan_result.candidates)
    return LiveClearJsonAuditReport(
        report_version=LIVE_CLEAR_JSON_PIPELINE_VERSION,
        generated_at=datetime.now(timezone.utc).isoformat(),
        source_root=scan_result.source_root,
        reports=reports,
        total_files_seen=scan_result.total_files_seen,
        total_clear_json_processed=len(reports),
        module_chain_status=_envelope_chain_status(reports),
        runtime_click_chain_status=RuntimeClickChainStatus.EXISTING_PROJECT_CHAIN_NOT_INVOKED_BY_AUDIT,
        clear_json_capture_status=ClearJsonCaptureStatus.NOT_CHECKED,
        notes=(
            "v0.9.3_pipeline_runner_clear_json_candidates_only",
            "main_live_not_started_by_audit_layer",
            "existing_project_click_chain_not_invoked_by_postflop_solver",
        ),
    )


def audit_live_clear_json_candidate(candidate: LiveClearJsonCandidate) -> LiveModuleAuditReport:
    """Run the V0.9.3 module pipeline for one accepted Clear_JSON candidate."""

    return audit_live_clear_json_file(
        candidate.source_file,
        table_id_hint=candidate.table_id,
        hand_id_hint=candidate.hand_id,
    )


def audit_live_clear_json_file(
    source_file: PathLike,
    *,
    table_id_hint: Optional[str] = None,
    hand_id_hint: Optional[str] = None,
) -> LiveModuleAuditReport:
    """Run ClearJsonInput -> DrawFeatures for one Clear_JSON file.

    Non-flop branches produce a structured skipped report. Module errors are
    captured in a report instead of breaking the whole scan result.
    """

    source_file_text = str(source_file)
    try:
        clear_input = load_clear_json_input(source_file)
        solver_input, solver_trace = build_solver_input(clear_input)
        field_usage_trace = build_field_usage_trace(clear_input, solver_input)
        branch_result = resolve_solver_branch(solver_input, solver_trace)

        fields_used = _dedupe_text((*solver_trace.fields_used, *field_usage_trace.fields_used))
        fields_not_provided = _dedupe_text(
            (*solver_trace.fields_not_provided, *field_usage_trace.fields_not_provided)
        )
        branch_value = _enum_value(branch_result.branch)

        if branch_result.branch is not SolverBranch.FLOP:
            skipped_note = f"non_flop_branch_skipped:{branch_value}"
            skipped_result = _skipped_module_result("flop_only_feature_modules", skipped_note)
            return LiveModuleAuditReport(
                source_file=clear_input.source_file,
                table_id=solver_input.table_id or clear_input.table_id or table_id_hint,
                hand_id=solver_input.hand_id or clear_input.hand_id or hand_id_hint,
                branch=branch_value,
                spot_family=None,
                board_texture_result=skipped_result,
                made_hand_result=skipped_result,
                draw_result=skipped_result,
                fields_used=fields_used,
                fields_not_provided=fields_not_provided,
                module_chain_status=ModuleChainStatus.NON_FLOP_SKIPPED,
                runtime_click_chain_status=RuntimeClickChainStatus.EXISTING_PROJECT_CHAIN_NOT_INVOKED_BY_AUDIT,
                clear_json_capture_status=ClearJsonCaptureStatus.NOT_CHECKED,
                notes=(
                    "clear_json_loaded",
                    "solver_input_mapped",
                    "branch_resolved",
                    skipped_note,
                    branch_result.branch_reason,
                ),
            )

        flop_context = build_flop_context(solver_input, branch_result)
        board_texture_features = build_board_texture_features(flop_context)
        made_hand_features = build_made_hand_features(flop_context, board_texture_features)
        draw_features = build_draw_features(flop_context, board_texture_features, made_hand_features)

        fields_used = _dedupe_text((*fields_used, *flop_context.context_fields_used))
        fields_not_provided = _dedupe_text((*fields_not_provided, *flop_context.context_fields_not_provided))

        return LiveModuleAuditReport(
            source_file=clear_input.source_file,
            table_id=solver_input.table_id or clear_input.table_id or table_id_hint,
            hand_id=solver_input.hand_id or clear_input.hand_id or hand_id_hint,
            branch=branch_value,
            spot_family=_enum_value(flop_context.spot_family),
            board_texture_result=_passed_module_result(
                "board_texture_features",
                board_texture_features.to_json_dict(),
                ("flop_context_builder_completed",),
            ),
            made_hand_result=_passed_module_result(
                "made_hand_features",
                made_hand_features.to_json_dict(),
                ("board_texture_features_completed",),
            ),
            draw_result=_passed_module_result(
                "draw_features",
                draw_features.to_json_dict(),
                ("made_hand_features_completed",),
            ),
            fields_used=fields_used,
            fields_not_provided=fields_not_provided,
            module_chain_status=ModuleChainStatus.FLOP_FEATURES_COMPLETED,
            runtime_click_chain_status=RuntimeClickChainStatus.EXISTING_PROJECT_CHAIN_NOT_INVOKED_BY_AUDIT,
            clear_json_capture_status=ClearJsonCaptureStatus.NOT_CHECKED,
            notes=(
                "clear_json_loaded",
                "solver_input_mapped",
                "field_usage_trace_built",
                "branch_resolved",
                "flop_feature_chain_completed_to_draw_features",
            ),
        )
    except Exception as error:  # noqa: BLE001 - V0.9 audit reports module errors without stopping a scan.
        return _module_error_report(
            source_file=source_file_text,
            table_id_hint=table_id_hint,
            hand_id_hint=hand_id_hint,
            error=error,
        )


def _passed_module_result(module_name: str, payload: dict[str, Any], notes: tuple[str, ...]) -> LiveModuleResult:
    return LiveModuleResult(
        module_name=module_name,
        status=LiveAuditModuleStatus.PASSED,
        payload=payload,
        notes=notes,
    )


def _skipped_module_result(module_name: str, note: str) -> LiveModuleResult:
    return LiveModuleResult(
        module_name=module_name,
        status=LiveAuditModuleStatus.SKIPPED,
        notes=(note,),
    )


def _failed_module_result(module_name: str, error: Exception) -> LiveModuleResult:
    return LiveModuleResult(
        module_name=module_name,
        status=LiveAuditModuleStatus.FAILED,
        errors=(f"{error.__class__.__name__}: {error}",),
    )


def _module_error_report(
    *,
    source_file: str,
    table_id_hint: Optional[str],
    hand_id_hint: Optional[str],
    error: Exception,
) -> LiveModuleAuditReport:
    failed_result = _failed_module_result("clear_json_to_draw_features_pipeline", error)
    return LiveModuleAuditReport(
        source_file=source_file,
        table_id=table_id_hint,
        hand_id=hand_id_hint,
        branch="unknown",
        spot_family=None,
        board_texture_result=failed_result,
        made_hand_result=failed_result,
        draw_result=failed_result,
        module_chain_status=ModuleChainStatus.MODULE_ERROR,
        runtime_click_chain_status=RuntimeClickChainStatus.EXISTING_PROJECT_CHAIN_NOT_INVOKED_BY_AUDIT,
        clear_json_capture_status=ClearJsonCaptureStatus.NOT_CHECKED,
        errors=(f"{error.__class__.__name__}: {error}",),
        notes=("module_error_captured_without_breaking_scan",),
    )


def _envelope_chain_status(reports: tuple[LiveModuleAuditReport, ...]) -> ModuleChainStatus:
    if not reports:
        return ModuleChainStatus.NOT_STARTED
    if any(report.module_chain_status is ModuleChainStatus.MODULE_ERROR for report in reports):
        return ModuleChainStatus.MODULE_ERROR
    if any(report.module_chain_status is ModuleChainStatus.FLOP_FEATURES_COMPLETED for report in reports):
        return ModuleChainStatus.FLOP_FEATURES_COMPLETED
    if all(report.module_chain_status is ModuleChainStatus.NON_FLOP_SKIPPED for report in reports):
        return ModuleChainStatus.NON_FLOP_SKIPPED
    return ModuleChainStatus.BRANCH_RESOLVED



def classify_live_clear_json_source(path: PathLike) -> LiveClearJsonSourceType:
    """Classify a file path without opening or parsing the file."""

    source_path = Path(path)
    lowered_name = source_path.name.lower()
    lowered_parts = tuple(part.lower() for part in source_path.parts)
    lowered_full = "/".join(lowered_parts)

    if source_path.suffix.lower() != ".json":
        return LiveClearJsonSourceType.NON_JSON

    for source_type, markers in _FORBIDDEN_MARKERS:
        if any(marker in lowered_full for marker in markers):
            return source_type

    if any(marker in lowered_name for marker in _CLEAR_MARKERS):
        return LiveClearJsonSourceType.CLEAR_JSON

    if any(part in _CLEAR_PATH_PARTS for part in lowered_parts):
        return LiveClearJsonSourceType.CLEAR_JSON

    return LiveClearJsonSourceType.UNKNOWN_JSON


def clear_json_candidate_paths(result: LiveClearJsonScanResult) -> tuple[str, ...]:
    """Return accepted candidate paths in deterministic discovery order."""

    return tuple(candidate.source_file for candidate in result.candidates)


def _iter_files(root: Path, *, recursive: bool) -> tuple[Path, ...]:
    pattern = "**/*" if recursive else "*"
    return tuple(sorted((path for path in root.glob(pattern) if path.is_file()), key=lambda item: str(item)))


def _build_candidate(file_path: Path) -> LiveClearJsonCandidate:
    stat = file_path.stat()
    return LiveClearJsonCandidate(
        source_file=str(file_path),
        file_name=file_path.name,
        table_id=_extract_id_from_name(file_path.name, "table"),
        hand_id=_extract_id_from_name(file_path.name, "hand"),
        case_id=file_path.stem,
        size_bytes=stat.st_size,
        modified_at=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        notes=("clear_json_candidate",),
    )


def _extract_id_from_name(file_name: str, prefix: str) -> Optional[str]:
    lowered = file_name.lower().replace("-", "_")
    parts = lowered.split("_")
    for index, part in enumerate(parts[:-1]):
        if part != prefix:
            continue
        next_part = parts[index + 1].split(".")[0]
        if next_part:
            return f"{prefix}_{next_part}"
    return None


def _skip_reason_for(source_type: LiveClearJsonSourceType) -> LiveClearJsonSkipReason:
    if source_type is LiveClearJsonSourceType.NON_JSON:
        return LiveClearJsonSkipReason.NOT_JSON
    if source_type in LIVE_CLEAR_JSON_FORBIDDEN_SOURCE_TYPES:
        return LiveClearJsonSkipReason.FORBIDDEN_SOURCE_TYPE
    return LiveClearJsonSkipReason.UNKNOWN_JSON_SHAPE


def _status_for(*, files_seen: int, candidates_count: int) -> LiveClearJsonScanStatus:
    if files_seen == 0:
        return LiveClearJsonScanStatus.NO_FILES_FOUND
    if candidates_count > 0:
        return LiveClearJsonScanStatus.CLEAR_JSON_FOUND
    return LiveClearJsonScanStatus.NO_CLEAR_JSON_FOUND


def _enum_value(value: Any) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


def _dedupe_text(values: Iterable[Any]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in (None, ""):
            continue
        text_value = str(value)
        if text_value in seen:
            continue
        seen.add(text_value)
        result.append(text_value)
    return tuple(result)



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
