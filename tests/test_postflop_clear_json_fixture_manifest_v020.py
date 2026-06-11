"""Strict manifest gate for the Clear_JSON postflop fixture library.

V0.2.5 protects the fixture manifest as a stable contract for later
postflop solver modules. The fixture library must stay Clear_JSON-only and
must not drift back into temporary source artifact layouts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FIXTURE_ROOT = Path("tests/fixtures/postflop_clear_json")
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"
FORBIDDEN_PATH_FRAGMENTS = (
    "source_json",
    "dark_json",
    "pending_json",
    "service_json",
    "runtime_json",
    "dark",
    "pending",
    "service",
    "runtime",
)
VALID_STREET_GROUPS = {"flop", "turn", "river"}
VALID_SOURCE_KINDS = {"real", "synthetic"}
VALID_STATUSES = {"active", "planned", "deprecated"}
REQUIRED_CASE_FIELDS = {
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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest() -> dict[str, Any]:
    return _load_json(MANIFEST_PATH)


def _cases() -> list[dict[str, Any]]:
    cases = _manifest()["cases"]
    assert isinstance(cases, list)
    return cases


def _as_project_path(path_value: str) -> Path:
    return Path(path_value)


def _normalized_path_text(path_value: str) -> str:
    return path_value.replace("\\", "/").lower()


def test_manifest_exists_and_declares_clear_json_library_contract() -> None:
    assert MANIFEST_PATH.exists()

    manifest = _manifest()

    assert isinstance(manifest.get("schema_version"), str)
    assert manifest["schema_version"].startswith("0.2.")
    assert manifest["library_kind"] == "clear_json_fixture_library"
    assert manifest["architecture"] == "clear_json_only"
    assert manifest["fixture_root"] == str(FIXTURE_ROOT).replace("\\", "/")
    assert isinstance(manifest.get("source_policy"), dict)
    assert isinstance(manifest.get("expected_policy"), dict)
    assert isinstance(manifest.get("cases"), list)
    assert manifest["cases"]


def test_manifest_case_ids_are_unique_and_stable_strings() -> None:
    case_ids = [case["case_id"] for case in _cases()]

    assert len(case_ids) == len(set(case_ids))
    for case_id in case_ids:
        assert isinstance(case_id, str)
        assert case_id
        assert case_id == case_id.strip()
        assert " " not in case_id
        assert case_id.lower() == case_id


def test_each_manifest_case_has_required_fields_and_metadata() -> None:
    for case in _cases():
        assert REQUIRED_CASE_FIELDS.issubset(case.keys())
        assert isinstance(case["case_name"], str) and case["case_name"]
        assert case["street_group"] in VALID_STREET_GROUPS
        assert isinstance(case["spot_family"], str) and case["spot_family"]
        assert case["source_kind"] in VALID_SOURCE_KINDS
        assert isinstance(case["purpose"], str) and case["purpose"]
        assert case["status"] in VALID_STATUSES
        assert isinstance(case["notes"], list)
        assert all(isinstance(note, str) and note for note in case["notes"])

        modules = case["solver_modules_targeted"]
        assert isinstance(modules, list)
        assert modules
        assert all(isinstance(module, str) and module for module in modules)


def test_each_clear_json_file_exists_under_matching_real_or_synthetic_tree() -> None:
    for case in _cases():
        clear_json_path = _as_project_path(case["clear_json_file"])
        assert clear_json_path.exists(), case["clear_json_file"]
        assert clear_json_path.suffix == ".json"
        assert clear_json_path.name.endswith(".clear.json")
        assert FIXTURE_ROOT in clear_json_path.parents

        path_text = _normalized_path_text(case["clear_json_file"])
        if case["source_kind"] == "real":
            assert "/real/" in path_text
            assert case["base_real_case_id"] is None
        else:
            assert "/synthetic/" in path_text
            assert isinstance(case["base_real_case_id"], str)
            assert case["base_real_case_id"]


def test_each_expected_file_exists_under_expected_tree() -> None:
    for case in _cases():
        expected_path = _as_project_path(case["expected_file"])
        assert expected_path.exists(), case["expected_file"]
        assert expected_path.suffix == ".json"
        assert expected_path.name.endswith(".expected.json")
        assert expected_path.parent == FIXTURE_ROOT / "expected"

        expected = _load_json(expected_path)
        assert expected["case_id"] == case["case_id"]
        assert expected["expected_street_group"] == case["street_group"]
        assert expected["expected_spot_family"] == case["spot_family"]


def test_synthetic_cases_reference_existing_real_cases() -> None:
    real_case_ids = {
        case["case_id"]
        for case in _cases()
        if case["source_kind"] == "real"
    }
    assert real_case_ids

    synthetic_cases = [case for case in _cases() if case["source_kind"] == "synthetic"]
    assert synthetic_cases

    for case in synthetic_cases:
        assert case["base_real_case_id"] in real_case_ids


def test_manifest_paths_do_not_use_temporary_source_artifact_layouts() -> None:
    searchable_values: list[str] = [
        str(MANIFEST_PATH).replace("\\", "/"),
    ]

    for case in _cases():
        searchable_values.extend(
            [
                case["clear_json_file"],
                case["expected_file"],
                case["case_id"],
                case["case_name"],
            ]
        )

    for raw_value in searchable_values:
        value = _normalized_path_text(raw_value)
        for forbidden in FORBIDDEN_PATH_FRAGMENTS:
            assert forbidden not in value


def test_manifest_cases_and_fixture_payloads_agree_on_identity_and_street() -> None:
    for case in _cases():
        clear_json = _load_json(_as_project_path(case["clear_json_file"]))
        expected = _load_json(_as_project_path(case["expected_file"]))

        assert clear_json["case_id"] == case["case_id"]
        assert expected["case_id"] == case["case_id"]
        assert expected["expected_street_group"] == case["street_group"]
        assert clear_json.get("street_group") == case["street_group"] or clear_json.get("action_context", {}).get("street") == case["street_group"]


def test_expected_files_do_not_contain_final_poker_decisions_or_runtime_plan() -> None:
    forbidden_keys = {
        "decision",
        "final_decision",
        "action",
        "final_action",
        "solver_action",
        "click_action",
        "runtime_plan",
        "click_result",
    }

    for case in _cases():
        expected = _load_json(_as_project_path(case["expected_file"]))
        present_forbidden = forbidden_keys.intersection(expected.keys())
        assert not present_forbidden, (case["case_id"], present_forbidden)

        assert expected["contains_final_poker_decision"] is False
        assert expected.get("requires_runtime_plan", False) is False
        assert expected.get("requires_click_chain", False) is False
