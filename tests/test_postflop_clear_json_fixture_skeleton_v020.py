from __future__ import annotations

import json
from pathlib import Path


FIXTURE_ROOT = Path("tests/fixtures/postflop_clear_json")


REQUIRED_DIRECTORIES = (
    FIXTURE_ROOT / "real" / "flop",
    FIXTURE_ROOT / "real" / "turn",
    FIXTURE_ROOT / "real" / "river",
    FIXTURE_ROOT / "synthetic" / "flop",
    FIXTURE_ROOT / "synthetic" / "turn",
    FIXTURE_ROOT / "synthetic" / "river",
    FIXTURE_ROOT / "templates",
    FIXTURE_ROOT / "expected",
)


LEGACY_SOURCE_FIRST_NAMES = (
    "source_json",
    "dark_json",
    "pending_json",
    "service_json",
    "runtime_json",
)


def test_clear_json_fixture_root_exists() -> None:
    assert FIXTURE_ROOT.exists()
    assert FIXTURE_ROOT.is_dir()


def test_real_street_directories_exist() -> None:
    for street in ("flop", "turn", "river"):
        path = FIXTURE_ROOT / "real" / street
        assert path.exists()
        assert path.is_dir()


def test_synthetic_street_directories_exist() -> None:
    for street in ("flop", "turn", "river"):
        path = FIXTURE_ROOT / "synthetic" / street
        assert path.exists()
        assert path.is_dir()


def test_template_and_expected_directories_exist() -> None:
    assert (FIXTURE_ROOT / "templates").is_dir()
    assert (FIXTURE_ROOT / "expected").is_dir()


def test_skeleton_directories_are_git_tracked_with_gitkeep() -> None:
    for path in REQUIRED_DIRECTORIES:
        marker = path / ".gitkeep"
        assert marker.exists()
        assert marker.is_file()


def test_manifest_exists_and_uses_clear_json_library_schema() -> None:
    manifest_path = FIXTURE_ROOT / "manifest.json"
    assert manifest_path.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["schema_version"] in {"0.2.2", "0.2.3"}
    assert manifest["library_kind"] == "clear_json_fixture_library"
    assert manifest["architecture"] == "clear_json_only"
    assert manifest["fixture_root"] == "tests/fixtures/postflop_clear_json"


def test_manifest_cases_are_list_for_current_fixture_library_state() -> None:
    manifest_path = FIXTURE_ROOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert "cases" in manifest
    assert isinstance(manifest["cases"], list)


def test_fixture_root_does_not_recreate_source_first_tree() -> None:
    existing_names = {path.name for path in FIXTURE_ROOT.rglob("*")}

    for forbidden_name in LEGACY_SOURCE_FIRST_NAMES:
        assert forbidden_name not in existing_names
