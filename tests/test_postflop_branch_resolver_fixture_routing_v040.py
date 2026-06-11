from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from solver_postflop import (
    build_solver_input,
    load_clear_json_input,
    resolve_solver_branch,
)


FIXTURE_ROOT = Path("tests/fixtures/postflop_clear_json")
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"

REQUIRED_BRANCH_EXPECTED_FIELDS = {
    "expected_branch",
    "expected_branch_family",
    "expected_branch_reason",
    "expected_branch_next_module",
    "expected_branch_contract_version",
}


def _load_json(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _manifest() -> dict[str, Any]:
    return _load_json(MANIFEST_PATH)


def _cases() -> list[dict[str, Any]]:
    cases = _manifest()["cases"]
    assert isinstance(cases, list)
    return cases


def _expected_payload(case: dict[str, Any]) -> dict[str, Any]:
    return _load_json(case["expected_file"])


def _enum_value(value: Any) -> Any:
    return getattr(value, "value", value)


def _load_map_and_route(case: dict[str, Any]):
    clear_input = load_clear_json_input(case["clear_json_file"])
    solver_input, solver_trace = build_solver_input(clear_input)
    branch_result = resolve_solver_branch(solver_input, solver_trace)
    return clear_input, solver_input, solver_trace, branch_result


def test_expected_files_contain_v040_branch_routing_fields() -> None:
    for case in _cases():
        expected = _expected_payload(case)

        assert REQUIRED_BRANCH_EXPECTED_FIELDS <= set(expected)
        assert expected["expected_branch_contract_version"] == "v0.4.3"
        assert isinstance(expected["expected_branch"], str) and expected["expected_branch"]
        assert isinstance(expected["expected_branch_family"], str) and expected["expected_branch_family"]
        assert isinstance(expected["expected_branch_reason"], str) and expected["expected_branch_reason"]
        assert isinstance(expected["expected_branch_next_module"], str) and expected["expected_branch_next_module"]


def test_fixture_cases_route_through_clear_json_to_solver_input_to_branch_result() -> None:
    expected_branch_by_street = {
        "flop": "flop",
        "turn": "turn_not_implemented_yet",
        "river": "river_not_implemented_yet",
    }

    for case in _cases():
        _, _, _, branch_result = _load_map_and_route(case)
        expected = _expected_payload(case)

        assert _enum_value(branch_result.branch) == expected_branch_by_street[case["street_group"]]
        assert _enum_value(branch_result.branch) == expected["expected_branch"]
        assert _enum_value(branch_result.branch_family) == expected["expected_branch_family"]
        assert branch_result.branch_reason == expected["expected_branch_reason"]
        assert branch_result.next_module == expected["expected_branch_next_module"]


def test_flop_fixtures_route_to_flop_context_builder() -> None:
    flop_cases = [case for case in _cases() if case["street_group"] == "flop"]
    assert flop_cases

    for case in flop_cases:
        _, _, _, branch_result = _load_map_and_route(case)

        assert _enum_value(branch_result.branch) == "flop"
        assert _enum_value(branch_result.branch_family) == "postflop_flop"
        assert branch_result.next_module == "flop_context_builder"
        assert branch_result.branch_reason == "board_card_count_3_routes_to_flop"


def test_turn_and_river_fixtures_route_to_not_implemented_placeholders() -> None:
    expected_by_street = {
        "turn": (
            "turn_not_implemented_yet",
            "postflop_turn",
            "turn_branch_not_implemented_yet",
            "board_card_count_4_routes_to_turn_placeholder",
        ),
        "river": (
            "river_not_implemented_yet",
            "postflop_river",
            "river_branch_not_implemented_yet",
            "board_card_count_5_routes_to_river_placeholder",
        ),
    }

    for case in _cases():
        if case["street_group"] not in expected_by_street:
            continue

        branch, family, next_module, reason = expected_by_street[case["street_group"]]
        _, _, _, branch_result = _load_map_and_route(case)

        assert _enum_value(branch_result.branch) == branch
        assert _enum_value(branch_result.branch_family) == family
        assert branch_result.next_module == next_module
        assert branch_result.branch_reason == reason


def test_branch_result_keeps_decision_and_runtime_disabled_for_all_fixtures() -> None:
    for case in _cases():
        _, _, _, branch_result = _load_map_and_route(case)

        assert branch_result.is_decision_branch_enabled is False
        assert branch_result.is_runtime_branch_enabled is False
        assert not any("decision_enabled" in note for note in branch_result.notes)
        assert not any("runtime_enabled" in note for note in branch_result.notes)


def test_branch_result_keeps_case_identity_and_source_trace() -> None:
    for case in _cases():
        clear_input, _, solver_trace, branch_result = _load_map_and_route(case)

        assert branch_result.case_id == case["case_id"]
        assert Path(clear_input.source_file).resolve() == Path(case["clear_json_file"]).resolve()
        assert solver_trace.module_chain_next_step == branch_result.next_module
        assert f"branch={_enum_value(branch_result.branch)}" in solver_trace.notes
        assert f"branch_reason={branch_result.branch_reason}" in solver_trace.notes


def test_fixture_routing_does_not_mutate_clear_json_payloads() -> None:
    for case in _cases():
        clear_path = Path(case["clear_json_file"])
        before = _load_json(clear_path)
        before_copy = copy.deepcopy(before)

        clear_input, solver_input, _, _ = _load_map_and_route(case)

        after = _load_json(clear_path)
        assert after == before_copy
        assert clear_input.raw_data == before_copy
        assert solver_input.raw_clear_json_ref is clear_input.raw_data


def test_branch_expected_files_do_not_contain_final_poker_decisions_or_click_payloads() -> None:
    forbidden_keys = {
        "decision",
        "final_decision",
        "solver_decision",
        "runtime_plan",
        "click_result",
        "action_to_click",
        "planned_action",
    }

    for case in _cases():
        expected = _expected_payload(case)
        assert not forbidden_keys.intersection(expected)
        assert expected["contains_final_poker_decision"] is False
        assert expected.get("requires_runtime_plan", False) is False
        assert expected.get("requires_click_chain", False) is False
