from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_v2_56_project_logic_coverage_report_builds(tmp_path: Path) -> None:
    static_json = tmp_path / "static.json"
    dynamic_json = tmp_path / "dynamic.json"
    output_json = tmp_path / "merge.json"
    output_md = tmp_path / "merge.md"

    completed = subprocess.run(
        [
            sys.executable,
            "tools/run_v2_56_project_logic_coverage_report.py",
            "--project-root",
            str(PROJECT_ROOT),
            "--static-json",
            str(static_json),
            "--dynamic-json",
            str(dynamic_json),
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
            "--refresh-static",
            "--refresh-dynamic",
            "--dynamic-profile",
            "smoke",
            "--dynamic-skip-tools",
            "--dynamic-skip-pytest",
            "--skip-pytest-collect",
        ],
        cwd=str(PROJECT_ROOT),
        check=True,
        text=True,
        capture_output=True,
    )

    assert "V2.56_PROJECT_LOGIC_COVERAGE_REPORT_OK = True" in completed.stdout
    assert output_json.exists()
    assert output_md.exists()

    report = json.loads(output_json.read_text(encoding="utf-8"))
    summary = report["summary"]

    assert report["schema"] == "v2_56_project_logic_coverage_report_v1"
    assert summary["static_python_files_total"] > 0
    assert summary["dynamic_executed_files_total"] > 0
    assert "safe_to_delete_candidates" in report
    assert "dead_legacy_candidates" in report
    assert "runtime_only_files" in report
