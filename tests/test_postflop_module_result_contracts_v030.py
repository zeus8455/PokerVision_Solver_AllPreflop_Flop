import json

import pytest

from solver_postflop.contracts import (
    ContractValidationError,
    ModuleError,
    ModuleWarning,
    NormalizationStatus,
    PostflopConfidence,
    PostflopDecision,
    PostflopDecisionAction,
    PostflopProbeReport,
    PostflopRuntimePlan,
    PostflopSourceCandidate,
    PostflopSourceType,
    PostflopTrace,
    PreflopHistoryResult,
    PreflopHistoryStatus,
    ProbeReportStatus,
    RawSourceLoadStatus,
    RuntimeGuardStatus,
    StreetDetectionResult,
    StreetName,
)


def test_v034_module_result_enums_are_stable():
    assert StreetName.values() == ["preflop", "flop", "turn", "river", "unknown", "invalid"]
    assert PreflopHistoryStatus.values() == ["available", "partial", "missing", "unknown", "pending"]
    assert PostflopDecisionAction.values() == ["fold", "check", "call", "bet", "raise", "none", "unknown"]
    assert RuntimeGuardStatus.values() == ["safe", "blocked", "not_required", "unknown", "pending"]
    assert ProbeReportStatus.values() == ["ok", "partial", "failed", "empty", "unknown"]


def test_v034_street_detection_result_is_structured_and_serializable():
    result = StreetDetectionResult(
        street="flop",
        board_card_count=3,
        is_valid=True,
        source_file="tests/fixtures/postflop/source_json/dark_json/flop_source_case_001.dark.json",
        source_type=PostflopSourceType.DARK_JSON,
        reason="board_cards_count_is_3",
    )

    payload = result.to_dict()

    assert payload["street"] == "flop"
    assert payload["board_card_count"] == 3
    assert payload["is_valid"] is True
    assert payload["source_type"] == "dark_json"
    assert payload["reason"] == "board_cards_count_is_3"
    json.dumps(payload)


def test_v034_invalid_street_detection_result_preserves_error_code_and_warnings():
    result = StreetDetectionResult(
        street="invalid",
        board_card_count=2,
        is_valid=False,
        error_code="invalid_board_card_count",
        warnings=[ModuleWarning(code="street_invalid", message="Board has 2 cards.")],
        reason="board_cards_count_is_2",
    )

    payload = result.to_dict()

    assert payload["street"] == "invalid"
    assert payload["is_valid"] is False
    assert payload["error_code"] == "invalid_board_card_count"
    assert payload["warnings"][0]["code"] == "street_invalid"


def test_v034_street_detection_rejects_bad_street_or_negative_count():
    with pytest.raises(ContractValidationError):
        StreetDetectionResult(street="bad_street", board_card_count=3)

    with pytest.raises(ContractValidationError):
        StreetDetectionResult(street="flop", board_card_count=-1)


def test_v034_preflop_history_result_can_be_unknown_or_pending():
    pending = PreflopHistoryResult(
        status="pending",
        line_type="unknown",
        warnings=[{"code": "history_not_loaded", "message": "History module is not implemented yet."}],
        raw_history={"source": "future"},
    )

    payload = pending.to_dict()

    assert payload["status"] == "pending"
    assert payload["line_type"] == "unknown"
    assert payload["warnings"][0]["code"] == "history_not_loaded"
    assert payload["raw_history"] == {"source": "future"}


def test_v034_preflop_history_result_validates_flags_and_status():
    with pytest.raises(ContractValidationError):
        PreflopHistoryResult(status="bad_status")

    with pytest.raises(ContractValidationError):
        PreflopHistoryResult(three_bet_detected="yes")


def test_v034_postflop_decision_is_contract_only_not_solver_logic():
    decision = PostflopDecision(
        decision_id="decision_001",
        action="unknown",
        confidence=PostflopConfidence.UNKNOWN,
        reason="solver_not_implemented_in_v034",
    )

    payload = decision.to_dict()

    assert payload["decision_id"] == "decision_001"
    assert payload["action"] == "unknown"
    assert payload["confidence"] == "unknown"
    assert payload["amount"] is None
    assert payload["reason"] == "solver_not_implemented_in_v034"


def test_v034_postflop_decision_rejects_bad_action_or_negative_amount():
    with pytest.raises(ContractValidationError):
        PostflopDecision(decision_id="d1", action="jam")

    with pytest.raises(ContractValidationError):
        PostflopDecision(decision_id="d1", action="bet", amount=-1)


def test_v034_runtime_plan_is_contract_only_and_does_not_execute_click():
    plan = PostflopRuntimePlan(
        decision_id="decision_001",
        planned_action="raise",
        button_sequence=["50%", "Raise"],
        requires_click=True,
        is_click_safe=False,
        guard_status="blocked",
        warnings=[ModuleWarning(code="runtime_not_connected", message="Runtime bridge is future work.")],
    )

    payload = plan.to_dict()

    assert payload["planned_action"] == "raise"
    assert payload["button_sequence"] == ["50%", "Raise"]
    assert payload["requires_click"] is True
    assert payload["is_click_safe"] is False
    assert payload["guard_status"] == "blocked"


def test_v034_runtime_plan_rejects_bad_guard_status():
    with pytest.raises(ContractValidationError):
        PostflopRuntimePlan(decision_id="decision_001", guard_status="unsafe")


def test_v034_trace_collects_chain_objects_and_serializes():
    candidate = PostflopSourceCandidate(
        source_file="tests/fixtures/postflop/source_json/dark_json/flop_source_case_001.dark.json",
        source_type="dark_json",
        table_id="table_01",
        hand_id="hand_001",
        has_board_cards=True,
        has_hero_cards=True,
        has_players=True,
        can_be_normalized=True,
        confidence="medium",
    )
    street = StreetDetectionResult(street="flop", board_card_count=3, reason="board_cards_count_is_3")
    history = PreflopHistoryResult(status="unknown")
    decision = PostflopDecision(decision_id="decision_001", action="unknown")
    plan = PostflopRuntimePlan(decision_id="decision_001", guard_status="pending")

    trace = PostflopTrace(
        source_candidate=candidate,
        raw_source_status=RawSourceLoadStatus.LOADED,
        normalized_frame_status=NormalizationStatus.PARTIAL,
        street_result=street,
        preflop_history_result=history,
        decision=decision,
        runtime_plan=plan,
        warnings=[ModuleWarning(code="trace_partial", message="Trace is partial in V0.3.4.")],
    )

    payload = trace.to_dict()

    assert payload["source_candidate"]["source_type"] == "dark_json"
    assert payload["raw_source_status"] == "loaded"
    assert payload["normalized_frame_status"] == "partial"
    assert payload["street_result"]["street"] == "flop"
    assert payload["decision"]["action"] == "unknown"
    json.dumps(payload)


def test_v034_trace_rejects_wrong_nested_types():
    with pytest.raises(ContractValidationError):
        PostflopTrace(street_result={"street": "flop"})


def test_v034_probe_report_serializes_traces_and_counts():
    trace = PostflopTrace(
        raw_source_status="loaded",
        normalized_frame_status="partial",
        street_result=StreetDetectionResult(street="flop", board_card_count=3),
    )
    report = PostflopProbeReport(
        report_id="probe_001",
        created_at="2026-06-09T21:30:00Z",
        status="partial",
        input_root="tests/fixtures/postflop",
        source_count=1,
        valid_frame_count=1,
        trace_count=1,
        traces=[trace],
        errors=[ModuleError(code="future_module_missing", message="Source discovery is not implemented in V0.3.4.")],
    )

    payload = report.to_dict()

    assert payload["report_id"] == "probe_001"
    assert payload["status"] == "partial"
    assert payload["source_count"] == 1
    assert payload["trace_count"] == 1
    assert payload["errors"][0]["code"] == "future_module_missing"
    assert payload["traces"][0]["street_result"]["street"] == "flop"
    json.dumps(payload)


def test_v034_probe_report_rejects_bad_counts_or_bad_trace_type():
    with pytest.raises(ContractValidationError):
        PostflopProbeReport(report_id="probe", source_count=-1)

    with pytest.raises(ContractValidationError):
        PostflopProbeReport(report_id="probe", traces=[{"bad": "trace"}])
