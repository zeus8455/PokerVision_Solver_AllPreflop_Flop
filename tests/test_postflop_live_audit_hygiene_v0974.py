from __future__ import annotations

from pathlib import Path

from tools.run_postflop_live_clear_json_audit_v090 import (
    LIVE_CLEAR_JSON_AUDIT_EVIDENCE_STATUS_FAILED,
    LIVE_CLEAR_JSON_AUDIT_EVIDENCE_STATUS_PASSED,
    LIVE_CLEAR_JSON_AUDIT_EXPECTED_MODULE_CHAIN_STATUS,
    LIVE_CLEAR_JSON_AUDIT_EXPECTED_RUNTIME_CLICK_CHAIN_STATUS,
    LiveClearJsonAuditToolConfig,
    LiveClearJsonAuditToolResult,
    build_live_clear_json_audit_evidence_checks,
    evaluate_live_clear_json_audit_evidence,
)


def _base_result(**overrides: object) -> LiveClearJsonAuditToolResult:
    payload = {
        "tool_version": "v0.9.5",
        "config": LiveClearJsonAuditToolConfig(project_root=".", clear_json_root="clear", output_root="out"),
        "latest_report_file": "out/latest_report.json",
        "output_root": "out",
        "total_files_seen": 4,
        "total_clear_json_processed": 4,
        "module_chain_status": LIVE_CLEAR_JSON_AUDIT_EXPECTED_MODULE_CHAIN_STATUS,
        "runtime_click_chain_status": LIVE_CLEAR_JSON_AUDIT_EXPECTED_RUNTIME_CLICK_CHAIN_STATUS,
        "clear_json_capture_status": "not_checked",
        "artifacts_written": {
            "processed_clear_json": 4,
            "solver_inputs": 4,
            "branch_results": 4,
            "flop_contexts": 2,
            "board_texture": 2,
            "made_hand": 2,
            "draw_features": 2,
            "module_chain_reports": 4,
        },
        "errors": (),
        "notes": (),
    }
    payload.update(overrides)
    return LiveClearJsonAuditToolResult(**payload)  # type: ignore[arg-type]


def test_v0974_audit_runner_bootstraps_project_root_before_solver_imports() -> None:
    source_text = Path("tools/run_postflop_live_clear_json_audit_v090.py").read_text(encoding="utf-8")

    assert "def _bootstrap_project_root_import_path" in source_text
    assert "Path(__file__).resolve().parents[1]" in source_text
    assert "sys.path.insert(0, project_root_text)" in source_text
    assert source_text.index("_BOOTSTRAPPED_PROJECT_ROOT") < source_text.index("from solver_postflop.board_texture")


def test_v0974_evidence_checklist_passes_only_for_real_flop_feature_evidence() -> None:
    result = _base_result()
    checks = build_live_clear_json_audit_evidence_checks(result)

    assert checks == {
        "total_files_seen_gt_0": True,
        "total_clear_json_processed_gt_0": True,
        "module_chain_status_flop_features_completed": True,
        "board_texture_gt_0": True,
        "made_hand_gt_0": True,
        "draw_features_gt_0": True,
        "runtime_click_chain_status_audit_only": True,
        "errors_empty": True,
    }
    assert evaluate_live_clear_json_audit_evidence(result) == LIVE_CLEAR_JSON_AUDIT_EVIDENCE_STATUS_PASSED


def test_v0974_evidence_checklist_fails_when_feature_artifacts_are_missing() -> None:
    result = _base_result(
        total_files_seen=1,
        total_clear_json_processed=1,
        artifacts_written={
            "processed_clear_json": 1,
            "solver_inputs": 1,
            "branch_results": 1,
            "flop_contexts": 0,
            "board_texture": 0,
            "made_hand": 0,
            "draw_features": 0,
            "module_chain_reports": 1,
        },
    )
    checks = build_live_clear_json_audit_evidence_checks(result)

    assert checks["board_texture_gt_0"] is False
    assert checks["made_hand_gt_0"] is False
    assert checks["draw_features_gt_0"] is False
    assert evaluate_live_clear_json_audit_evidence(result) == LIVE_CLEAR_JSON_AUDIT_EVIDENCE_STATUS_FAILED


def test_v0974_live_runner_uses_neutral_capture_label() -> None:
    source_text = Path("tools/run_live_main_with_postflop_capture_v0972.py").read_text(encoding="utf-8")

    assert "capture runner install status" in source_text
    assert "V0.9.7.2 install status" not in source_text


def test_v0974_docs_clean_stale_capture_and_define_evidence_gate() -> None:
    doc_text = Path("docs/POSTFLOP_MAIN_LIVE_AUDIT_COMMAND.md").read_text(encoding="utf-8")

    assert "Remove-Item \"outputs\\postflop_live_clear_json_audit_v090\"" in doc_text
    assert "Remove-Item \"external\\PokerVisionFinalVersionNoSolver_snapshot\\PokerVision V1_2\\outputs\\postflop_live_clear_json\"" in doc_text
    assert "$env:PYTHONPATH" not in doc_text
    assert "total_files_seen > 0" in doc_text
    assert "module_chain_status = flop_features_completed" in doc_text
    assert "artifacts_written.board_texture > 0" in doc_text
    assert "artifacts_written.made_hand > 0" in doc_text
    assert "artifacts_written.draw_features > 0" in doc_text
    assert "runtime_click_chain_status = existing_project_chain_not_invoked_by_audit" in doc_text
    assert "evidence_status = passed" in doc_text
