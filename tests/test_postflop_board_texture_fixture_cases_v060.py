from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from solver_postflop import (
    SolverBranch,
    build_board_texture_features,
    build_flop_context,
    build_solver_input,
    load_clear_json_input,
    resolve_solver_branch,
)

FIXTURE_ROOT = Path("tests/fixtures/postflop_clear_json")
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"
TEXTURE_PURPOSE = "test_board_texture_features"

REQUIRED_TEXTURE_EXPECTED_FIELDS = {
    "expected_suit_texture",
    "expected_paired_texture",
    "expected_rank_texture",
    "expected_connection_texture",
    "expected_volatility_class",
    "expected_texture_tags",
    "expected_board_texture_version",
}

EXPECTED_TEXTURE_CASE_IDS = {
    "flop_texture_ace_high_dry_rainbow",
    "flop_texture_king_high_two_tone",
    "flop_texture_monotone_broadway",
    "flop_texture_low_connected",
    "flop_texture_middle_connected_two_tone",
    "flop_texture_paired_dry",
    "flop_texture_paired_dynamic",
    "flop_texture_very_wet_connected",
}


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _manifest() -> dict[str, Any]:
    return _load_json(MANIFEST_PATH)


def _texture_cases() -> list[dict[str, Any]]:
    cases = [
        case
        for case in _manifest()["cases"]
        if case["purpose"] == TEXTURE_PURPOSE
    ]
    assert cases
    return cases


def _expected_payload(case: dict[str, Any]) -> dict[str, Any]:
    return _load_json(case["expected_file"])


def _build_texture_for(case: dict[str, Any]):
    clear_input = load_clear_json_input(case["clear_json_file"])
    raw_before = copy.deepcopy(clear_input.raw_data)
    solver_input, solver_trace = build_solver_input(clear_input)
    branch_result = resolve_solver_branch(solver_input, solver_trace)
    flop_context = build_flop_context(solver_input, branch_result)
    flop_context_json_before = copy.deepcopy(flop_context.to_json_dict())
    texture_features = build_board_texture_features(flop_context)
    return (
        clear_input,
        raw_before,
        solver_input,
        branch_result,
        flop_context,
        flop_context_json_before,
        texture_features,
    )


def test_texture_fixture_cases_are_declared_in_manifest() -> None:
    texture_cases = _texture_cases()

    assert {case["case_id"] for case in texture_cases} == EXPECTED_TEXTURE_CASE_IDS
    for case in texture_cases:
        assert case["source_kind"] == "synthetic"
        assert case["street_group"] == "flop"
        assert case["base_real_case_id"] == "real_flop_srp_btn_vs_bb_check_option"
        assert "board_texture_builder" in case["solver_modules_targeted"]
        assert Path(case["clear_json_file"]).exists()
        assert Path(case["expected_file"]).exists()


def test_texture_expected_files_contain_v060_fields() -> None:
    for case in _texture_cases():
        expected = _expected_payload(case)

        assert REQUIRED_TEXTURE_EXPECTED_FIELDS <= set(expected)
        assert expected["expected_board_texture_version"] == "v0.6.4"
        assert expected["contains_final_poker_decision"] is False
        assert isinstance(expected["expected_texture_tags"], list)
        assert expected["expected_texture_tags"]


def test_texture_fixtures_run_through_clear_json_to_board_texture_pipeline() -> None:
    for case in _texture_cases():
        (
            _clear_input,
            _raw_before,
            _solver_input,
            branch_result,
            _flop_context,
            _flop_context_json_before,
            texture_features,
        ) = _build_texture_for(case)

        assert branch_result.branch is SolverBranch.FLOP
        assert texture_features.case_id == case["case_id"]
        assert Path(texture_features.source_file).as_posix() == case["clear_json_file"]
        assert len(texture_features.board_cards) == 3


def test_texture_features_match_expected_json_contract() -> None:
    for case in _texture_cases():
        expected = _expected_payload(case)
        *_, texture_features = _build_texture_for(case)

        assert texture_features.suit_texture.value == expected["expected_suit_texture"]
        assert texture_features.paired_texture.value == expected["expected_paired_texture"]
        assert texture_features.rank_texture.value == expected["expected_rank_texture"]
        assert texture_features.connection_texture.value == expected["expected_connection_texture"]
        assert texture_features.volatility_class.value == expected["expected_volatility_class"]
        assert list(texture_features.texture_tags) == expected["expected_texture_tags"]


def test_texture_fixture_pipeline_does_not_mutate_clear_json_or_flop_context() -> None:
    for case in _texture_cases():
        (
            clear_input,
            raw_before,
            solver_input,
            _branch_result,
            flop_context,
            flop_context_json_before,
            texture_features,
        ) = _build_texture_for(case)

        assert clear_input.raw_data == raw_before
        assert solver_input.raw_clear_json_ref is clear_input.raw_data
        assert flop_context.to_json_dict() == flop_context_json_before
        assert texture_features.board_cards == flop_context.board_cards
        assert texture_features.case_id == flop_context.case_id


def test_texture_expected_files_do_not_attach_future_solver_outputs() -> None:
    forbidden_keys = {
        "decision",
        "final_decision",
        "solver_decision",
        "runtime_plan",
        "click_result",
        "equity",
        "range",
        "made_hand",
        "draw_features",
    }

    for case in _texture_cases():
        expected = _expected_payload(case)
        assert forbidden_keys.isdisjoint(expected)
        assert expected.get("requires_runtime_plan", False) is False
        assert expected.get("requires_click_chain", False) is False
