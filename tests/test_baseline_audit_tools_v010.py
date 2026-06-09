from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASELINE_TOOL = PROJECT_ROOT / "tools" / "audit_current_project_baseline_v010.py"
TEST_SUITE_TOOL = PROJECT_ROOT / "tools" / "audit_current_test_suite_health_v010.py"
JSON_SOURCE_TOOL = PROJECT_ROOT / "tools" / "audit_current_json_source_map_v010.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_v010_audit_tool_files_exist():
    assert BASELINE_TOOL.exists(), "V0.1.1 baseline audit tool is missing"
    assert TEST_SUITE_TOOL.exists(), "V0.1.2 test suite health audit tool is missing"
    assert JSON_SOURCE_TOOL.exists(), "V0.1.3 JSON source map audit tool is missing"


def test_v012_classifies_core_legacy_live_and_static_files():
    module = load_module(TEST_SUITE_TOOL, "audit_current_test_suite_health_v010")

    assert module.classify_test_file("tests/test_decision_engine.py", "from solver_preflop.decision_engine import x") == "core_baseline"
    assert module.classify_test_file("tests/test_v2_60_fixture_review_inspection.py", "def test_fixture(): pass") == "legacy_old_audit"
    assert module.classify_test_file("tests/test_live_runtime_click.py", "POKERVISION_CONTROLLED_LIVE_CLICK = True") == "live_dry_run"
    assert module.classify_test_file("tests/test_baseline_audit_tools_v010.py", "baseline_audit source_map") == "static_dynamic_map"


def test_v012_detects_requirements_and_recommendations():
    module = load_module(TEST_SUITE_TOOL, "audit_current_test_suite_health_v010")

    live, external, old_outputs, notes = module.detect_requirements(
        "tests/test_runtime_snapshot.py",
        "external/PokerVisionFinalVersionNoSolver_snapshot outputs/ui_display_cycle/current_cycle real_click",
    )

    assert live is True
    assert external is True
    assert old_outputs is True
    assert notes

    action = module.choose_recommended_action(
        category="core_baseline",
        collect_status="passed",
        run_status="passed",
        requires_live_environment=False,
        requires_external_snapshot=False,
        requires_old_outputs=False,
    )
    assert action == "keep_as_required_baseline"


def test_v012_builds_report_and_writes_outputs(tmp_path: Path):
    module = load_module(TEST_SUITE_TOOL, "audit_current_test_suite_health_v010")

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_decision_engine.py").write_text(
        "def test_minimal_core():\n    assert 1 + 1 == 2\n",
        encoding="utf-8",
    )
    (tests_dir / "test_live_runtime_click.py").write_text(
        "def test_live_marker():\n    POKERVISION_CONTROLLED_LIVE_CLICK = False\n    assert POKERVISION_CONTROLLED_LIVE_CLICK is False\n",
        encoding="utf-8",
    )

    report = module.build_report(tmp_path, run_mode="collect-only", timeout_seconds=15)
    assert report["schema_version"] == module.SCHEMA_VERSION
    assert report["summary"]["total_test_files"] == 2

    json_path, markdown_path = module.write_reports(tmp_path, report)
    assert json_path.exists()
    assert markdown_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["summary"]["total_test_files"] == 2
    assert "Test Suite Health Audit" in markdown_path.read_text(encoding="utf-8")


def test_v013_source_types_match_v020_v030_policy():
    module = load_module(JSON_SOURCE_TOOL, "audit_current_json_source_map_v010")

    assert module.SCHEMA_VERSION == "v0.1.3-json-source-map"
    assert set(module.ALLOWED_SOURCE_TYPES) == {
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
    assert module.infer_source_type_from_path_and_payload("outputs/Dark_JSON/flop_case.dark.json", None) == "dark_json"
    assert module.infer_source_type_from_path_and_payload("outputs/solver_payloads/table_01.json", None) == "solver_payload_json"
    assert module.infer_source_type_from_path_and_payload("tests/fixtures/postflop/source_json/manual_live_like_json/case.json", None) == "manual_live_like_json"


def test_v013_scans_json_features_and_click_availability(tmp_path: Path):
    module = load_module(JSON_SOURCE_TOOL, "audit_current_json_source_map_v010")

    dark_dir = tmp_path / "outputs" / "Dark_JSON"
    final_dir = tmp_path / "outputs" / "JSON_Complete"
    manual_dir = tmp_path / "tests" / "fixtures" / "postflop" / "source_json" / "manual_live_like_json"
    dark_dir.mkdir(parents=True)
    final_dir.mkdir(parents=True)
    manual_dir.mkdir(parents=True)

    dark_file = dark_dir / "flop_source_case_001.dark.json"
    dark_file.write_text(
        json.dumps(
            {
                "street": "flop",
                "board_cards": ["As", "Kd", "7c"],
                "hero_cards": ["Ah", "Kh"],
                "players": [{"seat": 1, "stack": 100}],
                "actions": [],
            }
        ),
        encoding="utf-8",
    )
    final_file = final_dir / "table_01_final_clear.json"
    final_file.write_text(
        json.dumps({"street": "flop", "click_result": {"status": "clicked"}, "players": []}),
        encoding="utf-8",
    )
    manual_file = manual_dir / "manual_case.json"
    manual_file.write_text(json.dumps({"street_candidate": "flop", "players": []}), encoding="utf-8")

    dark = module.scan_json_file(dark_file, tmp_path)
    final = module.scan_json_file(final_file, tmp_path)
    manual = module.scan_json_file(manual_file, tmp_path)

    assert dark["source_type"] == "dark_json"
    assert dark["available_before_click"] is True
    assert dark["requires_click_cycle"] is False
    assert dark["contains_board_cards"] is True
    assert dark["contains_hero_cards"] is True
    assert dark["can_be_used_for_fixture_lab_v020"] is True
    assert dark["can_become_source_candidate_v030"] is True

    assert final["source_type"] == "final_clear_json"
    assert final["available_after_click"] is True
    assert final["requires_click_cycle"] is True
    assert final["contains_click_result"] is True

    assert manual["source_type"] == "manual_live_like_json"
    assert manual["is_manual_live_like_source"] is True
    assert manual["is_real_project_source"] is False


def test_v013_builds_report_and_writes_outputs(tmp_path: Path):
    module = load_module(JSON_SOURCE_TOOL, "audit_current_json_source_map_v010")

    source_dir = tmp_path / "outputs" / "current_cycle"
    tools_dir = tmp_path / "tools"
    source_dir.mkdir(parents=True)
    tools_dir.mkdir(parents=True)

    (source_dir / "table_01_current_cycle.json").write_text(
        json.dumps({"street": "flop", "players": [], "board_cards": ["2h", "3d", "4c"]}),
        encoding="utf-8",
    )
    (tools_dir / "fake_writer.py").write_text(
        "import json\n\ndef save(path, data):\n    json.dump(data, open(path, 'w'))\n",
        encoding="utf-8",
    )

    report = module.build_report(tmp_path)
    assert report["schema_version"] == module.SCHEMA_VERSION
    assert report["fixture_lab_v020_policy"]["final_clear_json_is_optional"] is True
    assert report["fixture_lab_v020_policy"]["manual_live_like_json_must_be_explicit"] is True
    assert report["summary"]["total_json_files_scanned"] == 1
    assert report["summary"]["available_before_click_count"] == 1
    assert report["summary"]["total_code_references"] >= 1

    json_path, markdown_path = module.write_reports(tmp_path, report)
    assert json_path.exists()
    assert markdown_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["summary"]["final_clear_json_optional_confirmed"] is True
    assert "JSON Source Map Audit" in markdown_path.read_text(encoding="utf-8")
