from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "build_v010_final_report.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("build_v010_final_report", TOOL)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def seed_reports(root: Path):
    out = root / "outputs" / "baseline_audit_v010"
    write_json(out / "project_baseline_report.json", {
        "risk_flags": ["readme_identity_mismatch"],
        "repo_identity": {"name": "PokerVision_Solver_AllPreflop_Flop"},
        "preflop_baseline_presence": {"solver_preflop": True},
        "external_snapshot_presence": {"external_snapshot": True},
    })
    write_json(out / "test_suite_health_report.json", {
        "total_test_files": 81,
        "by_category": {"core_baseline": 4, "live_dry_run": 55},
        "by_recommended_action": {"keep_but_not_blocking": 67},
    })
    write_json(out / "json_source_map_report.json", {
        "total_json_files": 187,
        "by_source_type": {"solver_payload_json": 101, "final_clear_json": 10},
        "before_click": 78,
        "after_click": 109,
    })
    write_json(out / "player_state_filtering_report.json", {
        "total_files_scanned": 1015,
        "mechanisms_found": 1297,
        "by_logic_type": {"hero_detection": 449, "sitout_filtering": 284},
        "should_not_duplicate": 1256,
    })


def test_v015_builds_final_report_from_four_source_reports(tmp_path: Path):
    module = load_tool()
    seed_reports(tmp_path)
    report = module.build_final_report(tmp_path)
    assert report["version"] == "V0.1.5"
    assert report["readiness_decision"]["ready_for_v020_design"] is True
    assert report["v010_findings"]["json_source_map"]["final_clear_json_optional"] is True
    assert "manual_live_like_json" in report["v020_plan"]["allowed_source_types"]
    assert report["v010_findings"]["player_state_filtering"]["should_not_duplicate_count"] == 1256


def test_v015_writes_final_json_and_markdown_outputs(tmp_path: Path):
    module = load_tool()
    seed_reports(tmp_path)
    report = module.build_final_report(tmp_path)
    paths = module.write_outputs(tmp_path, report)
    assert Path(paths["final_json"]).exists()
    assert Path(paths["final_markdown"]).exists()
    assert Path(paths["v020_plan_markdown"]).exists()
    loaded = json.loads(Path(paths["final_json"]).read_text(encoding="utf-8"))
    assert loaded["v020_plan"]["final_clear_json_required"] is False
    md = Path(paths["final_markdown"]).read_text(encoding="utf-8")
    assert "Final Clear_JSON" in md
    assert "V0.2.0" in md


def test_v015_reports_not_ready_when_required_source_report_missing(tmp_path: Path):
    module = load_tool()
    seed_reports(tmp_path)
    (tmp_path / "outputs" / "baseline_audit_v010" / "json_source_map_report.json").unlink()
    report = module.build_final_report(tmp_path)
    assert report["readiness_decision"]["ready_for_v020_design"] is False
    assert any(item["key"] == "json_source_map" for item in report["missing_or_failed_source_reports"])
