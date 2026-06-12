from __future__ import annotations

from pathlib import Path

DOC_PATH = Path("docs/POSTFLOP_MAIN_LIVE_AUDIT_COMMAND.md")


def _doc() -> str:
    assert DOC_PATH.exists(), "V0.9.7 live audit command document is missing."
    return DOC_PATH.read_text(encoding="utf-8")


def _lower() -> str:
    return _doc().lower()


def test_v097_document_exists_and_declares_scope() -> None:
    text = _doc()
    assert "V0.9.7" in text
    assert "Main/Live Audit Command" in text
    assert "Clear_JSON → SolverInput → Branch Resolver" in text
    assert "Pytest remains safe and non-interactive" in text


def test_v097_documents_existing_project_click_chain_allowed_but_postflop_solver_click_forbidden() -> None:
    text = _lower()
    assert "existing project live click-chain is allowed" in text
    assert "postflop solver click-chain is prohibited" in text
    assert "main.py" in text
    assert "postflop solver only" not in text  # guard against implying solver owns project clicks


def test_v097_contains_real_live_audit_command_phases() -> None:
    text = _doc()
    assert "PHASE 1: RUN EXISTING PROJECT MAIN/LIVE CYCLE" in text
    assert "PHASE 2: RUN POSTFLOP CLEAR_JSON AUDIT" in text
    assert "PHASE 3: VERIFY AUDIT OUTPUT" in text
    assert "tools\\run_postflop_live_clear_json_audit_v090.py" in text
    assert "--clear-json-root" in text
    assert "--output-root" in text
    assert "--max-files 50" in text


def test_v097_documents_clear_json_only_input_policy_and_rejected_sources() -> None:
    text = _lower()
    assert "clear_json-only input policy" in text
    assert "*.clear.json" in text
    for forbidden in (
        "dark_json",
        "pending_json",
        "service_json",
        "runtime_json",
        "action_decision_json",
        "action_runtime_plan_json",
        "button detector json",
    ):
        assert forbidden in text
    assert "must not use dark/pending/service/runtime json as fallback solver input" in text


def test_v097_documents_latest_report_and_expected_output_folders() -> None:
    text = _doc()
    assert "outputs/postflop_live_clear_json_audit_v090/latest_report.json" in text
    for folder in (
        "processed_clear_json/",
        "solver_inputs/",
        "branch_results/",
        "flop_contexts/",
        "board_texture/",
        "made_hand/",
        "draw_features/",
        "module_chain_reports/",
    ):
        assert folder in text


def test_v097_documents_post_run_validation_points() -> None:
    text = _lower()
    for required in (
        "clear_json files were found",
        "branch is present",
        "drawfeatures",
        "non-flop clear_json gets a structured",
        "bad clear_json does not break the full report",
        "fields_used",
        "fields_not_provided",
    ):
        assert required in text


def test_v097_explicitly_forbids_postflop_decision_runtime_and_action_button() -> None:
    text = _lower()
    for forbidden_rule in (
        "does not produce action_decision_json",
        "does not produce action_runtime_plan_json",
        "does not call action_button detector",
        "does not perform physical mouse clicks",
        "does not click",
        "does not launch ui",
    ):
        assert forbidden_rule in text


def test_v097_handoff_requires_real_report_before_version_close() -> None:
    text = _lower()
    assert "handoff to v0.9.8" in text
    assert "run the documented real-live audit locally" in text
    assert "inspect `outputs/postflop_live_clear_json_audit_v090/latest_report.json`" in text
    assert "then close v0.9.0 in v0.9.8" in text
    assert "capture-hook integration fix before closing v0.9.0" in text
