from __future__ import annotations

import json
from pathlib import Path

from solver_postflop import (
    CAPTURE_HOOK_FORBIDDEN_INPUT_LABELS,
    CAPTURE_HOOK_FUTURE_MODULES,
    CAPTURE_HOOK_REQUIRED_FIELDS,
    DEFAULT_LIVE_CLEAR_JSON_FILE_SUFFIX,
    DEFAULT_LIVE_CLEAR_JSON_FOLDER,
    LIVE_CLEAR_JSON_CAPTURE_HOOK_VERSION,
    ClearJsonCaptureHookAudit,
    ClearJsonCaptureHookMode,
    ClearJsonCaptureSaveTarget,
    ClearJsonCaptureStatus,
    ClearJsonCaptureTargetStatus,
    LiveClearJsonSourceType,
    RuntimeClickChainStatus,
    audit_clear_json_capture_target,
    audit_default_clear_json_capture_hook,
    build_clear_json_capture_file_path,
    build_default_clear_json_capture_target,
    capture_hook_policy_summary,
    capture_hook_rejects_solver_input_path,
    is_solver_readable_clear_json_capture_path,
)


def test_v094_capture_hook_version_and_defaults_are_fixed() -> None:
    assert LIVE_CLEAR_JSON_CAPTURE_HOOK_VERSION == "v0.9.4"
    assert DEFAULT_LIVE_CLEAR_JSON_FOLDER == "outputs/postflop_live_clear_json"
    assert DEFAULT_LIVE_CLEAR_JSON_FILE_SUFFIX == ".clear.json"
    assert CAPTURE_HOOK_REQUIRED_FIELDS == (
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


def test_v094_capture_hook_mode_labels_are_fixed() -> None:
    assert {mode.value for mode in ClearJsonCaptureHookMode} == {
        "audit_only",
        "existing_project_save_point",
        "hook_required",
        "unknown",
    }


def test_v094_capture_target_status_labels_are_fixed() -> None:
    assert {status.value for status in ClearJsonCaptureTargetStatus} == {
        "not_checked",
        "valid_clear_json_target",
        "missing_clear_folder",
        "invalid_non_clear_target",
        "forbidden_temporary_target",
        "unknown",
    }


def test_v094_default_capture_target_points_to_clear_folder(tmp_path: Path) -> None:
    target = build_default_clear_json_capture_target(tmp_path)
    payload = target.to_json_dict()

    assert isinstance(target, ClearJsonCaptureSaveTarget)
    assert payload["project_root"] == str(tmp_path)
    clear_folder_parts = Path(payload["clear_json_folder"]).parts
    assert clear_folder_parts[-2:] == ("outputs", "postflop_live_clear_json")
    assert payload["file_suffix"] == ".clear.json"
    assert payload["source_type"] == "clear_json"
    json.dumps(payload, sort_keys=True)


def test_v094_capture_file_path_is_deterministic_and_solver_readable(tmp_path: Path) -> None:
    target = build_default_clear_json_capture_target(tmp_path)
    path = build_clear_json_capture_file_path(target, table_id="table_01", hand_id="hand_77", street="flop")

    assert path.endswith("table_01_hand_77_flop.clear.json")
    assert "postflop_live_clear_json" in path
    assert is_solver_readable_clear_json_capture_path(path) is True


def test_v094_capture_target_audit_marks_existing_clear_folder_available(tmp_path: Path) -> None:
    clear_folder = tmp_path / "outputs" / "postflop_live_clear_json"
    clear_folder.mkdir(parents=True)
    target = build_default_clear_json_capture_target(tmp_path)

    audit = audit_clear_json_capture_target(target)
    payload = audit.to_json_dict()

    assert isinstance(audit, ClearJsonCaptureHookAudit)
    assert audit.hook_mode is ClearJsonCaptureHookMode.EXISTING_PROJECT_SAVE_POINT
    assert audit.target_status is ClearJsonCaptureTargetStatus.VALID_CLEAR_JSON_TARGET
    assert audit.clear_json_capture_status is ClearJsonCaptureStatus.CAPTURE_HOOK_AVAILABLE
    assert audit.runtime_click_chain_status is RuntimeClickChainStatus.EXISTING_PROJECT_CHAIN_NOT_INVOKED_BY_AUDIT
    assert payload["accepted_source_types"] == ["clear_json"]
    assert "dark_json" in payload["forbidden_source_types"]
    json.dumps(payload, sort_keys=True)


def test_v094_missing_clear_folder_requires_capture_hook_before_real_live_audit(tmp_path: Path) -> None:
    audit = audit_default_clear_json_capture_hook(tmp_path)
    payload = audit.to_json_dict()

    assert audit.hook_mode is ClearJsonCaptureHookMode.HOOK_REQUIRED
    assert audit.target_status is ClearJsonCaptureTargetStatus.MISSING_CLEAR_FOLDER
    assert audit.clear_json_capture_status is ClearJsonCaptureStatus.CAPTURE_HOOK_REQUIRED
    assert payload["warnings"] == ["clear_json_folder_missing_capture_hook_required_before_real_live_audit"]
    assert payload["writes_runtime_files"] is False
    assert payload["executes_clicks"] is False


def test_v094_forbidden_runtime_target_is_rejected(tmp_path: Path) -> None:
    target = build_default_clear_json_capture_target(tmp_path, clear_json_folder="outputs/current_cycle/runtime_json")
    audit = audit_clear_json_capture_target(target)
    payload = audit.to_json_dict()

    assert audit.hook_mode is ClearJsonCaptureHookMode.HOOK_REQUIRED
    assert audit.target_status is ClearJsonCaptureTargetStatus.FORBIDDEN_TEMPORARY_TARGET
    assert audit.clear_json_capture_status is ClearJsonCaptureStatus.CAPTURE_HOOK_REQUIRED
    assert payload["errors"] == ["capture_target_points_to_forbidden_temporary_or_runtime_area"]


def test_v094_capture_hook_rejects_non_clear_json_solver_input_paths(tmp_path: Path) -> None:
    paths = (
        tmp_path / "dark_json" / "table_01.dark.json",
        tmp_path / "pending_json" / "table_01.pending.json",
        tmp_path / "service_json" / "table_01.service.json",
        tmp_path / "runtime_json" / "table_01.runtime.json",
        tmp_path / "action_decision_json" / "table_01.json",
        tmp_path / "action_runtime_plan_json" / "table_01.json",
        tmp_path / "button_detector" / "table_01.json",
        tmp_path / "unknown" / "table_01.json",
    )

    for path in paths:
        assert capture_hook_rejects_solver_input_path(path) is True
        assert is_solver_readable_clear_json_capture_path(path) is False


def test_v094_capture_policy_summary_is_json_safe_and_clear_only() -> None:
    summary = capture_hook_policy_summary()

    assert summary["hook_version"] == "v0.9.4"
    assert summary["solver_input_policy"] == "clear_json_only"
    assert summary["accepted_source_types"] == ["clear_json"]
    assert set(summary["forbidden_source_types"]) == set(CAPTURE_HOOK_FORBIDDEN_INPUT_LABELS)
    assert summary["runtime_click_chain_policy"] == "existing_project_chain_not_modified"
    assert summary["postflop_solver_click_policy"] == "no_postflop_solver_clicks"
    json.dumps(summary, sort_keys=True)


def test_v094_capture_hook_audit_payload_does_not_create_runtime_or_decision() -> None:
    target = ClearJsonCaptureSaveTarget(
        project_root="C:/PokerVision_Solver_AllPreflop_Flop",
        clear_json_folder="C:/PokerVision_Solver_AllPreflop_Flop/outputs/postflop_live_clear_json",
        source_type=LiveClearJsonSourceType.CLEAR_JSON,
    )
    audit = audit_clear_json_capture_target(target)
    payload = audit.to_json_dict()

    assert payload["solver_input_policy"] == "clear_json_only"
    assert payload["writes_runtime_files"] is False
    assert payload["invokes_action_button"] is False
    assert payload["creates_postflop_decision"] is False
    assert payload["creates_runtime_plan"] is False
    assert payload["executes_clicks"] is False

    forbidden_keys = {
        "action_decision",
        "decision_json",
        "runtime_plan",
        "action_button_target",
        "click_result",
        "click_sequence",
        "physical_click",
        "equity_result",
        "range_assignment",
    }
    assert forbidden_keys.isdisjoint(payload)


def test_v094_capture_hook_module_does_not_run_main_live_or_click_layers() -> None:
    module_text = Path("solver_postflop/live_clear_json_capture_hook.py").read_text(encoding="utf-8")

    forbidden_runtime_tokens = (
        "subprocess",
        "pyautogui",
        "win32api",
        "mouseDown",
        "mouseUp",
        "ActionButtonDetector",
        "send_click",
        "physical_click",
        "main.py",
        "create_runtime_plan",
        "build_equity",
        "PokerKit",
        "range_builder",
    )

    for token in forbidden_runtime_tokens:
        assert token not in module_text


def test_v094_capture_hook_future_modules_are_fixed_metadata_targets() -> None:
    assert CAPTURE_HOOK_FUTURE_MODULES == (
        "live_audit_tool_runner_v095",
        "no_postflop_click_gate_v096",
        "main_live_audit_command_docs_v097",
    )


def test_v094_capture_hook_exports_are_public() -> None:
    import solver_postflop

    for public_name in (
        "CAPTURE_HOOK_FORBIDDEN_INPUT_LABELS",
        "CAPTURE_HOOK_FUTURE_MODULES",
        "CAPTURE_HOOK_REQUIRED_FIELDS",
        "DEFAULT_LIVE_CLEAR_JSON_FILE_SUFFIX",
        "DEFAULT_LIVE_CLEAR_JSON_FOLDER",
        "LIVE_CLEAR_JSON_CAPTURE_HOOK_VERSION",
        "ClearJsonCaptureHookAudit",
        "ClearJsonCaptureHookMode",
        "ClearJsonCaptureSaveTarget",
        "ClearJsonCaptureTargetStatus",
        "audit_clear_json_capture_target",
        "audit_default_clear_json_capture_hook",
        "build_clear_json_capture_file_path",
        "build_default_clear_json_capture_target",
        "capture_hook_policy_summary",
        "capture_hook_rejects_solver_input_path",
        "is_solver_readable_clear_json_capture_path",
    ):
        assert public_name in solver_postflop.__all__
        assert hasattr(solver_postflop, public_name)
