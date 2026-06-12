"""Clear_JSON discovery for the V0.9 live postflop audit layer.

This module is intentionally a discovery-only layer for V0.9.2. It finds
candidate Clear_JSON files and records skipped files that are not acceptable
solver inputs. It does not run main/live, does not execute the feature pipeline,
and does not create poker decisions, runtime plans, Action_Button commands, or
physical clicks.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Optional, Union

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
