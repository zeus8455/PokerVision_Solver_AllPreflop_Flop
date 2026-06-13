"""Tests for the V0.11.2 PokerKit backend adapter skeleton."""

from __future__ import annotations

import importlib
import inspect
import json
from pathlib import Path

from solver_postflop.equity_contracts import (
    EquityBackendStatus,
    EquityComputationMode,
)
from solver_postflop.equity_input_contracts import EquityScenarioInput


MODULE_NAME = "solver_postflop.equity_backend_pokerkit"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_SOURCE = PROJECT_ROOT / "solver_postflop" / "equity_backend_pokerkit.py"


def _scenario() -> EquityScenarioInput:
    return EquityScenarioInput(
        case_id="v0112_backend_skeleton_case",
        source_file="synthetic://v0112_backend_skeleton_case.clear.json",
        fields_used=("case_id", "source_file"),
    )


def test_backend_module_imports_without_installed_pokerkit_requirement() -> None:
    module = importlib.import_module(MODULE_NAME)

    assert hasattr(module, "is_pokerkit_available")
    assert hasattr(module, "run_pokerkit_backend")



def test_pokerkit_availability_check_returns_boolean() -> None:
    module = importlib.import_module(MODULE_NAME)

    assert isinstance(module.is_pokerkit_available(), bool)



def test_backend_unavailable_result_is_structured_and_json_safe() -> None:
    module = importlib.import_module(MODULE_NAME)

    result = module.build_backend_unavailable_result(reason="pokerkit_not_installed")
    payload = result.to_json_dict()

    assert result.backend_status is EquityBackendStatus.UNAVAILABLE
    assert result.computation_mode is EquityComputationMode.BACKEND_UNAVAILABLE
    assert result.backend_name == "pokerkit"
    assert result.hero_equity is None
    assert "pokerkit_not_installed" in result.notes
    assert payload["backend_status"] == "unavailable"
    assert payload["computation_mode"] == "backend_unavailable"
    json.dumps(payload, sort_keys=True)



def test_backend_error_result_is_structured_and_json_safe() -> None:
    module = importlib.import_module(MODULE_NAME)

    result = module.build_backend_error_result(error_message="synthetic backend error")
    payload = result.to_json_dict()

    assert result.backend_status is EquityBackendStatus.ERROR
    assert result.computation_mode is EquityComputationMode.BACKEND_ERROR
    assert result.hero_equity is None
    assert result.error_message == "synthetic backend error"
    assert "pokerkit_backend_error" in result.notes
    assert payload["backend_status"] == "error"
    json.dumps(payload, sort_keys=True)



def test_run_pokerkit_backend_never_breaks_pipeline() -> None:
    module = importlib.import_module(MODULE_NAME)

    result = module.run_pokerkit_backend(_scenario(), sample_count=128)

    assert result.backend_name == "pokerkit"
    assert result.hero_equity is None
    assert result.hero_win_rate is None
    assert result.hero_tie_rate is None
    assert result.runtime_ms is not None
    assert result.backend_metadata["sample_count_requested"] == 128
    assert result.backend_metadata["scenario_case_id"] == "v0112_backend_skeleton_case"
    assert result.backend_status in {
        EquityBackendStatus.UNAVAILABLE,
        EquityBackendStatus.NOT_RUN,
    }



def test_backend_source_has_no_hard_pokerkit_import() -> None:
    source = BACKEND_SOURCE.read_text(encoding="utf-8")

    forbidden_fragments = (
        "import pokerkit",
        "from pokerkit",
        "pokerkit import",
    )
    for fragment in forbidden_fragments:
        assert fragment not in source



def test_backend_source_has_no_decision_runtime_click_or_range_logic() -> None:
    source = BACKEND_SOURCE.read_text(encoding="utf-8").lower()

    forbidden_fragments = (
        "decision_engine",
        "runtime_plan",
        "click_result",
        "mouse",
        "action_button",
        "range_state",
        "range_importer",
        "blocker",
        "clear_json_pending",
        "dark_json",
        "current_cycle",
        "duplicate_card",
        "hero_board_collision",
        "filter_players",
    )
    for fragment in forbidden_fragments:
        assert fragment not in source



def test_backend_public_functions_are_small_skeleton_surface() -> None:
    module = importlib.import_module(MODULE_NAME)
    public_functions = {
        name
        for name, value in inspect.getmembers(module, inspect.isfunction)
        if not name.startswith("_")
    }

    assert public_functions == {
        "build_backend_error_result",
        "build_backend_unavailable_result",
        "is_pokerkit_available",
        "run_pokerkit_backend",
    }
