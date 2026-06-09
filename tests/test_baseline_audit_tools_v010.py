from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_audit_module():
    module_path = Path(__file__).resolve().parents[1] / "tools" / "audit_current_project_baseline_v010.py"
    spec = importlib.util.spec_from_file_location("audit_current_project_baseline_v010", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def create_minimal_project(root: Path) -> None:
    (root / "solver_preflop").mkdir(parents=True)
    (root / "external" / "PokerVisionFinalVersionNoSolver_snapshot" / "PokerVision V1_2").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "tools").mkdir()
    (root / "outputs").mkdir()
    (root / "ranges").mkdir()
    (root / "examples" / "clear_json").mkdir(parents=True)
    (root / "docs" / "checkpoints").mkdir(parents=True)
    (root / "README.md").write_text(
        "# PokerVision_Solver_Preflop\n\ncd C:\\PokerVision_Solver_Preflop\n",
        encoding="utf-8",
    )
    (root / "VERSION.md").write_text("# VERSION\n\n## V2.60.0 fixture review inspection\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[tool.pytest.ini_options]\npythonpath = ['.']\n", encoding="utf-8")
    (root / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    for relative in [
        "__init__.py",
        "clear_json_adapter.py",
        "contracts.py",
        "decision_engine.py",
        "output_files.py",
        "pokervision_bridge.py",
        "range_engine.py",
        "range_loader.py",
        "range_parser.py",
        "sizing_policy.py",
        "spot_classifier.py",
    ]:
        (root / "solver_preflop" / relative).write_text("# test fixture\n", encoding="utf-8")


def test_build_report_detects_legacy_readme_and_preflop_baseline(tmp_path: Path) -> None:
    module = load_audit_module()
    create_minimal_project(tmp_path)

    report = module.build_report(tmp_path)

    assert report["schema_version"] == module.SCHEMA_VERSION
    assert report["readme_identity_check"]["contains_legacy_preflop_name"] is True
    assert report["readme_identity_check"]["identity_mismatch_detected"] is True
    assert report["preflop_baseline_presence"]["missing_count"] == 0
    assert report["postflop_core_presence"]["present_count"] == 0
    assert any(flag["code"] == "README_IDENTITY_MISMATCH" for flag in report["risk_flags"])


def test_write_reports_creates_json_and_markdown(tmp_path: Path) -> None:
    module = load_audit_module()
    create_minimal_project(tmp_path)
    report = module.build_report(tmp_path)

    paths = module.write_reports(report, tmp_path)

    json_path = Path(paths["json_report"])
    md_path = Path(paths["markdown_report"])
    assert json_path.exists()
    assert md_path.exists()
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["version_label"] == "V0.1.1"
    assert "Repo Identity / Baseline Audit" in md_path.read_text(encoding="utf-8")


def test_find_project_root_prefers_git_and_pyproject(tmp_path: Path) -> None:
    module = load_audit_module()
    project = tmp_path / "PokerVision_Solver_AllPreflop_Flop"
    nested = project / "tools" / "nested"
    nested.mkdir(parents=True)
    (project / ".git").mkdir()
    (project / "pyproject.toml").write_text("", encoding="utf-8")

    assert module.find_project_root(nested) == project
