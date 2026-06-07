from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_v2_54_project_static_logic_map_builds(tmp_path: Path) -> None:
    out_json = tmp_path / "static_map.json"
    out_md = tmp_path / "static_map.md"

    completed = subprocess.run(
        [
            sys.executable,
            "tools/run_v2_54_project_static_logic_map.py",
            "--project-root",
            str(PROJECT_ROOT),
            "--output-json",
            str(out_json),
            "--output-md",
            str(out_md),
            "--skip-pytest-collect",
        ],
        cwd=str(PROJECT_ROOT),
        check=True,
        text=True,
        capture_output=True,
    )

    assert "V2.54_PROJECT_STATIC_LOGIC_MAP_OK = True" in completed.stdout
    assert out_json.exists()
    assert out_md.exists()

    report = json.loads(out_json.read_text(encoding="utf-8"))
    summary = report["summary"]

    assert report["schema"] == "v2_54_project_static_logic_map_v1"
    assert summary["python_files_total"] > 0
    assert summary["entrypoints_total"] > 0
    assert summary["tool_scripts_total"] > 0
    assert summary["tests_total"] > 0
    assert "syntax_errors_total" in summary

    relpaths = {item["relpath"] for item in report["files"]}
    assert "solver_preflop/spot_classifier.py" in relpaths
    assert "solver_preflop/range_engine.py" in relpaths
    assert "tools/run_v2_54_project_static_logic_map.py" in relpaths
