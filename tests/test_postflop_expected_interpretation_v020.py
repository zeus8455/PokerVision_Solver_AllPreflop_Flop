from __future__ import annotations

import json
from pathlib import Path


FIXTURE_ROOT = Path("tests/fixtures/postflop_clear_json")
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"

REQUIRED_EXPECTED_FIELDS = {
    "case_id",
    "expected_street_group",
    "expected_spot_family",
    "expected_hero_position",
    "expected_is_heads_up",
    "expected_is_multiway",
    "expected_pot_type",
    "expected_action_context",
    "expected_available_solver_branch",
    "expected_next_module",
    "expected_notes",
    "contains_final_poker_decision",
    "expected_interpretation_version",
}

FORBIDDEN_DECISION_FIELDS = {
    "decision",
    "final_decision",
    "solver_decision",
    "action",
    "action_to_click",
    "planned_action",
    "click_sequence",
    "runtime_plan",
    "fold",
    "call",
    "check",
    "bet",
    "raise",
}

FORBIDDEN_RUNTIME_MARKERS = (
    "Action_Button",
    "click_chain",
    "display_analysis_cycle",
    "Dark_JSON",
    "Pending_JSON",
    "Service JSON",
    "Runtime JSON",
)


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _cases() -> list[dict]:
    cases = _manifest()["cases"]
    assert isinstance(cases, list)
    return cases


def _expected_payload(case: dict) -> dict:
    expected_path = Path(case["expected_file"])
    return json.loads(expected_path.read_text(encoding="utf-8"))


def _clear_payload(case: dict) -> dict:
    clear_path = Path(case["clear_json_file"])
    return json.loads(clear_path.read_text(encoding="utf-8"))


def test_each_case_has_expected_interpretation_file() -> None:
    for case in _cases():
        expected_file = case["expected_file"]
        assert isinstance(expected_file, str)
        assert expected_file.endswith(".expected.json")

        expected_path = Path(expected_file)
        assert expected_path.exists(), expected_file
        assert expected_path.is_file()
        assert FIXTURE_ROOT / "expected" in expected_path.parents


def test_expected_payload_contains_required_interpretation_fields() -> None:
    for case in _cases():
        expected = _expected_payload(case)

        assert REQUIRED_EXPECTED_FIELDS <= set(expected)
        assert expected["case_id"] == case["case_id"]
        assert expected["contains_final_poker_decision"] is False
        assert expected["expected_interpretation_version"] == "v0.2.4"
        assert isinstance(expected["expected_notes"], list)
        assert expected["expected_notes"]


def test_expected_interpretation_matches_manifest_street_and_spot_family() -> None:
    for case in _cases():
        expected = _expected_payload(case)

        assert expected["expected_street_group"] == case["street_group"]
        assert expected["expected_spot_family"] == case["spot_family"]
        assert expected["expected_available_solver_branch"]
        assert expected["expected_next_module"]


def test_expected_interpretation_matches_clear_json_basic_context() -> None:
    for case in _cases():
        expected = _expected_payload(case)
        clear_json = _clear_payload(case)

        assert expected["expected_hero_position"] == clear_json["hero_position"]
        assert expected["expected_pot_type"] == clear_json["pot_type"]
        assert expected["expected_street_group"] == clear_json["street_group"]

        active_players = [
            player
            for player in clear_json["players"]
            if not player.get("folded", False)
        ]
        assert expected["expected_is_heads_up"] is (len(active_players) == 2)
        assert expected["expected_is_multiway"] is (len(active_players) > 2)


def test_flop_cases_route_to_future_flop_context_builder() -> None:
    flop_cases = [case for case in _cases() if case["street_group"] == "flop"]
    assert flop_cases

    for case in flop_cases:
        expected = _expected_payload(case)
        assert expected["expected_available_solver_branch"] == "flop_srp_branch"
        assert expected["expected_next_module"] == "flop_context_builder"


def test_turn_and_river_cases_are_marked_not_implemented_yet() -> None:
    expected_by_street = {
        "turn": "turn_branch_not_implemented_yet",
        "river": "river_branch_not_implemented_yet",
    }

    for case in _cases():
        if case["street_group"] in expected_by_street:
            expected = _expected_payload(case)
            assert expected["expected_available_solver_branch"] == expected_by_street[case["street_group"]]
            assert expected["expected_next_module"] == "branch_resolver"


def test_expected_files_do_not_contain_final_poker_decision_fields() -> None:
    for case in _cases():
        expected = _expected_payload(case)
        for forbidden_field in FORBIDDEN_DECISION_FIELDS:
            assert forbidden_field not in expected


def test_expected_files_do_not_reference_runtime_or_temporary_sources() -> None:
    for case in _cases():
        expected_text = Path(case["expected_file"]).read_text(encoding="utf-8")
        for forbidden_marker in FORBIDDEN_RUNTIME_MARKERS:
            assert forbidden_marker not in expected_text
