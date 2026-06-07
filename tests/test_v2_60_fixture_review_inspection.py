from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_v2_60_fixture_review_inspection_builds(tmp_path: Path) -> None:
    root = tmp_path / "project"
    fixture_dir = root / "tests" / "fixtures" / "old_case"
    fixture_dir.mkdir(parents=True)
    fixture = fixture_dir / "cases.json"
    fixture.write_text(json.dumps({"cases": [{"expected": "fold", "hero_cards": ["A_spades", "K_spades"]}]}), encoding="utf-8")
    trust = {
        "schema": "v2_59_fixture_json_trust_review_v1",
        "json_files": [{
            "relpath": "tests/fixtures/old_case/cases.json",
            "group": "FIXTURE_REVIEW",
            "references_count": 0,
            "references_sample": [],
        }],
    }
    trust_path = root / "trust.json"
    trust_path.write_text(json.dumps(trust), encoding="utf-8")
    out_json = root / "inspection.json"
    out_md = root / "inspection.md"
    completed = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "tools/run_v2_60_fixture_review_inspection.py"),
            "--project-root", str(root),
            "--trust-json", str(trust_path),
            "--output-json", str(out_json),
            "--output-md", str(out_md),
        ],
        cwd=str(PROJECT_ROOT),
        check=True,
        text=True,
        capture_output=True,
    )
    assert "V2.60_FIXTURE_REVIEW_INSPECTION_OK = True" in completed.stdout
    report = json.loads(out_json.read_text(encoding="utf-8"))
    assert report["schema"] == "v2_60_fixture_review_inspection_v1"
    assert report["summary"]["fixture_review_total"] == 1
    assert report["fixtures"][0]["recommendation"] in {"ARCHIVE_CANDIDATE", "MIGRATE_TO_CURRENT_FIXTURE", "KEEP", "DELETE_CANDIDATE"}
