from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOL = PROJECT_ROOT / "tools" / "run_pokerkit_capability_probe.py"
REPORT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "postflop_pokerkit_capability"
    / "latest_pokerkit_capability_report.json"
)


def test_pokerkit_capability_probe_runs_and_writes_report() -> None:
    completed = subprocess.run(
        [sys.executable, str(TOOL)],
        cwd=str(PROJECT_ROOT),
        text=True,
        capture_output=True,
        check=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["schema"] == "pokervision_solver_postflop_pokerkit_capability_probe_v1"
    assert payload["version_block"] == "V0.11.3"
    assert payload["backend_name"] == "pokerkit"
    assert payload["status"] in {"available", "partial", "backend_unavailable"}
    assert payload["real_project_touched"] is False
    assert payload["equity_calculation_executed"] is False
    assert payload["monte_carlo_executed"] is False
    assert payload["simulation_executed"] is False
    assert payload["range_logic_executed"] is False
    assert payload["decision_logic_executed"] is False
    assert payload["runtime_plan_created"] is False
    assert payload["physical_click_executed"] is False

    assert REPORT_PATH.exists()
    saved_payload = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert saved_payload == payload


def test_pokerkit_capability_probe_reports_available_when_installed() -> None:
    completed = subprocess.run(
        [sys.executable, str(TOOL)],
        cwd=str(PROJECT_ROOT),
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(completed.stdout)

    if payload["importable"]:
        assert payload["status"] in {"available", "partial"}
        assert payload["package_version"]
        assert "pokerkit_importable" in payload["notes"]
    else:
        assert payload["status"] == "backend_unavailable"
        assert "pokerkit_not_importable" in payload["notes"]


def test_pokerkit_capability_probe_source_has_no_equity_or_runtime_logic() -> None:
    source = TOOL.read_text(encoding="utf-8").lower()

    forbidden_terms = [
        "calculate_equity(",
        "monte_carlo(",
        "run_simulation(",
        "build_range(",
        "narrow_range(",
        "blocker_filter(",
        "decision_engine(",
        "runtime_plan(",
        "click(",
        "mouse",
        "clear_json_pending",
        "dark_json",
        "current_cycle",
    ]

    for forbidden in forbidden_terms:
        assert forbidden not in source
