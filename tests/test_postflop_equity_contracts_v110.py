from __future__ import annotations

import inspect
import json
import sys
from dataclasses import asdict, is_dataclass

from solver_postflop.equity_contracts import (
    DEFAULT_EQUITY_BACKEND_NAME,
    EQUITY_BACKEND_STATUSES,
    EQUITY_COMPUTATION_MODES,
    EQUITY_CONFIDENCE_CLASSES,
    EQUITY_CONTRACT_VERSION,
    EquityBackendResult,
    EquityBackendStatus,
    EquityComputationMode,
    EquityConfidenceClass,
    EquityPlayerResult,
    EquityResult,
)
import solver_postflop.equity_contracts as equity_contracts


def test_equity_contract_version_is_fixed_for_v0111() -> None:
    assert EQUITY_CONTRACT_VERSION == "v0.11.1"


def test_equity_computation_modes_are_fixed_for_raw_snapshot_layer() -> None:
    assert {mode.value for mode in EquityComputationMode} == {
        "heads_up_raw_equity",
        "multiway_raw_equity",
        "unknown_context_equity",
        "backend_unavailable",
        "backend_error",
    }
    assert EQUITY_COMPUTATION_MODES == tuple(EquityComputationMode)


def test_equity_confidence_classes_are_fixed() -> None:
    assert {item.value for item in EquityConfidenceClass} == {
        "high",
        "medium",
        "low",
        "unknown",
    }
    assert EQUITY_CONFIDENCE_CLASSES == tuple(EquityConfidenceClass)


def test_equity_backend_statuses_are_structured() -> None:
    assert {item.value for item in EquityBackendStatus} == {
        "ok",
        "unavailable",
        "error",
        "not_run",
    }
    assert EQUITY_BACKEND_STATUSES == tuple(EquityBackendStatus)
    assert DEFAULT_EQUITY_BACKEND_NAME == "pokerkit"


def test_equity_player_result_can_be_created_and_serialized() -> None:
    player = EquityPlayerResult(
        player_id="hero",
        position="BTN",
        role="hero",
        equity=0.64,
        win_rate=0.61,
        tie_rate=0.03,
        confidence=EquityConfidenceClass.MEDIUM,
        notes=("raw_snapshot",),
    )

    assert is_dataclass(player)
    assert asdict(player)["player_id"] == "hero"

    payload = player.to_json_dict()
    assert payload == {
        "player_id": "hero",
        "position": "BTN",
        "role": "hero",
        "equity": 0.64,
        "win_rate": 0.61,
        "tie_rate": 0.03,
        "confidence": "medium",
        "notes": ["raw_snapshot"],
    }
    json.dumps(payload, sort_keys=True)


def test_equity_backend_result_can_represent_unavailable_backend() -> None:
    backend = EquityBackendResult(
        backend_name="pokerkit",
        backend_status=EquityBackendStatus.UNAVAILABLE,
        computation_mode=EquityComputationMode.BACKEND_UNAVAILABLE,
        error_message="backend package is not installed",
        notes=("structured_unavailable_result",),
    )

    payload = backend.to_json_dict()
    assert payload["backend_name"] == "pokerkit"
    assert payload["backend_status"] == "unavailable"
    assert payload["computation_mode"] == "backend_unavailable"
    assert payload["hero_equity"] is None
    assert payload["player_results"] == []
    assert payload["error_message"] == "backend package is not installed"
    json.dumps(payload, sort_keys=True)


def test_equity_backend_result_can_hold_raw_backend_metadata() -> None:
    backend = EquityBackendResult(
        backend_name="pokerkit",
        backend_status=EquityBackendStatus.OK,
        computation_mode=EquityComputationMode.HEADS_UP_RAW_EQUITY,
        hero_equity=0.64,
        hero_win_rate=0.61,
        hero_tie_rate=0.03,
        player_results=(
            EquityPlayerResult(
                player_id="hero",
                equity=0.64,
                win_rate=0.61,
                tie_rate=0.03,
                confidence=EquityConfidenceClass.MEDIUM,
            ),
        ),
        sample_count_used=2500,
        runtime_ms=12.5,
        backend_metadata={"mode": "heads_up_raw_snapshot"},
    )

    payload = backend.to_json_dict()
    assert payload["backend_status"] == "ok"
    assert payload["hero_equity"] == 0.64
    assert payload["player_results"][0]["player_id"] == "hero"
    assert payload["sample_count_used"] == 2500
    assert payload["runtime_ms"] == 12.5
    assert payload["backend_metadata"] == {"mode": "heads_up_raw_snapshot"}
    json.dumps(payload, sort_keys=True)


def test_equity_result_can_be_created_and_serialized() -> None:
    result = EquityResult(
        case_id="flop_equity_top_pair_heads_up",
        source_file="tests/fixtures/postflop_equity_input_v0103/synthetic/flop_equity_input_srp_heads_up.clear.json",
        hero_equity=0.64,
        hero_win_rate=0.61,
        hero_tie_rate=0.03,
        player_equities=(
            EquityPlayerResult(
                player_id="hero",
                position="BTN",
                role="hero",
                equity=0.64,
                win_rate=0.61,
                tie_rate=0.03,
                confidence=EquityConfidenceClass.MEDIUM,
            ),
            EquityPlayerResult(
                player_id="BB",
                position="BB",
                role="opponent",
                equity=0.36,
                win_rate=0.33,
                tie_rate=0.03,
                confidence=EquityConfidenceClass.MEDIUM,
            ),
        ),
        opponents_count=1,
        computation_mode=EquityComputationMode.HEADS_UP_RAW_EQUITY,
        backend_name="pokerkit",
        backend_status=EquityBackendStatus.OK,
        sample_count_used=2500,
        equity_confidence=EquityConfidenceClass.MEDIUM,
        input_features_used=("hero_cards", "board_cards", "opponents_count"),
        runtime_ms=12.5,
        backend_metadata={"adapter": "future_pokerkit_backend"},
        notes=("contract_only_no_engine",),
    )

    assert is_dataclass(result)
    payload = result.to_json_dict()
    assert payload["case_id"] == "flop_equity_top_pair_heads_up"
    assert payload["source_file"].endswith("flop_equity_input_srp_heads_up.clear.json")
    assert payload["hero_equity"] == 0.64
    assert payload["hero_win_rate"] == 0.61
    assert payload["hero_tie_rate"] == 0.03
    assert payload["player_equities"][0]["player_id"] == "hero"
    assert payload["opponents_count"] == 1
    assert payload["computation_mode"] == "heads_up_raw_equity"
    assert payload["backend_name"] == "pokerkit"
    assert payload["backend_status"] == "ok"
    assert payload["sample_count_used"] == 2500
    assert payload["equity_confidence"] == "medium"
    assert payload["input_features_used"] == ["hero_cards", "board_cards", "opponents_count"]
    assert payload["runtime_ms"] == 12.5
    assert payload["backend_metadata"] == {"adapter": "future_pokerkit_backend"}
    json.dumps(payload, sort_keys=True)


def test_equity_result_can_represent_backend_unavailable_without_crashing() -> None:
    result = EquityResult(
        case_id="backend_unavailable_case",
        source_file="backend_unavailable.clear.json",
        opponents_count=1,
        computation_mode=EquityComputationMode.BACKEND_UNAVAILABLE,
        backend_name="pokerkit",
        backend_status=EquityBackendStatus.UNAVAILABLE,
        equity_confidence=EquityConfidenceClass.UNKNOWN,
        notes=("backend_unavailable_structured_result",),
    )

    payload = result.to_json_dict()
    assert payload["hero_equity"] is None
    assert payload["computation_mode"] == "backend_unavailable"
    assert payload["backend_status"] == "unavailable"
    assert payload["equity_confidence"] == "unknown"
    assert payload["notes"] == ["backend_unavailable_structured_result"]
    json.dumps(payload, sort_keys=True)


def test_equity_contracts_define_module_exports() -> None:
    assert set(equity_contracts.__all__) == {
        "DEFAULT_EQUITY_BACKEND_NAME",
        "EQUITY_BACKEND_STATUSES",
        "EQUITY_COMPUTATION_MODES",
        "EQUITY_CONFIDENCE_CLASSES",
        "EQUITY_CONTRACT_VERSION",
        "EquityBackendResult",
        "EquityBackendStatus",
        "EquityComputationMode",
        "EquityConfidenceClass",
        "EquityPlayerResult",
        "EquityResult",
    }


def test_equity_contracts_do_not_import_backend_or_action_modules() -> None:
    source = inspect.getsource(equity_contracts).lower()

    forbidden_fragments = (
        "from pokerkit",
        "import pokerkit",
        "monte_carlo",
        "run_simulation",
        "build_range_state",
        "narrow_range",
        "resolve_decision",
        "runtime_plan",
        "button_targets",
        "click_result",
        "current_cycle",
        "clear_json_pending",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source


def test_importing_equity_contracts_does_not_require_backend_package() -> None:
    assert "pokerkit" not in sys.modules
    assert EquityResult(case_id="no_backend_import", source_file="x.clear.json").backend_name == "pokerkit"
