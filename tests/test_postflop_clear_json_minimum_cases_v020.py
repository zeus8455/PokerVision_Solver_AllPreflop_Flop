from __future__ import annotations

import json
from pathlib import Path

from solver_postflop import load_clear_json_input


FIXTURE_ROOT = Path("tests/fixtures/postflop_clear_json")
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"
FORBIDDEN_PATH_MARKERS = (
    "source_json",
    "dark_json",
    "pending_json",
    "service_json",
    "runtime_json",
)


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _cases() -> list[dict]:
    cases = _manifest()["cases"]
    assert isinstance(cases, list)
    return cases


def _case_payload(case: dict) -> dict:
    clear_json_path = Path(case["clear_json_file"])
    return json.loads(clear_json_path.read_text(encoding="utf-8"))


def test_manifest_contains_minimum_clear_json_case_set() -> None:
    cases = _cases()

    assert len(cases) >= 4
    assert any(case["source_kind"] == "real" and case["street_group"] == "flop" for case in cases)
    assert any(case["source_kind"] == "synthetic" and case["street_group"] == "flop" for case in cases)
    assert any(case["street_group"] == "turn" for case in cases)
    assert any(case["street_group"] == "river" for case in cases)


def test_case_ids_are_unique_and_required_manifest_fields_exist() -> None:
    required_fields = {
        "case_id",
        "case_name",
        "street_group",
        "spot_family",
        "source_kind",
        "clear_json_file",
        "expected_file",
        "base_real_case_id",
        "purpose",
        "solver_modules_targeted",
        "status",
        "notes",
    }
    cases = _cases()
    case_ids = [case["case_id"] for case in cases]

    assert len(case_ids) == len(set(case_ids))
    for case in cases:
        assert required_fields <= set(case)
        assert case["case_id"]
        assert case["purpose"]
        assert case["status"] == "active"
        assert isinstance(case["solver_modules_targeted"], list)
        assert case["solver_modules_targeted"]


def test_each_manifest_clear_json_file_exists_and_uses_clear_json_extension() -> None:
    for case in _cases():
        clear_json_path = Path(case["clear_json_file"])

        assert clear_json_path.exists(), case["clear_json_file"]
        assert clear_json_path.is_file()
        assert clear_json_path.name.endswith(".clear.json")
        assert FIXTURE_ROOT in clear_json_path.parents


def test_expected_files_are_attached_from_v0_2_4() -> None:
    for case in _cases():
        expected_file = case["expected_file"]
        assert isinstance(expected_file, str)
        assert expected_file.endswith(".expected.json")
        assert Path(expected_file).exists()


def test_each_clear_json_fixture_loads_through_trusted_loader() -> None:
    for case in _cases():
        clear_input = load_clear_json_input(case["clear_json_file"])

        assert clear_input.case_id == case["case_id"]
        assert clear_input.raw_data["case_id"] == case["case_id"]
        assert Path(clear_input.source_file).resolve() == Path(case["clear_json_file"]).resolve()


def test_case_id_and_source_kind_match_between_manifest_and_payload() -> None:
    for case in _cases():
        payload = _case_payload(case)

        assert payload["case_id"] == case["case_id"]
        assert payload["source_kind"] == case["source_kind"]
        assert payload["street_group"] == case["street_group"]
        assert payload["spot_family"] == case["spot_family"]


def test_source_kind_values_are_strictly_real_or_synthetic() -> None:
    for case in _cases():
        assert case["source_kind"] in {"real", "synthetic"}


def test_synthetic_cases_reference_a_base_real_case() -> None:
    case_ids = {case["case_id"] for case in _cases()}

    for case in _cases():
        if case["source_kind"] == "synthetic":
            assert case["base_real_case_id"] in case_ids
        else:
            assert case["base_real_case_id"] is None


def test_minimum_cases_cover_flop_turn_and_river_board_card_counts() -> None:
    expected_counts = {
        "flop": 3,
        "turn": 4,
        "river": 5,
    }

    for case in _cases():
        payload = _case_payload(case)
        street_group = case["street_group"]

        assert len(payload["board_cards"]) == expected_counts[street_group]


def test_clear_json_fixtures_include_baseline_solver_input_fields() -> None:
    required_payload_fields = {
        "case_id",
        "table_id",
        "hand_id",
        "hero_cards",
        "board_cards",
        "players",
        "pot",
        "total_pot",
        "to_call",
        "stacks",
        "committed_amounts",
        "positions",
        "button",
        "blinds",
        "allowed_actions",
        "action_context",
    }

    for case in _cases():
        payload = _case_payload(case)
        assert required_payload_fields <= set(payload)


def test_clear_json_loader_does_not_mutate_fixture_files() -> None:
    for case in _cases():
        clear_json_path = Path(case["clear_json_file"])
        before = json.loads(clear_json_path.read_text(encoding="utf-8"))

        load_clear_json_input(clear_json_path)

        after = json.loads(clear_json_path.read_text(encoding="utf-8"))
        assert after == before


def test_fixture_paths_do_not_use_temporary_source_artifact_names() -> None:
    for case in _cases():
        clear_json_path = case["clear_json_file"].lower()
        for forbidden_marker in FORBIDDEN_PATH_MARKERS:
            assert forbidden_marker not in clear_json_path
