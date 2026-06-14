from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOL = PROJECT_ROOT / "tools" / "run_postflop_range_source_inventory.py"
RANGE_ROOT = PROJECT_ROOT / "ranges"
HERO_RANGE_FILE = RANGE_ROOT / "hero_preflop_ranges.json"
REPORT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "postflop_range_inventory"
    / "latest_range_source_inventory_report.json"
)


def _run_inventory() -> dict:
    completed = subprocess.run(
        [sys.executable, str(TOOL)],
        cwd=str(PROJECT_ROOT),
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert REPORT_PATH.exists()
    saved_payload = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert saved_payload == payload
    return payload


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_range_source_inventory_tool_runs_and_writes_report() -> None:
    payload = _run_inventory()

    assert payload["schema"] == "pokervision_solver_postflop_range_source_inventory_v1"
    assert payload["version_block"] == "V0.12.2"
    assert payload["status"] in {"ok", "range_root_missing", "no_json_range_files"}
    assert payload["real_project_touched"] is False
    assert payload["range_files_mutated"] is False
    assert payload["range_importer_executed"] is False
    assert payload["range_state_created"] is False
    assert payload["blocker_filtering_executed"] is False
    assert payload["equity_recalculation_executed"] is False
    assert payload["decision_logic_executed"] is False
    assert payload["runtime_plan_created"] is False
    assert payload["physical_click_executed"] is False


def test_range_source_inventory_finds_existing_hero_preflop_ranges_when_present() -> None:
    payload = _run_inventory()

    if not HERO_RANGE_FILE.exists():
        assert payload["hero_preflop_ranges_found"] is False
        return

    assert payload["range_root_exists"] is True
    assert payload["json_files_total"] >= 1
    assert payload["hero_preflop_ranges_found"] is True

    hero_entries = [
        item for item in payload["files"] if item["relative_path"] == "ranges/hero_preflop_ranges.json"
    ]
    assert len(hero_entries) == 1
    hero_entry = hero_entries[0]

    assert hero_entry["exists"] is True
    assert hero_entry["json_load_status"] == "ok"
    assert hero_entry["schema"] == "preflop_ranges_v1"
    assert hero_entry["source_type_candidate"] == "existing_project_ranges"
    assert hero_entry["contains_range_shorthand_strings"] is True
    assert hero_entry["usable_as_existing_project_range_source"] is True
    assert hero_entry["requires_expansion_before_v013"] is True
    assert "nodes" in hero_entry["top_level_keys"]
    assert "rfi" in hero_entry["detected_section_keys"]


def test_range_source_inventory_is_read_only_for_range_files() -> None:
    range_files = sorted(RANGE_ROOT.rglob("*.json")) if RANGE_ROOT.exists() else []
    before = {path.as_posix(): _sha256(path) for path in range_files}

    _run_inventory()

    after = {path.as_posix(): _sha256(path) for path in range_files}
    assert after == before


def test_range_source_inventory_classifies_shorthand_vs_combo_level_sources() -> None:
    payload = _run_inventory()

    if payload["status"] != "ok":
        assert payload["files"] == []
        return

    assert payload["existing_project_ranges_detected"] is True
    assert payload["shorthand_source_available"] is True
    assert payload["requires_combo_expansion_before_v013"] is True

    for item in payload["files"]:
        if item["json_load_status"] != "ok":
            continue
        assert "relative_path" in item
        assert "sha256" in item
        assert "top_level_type" in item
        assert "detected_action_keys" in item
        assert "contains_combo_level_compact_strings" in item


def test_range_source_inventory_source_has_no_importer_blocker_decision_or_runtime_logic() -> None:
    source = TOOL.read_text(encoding="utf-8").lower()
    forbidden_terms = [
        "build_range_state(",
        "create_rangestate(",
        "range_importer(",
        "filter_blockers(",
        "availablecombostate(",
        "calculate_equity(",
        "run_equity_engine(",
        "decision_engine(",
        "runtime_plan(",
        "click(",
        "mouse",
        "clear_json_pending",
        "dark_json",
        "current_cycle",
        "display_analysis_cycle",
    ]

    for forbidden in forbidden_terms:
        assert forbidden not in source
