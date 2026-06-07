from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_v2_58_delete_candidate_inspection_builds(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    (root / "apply_old.ps1").write_text("Write-Host old", encoding="utf-8")
    (root / "keep.py").write_text('print("keep")\n', encoding="utf-8")

    cleanup = {
        "schema": "v2_57_cleanup_review_report_v1",
        "groups": {
            "DELETE_CANDIDATE": [
                {
                    "relpath": "apply_old.ps1",
                    "category": "temp_scripts_or_archives",
                    "tracked": False,
                    "reasons": ["temporary apply artifact"],
                }
            ]
        },
    }
    cleanup_path = root / "cleanup.json"
    cleanup_path.write_text(json.dumps(cleanup), encoding="utf-8")

    out_json = root / "inspection.json"
    out_md = root / "inspection.md"

    completed = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "tools/run_v2_58_delete_candidate_inspection.py"),
            "--project-root",
            str(root),
            "--cleanup-json",
            str(cleanup_path),
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

    assert "V2.58_DELETE_CANDIDATE_INSPECTION_OK = True" in completed.stdout
    report = json.loads(out_json.read_text(encoding="utf-8"))

    assert report["schema"] == "v2_58_delete_candidate_inspection_v1"
    assert report["summary"]["delete_candidates_total"] == 1
    assert report["candidates"][0]["decision"]["verdict"] == "APPROVE_DELETE_CANDIDATE"
