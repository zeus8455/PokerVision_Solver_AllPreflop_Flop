from __future__ import annotations

import dataclasses
import json
from copy import deepcopy

from solver_postflop import (
    CLEAR_JSON_FIELD_MAPPINGS,
    FIELD_MAPPING_VERSION,
    ClearJsonInput,
    FieldUsageRecord,
    FieldUsageStatus,
    FieldUsageTrace,
    FutureSolverModule,
    build_field_usage_trace,
    build_solver_input,
    get_mapping_for_solver_input_field,
)


def _clear_input_with_extra_field() -> ClearJsonInput:
    raw_data = {
        "case_id": "field_usage_trace_case_001",
        "table_id": "table_01",
        "hand_id": "hand_001",
        "hero_cards": ["As", "Kd"],
        "board_cards": ["Ah", "7c", "2d"],
        "players": [
            {"id": "hero", "position": "BTN", "stack": 100.0},
            {"id": "villain", "position": "BB", "stack": 100.0},
        ],
        "total_pot": 5.5,
        "to_call": 0.0,
        "allowed_actions": ["check", "bet"],
        "action_context": {"spot": "check_option"},
        "pot_type": "srp",
        "not_described_debug_field": {"kept": True},
    }
    return ClearJsonInput(
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/field_usage_trace_case_001.clear.json",
        raw_data=raw_data,
        loaded_at="2026-06-11T00:00:00+00:00",
        case_id="field_usage_trace_case_001",
        hand_id="hand_001",
        table_id="table_01",
    )


def test_field_usage_trace_contracts_create_serializable_trace() -> None:
    clear_input = _clear_input_with_extra_field()
    solver_input, _solver_trace = build_solver_input(clear_input)

    trace = build_field_usage_trace(clear_input, solver_input)

    assert isinstance(trace, FieldUsageTrace)
    assert dataclasses.is_dataclass(trace)
    assert trace.case_id == "field_usage_trace_case_001"
    assert trace.source_file == clear_input.source_file
    assert trace.mapping_version == FIELD_MAPPING_VERSION == "v0.3.0"
    assert trace.records

    payload = json.loads(json.dumps(trace.to_json_dict(), sort_keys=True))
    assert payload["case_id"] == "field_usage_trace_case_001"
    assert payload["mapping_version"] == "v0.3.0"
    assert payload["records"]


def test_fields_used_and_not_provided_are_populated_from_mapping_contract() -> None:
    clear_input = _clear_input_with_extra_field()
    solver_input, _solver_trace = build_solver_input(clear_input)

    trace = build_field_usage_trace(clear_input, solver_input)

    assert "hero_cards" in trace.fields_used
    assert "board_cards" in trace.fields_used
    assert "players" in trace.fields_used
    assert "pot" in trace.fields_used
    assert "allowed_actions" in trace.fields_used
    assert "action_context" in trace.fields_used
    assert "pot_type" in trace.fields_used

    assert "source_timestamp" in trace.fields_not_provided
    assert "preflop_context_raw" in trace.fields_not_provided
    assert "preflop_aggressor" in trace.fields_not_provided
    assert "hero_preflop_role" in trace.fields_not_provided


def test_unknown_clear_json_fields_are_reported_as_ignored() -> None:
    clear_input = _clear_input_with_extra_field()
    solver_input, _solver_trace = build_solver_input(clear_input)

    trace = build_field_usage_trace(clear_input, solver_input)

    assert trace.fields_ignored == ("not_described_debug_field",)

    ignored_records = [record for record in trace.records if record.status == FieldUsageStatus.IGNORED]
    assert len(ignored_records) == 1
    assert ignored_records[0].clear_json_fields == ("not_described_debug_field",)
    assert ignored_records[0].solver_input_field == ""


def test_future_modules_enabled_are_derived_from_used_contract_fields() -> None:
    clear_input = _clear_input_with_extra_field()
    solver_input, _solver_trace = build_solver_input(clear_input)

    trace = build_field_usage_trace(clear_input, solver_input)

    assert FutureSolverModule.BRANCH_RESOLVER.value in trace.future_modules_enabled
    assert FutureSolverModule.FLOP_CONTEXT_BUILDER.value in trace.future_modules_enabled
    assert FutureSolverModule.HAND_STRENGTH_LATER.value in trace.future_modules_enabled
    assert FutureSolverModule.DECISION_AVAILABILITY_LATER.value in trace.future_modules_enabled


def test_each_used_record_is_linked_to_field_mapping_contract() -> None:
    clear_input = _clear_input_with_extra_field()
    solver_input, _solver_trace = build_solver_input(clear_input)

    trace = build_field_usage_trace(clear_input, solver_input)
    contract_targets = {entry.solver_input_field for entry in CLEAR_JSON_FIELD_MAPPINGS}

    for record in trace.records:
        assert isinstance(record, FieldUsageRecord)
        assert dataclasses.is_dataclass(record)
        if record.status is FieldUsageStatus.IGNORED:
            continue
        assert record.solver_input_field in contract_targets
        contract_entry = get_mapping_for_solver_input_field(record.solver_input_field)
        assert record.clear_json_fields == contract_entry.clear_json_fields
        assert record.requirement == contract_entry.requirement
        assert record.future_modules == contract_entry.future_modules


def test_field_usage_trace_keeps_raw_clear_json_reference_and_does_not_mutate_payload() -> None:
    clear_input = _clear_input_with_extra_field()
    before = deepcopy(clear_input.raw_data)
    solver_input, _solver_trace = build_solver_input(clear_input)

    trace = build_field_usage_trace(clear_input, solver_input)

    assert solver_input.raw_clear_json_ref is clear_input.raw_data
    assert clear_input.raw_data == before
    assert solver_input.raw_clear_json_ref == before
    assert "original Clear JSON object" in " ".join(trace.notes)


def test_field_usage_record_json_dict_uses_plain_values() -> None:
    clear_input = _clear_input_with_extra_field()
    solver_input, _solver_trace = build_solver_input(clear_input)

    trace = build_field_usage_trace(clear_input, solver_input)
    first_record = trace.records[0]
    payload = first_record.to_json_dict()

    assert isinstance(payload["requirement"], str)
    assert isinstance(payload["status"], str)
    assert all(isinstance(module, str) for module in payload["future_modules"])
    json.dumps(payload, sort_keys=True)


def test_field_usage_trace_text_has_no_action_or_source_pipeline_markers() -> None:
    trace_source = "\n".join(
        [
            FieldUsageStatus.USED.value,
            FieldUsageStatus.NOT_PROVIDED.value,
            FieldUsageStatus.IGNORED.value,
        ]
    )

    forbidden = (
        "Dark_JSON",
        "Pending_JSON",
        "Service JSON",
        "Runtime JSON",
        "source_discovery",
        "display_analysis_cycle",
        "Action_Button",
        "PokerVisionFinalVersionNoSolver_snapshot",
    )

    for marker in forbidden:
        assert marker not in trace_source
