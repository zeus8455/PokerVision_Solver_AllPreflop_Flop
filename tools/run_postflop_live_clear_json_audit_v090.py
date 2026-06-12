"""Offline V0.9.5 Clear_JSON audit tool runner.

The runner reads a Clear_JSON root, runs the V0.9.3 module audit pipeline,
and writes deterministic report artifacts under
outputs/postflop_live_clear_json_audit_v090. It does not start the live client,
modify the existing project chain, create poker decisions, build runtime plans,
or call UI button detectors.
"""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

from solver_postflop.board_texture import build_board_texture_features
from solver_postflop.branch_contracts import SolverBranch
from solver_postflop.branch_resolver import resolve_solver_branch
from solver_postflop.clear_json_input import load_clear_json_input
from solver_postflop.field_usage_trace import build_field_usage_trace
from solver_postflop.flop_context import build_flop_context
from solver_postflop.hero_draw import build_draw_features
from solver_postflop.hero_made_hand import build_made_hand_features
from solver_postflop.live_clear_json_integration import audit_live_clear_json_root
from solver_postflop.solver_input import build_solver_input

PathLike = Union[str, Path]

LIVE_CLEAR_JSON_AUDIT_TOOL_VERSION = "v0.9.5"
LIVE_CLEAR_JSON_AUDIT_DEFAULT_OUTPUT_ROOT = "outputs/postflop_live_clear_json_audit_v090"
LIVE_CLEAR_JSON_AUDIT_DEFAULT_CLEAR_ROOT = "outputs/postflop_live_clear_json"
LIVE_CLEAR_JSON_AUDIT_LATEST_REPORT_NAME = "latest_report.json"
LIVE_CLEAR_JSON_AUDIT_OUTPUT_SUBFOLDERS: tuple[str, ...] = (
    "processed_clear_json",
    "solver_inputs",
    "branch_results",
    "flop_contexts",
    "board_texture",
    "made_hand",
    "draw_features",
    "module_chain_reports",
)


@dataclass(frozen=True, slots=True)
class LiveClearJsonAuditToolConfig:
    """Configuration for one offline V0.9.5 Clear_JSON audit run."""

    project_root: str
    clear_json_root: str
    output_root: str
    max_files: Optional[int] = None
    recursive: bool = True
    include_non_json_skips: bool = True

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe config payload."""
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class LiveClearJsonAuditToolResult:
    """Summary produced by the V0.9.5 tool runner."""

    tool_version: str
    config: LiveClearJsonAuditToolConfig
    latest_report_file: str
    output_root: str
    output_subfolders: tuple[str, ...] = LIVE_CLEAR_JSON_AUDIT_OUTPUT_SUBFOLDERS
    total_files_seen: int = 0
    total_clear_json_processed: int = 0
    module_chain_status: str = "not_started"
    runtime_click_chain_status: str = "existing_project_chain_not_invoked_by_audit"
    clear_json_capture_status: str = "not_checked"
    artifacts_written: dict[str, int] = field(default_factory=dict)
    errors: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe tool result payload."""
        return _json_safe(asdict(self))


def build_live_clear_json_audit_config(
    *,
    project_root: PathLike = ".",
    clear_json_root: Optional[PathLike] = None,
    output_root: Optional[PathLike] = None,
    max_files: Optional[int] = None,
    recursive: bool = True,
    include_non_json_skips: bool = True,
) -> LiveClearJsonAuditToolConfig:
    """Build deterministic paths for an offline Clear_JSON audit run."""

    project_path = Path(project_root)
    clear_path = Path(clear_json_root) if clear_json_root is not None else project_path / LIVE_CLEAR_JSON_AUDIT_DEFAULT_CLEAR_ROOT
    output_path = Path(output_root) if output_root is not None else project_path / LIVE_CLEAR_JSON_AUDIT_DEFAULT_OUTPUT_ROOT

    return LiveClearJsonAuditToolConfig(
        project_root=str(project_path),
        clear_json_root=str(clear_path),
        output_root=str(output_path),
        max_files=max_files,
        recursive=recursive,
        include_non_json_skips=include_non_json_skips,
    )


def build_live_clear_json_audit_output_structure(output_root: PathLike) -> dict[str, str]:
    """Create and return the V0.9.5 audit output folder structure."""

    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    subfolders: dict[str, str] = {}
    for subfolder in LIVE_CLEAR_JSON_AUDIT_OUTPUT_SUBFOLDERS:
        path = root / subfolder
        path.mkdir(parents=True, exist_ok=True)
        subfolders[subfolder] = str(path)
    return subfolders


def run_postflop_live_clear_json_audit(
    *,
    project_root: PathLike = ".",
    clear_json_root: Optional[PathLike] = None,
    output_root: Optional[PathLike] = None,
    max_files: Optional[int] = None,
    recursive: bool = True,
    include_non_json_skips: bool = True,
) -> LiveClearJsonAuditToolResult:
    """Run the offline V0.9.5 Clear_JSON audit and write report artifacts.

    The function reads accepted Clear_JSON candidates only. It delegates the
    module chain to V0.9.3 audit functions and records artifacts for inspection.
    """

    config = build_live_clear_json_audit_config(
        project_root=project_root,
        clear_json_root=clear_json_root,
        output_root=output_root,
        max_files=max_files,
        recursive=recursive,
        include_non_json_skips=include_non_json_skips,
    )
    output_path = Path(config.output_root)
    build_live_clear_json_audit_output_structure(output_path)

    audit_report = audit_live_clear_json_root(
        config.clear_json_root,
        recursive=config.recursive,
        include_non_json_skips=config.include_non_json_skips,
        max_files=config.max_files,
    )

    artifacts_written: dict[str, int] = {key: 0 for key in LIVE_CLEAR_JSON_AUDIT_OUTPUT_SUBFOLDERS}
    errors: list[str] = []

    latest_report_file = output_path / LIVE_CLEAR_JSON_AUDIT_LATEST_REPORT_NAME
    _write_json(latest_report_file, audit_report.to_json_dict())

    for index, report in enumerate(audit_report.reports, start=1):
        report_stem = _safe_stem(report.source_file, fallback=f"clear_json_{index:03d}")
        module_report_file = output_path / "module_chain_reports" / f"{report_stem}.module_report.json"
        _write_json(module_report_file, report.to_json_dict())
        artifacts_written["module_chain_reports"] += 1

        source_path = Path(report.source_file)
        if source_path.exists():
            target_file = output_path / "processed_clear_json" / f"{report_stem}.clear.json"
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target_file)
            artifacts_written["processed_clear_json"] += 1

        try:
            written = _write_feature_artifacts(source_path, output_path, report_stem)
            for key, count in written.items():
                artifacts_written[key] += count
        except Exception as error:  # noqa: BLE001 - artifact generation must not break the run report.
            errors.append(f"artifact_generation_error:{report_stem}:{error.__class__.__name__}:{error}")

    result = LiveClearJsonAuditToolResult(
        tool_version=LIVE_CLEAR_JSON_AUDIT_TOOL_VERSION,
        config=config,
        latest_report_file=str(latest_report_file),
        output_root=str(output_path),
        total_files_seen=audit_report.total_files_seen,
        total_clear_json_processed=audit_report.total_clear_json_processed,
        module_chain_status=_enum_value(audit_report.module_chain_status),
        runtime_click_chain_status=_enum_value(audit_report.runtime_click_chain_status),
        clear_json_capture_status=_enum_value(audit_report.clear_json_capture_status),
        artifacts_written=artifacts_written,
        errors=tuple(errors),
        notes=(
            "offline_clear_json_audit_tool_runner_v095",
            "main_live_not_started_by_tool_runner",
            "postflop_solver_does_not_create_decision_or_runtime_plan",
        ),
    )
    _write_json(output_path / "tool_result.json", result.to_json_dict())
    return result


def _write_feature_artifacts(source_path: Path, output_path: Path, report_stem: str) -> dict[str, int]:
    written = {
        "solver_inputs": 0,
        "branch_results": 0,
        "flop_contexts": 0,
        "board_texture": 0,
        "made_hand": 0,
        "draw_features": 0,
    }
    clear_input = load_clear_json_input(source_path)
    solver_input, solver_trace = build_solver_input(clear_input)
    field_usage_trace = build_field_usage_trace(clear_input, solver_input)
    branch_result = resolve_solver_branch(solver_input, solver_trace)

    _write_json(
        output_path / "solver_inputs" / f"{report_stem}.solver_input.json",
        {
            "clear_json_input": _json_safe(asdict(clear_input)),
            "solver_input": _json_safe(asdict(solver_input)),
            "solver_trace": _json_safe(asdict(solver_trace)),
            "field_usage_trace": field_usage_trace.to_json_dict(),
        },
    )
    written["solver_inputs"] += 1

    _write_json(output_path / "branch_results" / f"{report_stem}.branch_result.json", branch_result.to_json_dict())
    written["branch_results"] += 1

    if branch_result.branch is not SolverBranch.FLOP:
        return written

    flop_context = build_flop_context(solver_input, branch_result)
    board_texture = build_board_texture_features(flop_context)
    made_hand = build_made_hand_features(flop_context, board_texture)
    draw_features = build_draw_features(flop_context, board_texture, made_hand)

    _write_json(output_path / "flop_contexts" / f"{report_stem}.flop_context.json", flop_context.to_json_dict())
    written["flop_contexts"] += 1
    _write_json(output_path / "board_texture" / f"{report_stem}.board_texture.json", board_texture.to_json_dict())
    written["board_texture"] += 1
    _write_json(output_path / "made_hand" / f"{report_stem}.made_hand.json", made_hand.to_json_dict())
    written["made_hand"] += 1
    _write_json(output_path / "draw_features" / f"{report_stem}.draw_features.json", draw_features.to_json_dict())
    written["draw_features"] += 1

    return written


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")


def _safe_stem(source_file: str, *, fallback: str) -> str:
    stem = Path(source_file).name
    if stem.endswith(".clear.json"):
        stem = stem[: -len(".clear.json")]
    elif stem.endswith(".json"):
        stem = stem[: -len(".json")]
    stem = stem.replace(" ", "_").replace("/", "_").replace("\\", "_")
    return stem or fallback


def _enum_value(value: Any) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


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


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run offline V0.9.5 postflop Clear_JSON audit.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--clear-json-root", default=None)
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--max-files", type=int, default=None)
    parser.add_argument("--non-recursive", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)
    result = run_postflop_live_clear_json_audit(
        project_root=args.project_root,
        clear_json_root=args.clear_json_root,
        output_root=args.output_root,
        max_files=args.max_files,
        recursive=not args.non_recursive,
    )
    print(json.dumps(result.to_json_dict(), indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
