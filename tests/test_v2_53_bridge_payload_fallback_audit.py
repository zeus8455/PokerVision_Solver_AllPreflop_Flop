from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_v2_53_bridge_payload_fallback_audit_passes(tmp_path: Path) -> None:
    report_path = tmp_path / "v2_53_bridge_payload_fallback_audit.json"
    completed = subprocess.run(
        [
            sys.executable,
            "tools/run_v2_53_bridge_payload_fallback_audit.py",
            "--report-json",
            str(report_path),
        ],
        cwd=str(PROJECT_ROOT),
        check=True,
        text=True,
        capture_output=True,
    )

    assert "V2.53_BRIDGE_PAYLOAD_FALLBACK_AUDIT_OK = True" in completed.stdout

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["ok"] is True
    checks = report["checks"]

    assert checks["invalid_hero_payload_status_ok"] is True
    assert checks["invalid_hero_decision_action_fold"] is True
    assert checks["invalid_hero_decision_sequence_fold"] is True
    assert checks["postflop_payload_status_ok"] is True
    assert checks["postflop_decision_action_check_fold"] is True
    assert checks["postflop_decision_sequence_check_fold"] is True
