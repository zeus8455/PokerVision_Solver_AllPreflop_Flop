from __future__ import annotations

import copy
import json
from pathlib import Path

from solver_postflop import (
    SolverBranch,
    build_flop_context,
    build_solver_input,
    load_clear_json_input,
    resolve_solver_branch,
)

FIXTURE_ROOT = Path("tests/fixtures/postflop_clear_json")
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _flop_cases() -> list[dict]:
    cases = _manifest()["cases"]
    return [case for case in cases if case["street_group"] == "flop"]


def _expected_for(case: dict) -> dict:
    return json.loads(Path(case["expected_file"]).read_text(encoding="utf-8"))


def _build_context_for(case: dict):
    clear_input = load_clear_json_input(case["clear_json_file"])
    before = copy.deepcopy(clear_input.raw_data)
    solver_input, solver_trace = build_solver_input(clear_input)
    branch_result = resolve_solver_branch(solver_input, solver_trace)
    context = build_flop_context(solver_input, branch_result)
    return clear_input, before, solver_input, branch_result, context


def test_fixture_library_contains_flop_context_expected_fields() -> None:
    flop_cases = _flop_cases()

    # V0.5.4 introduced fixture-backed FlopContext coverage for the two seed
    # flop cases. Later versions may extend the same flop fixture library for
    # downstream modules such as BoardTexture, so this gate protects the seed
    # cases without freezing the flop fixture set size.
    assert {
        "real_flop_srp_btn_vs_bb_check_option",
        "synthetic_flop_srp_oop_facing_cbet",
    }.issubset({case["case_id"] for case in flop_cases})

    required_fields = {
        "expected_flop_spot_family",
        "expected_flop_action_context",
        "expected_flop_position_context",
        "expected_flop_next_module",
        "expected_flop_fields_used",
        "expected_flop_fields_not_provided",
        "expected_flop_context_version",
    }
    for case in flop_cases:
        expected = _expected_for(case)
        assert required_fields <= set(expected)
        assert expected["expected_flop_context_version"] == "v0.5.4"
        assert expected["contains_final_poker_decision"] is False


def test_flop_fixtures_build_flop_context_through_full_pipeline() -> None:
    for case in _flop_cases():
        expected = _expected_for(case)
        _clear_input, _before, _solver_input, branch_result, context = _build_context_for(case)

        assert branch_result.branch == SolverBranch.FLOP
        assert context.branch == SolverBranch.FLOP.value
        assert context.case_id == case["case_id"]
        assert context.spot_family.value == expected["expected_flop_spot_family"]
        assert context.next_module == expected["expected_flop_next_module"]
        assert context.action_context.action_context_label == expected["expected_flop_action_context"]

        expected_position = expected["expected_flop_position_context"]
        assert context.position_context.hero_id == expected_position["hero_id"]
        assert context.position_context.hero_position == expected_position["hero_position"]
        assert context.position_context.is_in_position == expected_position["is_in_position"]
        assert context.position_context.position_label == expected_position["position_label"]


def test_flop_context_expected_fields_used_are_present_in_context() -> None:
    for case in _flop_cases():
        expected = _expected_for(case)
        _clear_input, _before, _solver_input, _branch_result, context = _build_context_for(case)

        for field_name in expected["expected_flop_fields_used"]:
            assert field_name in context.context_fields_used

        for field_name in expected["expected_flop_fields_not_provided"]:
            assert field_name in context.context_fields_not_provided

        assert "decision" not in context.context_fields_used
        assert "runtime_plan" not in context.context_fields_used
        assert "click_result" not in context.context_fields_used


def test_flop_fixture_context_preserves_solver_input_without_filtering_or_repair() -> None:
    for case in _flop_cases():
        clear_input, before, solver_input, _branch_result, context = _build_context_for(case)

        assert clear_input.raw_data == before
        assert context.raw_clear_json_ref is solver_input.raw_clear_json_ref
        assert context.hero_cards == solver_input.hero_cards
        assert context.board_cards == solver_input.board_cards
        assert context.player_context.players == solver_input.players
        assert context.action_context.allowed_actions == solver_input.allowed_actions
        assert context.pot_context.pot == solver_input.pot
        assert context.pot_context.to_call == solver_input.to_call


def test_flop_fixture_context_does_not_attach_future_solver_outputs() -> None:
    forbidden_keys = {
        "final_decision",
        "poker_decision",
        "decision_action",
        "runtime_plan",
        "click_plan",
        "click_result",
        "equity",
        "range",
        "board_texture",
        "made_hand",
    }

    for case in _flop_cases():
        expected = _expected_for(case)
        _clear_input, _before, _solver_input, _branch_result, context = _build_context_for(case)
        payload = context.to_json_dict()

        assert forbidden_keys.isdisjoint(expected)
        assert forbidden_keys.isdisjoint(payload)
