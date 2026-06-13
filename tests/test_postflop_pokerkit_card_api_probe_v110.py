from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOL = PROJECT_ROOT / "tools" / "run_pokerkit_card_api_probe.py"
REPORT = (
    PROJECT_ROOT
    / "outputs"
    / "postflop_pokerkit_card_api"
    / "latest_pokerkit_card_api_report.json"
)


def _run_probe() -> dict:
    completed = subprocess.run(
        [sys.executable, str(TOOL)],
        cwd=str(PROJECT_ROOT),
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(completed.stdout)
    assert REPORT.exists()
    report_payload = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report_payload == payload
    return payload


def test_pokerkit_card_api_probe_runs_and_writes_report() -> None:
    payload = _run_probe()

    assert payload["schema"] == "pokervision_solver_postflop_pokerkit_card_api_probe_v1"
    assert payload["version_block"] == "V0.11.5"
    assert payload["backend_name"] == "pokerkit"
    assert payload["status"] in {"available", "api_probe_partial", "backend_unavailable", "symbol_mismatch"}
    assert payload["real_project_touched"] is False


def test_pokerkit_card_api_probe_reports_card_mapping_when_available() -> None:
    payload = _run_probe()

    if payload["status"] != "available":
        assert payload["importable"] in {False, True}
        return

    assert payload["importable"] is True
    assert payload["package_version"]
    assert payload["missing_symbols"] == []
    assert {"Card", "Rank", "Suit", "StandardHighHand"}.issubset(set(payload["available_symbols"]))
    assert payload["hero_compact"] == "AsKh"
    assert payload["board_compact"] == "QdJcTs2c3d"

    mapping = {item["source"]: item for item in payload["sample_mapping_results"]}
    assert mapping["A_spades"]["compact"] == "As"
    assert mapping["K_hearts"]["compact"] == "Kh"
    assert mapping["10_spades"]["compact"] == "Ts"
    assert all(item["ok"] for item in payload["sample_mapping_results"])


def test_pokerkit_card_api_probe_evaluates_standard_high_hand_when_available() -> None:
    payload = _run_probe()

    if payload["status"] != "available":
        return

    assert payload["card_parse_error"] is None
    assert payload["hand_evaluation_error"] is None
    assert payload["parsed_card_compacts"] == ["As", "Kh", "Qd", "Jc", "Ts", "2c", "3d"]
    assert len(payload["parsed_card_strings"]) == 7
    assert payload["parsed_card_strings"][0].endswith("(As)")
    assert payload["parsed_card_strings"][1].endswith("(Kh)")
    assert payload["standard_high_hand_created"] is True
    assert payload["standard_high_hand_cards"]
    assert payload["standard_high_comparison_ok"] is True
    assert "standard_high_hand_evaluation_ok" in payload["notes"]


def test_pokerkit_card_api_probe_has_no_solver_side_effects() -> None:
    payload = _run_probe()

    assert payload["equity_calculation_executed"] is False
    assert payload["simulation_executed"] is False
    assert payload["monte_carlo_executed"] is False
    assert payload["range_logic_executed"] is False
    assert payload["decision_logic_executed"] is False
    assert payload["runtime_plan_created"] is False
    assert payload["physical_click_executed"] is False


def test_pokerkit_card_api_probe_source_has_no_equity_or_runtime_logic() -> None:
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
