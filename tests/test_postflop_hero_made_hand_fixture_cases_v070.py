from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from solver_postflop import (
    SolverBranch,
    build_board_texture_features,
    build_flop_context,
    build_made_hand_features,
    build_solver_input,
    load_clear_json_input,
    resolve_solver_branch,
)

FIXTURE_ROOT = Path("tests/fixtures/postflop_clear_json")
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"
MADE_HAND_PURPOSE = "test_hero_made_hand_features"

REQUIRED_MADE_HAND_EXPECTED_FIELDS = {
    "expected_made_hand_class",
    "expected_pair_class",
    "expected_strength_tier",
    "expected_kicker_relevance",
    "expected_board_interaction_tags",
    "expected_made_hand_version",
}

EXPECTED_MADE_HAND_CASE_IDS = {
    "flop_made_hand_high_card",
    "flop_made_hand_top_pair_good_kicker",
    "flop_made_hand_middle_pair",
    "flop_made_hand_bottom_pair",
    "flop_made_hand_overpair",
    "flop_made_hand_underpair",
    "flop_made_hand_two_pair",
    "flop_made_hand_set",
    "flop_made_hand_trips",
    "flop_made_hand_straight",
    "flop_made_hand_flush",
    "flop_made_hand_full_house",
    "flop_made_hand_quads",
}


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _manifest() -> dict[str, Any]:
    return _load_json(MANIFEST_PATH)


def _made_hand_cases() -> list[dict[str, Any]]:
    cases = [
        case
        for case in _manifest()["cases"]
        if case["purpose"] == MADE_HAND_PURPOSE
    ]
    assert cases
    return cases


def _expected_payload(case: dict[str, Any]) -> dict[str, Any]:
    return _load_json(case["expected_file"])


def _build_made_hand_for(case: dict[str, Any]):
    clear_input = load_clear_json_input(case["clear_json_file"])
    raw_before = copy.deepcopy(clear_input.raw_data)
    solver_input, solver_trace = build_solver_input(clear_input)
    branch_result = resolve_solver_branch(solver_input, solver_trace)
    flop_context = build_flop_context(solver_input, branch_result)
    flop_context_json_before = copy.deepcopy(flop_context.to_json_dict())
    board_texture_features = build_board_texture_features(flop_context)
    board_texture_json_before = copy.deepcopy(board_texture_features.to_json_dict())
    made_hand_features = build_made_hand_features(flop_context, board_texture_features)
    return (
        clear_input,
        raw_before,
        solver_input,
        branch_result,
        flop_context,
        flop_context_json_before,
        board_texture_features,
        board_texture_json_before,
        made_hand_features,
    )


def test_made_hand_fixture_cases_are_declared_in_manifest() -> None:
    made_hand_cases = _made_hand_cases()

    assert {case["case_id"] for case in made_hand_cases} == EXPECTED_MADE_HAND_CASE_IDS
    for case in made_hand_cases:
        assert case["source_kind"] == "synthetic"
        assert case["street_group"] == "flop"
        assert case["base_real_case_id"] == "real_flop_srp_btn_vs_bb_check_option"
        assert "hero_made_hand_classifier" in case["solver_modules_targeted"]
        assert Path(case["clear_json_file"]).exists()
        assert Path(case["expected_file"]).exists()


def test_made_hand_expected_files_contain_v070_fields() -> None:
    for case in _made_hand_cases():
        expected = _expected_payload(case)

        assert REQUIRED_MADE_HAND_EXPECTED_FIELDS <= set(expected)
        assert expected["expected_made_hand_version"] == "v0.7.4"
        assert expected["contains_final_poker_decision"] is False
        assert isinstance(expected["expected_board_interaction_tags"], list)
        assert expected["expected_board_interaction_tags"]


def test_made_hand_fixtures_run_through_clear_json_to_made_hand_pipeline() -> None:
    for case in _made_hand_cases():
        (
            _clear_input,
            _raw_before,
            _solver_input,
            branch_result,
            _flop_context,
            _flop_context_json_before,
            _board_texture_features,
            _board_texture_json_before,
            made_hand_features,
        ) = _build_made_hand_for(case)

        assert branch_result.branch is SolverBranch.FLOP
        assert made_hand_features.case_id == case["case_id"]
        assert Path(made_hand_features.source_file).as_posix() == case["clear_json_file"]
        assert len(made_hand_features.hero_cards) == 2
        assert len(made_hand_features.board_cards) == 3


def test_made_hand_features_match_expected_json_contract() -> None:
    for case in _made_hand_cases():
        expected = _expected_payload(case)
        *_, made_hand_features = _build_made_hand_for(case)

        assert made_hand_features.made_hand_class.value == expected["expected_made_hand_class"]
        assert made_hand_features.pair_class.value == expected["expected_pair_class"]
        assert made_hand_features.strength_tier.value == expected["expected_strength_tier"]
        assert made_hand_features.kicker_relevance == expected["expected_kicker_relevance"]
        assert list(made_hand_features.board_interaction_tags) == expected["expected_board_interaction_tags"]


def test_made_hand_fixture_pipeline_does_not_mutate_prior_contexts() -> None:
    for case in _made_hand_cases():
        (
            clear_input,
            raw_before,
            solver_input,
            _branch_result,
            flop_context,
            flop_context_json_before,
            board_texture_features,
            board_texture_json_before,
            made_hand_features,
        ) = _build_made_hand_for(case)

        assert clear_input.raw_data == raw_before
        assert solver_input.raw_clear_json_ref is clear_input.raw_data
        assert flop_context.to_json_dict() == flop_context_json_before
        assert board_texture_features.to_json_dict() == board_texture_json_before
        assert made_hand_features.hero_cards == flop_context.hero_cards
        assert made_hand_features.board_cards == flop_context.board_cards


def test_made_hand_expected_files_do_not_attach_future_solver_outputs() -> None:
    forbidden_keys = {
        "decision",
        "final_decision",
        "solver_decision",
        "runtime_plan",
        "click_result",
        "equity",
        "range",
        "draw_features",
    }

    for case in _made_hand_cases():
        expected = _expected_payload(case)
        assert forbidden_keys.isdisjoint(expected)
        assert expected.get("requires_runtime_plan", False) is False
        assert expected.get("requires_click_chain", False) is False
