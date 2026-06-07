from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_v2_57_cleanup_review_report_builds(tmp_path: Path) -> None:
    out_json = tmp_path / "cleanup.json"
    out_md = tmp_path / "cleanup.md"

    completed = subprocess.run(
        [
            sys.executable,
            "tools/run_v2_57_cleanup_review_report.py",
            "--project-root",
            str(PROJECT_ROOT),
            "--output-json",
            str(out_json),
            "--output-md",
            str(out_md),
        ],
        cwd=str(PROJECT_ROOT),
        check=True,
        text=True,
        capture_output=True,
    )

    assert "V2.57_CLEANUP_REVIEW_REPORT_OK = True" in completed.stdout
    assert out_json.exists()
    assert out_md.exists()

    report = json.loads(out_json.read_text(encoding="utf-8"))
    summary = report["summary"]

    assert report["schema"] == "v2_57_cleanup_review_report_v1"
    assert summary["files_scanned"] > 0
    assert "KEEP" in report["groups"]
    assert "REVIEW" in report["groups"]
    assert summary["external_protected_total"] > 0
