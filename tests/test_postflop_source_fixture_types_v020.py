"""V0.2.5 source-type policy tests for the postflop fixture lab."""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures" / "postflop"
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"

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


def _load_manifest() -> dict:
    assert MANIFEST_PATH.exists(), f"Missing manifest: {MANIFEST_PATH}"
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _load_expected(case: dict) -> dict:
    expected_path = FIXTURE_ROOT / case["expected_file"]
    assert expected_path.exists(), f"Missing expected JSON for {case['case_id']}: {expected_path}"
    return json.loads(expected_path.read_text(encoding="utf-8"))


def test_allowed_source_types_are_exact_and_stable() -> None:
    manifest = _load_manifest()
    assert set(manifest["allowed_source_types"]) == EXPECTED_SOURCE_TYPES


def test_every_case_uses_allowed_source_type() -> None:
    manifest = _load_manifest()
    allowed_source_types = set(manifest["allowed_source_types"])

    for case in manifest["cases"]:
        assert case["source_type"] in allowed_source_types, (
            f"Invalid source_type for {case['case_id']}: {case['source_type']}"
        )


def test_expected_json_matches_manifest_source_type() -> None:
    manifest = _load_manifest()

    for case in manifest["cases"]:
        expected = _load_expected(case)
        assert expected["expected_source_type"] == case["source_type"], (
            f"expected_source_type mismatch for {case['case_id']}"
        )


def test_manual_live_like_cases_are_not_real_sources() -> None:
    manifest = _load_manifest()

    for case in manifest["cases"]:
        if case["is_manual_live_like_source"]:
            assert case["is_real_project_source"] is False, (
                f"Manual live-like case cannot also be real source: {case['case_id']}"
            )
            joined_notes = " ".join(
                str(case.get(key, ""))
                for key in ("description", "source_of_truth_note", "notes")
            ).lower()
            assert "manual" in joined_notes or "live-like" in joined_notes, (
                f"Manual live-like case {case['case_id']} must be explicitly documented"
            )


def test_manual_live_like_source_type_is_not_required_for_manual_flag() -> None:
    manifest = _load_manifest()

    manual_cases = [case for case in manifest["cases"] if case["is_manual_live_like_source"]]
    assert manual_cases, "V0.2 fixture lab should include at least one manual live-like seed case"

    for case in manual_cases:
        assert case["source_type"] in EXPECTED_SOURCE_TYPES
        # A manual live-like case can emulate a real PokerVision source type,
        # for example source_type=dark_json with is_manual_live_like_source=true.
        assert case["is_real_project_source"] is False


def test_unknown_source_type_is_allowed_only_with_explicit_notes() -> None:
    manifest = _load_manifest()

    for case in manifest["cases"]:
        if case["source_type"] == "unknown":
            assert case.get("notes"), f"unknown source case {case['case_id']} must include notes"
            assert case.get("source_of_truth_note"), (
                f"unknown source case {case['case_id']} must include source_of_truth_note"
            )


def test_final_clear_json_is_optional_source_type() -> None:
    manifest = _load_manifest()
    rules = manifest["rules"]

    assert "final_clear_json" in manifest["allowed_source_types"]
    assert rules["final_clear_json_required"] is False

    # V0.2 must remain valid even without any final_clear_json case.
    final_clear_cases = [case for case in manifest["cases"] if case["source_type"] == "final_clear_json"]
    assert isinstance(final_clear_cases, list)


def test_source_type_controls_expected_click_cycle_policy() -> None:
    manifest = _load_manifest()

    for case in manifest["cases"]:
        expected = _load_expected(case)
        assert expected["expected_requires_click_cycle"] == case["requires_click_cycle"], (
            f"requires_click_cycle mismatch for {case['case_id']}"
        )


def test_no_fixture_expected_json_contains_poker_decision() -> None:
    manifest = _load_manifest()

    decision_keys = {
        "decision",
        "action",
        "recommended_action",
        "solver_action",
        "click_action",
        "runtime_plan",
    }

    for case in manifest["cases"]:
        expected = _load_expected(case)
        assert expected.get("expected_contains_poker_decision") is False
        assert not (decision_keys & set(expected.keys())), (
            f"Expected JSON for {case['case_id']} must not contain poker decision fields"
        )


def test_fixture_case_status_is_explicit() -> None:
    manifest = _load_manifest()
    allowed_statuses = {"active", "draft", "disabled", "needs_review"}

    for case in manifest["cases"]:
        assert case["status"] in allowed_statuses, (
            f"Unexpected fixture case status for {case['case_id']}: {case['status']}"
        )
