from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_v2_59_fixture_json_trust_review_builds(tmp_path: Path) -> None:
    root = tmp_path / "project"
    fixtures = root / "tests" / "fixtures" / "v2_59_case"
    tests = root / "tests"
    outputs = root / "outputs"
    fixtures.mkdir(parents=True)
    tests.mkdir(exist_ok=True)
    outputs.mkdir()

    (fixtures / "cases.json").write_text(json.dumps({"cases": [1]}), encoding="utf-8")
    (outputs / "report.json").write_text(json.dumps({"generated": True}), encoding="utf-8")
    (tests / "test_example.py").write_text('DATA = "tests/fixtures/v2_59_case/cases.json"\n', encoding="utf-8")

    out_json = root / "review.json"
    out_md = root / "review.md"

    completed = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "tools/run_v2_59_fixture_json_trust_review.py"),
            "--project-root",
            str(root),
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

    assert "V2.59_FIXTURE_JSON_TRUST_REVIEW_OK = True" in completed.stdout
    report = json.loads(out_json.read_text(encoding="utf-8"))

    assert report["schema"] == "v2_59_fixture_json_trust_review_v1"
    assert report["summary"]["json_files_total"] == 2

    by_rel = {row["relpath"]: row for row in report["json_files"]}
    assert by_rel["tests/fixtures/v2_59_case/cases.json"]["group"] == "FIXTURE_TRUTH_SOURCE_KEEP"
    assert by_rel["outputs/report.json"]["group"] == "GENERATED_OUTPUT_DELETE_CANDIDATE"
