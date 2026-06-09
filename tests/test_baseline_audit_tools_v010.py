from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASELINE_TOOL = PROJECT_ROOT / "tools" / "audit_current_project_baseline_v010.py"
TEST_SUITE_TOOL = PROJECT_ROOT / "tools" / "audit_current_test_suite_health_v010.py"


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
