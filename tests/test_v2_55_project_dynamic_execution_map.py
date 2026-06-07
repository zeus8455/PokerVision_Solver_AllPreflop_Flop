from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_v2_55_project_dynamic_execution_map_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "dynamic_map.json"
    out_md = tmp_path / "dynamic_map.md"

    completed = subprocess.run(
        [
            sys.executable,
            "tools/run_v2_55_project_dynamic_execution_map.py",
            "--project-root",
            str(PROJECT_ROOT),
            "--output-json",
            str(out_json),
            "--output-md",
            str(out_md),
            "--profile",
            "smoke",
            "--skip-pytest",
            "--skip-tools",
            "--self-smoke",
        ],
        cwd=str(PROJECT_ROOT),
        check=True,
        text=True,
        capture_output=True,
    )

    assert "V2.55_PROJECT_DYNAMIC_EXECUTION_MAP_OK = True" in completed.stdout
    assert out_json.exists()
    assert out_md.exists()

    report = json.loads(out_json.read_text(encoding="utf-8"))
    summary = report["summary"]

    assert report["schema"] == "v2_55_project_dynamic_execution_map_v1"
    assert summary["commands_total"] >= 1
    assert summary["executed_files_total"] >= 1
    assert summary["function_calls_total"] >= 1

    executed = {row["relpath"] for row in report["executed_files"]}
    assert "tools/run_v2_55_project_dynamic_execution_map.py" in executed
