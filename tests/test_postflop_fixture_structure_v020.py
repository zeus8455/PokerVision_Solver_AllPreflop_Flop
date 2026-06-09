"""V0.2.5 fixture-lab structure tests.

These tests protect the source-based postflop fixture lab directory layout.
They intentionally do not run source discovery, normalization, solver logic,
runtime logic, or click-chain logic.
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures" / "postflop"
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"

ROOT_DIRECTORIES = {
    "source_json",
    "live_like_tree",
    "normalized",
    "expected",
}

SOURCE_TYPE_DIRECTORIES = {
    "dark_json",
    "pending_json",
    "service_json",
    "current_cycle_json",
    "runtime_json",
    "solver_payload_json",
    "final_clear_json",
    "manual_live_like_json",
}


def _load_manifest() -> dict:
    assert MANIFEST_PATH.exists(), f"Missing postflop fixture manifest: {MANIFEST_PATH}"
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_postflop_fixture_root_and_manifest_exist() -> None:
    assert FIXTURE_ROOT.exists(), f"Missing fixture root: {FIXTURE_ROOT}"
    assert FIXTURE_ROOT.is_dir(), f"Fixture root is not a directory: {FIXTURE_ROOT}"
    assert MANIFEST_PATH.exists(), f"Missing manifest: {MANIFEST_PATH}"
    assert MANIFEST_PATH.is_file(), f"Manifest is not a file: {MANIFEST_PATH}"


def test_postflop_fixture_root_directories_exist() -> None:
    for directory_name in sorted(ROOT_DIRECTORIES):
        directory_path = FIXTURE_ROOT / directory_name
        assert directory_path.exists(), f"Missing fixture directory: {directory_path}"
        assert directory_path.is_dir(), f"Fixture path is not a directory: {directory_path}"


def test_postflop_source_json_type_directories_exist() -> None:
    source_root = FIXTURE_ROOT / "source_json"
    assert source_root.exists(), f"Missing source_json root: {source_root}"

    for source_type in sorted(SOURCE_TYPE_DIRECTORIES):
        source_type_dir = source_root / source_type
        assert source_type_dir.exists(), f"Missing source_json/{source_type} directory"
        assert source_type_dir.is_dir(), f"source_json/{source_type} is not a directory"


def test_manifest_allowed_source_types_are_represented_by_structure() -> None:
    manifest = _load_manifest()
    allowed_source_types = set(manifest["allowed_source_types"])

    # unknown is a valid classification, but it does not require its own
    # dedicated source_json/unknown directory at V0.2.x.
    allowed_types_requiring_dirs = allowed_source_types - {"unknown"}

    assert allowed_types_requiring_dirs == SOURCE_TYPE_DIRECTORIES


def test_manifest_case_files_are_inside_fixture_root() -> None:
    manifest = _load_manifest()

    for case in manifest["cases"]:
        case_id = case["case_id"]
        source_file = FIXTURE_ROOT / case["source_file"]
        expected_file = FIXTURE_ROOT / case["expected_file"]

        assert source_file.exists(), f"Missing source_file for {case_id}: {source_file}"
        assert expected_file.exists(), f"Missing expected_file for {case_id}: {expected_file}"

        assert source_file.resolve().is_relative_to(FIXTURE_ROOT.resolve())
        assert expected_file.resolve().is_relative_to(FIXTURE_ROOT.resolve())


def test_manifest_source_files_are_in_expected_source_type_locations() -> None:
    manifest = _load_manifest()

    for case in manifest["cases"]:
        case_id = case["case_id"]
        source_type = case["source_type"]
        source_file = Path(case["source_file"])

        if source_type == "unknown":
            # Unknown sources are allowed, but still need explicit notes.
            assert case.get("notes"), f"unknown source case {case_id} must include notes"
            continue

        expected_prefix = Path("source_json") / source_type
        assert source_file.parts[:2] == expected_prefix.parts, (
            f"Case {case_id} source_file must live under {expected_prefix}, "
            f"got {source_file}"
        )


def test_expected_directory_contains_expected_files_for_cases() -> None:
    manifest = _load_manifest()

    for case in manifest["cases"]:
        case_id = case["case_id"]
        expected_file = Path(case["expected_file"])
        assert expected_file.parts[0] == "expected", (
            f"Case {case_id} expected_file must live under expected/, got {expected_file}"
        )
        assert (FIXTURE_ROOT / expected_file).exists()


def test_normalized_directory_may_be_empty_before_normalizer() -> None:
    manifest = _load_manifest()
    normalized_root = FIXTURE_ROOT / "normalized"
    assert normalized_root.exists(), "normalized directory must exist even before normalizer"

    for case in manifest["cases"]:
        case_id = case["case_id"]
        normalized_file = case.get("normalized_file")
        assert normalized_file, f"Case {case_id} must reserve a normalized_file future path"
        assert Path(normalized_file).parts[0] == "normalized", (
            f"Case {case_id} normalized_file must be under normalized/, got {normalized_file}"
        )
        # The normalized output is intentionally allowed to be absent until V0.4.
        assert manifest["rules"]["normalized_file_required_to_exist_before_normalizer"] is False


def test_final_clear_json_directory_may_be_empty() -> None:
    manifest = _load_manifest()
    final_clear_dir = FIXTURE_ROOT / "source_json" / "final_clear_json"

    assert final_clear_dir.exists(), "final_clear_json directory should exist for future sources"
    assert manifest["rules"]["final_clear_json_required"] is False

    case_source_types = {case["source_type"] for case in manifest["cases"]}
    # A valid V0.2 fixture lab does not need a final_clear_json fixture case.
    assert "final_clear_json" not in case_source_types or manifest["rules"]["final_clear_json_required"] is False
