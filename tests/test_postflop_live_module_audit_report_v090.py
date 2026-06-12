from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass

from solver_postflop import (
    CLEAR_JSON_CAPTURE_STATUSES,
    LIVE_AUDIT_MODULE_STATUSES,
    LIVE_AUDIT_REPORT_CONTRACT_VERSION,
    LIVE_AUDIT_REPORT_FUTURE_MODULES,
    LIVE_AUDIT_REQUIRED_REPORT_FIELDS,
    MODULE_CHAIN_STATUSES,
    RUNTIME_CLICK_CHAIN_STATUSES,
    ClearJsonCaptureStatus,
    LiveAuditModuleStatus,
    LiveClearJsonAuditReport,
    LiveModuleAuditReport,
    LiveModuleResult,
    ModuleChainStatus,
    RuntimeClickChainStatus,
    build_not_run_module_result,
)


def _passed_result(module_name: str, payload: dict[str, object]) -> LiveModuleResult:
    return LiveModuleResult(
        module_name=module_name,
        status=LiveAuditModuleStatus.PASSED,
        payload=payload,
        notes=("fixture_contract_result",),
    )


def _sample_report() -> LiveModuleAuditReport:
    return LiveModuleAuditReport(
        source_file="outputs/clear_json/table_01_hand_77.clear.json",
        table_id="table_01",
        hand_id="hand_77",
        branch="flop",
        spot_family="srp_heads_up",
        board_texture_result=_passed_result(
            "board_texture",
            {"volatility_class": "semi_dynamic_board", "texture_tags": ["two_tone"]},
        ),
        made_hand_result=_passed_result(
            "made_hand",
            {"made_hand_class": "one_pair", "pair_class": "top_pair"},
        ),
        draw_result=_passed_result(
            "draw_features",
            {"draw_class": "combo_draw", "draw_strength_tier": "strong_draw"},
        ),
        fields_used=("hero_cards", "board_cards", "players", "pot"),
        fields_not_provided=("effective_stack",),
        module_chain_status=ModuleChainStatus.FLOP_FEATURES_COMPLETED,
        runtime_click_chain_status=RuntimeClickChainStatus.EXISTING_PROJECT_CHAIN_NOT_INVOKED_BY_AUDIT,
        clear_json_capture_status=ClearJsonCaptureStatus.CLEAR_JSON_CAPTURED,
        notes=("postflop_solver_read_only_audit",),
    )


def test_live_audit_report_contract_version_is_fixed_for_v090() -> None:
    assert LIVE_AUDIT_REPORT_CONTRACT_VERSION == "v0.9.0"


def test_live_audit_module_status_labels_are_fixed() -> None:
    assert {status.value for status in LiveAuditModuleStatus} == {
        "not_run",
        "passed",
        "skipped",
        "failed",
        "not_applicable",
        "unknown",
    }
    assert LIVE_AUDIT_MODULE_STATUSES == tuple(LiveAuditModuleStatus)


def test_module_chain_status_labels_are_fixed() -> None:
    assert {status.value for status in ModuleChainStatus} == {
        "not_started",
        "clear_json_loaded",
        "branch_resolved",
        "non_flop_skipped",
        "flop_features_completed",
        "module_error",
        "unknown",
    }
    assert MODULE_CHAIN_STATUSES == tuple(ModuleChainStatus)


def test_runtime_click_chain_status_labels_are_report_metadata_only() -> None:
    assert {status.value for status in RuntimeClickChainStatus} == {
        "not_checked",
        "existing_project_chain_not_invoked_by_audit",
        "existing_project_chain_observed",
        "not_applicable",
        "unknown",
    }
    assert RUNTIME_CLICK_CHAIN_STATUSES == tuple(RuntimeClickChainStatus)


def test_clear_json_capture_status_labels_are_fixed() -> None:
    assert {status.value for status in ClearJsonCaptureStatus} == {
        "not_checked",
        "clear_json_captured",
        "clear_json_missing",
        "capture_hook_required",
        "capture_hook_available",
        "unknown",
    }
    assert CLEAR_JSON_CAPTURE_STATUSES == tuple(ClearJsonCaptureStatus)


def test_live_module_result_can_be_created_and_serialized() -> None:
    result = LiveModuleResult(
        module_name="board_texture",
        status=LiveAuditModuleStatus.PASSED,
        payload={"texture_tags": ("ace_high_dry_rainbow",)},
        warnings=("minor_missing_optional_field",),
    )

    assert is_dataclass(result)
    assert asdict(result)["status"] == LiveAuditModuleStatus.PASSED
    payload = result.to_json_dict()
    assert payload["module_name"] == "board_texture"
    assert payload["status"] == "passed"
    assert payload["payload"]["texture_tags"] == ["ace_high_dry_rainbow"]
    assert payload["warnings"] == ["minor_missing_optional_field"]
    json.dumps(payload, sort_keys=True)


def test_live_module_audit_report_contains_required_v090_fields() -> None:
    report = _sample_report()
    payload = report.to_json_dict()

    assert set(LIVE_AUDIT_REQUIRED_REPORT_FIELDS).issubset(payload)
    assert payload["source_file"].endswith(".clear.json")
    assert payload["table_id"] == "table_01"
    assert payload["hand_id"] == "hand_77"
    assert payload["branch"] == "flop"
    assert payload["spot_family"] == "srp_heads_up"
    assert payload["module_chain_status"] == "flop_features_completed"
    assert payload["runtime_click_chain_status"] == "existing_project_chain_not_invoked_by_audit"
    assert payload["clear_json_capture_status"] == "clear_json_captured"
    assert payload["fields_used"] == ["hero_cards", "board_cards", "players", "pot"]
    assert payload["fields_not_provided"] == ["effective_stack"]
    json.dumps(payload, sort_keys=True)


def test_live_clear_json_audit_report_envelope_serializes_nested_reports() -> None:
    report = _sample_report()
    envelope = LiveClearJsonAuditReport(
        report_version=LIVE_AUDIT_REPORT_CONTRACT_VERSION,
        generated_at="2026-06-12T19:00:00Z",
        source_root="outputs/clear_json",
        reports=(report,),
        total_files_seen=1,
        total_clear_json_processed=1,
        module_chain_status=ModuleChainStatus.FLOP_FEATURES_COMPLETED,
        runtime_click_chain_status=RuntimeClickChainStatus.EXISTING_PROJECT_CHAIN_NOT_INVOKED_BY_AUDIT,
        clear_json_capture_status=ClearJsonCaptureStatus.CLEAR_JSON_CAPTURED,
    )

    payload = envelope.to_json_dict()
    assert payload["report_version"] == "v0.9.0"
    assert payload["total_files_seen"] == 1
    assert payload["total_clear_json_processed"] == 1
    assert payload["reports"][0]["draw_result"]["module_name"] == "draw_features"
    json.dumps(payload, sort_keys=True)


def test_not_run_module_result_factory_is_stable_for_future_v090_stages() -> None:
    result = build_not_run_module_result("draw_features")
    payload = result.to_json_dict()

    assert payload == {
        "module_name": "draw_features",
        "status": "not_run",
        "payload": {},
        "warnings": [],
        "errors": [],
        "notes": ["not_run_yet"],
    }


def test_live_audit_contracts_remain_report_metadata_only() -> None:
    payload = _sample_report().to_json_dict()

    forbidden_keys = {
        "action_decision",
        "decision_json",
        "runtime_plan",
        "action_button_target",
        "button_targets",
        "click_result",
        "click_sequence",
        "physical_click",
        "equity_result",
        "range_assignment",
    }
    assert forbidden_keys.isdisjoint(payload)
    assert forbidden_keys.isdisjoint(payload["board_texture_result"])
    assert forbidden_keys.isdisjoint(payload["made_hand_result"])
    assert forbidden_keys.isdisjoint(payload["draw_result"])


def test_live_audit_future_modules_are_fixed_metadata_targets() -> None:
    assert LIVE_AUDIT_REPORT_FUTURE_MODULES == (
        "live_clear_json_discovery_v092",
        "full_module_pipeline_runner_v093",
        "clear_json_capture_hook_audit_v094",
        "live_audit_tool_runner_v095",
        "no_postflop_click_gate_v096",
        "equity_input_builder_later",
    )


def test_live_audit_contracts_exported_from_public_package() -> None:
    import solver_postflop

    for public_name in (
        "CLEAR_JSON_CAPTURE_STATUSES",
        "LIVE_AUDIT_MODULE_STATUSES",
        "LIVE_AUDIT_REPORT_CONTRACT_VERSION",
        "LIVE_AUDIT_REPORT_FUTURE_MODULES",
        "LIVE_AUDIT_REQUIRED_REPORT_FIELDS",
        "MODULE_CHAIN_STATUSES",
        "RUNTIME_CLICK_CHAIN_STATUSES",
        "ClearJsonCaptureStatus",
        "LiveAuditModuleStatus",
        "LiveClearJsonAuditReport",
        "LiveModuleAuditReport",
        "LiveModuleResult",
        "ModuleChainStatus",
        "RuntimeClickChainStatus",
        "build_not_run_module_result",
    ):
        assert public_name in solver_postflop.__all__
        assert hasattr(solver_postflop, public_name)
