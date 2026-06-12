from __future__ import annotations

import json
from pathlib import Path

from solver_postflop import (
    LIVE_CLEAR_JSON_ALLOWED_SOURCE_TYPES,
    LIVE_CLEAR_JSON_SCAN_FUTURE_MODULES,
    LIVE_CLEAR_JSON_SCAN_VERSION,
    LIVE_CLEAR_JSON_FORBIDDEN_SOURCE_TYPES,
    LiveClearJsonCandidate,
    LiveClearJsonScanResult,
    LiveClearJsonScanStatus,
    LiveClearJsonSkipReason,
    LiveClearJsonSkippedFile,
    LiveClearJsonSourceType,
    classify_live_clear_json_source,
    clear_json_candidate_paths,
    discover_live_clear_json_files,
)


def _write_json(path: Path, payload: dict[str, object] | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload or {"ok": True}), encoding="utf-8")
    return path


def test_live_clear_json_scan_version_is_fixed_for_v092() -> None:
    assert LIVE_CLEAR_JSON_SCAN_VERSION == "v0.9.2"


def test_live_clear_json_source_type_labels_are_fixed() -> None:
    assert {source_type.value for source_type in LiveClearJsonSourceType} == {
        "clear_json",
        "dark_json",
        "pending_json",
        "service_json",
        "runtime_json",
        "action_decision_json",
        "action_runtime_plan_json",
        "button_detector_json",
        "temporary_json",
        "unknown_json",
        "non_json",
    }
    assert LIVE_CLEAR_JSON_ALLOWED_SOURCE_TYPES == (LiveClearJsonSourceType.CLEAR_JSON,)
    assert set(LIVE_CLEAR_JSON_FORBIDDEN_SOURCE_TYPES) == {
        LiveClearJsonSourceType.DARK_JSON,
        LiveClearJsonSourceType.PENDING_JSON,
        LiveClearJsonSourceType.SERVICE_JSON,
        LiveClearJsonSourceType.RUNTIME_JSON,
        LiveClearJsonSourceType.ACTION_DECISION_JSON,
        LiveClearJsonSourceType.ACTION_RUNTIME_PLAN_JSON,
        LiveClearJsonSourceType.BUTTON_DETECTOR_JSON,
        LiveClearJsonSourceType.TEMPORARY_JSON,
    }


def test_live_clear_json_scan_status_labels_are_fixed() -> None:
    assert {status.value for status in LiveClearJsonScanStatus} == {
        "not_started",
        "source_root_missing",
        "no_files_found",
        "clear_json_found",
        "no_clear_json_found",
        "unknown",
    }


def test_live_clear_json_skip_reason_labels_are_fixed() -> None:
    assert {reason.value for reason in LiveClearJsonSkipReason} == {
        "not_json",
        "forbidden_source_type",
        "unknown_json_shape",
        "source_root_missing",
    }


def test_classifies_clear_json_by_filename_and_clear_folder(tmp_path: Path) -> None:
    clear_by_name = _write_json(tmp_path / "table_01_hand_77.clear.json")
    clear_by_folder = _write_json(tmp_path / "clear_json" / "table_02_hand_88.json")
    final_clear = _write_json(tmp_path / "final_clear_json" / "table_03_hand_99.json")

    assert classify_live_clear_json_source(clear_by_name) is LiveClearJsonSourceType.CLEAR_JSON
    assert classify_live_clear_json_source(clear_by_folder) is LiveClearJsonSourceType.CLEAR_JSON
    assert classify_live_clear_json_source(final_clear) is LiveClearJsonSourceType.CLEAR_JSON


def test_classifies_forbidden_live_project_json_types_without_opening_files(tmp_path: Path) -> None:
    cases = {
        "dark_json/table_01.dark.json": LiveClearJsonSourceType.DARK_JSON,
        "pending_json/table_01.pending.json": LiveClearJsonSourceType.PENDING_JSON,
        "service_json/table_01.service.json": LiveClearJsonSourceType.SERVICE_JSON,
        "runtime_json/table_01.runtime.json": LiveClearJsonSourceType.RUNTIME_JSON,
        "action_decision_json/table_01.json": LiveClearJsonSourceType.ACTION_DECISION_JSON,
        "action_runtime_plan_json/table_01.json": LiveClearJsonSourceType.ACTION_RUNTIME_PLAN_JSON,
        "button_detector/table_01.json": LiveClearJsonSourceType.BUTTON_DETECTOR_JSON,
        "current_cycle/table_01.json": LiveClearJsonSourceType.TEMPORARY_JSON,
        "unknown/table_01.json": LiveClearJsonSourceType.UNKNOWN_JSON,
    }

    for relative, expected_source_type in cases.items():
        path = _write_json(tmp_path / relative)
        assert classify_live_clear_json_source(path) is expected_source_type

    text_file = tmp_path / "notes.txt"
    text_file.write_text("not json", encoding="utf-8")
    assert classify_live_clear_json_source(text_file) is LiveClearJsonSourceType.NON_JSON


def test_discovery_returns_only_clear_json_candidates_and_skips_everything_else(tmp_path: Path) -> None:
    accepted_a = _write_json(tmp_path / "clear_json" / "table_01_hand_77.clear.json")
    accepted_b = _write_json(tmp_path / "final_clear_json" / "table_02_hand_88.json")
    _write_json(tmp_path / "dark_json" / "table_01.dark.json")
    _write_json(tmp_path / "pending_json" / "table_01.pending.json")
    _write_json(tmp_path / "service_json" / "table_01.service.json")
    _write_json(tmp_path / "runtime_json" / "table_01.runtime.json")
    _write_json(tmp_path / "action_decision_json" / "table_01.json")
    _write_json(tmp_path / "action_runtime_plan_json" / "table_01.json")
    _write_json(tmp_path / "button_detector" / "table_01.json")
    _write_json(tmp_path / "unknown" / "table_01.json")
    (tmp_path / "readme.md").write_text("ignored", encoding="utf-8")

    result = discover_live_clear_json_files(tmp_path)

    assert result.status is LiveClearJsonScanStatus.CLEAR_JSON_FOUND
    assert result.total_files_seen == 11
    assert result.total_clear_json_candidates == 2
    assert set(clear_json_candidate_paths(result)) == {str(accepted_a), str(accepted_b)}
    assert all(candidate.source_type is LiveClearJsonSourceType.CLEAR_JSON for candidate in result.candidates)
    assert all(skipped.detected_source_type is not LiveClearJsonSourceType.CLEAR_JSON for skipped in result.skipped_files)


def test_discovery_candidate_records_stable_metadata(tmp_path: Path) -> None:
    path = _write_json(tmp_path / "clear_json" / "table_04_hand_123.clear.json")

    result = discover_live_clear_json_files(tmp_path)
    candidate = result.candidates[0]
    payload = candidate.to_json_dict()

    assert isinstance(candidate, LiveClearJsonCandidate)
    assert payload["source_file"] == str(path)
    assert payload["file_name"] == "table_04_hand_123.clear.json"
    assert payload["source_type"] == "clear_json"
    assert payload["table_id"] == "table_04"
    assert payload["hand_id"] == "hand_123"
    assert payload["size_bytes"] > 0
    assert payload["modified_at"]
    assert payload["notes"] == ["clear_json_candidate"]
    json.dumps(payload, sort_keys=True)


def test_skipped_file_records_reason_and_source_type(tmp_path: Path) -> None:
    _write_json(tmp_path / "dark_json" / "table_01.dark.json")
    _write_json(tmp_path / "unknown" / "table_02.json")
    (tmp_path / "notes.txt").write_text("not json", encoding="utf-8")

    result = discover_live_clear_json_files(tmp_path)
    payloads = [skipped.to_json_dict() for skipped in result.skipped_files]

    assert isinstance(result.skipped_files[0], LiveClearJsonSkippedFile)
    assert {payload["detected_source_type"] for payload in payloads} == {
        "dark_json",
        "unknown_json",
        "non_json",
    }
    assert {payload["skip_reason"] for payload in payloads} == {
        "forbidden_source_type",
        "unknown_json_shape",
        "not_json",
    }
    json.dumps(payloads, sort_keys=True)


def test_discovery_can_skip_non_json_without_reporting_them(tmp_path: Path) -> None:
    _write_json(tmp_path / "clear_json" / "table_01_hand_1.clear.json")
    (tmp_path / "readme.md").write_text("not json", encoding="utf-8")

    result = discover_live_clear_json_files(tmp_path, include_non_json_skips=False)

    assert result.total_files_seen == 2
    assert result.total_clear_json_candidates == 1
    assert result.skipped_files == ()


def test_discovery_missing_root_returns_structured_result_without_exception(tmp_path: Path) -> None:
    missing_root = tmp_path / "missing_clear_root"

    result = discover_live_clear_json_files(missing_root)
    payload = result.to_json_dict()

    assert isinstance(result, LiveClearJsonScanResult)
    assert result.status is LiveClearJsonScanStatus.SOURCE_ROOT_MISSING
    assert result.total_files_seen == 0
    assert result.total_clear_json_candidates == 0
    assert payload["status"] == "source_root_missing"
    assert payload["skipped_files"][0]["skip_reason"] == "source_root_missing"
    json.dumps(payload, sort_keys=True)


def test_discovery_empty_root_and_unknown_json_root_statuses_are_stable(tmp_path: Path) -> None:
    empty_result = discover_live_clear_json_files(tmp_path)
    assert empty_result.status is LiveClearJsonScanStatus.NO_FILES_FOUND

    _write_json(tmp_path / "unknown" / "table_01.json")
    unknown_result = discover_live_clear_json_files(tmp_path)
    assert unknown_result.status is LiveClearJsonScanStatus.NO_CLEAR_JSON_FOUND
    assert unknown_result.total_clear_json_candidates == 0


def test_discovery_is_deterministic_and_supports_non_recursive_scan(tmp_path: Path) -> None:
    _write_json(tmp_path / "b_table_02.clear.json")
    _write_json(tmp_path / "a_table_01.clear.json")
    _write_json(tmp_path / "nested" / "c_table_03.clear.json")

    recursive_result = discover_live_clear_json_files(tmp_path)
    non_recursive_result = discover_live_clear_json_files(tmp_path, recursive=False)

    assert [Path(path).name for path in clear_json_candidate_paths(recursive_result)] == [
        "a_table_01.clear.json",
        "b_table_02.clear.json",
        "c_table_03.clear.json",
    ]
    assert [Path(path).name for path in clear_json_candidate_paths(non_recursive_result)] == [
        "a_table_01.clear.json",
        "b_table_02.clear.json",
    ]


def test_v092_discovery_module_does_not_run_pipeline_or_live_click_layers() -> None:
    module_text = Path("solver_postflop/live_clear_json_integration.py").read_text(encoding="utf-8")

    forbidden_runtime_tokens = (
        "subprocess",
        "pyautogui",
        "win32api",
        "mouseDown",
        "mouseUp",
        "ActionButtonDetector",
        "send_click",
        "physical_click",
    )
    forbidden_pipeline_imports = (
        "build_solver_input",
        "resolve_solver_branch",
        "build_flop_context",
        "build_board_texture_features",
        "build_made_hand_features",
        "build_draw_features",
        "load_clear_json_input(",
    )

    for token in forbidden_runtime_tokens + forbidden_pipeline_imports:
        assert token not in module_text


def test_live_clear_json_scan_future_modules_are_fixed_metadata_targets() -> None:
    assert LIVE_CLEAR_JSON_SCAN_FUTURE_MODULES == (
        "full_module_pipeline_runner_v093",
        "clear_json_capture_hook_audit_v094",
        "live_audit_tool_runner_v095",
        "no_postflop_click_gate_v096",
    )


def test_live_clear_json_scan_exports_are_public() -> None:
    import solver_postflop

    for public_name in (
        "LIVE_CLEAR_JSON_ALLOWED_SOURCE_TYPES",
        "LIVE_CLEAR_JSON_SCAN_FUTURE_MODULES",
        "LIVE_CLEAR_JSON_SCAN_VERSION",
        "LIVE_CLEAR_JSON_FORBIDDEN_SOURCE_TYPES",
        "LiveClearJsonCandidate",
        "LiveClearJsonScanResult",
        "LiveClearJsonScanStatus",
        "LiveClearJsonSkipReason",
        "LiveClearJsonSkippedFile",
        "LiveClearJsonSourceType",
        "classify_live_clear_json_source",
        "clear_json_candidate_paths",
        "discover_live_clear_json_files",
    ):
        assert public_name in solver_postflop.__all__
        assert hasattr(solver_postflop, public_name)
