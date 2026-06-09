"""Run V0.3.0 postflop contract gate.

This tool is intentionally limited to the V0.3 contract test set.
It does not implement source discovery, normalization, street detection,
preflop history reconstruction, poker decisions, runtime plans, or clicks.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "postflop_contracts_v030"
REPORT_PATH = OUTPUT_DIR / "contract_gate_report.json"

TEST_FILES = [
    "tests/test_postflop_contracts_v030.py",
    "tests/test_postflop_source_contracts_v030.py",
    "tests/test_postflop_normalized_frame_contract_v030.py",
    "tests/test_postflop_module_result_contracts_v030.py",
]

CONTRACT_LAYERS = [
    {
        "layer_id": "base_types",
        "description": "PostflopSourceType, ContractSeverity, ContractValidationError, ModuleWarning, ModuleError.",
    },
    {
        "layer_id": "source_contracts",
        "description": "PostflopSourceCandidate, PostflopRawSource, PostflopSourceDiscoveryResult.",
    },
    {
        "layer_id": "normalized_frame_contracts",
        "description": "PostflopPlayerSnapshot, PostflopBoardSnapshot, PostflopActionSnapshot, NormalizedPostflopFrame.",
    },
    {
        "layer_id": "module_result_contracts",
        "description": "StreetDetectionResult, PreflopHistoryResult, PostflopDecision, PostflopRuntimePlan, PostflopTrace, PostflopProbeReport.",
    },
]


def _parse_pytest_counts(output: str) -> dict[str, int]:
    """Parse common pytest summary counts from stdout/stderr."""
    counts = {
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0,
    }
    patterns = {
        "passed": r"(\d+)\s+passed",
        "failed": r"(\d+)\s+failed",
        "errors": r"(\d+)\s+errors?",
        "skipped": r"(\d+)\s+skipped",
        "xfailed": r"(\d+)\s+xfailed",
        "xpassed": r"(\d+)\s+xpassed",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            counts[key] = int(match.group(1))
    return counts


def _test_file_statuses() -> list[dict[str, Any]]:
    statuses: list[dict[str, Any]] = []
    for test_file in TEST_FILES:
        path = PROJECT_ROOT / test_file
        statuses.append(
            {
                "test_file": test_file,
                "exists": path.exists(),
                "path": str(path),
            }
        )
    return statuses


def build_report(command: list[str], completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    combined_output = "\n".join(part for part in [completed.stdout, completed.stderr] if part)
    counts = _parse_pytest_counts(combined_output)
    missing_tests = [item["test_file"] for item in _test_file_statuses() if not item["exists"]]
    passed = completed.returncode == 0 and not missing_tests

    report: dict[str, Any] = {
        "version": "V0.3.0",
        "subversion": "V0.3.5",
        "name": "Postflop Source Contracts - Contract Test Gate",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if passed else "failed",
        "ready_for_v040": bool(passed),
        "pytest_command": command,
        "test_files": TEST_FILES,
        "test_file_statuses": _test_file_statuses(),
        "missing_test_files": missing_tests,
        "return_code": completed.returncode,
        "passed_count": counts["passed"],
        "failed_count": counts["failed"],
        "error_count": counts["errors"],
        "skipped_count": counts["skipped"],
        "contract_layers": CONTRACT_LAYERS,
        "v030_rules": {
            "does_not_search_json_files": True,
            "does_not_normalize_real_json": True,
            "does_not_detect_street": True,
            "does_not_reconstruct_preflop_history": True,
            "does_not_make_poker_decisions": True,
            "does_not_create_runtime_click_plan": True,
            "does_not_click": True,
            "does_not_modify_pokervision_runtime": True,
        },
        "stdout_tail": completed.stdout[-6000:] if completed.stdout else "",
        "stderr_tail": completed.stderr[-6000:] if completed.stderr else "",
        "notes": [
            "V0.3.5 closes the V0.3.0 contract layer only.",
            "The next block is V0.4.0 Source Discovery + Postflop Normalizer.",
            "contracts.py should not be changed in V0.3.5 unless the contract gate fails for a real compatibility reason.",
        ],
    }
    return report


def run_contract_gate() -> int:
    command = [sys.executable, "-m", "pytest", *TEST_FILES, "-q"]
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    report = build_report(command, completed)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)

    print(f"[V0.3.5] Contract gate status: {report['status']}")
    print(f"Report: {REPORT_PATH}")
    print(f"Ready for V0.4.0: {report['ready_for_v040']}")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(run_contract_gate())
