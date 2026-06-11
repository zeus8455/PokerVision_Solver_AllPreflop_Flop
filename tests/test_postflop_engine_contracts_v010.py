from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def test_solver_postflop_package_imports_engine_contracts() -> None:
    import solver_postflop

    assert hasattr(solver_postflop, "ClearJsonInput")
    assert hasattr(solver_postflop, "SolverInput")
    assert hasattr(solver_postflop, "SolverTrace")


def test_clear_json_input_contract_can_be_created() -> None:
    from solver_postflop import ClearJsonInput

    raw_data = {"table_id": "table_01", "hand_id": "hand_001"}
    loaded = ClearJsonInput(
        source_file="tests/fixtures/postflop_clear_json/example.json",
        raw_data=raw_data,
        case_id="case_001",
        hand_id="hand_001",
        table_id="table_01",
    )

    assert loaded.source_file == "tests/fixtures/postflop_clear_json/example.json"
    assert loaded.raw_data is raw_data
    assert loaded.case_id == "case_001"
    assert loaded.hand_id == "hand_001"
    assert loaded.table_id == "table_01"
    assert isinstance(loaded.loaded_at, datetime)
    assert loaded.loaded_at.tzinfo is not None


def test_solver_input_contract_can_be_created() -> None:
    from solver_postflop import SolverInput

    raw_clear_json = {"table_id": "table_01"}
    solver_input = SolverInput(
        table_id="table_01",
        hand_id="hand_001",
        hero_cards=("As", "Kd"),
        board_cards=("Ah", "7d", "2c"),
        players=({"seat": 1, "hero": True}, {"seat": 2, "hero": False}),
        pot=12.5,
        to_call=0.0,
        stacks={"hero": 87.5},
        committed_amounts={"hero": 2.5},
        positions={"hero": "BTN"},
        button="hero",
        blinds={"sb": 0.5, "bb": 1.0},
        allowed_actions=("check", "bet"),
        action_context={"facing_bet": False},
        raw_clear_json_ref=raw_clear_json,
    )

    assert solver_input.table_id == "table_01"
    assert solver_input.hand_id == "hand_001"
    assert solver_input.hero_cards == ("As", "Kd")
    assert solver_input.board_cards == ("Ah", "7d", "2c")
    assert solver_input.players[0]["hero"] is True
    assert solver_input.pot == 12.5
    assert solver_input.to_call == 0.0
    assert solver_input.stacks["hero"] == 87.5
    assert solver_input.committed_amounts["hero"] == 2.5
    assert solver_input.positions["hero"] == "BTN"
    assert solver_input.button == "hero"
    assert solver_input.blinds["bb"] == 1.0
    assert solver_input.allowed_actions == ("check", "bet")
    assert solver_input.action_context["facing_bet"] is False
    assert solver_input.raw_clear_json_ref is raw_clear_json


def test_solver_trace_contract_defaults_to_clear_json_input_kind() -> None:
    from solver_postflop import SolverTrace

    trace = SolverTrace(input_file=Path("case.json"))

    assert trace.input_file == Path("case.json")
    assert trace.input_kind == "clear_json"
    assert trace.mapping_version == "v0.1.1"
    assert trace.fields_used == ()
    assert trace.fields_not_provided == ()
    assert trace.module_chain_next_step is None
    assert trace.notes == ()


def test_solver_trace_contract_accepts_mapping_observability_fields() -> None:
    from solver_postflop import SolverTrace

    trace = SolverTrace(
        input_file="case.json",
        mapping_version="v0.1.1",
        fields_used=("hero_cards", "board_cards", "players"),
        fields_not_provided=("preflop_context",),
        module_chain_next_step="clear_json_input_loader",
        notes=("baseline contract only",),
    )

    assert trace.fields_used == ("hero_cards", "board_cards", "players")
    assert trace.fields_not_provided == ("preflop_context",)
    assert trace.module_chain_next_step == "clear_json_input_loader"
    assert trace.notes == ("baseline contract only",)


def test_engine_contracts_are_isolated_from_preflop_runtime_and_source_discovery() -> None:
    package_root = Path("solver_postflop")
    source_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            package_root / "__init__.py",
            package_root / "engine_contracts.py",
        ]
    )

    forbidden_import_markers = (
        "solver_preflop",
        "external.",
        "display_analysis_cycle",
        "Action_Button",
        "runtime",
        "source_discovery",
        "Dark_JSON",
        "Pending_JSON",
        "Service JSON",
        "Runtime JSON",
    )

    for marker in forbidden_import_markers:
        assert marker not in source_text
