from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from solver_postflop import (
    SolverBranch,
    build_board_texture_features,
    build_draw_features,
    build_flop_context,
    build_made_hand_features,
    build_solver_input,
    load_clear_json_input,
    resolve_solver_branch,
)

FIXTURE_ROOT = Path("tests/fixtures/postflop_clear_json")
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"
DRAW_PURPOSE = "test_hero_draw_features"

REQUIRED_DRAW_EXPECTED_FIELDS = {
    "expected_flush_draw_class",
    "expected_straight_draw_class",
    "expected_overcard_class",
    "expected_combo_draw_class",
    "expected_draw_strength_tier",
    "expected_draw_tags",
    "expected_draw_version",
}

EXPECTED_DRAW_CASE_IDS = {
    "flop_draw_no_draw",
    "flop_draw_backdoor_flush",
    "flop_draw_standard_flush_draw",
    "flop_draw_nut_flush_draw",
    "flop_draw_gutshot",
    "flop_draw_oesd",
    "flop_draw_double_gutshot",
    "flop_draw_two_overcards",
    "flop_draw_fd_plus_gutshot",
    "flop_draw_fd_plus_oesd",
    "flop_draw_pair_plus_fd",
    "flop_draw_pair_plus_straight_draw",
    "flop_draw_premium_combo_draw",
}


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _manifest() -> dict[str, Any]:
    return _load_json(MANIFEST_PATH)


def _draw_cases() -> list[dict[str, Any]]:
    cases = [
        case
        for case in _manifest()["cases"]
        if case["purpose"] == DRAW_PURPOSE
    ]
    assert cases
    return cases


def _expected_payload(case: dict[str, Any]) -> dict[str, Any]:
    return _load_json(case["expected_file"])


def _build_draw_for(case: dict[str, Any]):
    clear_input = load_clear_json_input(case["clear_json_file"])
    raw_before = copy.deepcopy(clear_input.raw_data)
    solver_input, solver_trace = build_solver_input(clear_input)
    branch_result = resolve_solver_branch(solver_input, solver_trace)
    flop_context = build_flop_context(solver_input, branch_result)
    flop_context_json_before = copy.deepcopy(flop_context.to_json_dict())
    board_texture_features = build_board_texture_features(flop_context)
    board_texture_json_before = copy.deepcopy(board_texture_features.to_json_dict())
    made_hand_features = build_made_hand_features(flop_context, board_texture_features)
    made_hand_json_before = copy.deepcopy(made_hand_features.to_json_dict())
    draw_features = build_draw_features(
        flop_context,
        board_texture_features,
        made_hand_features,
    )
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
        made_hand_json_before,
        draw_features,
    )


def test_draw_fixture_cases_are_declared_in_manifest() -> None:
    draw_cases = _draw_cases()

    assert {case["case_id"] for case in draw_cases} == EXPECTED_DRAW_CASE_IDS
    for case in draw_cases:
        assert case["source_kind"] == "synthetic"
        assert case["street_group"] == "flop"
        assert case["base_real_case_id"] == "real_flop_srp_btn_vs_bb_check_option"
        assert "hero_draw_classifier" in case["solver_modules_targeted"]
        assert Path(case["clear_json_file"]).exists()
        assert Path(case["expected_file"]).exists()


def test_draw_expected_files_contain_v080_fields() -> None:
    for case in _draw_cases():
        expected = _expected_payload(case)

        assert REQUIRED_DRAW_EXPECTED_FIELDS <= set(expected)
        assert expected["expected_draw_version"] == "v0.8.4"
        assert expected["contains_final_poker_decision"] is False
        assert isinstance(expected["expected_draw_tags"], list)
        assert expected["expected_draw_tags"]


def test_draw_fixtures_run_through_clear_json_to_draw_pipeline() -> None:
    for case in _draw_cases():
        (
            _clear_input,
            _raw_before,
            _solver_input,
            branch_result,
            _flop_context,
            _flop_context_json_before,
            _board_texture_features,
            _board_texture_json_before,
            _made_hand_features,
            _made_hand_json_before,
            draw_features,
        ) = _build_draw_for(case)

        assert branch_result.branch is SolverBranch.FLOP
        assert draw_features.case_id == case["case_id"]
        assert Path(draw_features.source_file).as_posix() == case["clear_json_file"]
        assert len(draw_features.hero_cards) == 2
        assert len(draw_features.board_cards) == 3


def test_draw_features_match_expected_json_contract() -> None:
    for case in _draw_cases():
        expected = _expected_payload(case)
        *_, draw_features = _build_draw_for(case)

        assert draw_features.flush_draw_class.value == expected["expected_flush_draw_class"]
        assert draw_features.straight_draw_class.value == expected["expected_straight_draw_class"]
        assert draw_features.overcard_class.value == expected["expected_overcard_class"]
        assert draw_features.combo_draw_class.value == expected["expected_combo_draw_class"]
        assert draw_features.draw_strength_tier.value == expected["expected_draw_strength_tier"]
        assert list(draw_features.draw_tags) == expected["expected_draw_tags"]


def test_draw_fixture_pipeline_does_not_mutate_upstream_objects() -> None:
    for case in _draw_cases():
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
            made_hand_json_before,
            draw_features,
        ) = _build_draw_for(case)

        assert clear_input.raw_data == raw_before
        assert solver_input.raw_clear_json_ref is clear_input.raw_data
        assert flop_context.to_json_dict() == flop_context_json_before
        assert board_texture_features.to_json_dict() == board_texture_json_before
        assert made_hand_features.to_json_dict() == made_hand_json_before
        assert draw_features.hero_cards == flop_context.hero_cards
        assert draw_features.board_cards == flop_context.board_cards


def test_draw_expected_files_do_not_attach_future_solver_outputs() -> None:
    forbidden_keys = {
        "decision",
        "final_decision",
        "solver_decision",
        "runtime_plan",
        "click_result",
        "equity",
        "range",
        "equity_input",
    }

    for case in _draw_cases():
        expected = _expected_payload(case)
        assert forbidden_keys.isdisjoint(expected)
        assert expected.get("requires_runtime_plan", False) is False
        assert expected.get("requires_click_chain", False) is False
