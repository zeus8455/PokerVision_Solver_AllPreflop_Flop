"""V0.2.4 manifest tests for the postflop source-based fixture lab.

These tests protect tests/fixtures/postflop/manifest.json.
They intentionally do not test source discovery, normalization, poker decisions,
or runtime/click-chain behavior.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures" / "postflop"
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"

EXPECTED_TOP_LEVEL_FIELDS = {
    "version",
    "schema_version",
    "description",
    "purpose",
    "allowed_source_types",
    "required_case_fields",
    "rules",
    "cases",
}

EXPECTED_CASE_FIELDS = {
    "case_id",
    "description",
    "source_type",
    "source_file",
    "expected_file",
    "normalized_file",
    "street_candidate",
    "pot_type_candidate",
    "is_real_project_source",
    "is_manual_live_like_source",
    "source_of_truth_note",
    "requires_click_cycle",
    "status",
    "notes",
}

EXPECTED_SOURCE_TYPES = {
    "dark_json",
    "pending_json",
    "service_json",
    "current_cycle_json",
    "runtime_json",
    "solver_payload_json",
    "final_clear_json",
    "manual_live_like_json",
    "unknown",
}


def load_manifest() -> dict[str, Any]:
    assert MANIFEST_PATH.exists(), f"Missing manifest: {MANIFEST_PATH}"
    with MANIFEST_PATH.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data, dict), "manifest.json must contain a JSON object"
    return data


def fixture_path(relative_path: str) -> Path:
    assert relative_path, "fixture relative path must not be empty"
    path = FIXTURE_ROOT / relative_path
    try:
        path.relative_to(FIXTURE_ROOT)
    except ValueError as exc:
        raise AssertionError(f"Fixture path escapes fixture root: {relative_path}") from exc
    return path


def test_v020_manifest_exists_and_has_required_top_level_fields() -> None:
    manifest = load_manifest()

    missing = EXPECTED_TOP_LEVEL_FIELDS - set(manifest)
    assert not missing, f"Missing manifest top-level fields: {sorted(missing)}"

    assert manifest["version"] == "0.2.0"
    assert manifest["schema_version"] == "v020_fixture_manifest_1"
    assert isinstance(manifest["allowed_source_types"], list)
    assert isinstance(manifest["required_case_fields"], list)
    assert isinstance(manifest["rules"], dict)
    assert isinstance(manifest["cases"], list)


def test_v020_allowed_source_types_are_complete_and_stable() -> None:
    manifest = load_manifest()
    allowed_source_types = set(manifest["allowed_source_types"])

    assert allowed_source_types == EXPECTED_SOURCE_TYPES
    assert "final_clear_json" in allowed_source_types
    assert "unknown" in allowed_source_types
    assert "manual_live_like_json" in allowed_source_types


def test_v020_manifest_rules_allow_future_normalized_output_and_optional_final_clear() -> None:
    manifest = load_manifest()
    rules = manifest["rules"]

    assert rules["final_clear_json_required"] is False
    assert rules["manual_live_like_json_must_be_marked"] is True
    assert rules["expected_json_contains_poker_decision"] is False
    assert rules["normalized_file_required_to_exist_before_normalizer"] is False
    assert rules["source_file_required_to_exist"] is True
    assert rules["expected_file_required_to_exist"] is True
    assert rules["duplicate_case_id_allowed"] is False


def test_v020_each_manifest_case_has_required_fields() -> None:
    manifest = load_manifest()
    required_fields = set(manifest["required_case_fields"])

    assert required_fields == EXPECTED_CASE_FIELDS
    assert manifest["cases"], "V0.2.4 expects at least one source-based fixture case"

    for case in manifest["cases"]:
        missing = required_fields - set(case)
        assert not missing, f"Case {case.get('case_id', '<missing>')} missing fields: {sorted(missing)}"


def test_v020_case_ids_are_unique() -> None:
    manifest = load_manifest()
    case_ids = [case["case_id"] for case in manifest["cases"]]

    assert len(case_ids) == len(set(case_ids)), f"Duplicate case_id values detected: {case_ids}"


def test_v020_case_source_types_are_valid() -> None:
    manifest = load_manifest()
    allowed_source_types = set(manifest["allowed_source_types"])

    for case in manifest["cases"]:
        assert case["source_type"] in allowed_source_types, (
            f"Case {case['case_id']} uses invalid source_type: {case['source_type']}"
        )


def test_v020_case_source_and_expected_files_exist() -> None:
    manifest = load_manifest()

    for case in manifest["cases"]:
        source_file = fixture_path(case["source_file"])
        expected_file = fixture_path(case["expected_file"])

        assert source_file.exists(), f"Missing source_file for {case['case_id']}: {source_file}"
        assert expected_file.exists(), f"Missing expected_file for {case['case_id']}: {expected_file}"

        with source_file.open("r", encoding="utf-8") as fh:
            source_data = json.load(fh)
        with expected_file.open("r", encoding="utf-8") as fh:
            expected_data = json.load(fh)

        assert isinstance(source_data, dict), f"Source JSON must be object for {case['case_id']}"
        assert isinstance(expected_data, dict), f"Expected JSON must be object for {case['case_id']}"


def test_v020_normalized_file_may_be_future_path_before_normalizer() -> None:
    manifest = load_manifest()
    rules = manifest["rules"]

    assert rules["normalized_file_required_to_exist_before_normalizer"] is False

    for case in manifest["cases"]:
        normalized_file = case["normalized_file"]
        assert normalized_file, f"normalized_file must be declared for {case['case_id']}"
        assert normalized_file.startswith("normalized/"), (
            f"normalized_file must point into normalized/: {case['case_id']} -> {normalized_file}"
        )
        # The file is intentionally not required to exist until the normalizer appears in V0.4.


def test_v020_final_clear_json_is_not_required_for_fixture_lab() -> None:
    manifest = load_manifest()
    rules = manifest["rules"]
    source_types_in_cases = {case["source_type"] for case in manifest["cases"]}

    assert rules["final_clear_json_required"] is False
    assert "dark_json" in source_types_in_cases
    # A fixture lab with no final_clear_json case is valid at this stage.


def test_v020_manual_live_like_source_is_not_mixed_with_real_source() -> None:
    manifest = load_manifest()

    for case in manifest["cases"]:
        is_real = case["is_real_project_source"]
        is_manual = case["is_manual_live_like_source"]

        assert isinstance(is_real, bool), f"is_real_project_source must be bool for {case['case_id']}"
        assert isinstance(is_manual, bool), f"is_manual_live_like_source must be bool for {case['case_id']}"
        assert not (is_real and is_manual), (
            f"Case cannot be both real-source and manual live-like: {case['case_id']}"
        )

        if is_manual:
            assert "manual" in case["source_of_truth_note"].lower() or "live-like" in case[
                "source_of_truth_note"
            ].lower(), f"Manual case must explain source-of-truth note: {case['case_id']}"


def test_v020_expected_json_contains_no_poker_decision() -> None:
    manifest = load_manifest()

    for case in manifest["cases"]:
        expected_file = fixture_path(case["expected_file"])
        with expected_file.open("r", encoding="utf-8") as fh:
            expected_data = json.load(fh)

        assert expected_data.get("expected_contains_poker_decision") is False
        forbidden_decision_keys = {
            "decision",
            "action",
            "recommended_action",
            "solver_action",
            "runtime_click_plan",
            "click_sequence",
        }
        forbidden_present = forbidden_decision_keys & set(expected_data)
        assert not forbidden_present, (
            f"Expected JSON must not contain poker decision keys for {case['case_id']}: "
            f"{sorted(forbidden_present)}"
        )
