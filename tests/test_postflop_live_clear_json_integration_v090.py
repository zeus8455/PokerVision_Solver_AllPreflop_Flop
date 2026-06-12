from __future__ import annotations

import json
from pathlib import Path

from solver_postflop import (
    LIVE_CLEAR_JSON_ALLOWED_SOURCE_TYPES,
    LIVE_CLEAR_JSON_SCAN_FUTURE_MODULES,
    LIVE_CLEAR_JSON_SCAN_VERSION,
    LIVE_CLEAR_JSON_PIPELINE_MODULE_CHAIN,
    LIVE_CLEAR_JSON_PIPELINE_VERSION,
    LIVE_CLEAR_JSON_FORBIDDEN_SOURCE_TYPES,
    LiveClearJsonCandidate,
    LiveClearJsonScanResult,
    LiveClearJsonScanStatus,
    LiveClearJsonSkipReason,
    LiveClearJsonSkippedFile,
    LiveClearJsonSourceType,
    ModuleChainStatus,
    LiveAuditModuleStatus,
    RuntimeClickChainStatus,
    audit_live_clear_json_file,
    audit_live_clear_json_root,
    audit_live_clear_json_scan_result,
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


def test_v093_pipeline_module_does_not_run_main_live_or_click_layers() -> None:
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
        "main.py",
    )

    for token in forbidden_runtime_tokens:
        assert token not in module_text

    required_pipeline_tokens = (
        "build_solver_input",
        "resolve_solver_branch",
        "build_flop_context",
        "build_board_texture_features",
        "build_made_hand_features",
        "build_draw_features",
        "load_clear_json_input",
    )
    for token in required_pipeline_tokens:
        assert token in module_text


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



def _flop_clear_json_payload(
    *,
    case_id: str = "flop_live_like_case",
    board_cards: list[str] | None = None,
    action_context_label: str = "srp heads_up",
) -> dict[str, object]:
    return {
        "case_id": case_id,
        "table_id": "table_01",
        "hand_id": "hand_200",
        "hero_id": "hero",
        "hero_position": "BTN",
        "hero_cards": ["As", "Ks"],
        "board_cards": board_cards if board_cards is not None else ["Qs", "Js", "2d"],
        "players": [
            {"id": "hero", "position": "BTN", "hero": True},
            {"id": "villain_1", "position": "BB", "hero": False},
        ],
        "positions": {"hero": "BTN", "villain_1": "BB"},
        "total_pot": 7.5,
        "to_call": 0,
        "stacks": {"hero": 95.0, "villain_1": 92.0},
        "allowed_actions": ["check", "bet"],
        "action_context": {
            "spot_family": action_context_label,
            "current_actor": "hero",
            "can_check": True,
            "can_bet": True,
        },
    }


def test_v093_pipeline_version_and_chain_are_fixed() -> None:
    assert LIVE_CLEAR_JSON_PIPELINE_VERSION == "v0.9.3"
    assert LIVE_CLEAR_JSON_PIPELINE_MODULE_CHAIN == (
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


def test_v093_audit_live_clear_json_file_runs_full_flop_pipeline(tmp_path: Path) -> None:
    source = _write_json(tmp_path / "clear_json" / "table_01_hand_200.clear.json", _flop_clear_json_payload())

    report = audit_live_clear_json_file(source)
    payload = report.to_json_dict()

    assert report.module_chain_status is ModuleChainStatus.FLOP_FEATURES_COMPLETED
    assert report.runtime_click_chain_status is RuntimeClickChainStatus.EXISTING_PROJECT_CHAIN_NOT_INVOKED_BY_AUDIT
    assert payload["source_file"] == str(source)
    assert payload["table_id"] == "table_01"
    assert payload["hand_id"] == "hand_200"
    assert payload["branch"] == "flop"
    assert payload["spot_family"] == "srp_heads_up"
    assert payload["board_texture_result"]["status"] == "passed"
    assert payload["made_hand_result"]["status"] == "passed"
    assert payload["draw_result"]["status"] == "passed"
    assert payload["draw_result"]["payload"]["draw_strength_tier"] in {
        "medium_draw",
        "strong_draw",
        "premium_combo_draw",
    }
    assert "raw_data->raw_clear_json_ref" in payload["fields_used"]
    json.dumps(payload, sort_keys=True)


def test_v093_audit_live_clear_json_root_processes_discovered_clear_json_only(tmp_path: Path) -> None:
    accepted = _write_json(tmp_path / "clear_json" / "table_01_hand_200.clear.json", _flop_clear_json_payload())
    _write_json(tmp_path / "dark_json" / "table_01.dark.json", {"board_cards": ["Qs", "Js", "2d"]})
    _write_json(tmp_path / "runtime_json" / "table_01.runtime.json", {"board_cards": ["Qs", "Js", "2d"]})
    _write_json(tmp_path / "unknown" / "table_01.json", {"board_cards": ["Qs", "Js", "2d"]})

    envelope = audit_live_clear_json_root(tmp_path)
    payload = envelope.to_json_dict()

    assert envelope.report_version == "v0.9.3"
    assert envelope.total_files_seen == 4
    assert envelope.total_clear_json_processed == 1
    assert payload["reports"][0]["source_file"] == str(accepted)
    assert payload["reports"][0]["branch"] == "flop"
    assert payload["runtime_click_chain_status"] == "existing_project_chain_not_invoked_by_audit"
    json.dumps(payload, sort_keys=True)


def test_v093_audit_scan_result_does_not_process_skipped_files(tmp_path: Path) -> None:
    _write_json(tmp_path / "clear_json" / "table_01_hand_200.clear.json", _flop_clear_json_payload())
    _write_json(tmp_path / "action_decision_json" / "table_01.json", {"action": "bet"})
    _write_json(tmp_path / "button_detector" / "table_01.json", {"button": "Raise"})

    scan_result = discover_live_clear_json_files(tmp_path)
    envelope = audit_live_clear_json_scan_result(scan_result)

    assert scan_result.total_clear_json_candidates == 1
    assert len(scan_result.skipped_files) == 2
    assert envelope.total_clear_json_processed == 1
    assert len(envelope.reports) == 1
    assert envelope.reports[0].module_chain_status is ModuleChainStatus.FLOP_FEATURES_COMPLETED


def test_v093_non_flop_clear_json_returns_structured_skipped_report(tmp_path: Path) -> None:
    source = _write_json(
        tmp_path / "clear_json" / "table_02_hand_201.clear.json",
        _flop_clear_json_payload(case_id="preflop_case", board_cards=[]),
    )

    report = audit_live_clear_json_file(source)
    payload = report.to_json_dict()

    assert report.module_chain_status is ModuleChainStatus.NON_FLOP_SKIPPED
    assert payload["branch"] == "preflop_not_handled"
    assert payload["spot_family"] is None
    assert payload["board_texture_result"]["status"] == "skipped"
    assert payload["made_hand_result"]["status"] == "skipped"
    assert payload["draw_result"]["status"] == "skipped"


def test_v093_unsupported_board_count_returns_structured_skipped_report(tmp_path: Path) -> None:
    source = _write_json(
        tmp_path / "clear_json" / "table_03_hand_202.clear.json",
        _flop_clear_json_payload(case_id="unsupported_case", board_cards=["Qs"]),
    )

    report = audit_live_clear_json_file(source)
    payload = report.to_json_dict()

    assert report.module_chain_status is ModuleChainStatus.NON_FLOP_SKIPPED
    assert payload["branch"] == "unsupported"
    assert payload["draw_result"]["status"] == "skipped"


def test_v093_bad_clear_json_file_returns_module_error_report_without_exception(tmp_path: Path) -> None:
    source = tmp_path / "clear_json" / "table_04_hand_203.clear.json"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("{bad json", encoding="utf-8")

    report = audit_live_clear_json_file(source)
    payload = report.to_json_dict()

    assert report.module_chain_status is ModuleChainStatus.MODULE_ERROR
    assert payload["branch"] == "unknown"
    assert payload["board_texture_result"]["status"] == "failed"
    assert payload["errors"]
    json.dumps(payload, sort_keys=True)


def test_v093_pipeline_reports_multiway_flop_context_without_rebuilding_players(tmp_path: Path) -> None:
    payload = _flop_clear_json_payload(case_id="multiway_case", action_context_label="multiway")
    payload["players"] = [
        {"id": "hero", "position": "CO", "hero": True},
        {"id": "villain_1", "position": "BTN", "hero": False},
        {"id": "villain_2", "position": "BB", "hero": False},
    ]
    source = _write_json(tmp_path / "clear_json" / "table_05_hand_204.clear.json", payload)

    report = audit_live_clear_json_file(source)
    report_payload = report.to_json_dict()

    assert report_payload["branch"] == "flop"
    assert report_payload["spot_family"] == "multiway_pot"
    assert report_payload["module_chain_status"] == "flop_features_completed"


def test_v093_pipeline_envelope_status_prefers_module_error_when_any_candidate_fails(tmp_path: Path) -> None:
    _write_json(tmp_path / "clear_json" / "table_01_hand_200.clear.json", _flop_clear_json_payload())
    bad = tmp_path / "clear_json" / "table_02_hand_201.clear.json"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text("not-json", encoding="utf-8")

    envelope = audit_live_clear_json_root(tmp_path)

    assert envelope.total_clear_json_processed == 2
    assert envelope.module_chain_status is ModuleChainStatus.MODULE_ERROR
    assert {report.module_chain_status for report in envelope.reports} == {
        ModuleChainStatus.FLOP_FEATURES_COMPLETED,
        ModuleChainStatus.MODULE_ERROR,
    }


def test_v093_pipeline_exports_are_public() -> None:
    import solver_postflop

    for public_name in (
        "LIVE_CLEAR_JSON_PIPELINE_MODULE_CHAIN",
        "LIVE_CLEAR_JSON_PIPELINE_VERSION",
        "ModuleChainStatus",
        "LiveAuditModuleStatus",
        "RuntimeClickChainStatus",
        "audit_live_clear_json_candidate",
        "audit_live_clear_json_file",
        "audit_live_clear_json_root",
        "audit_live_clear_json_scan_result",
    ):
        assert public_name in solver_postflop.__all__
        assert hasattr(solver_postflop, public_name)
