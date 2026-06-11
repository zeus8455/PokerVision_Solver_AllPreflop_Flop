from __future__ import annotations

from pathlib import Path


def test_postflop_package_exports_engine_contracts() -> None:
    import solver_postflop

    assert hasattr(solver_postflop, "ClearJsonInput")
    assert hasattr(solver_postflop, "SolverInput")
    assert hasattr(solver_postflop, "SolverTrace")


def test_clear_json_input_contract_can_be_created() -> None:
    from solver_postflop import ClearJsonInput

    clear_input = ClearJsonInput(
        source_file="case.clear.json",
        raw_data={"table_id": "table_01"},
        loaded_at="2026-06-11T00:00:00+00:00",
        case_id="case_001",
        hand_id="hand_001",
        table_id="table_01",
    )

    assert clear_input.source_file == "case.clear.json"
    assert clear_input.raw_data == {"table_id": "table_01"}
    assert clear_input.case_id == "case_001"
    assert clear_input.hand_id == "hand_001"
    assert clear_input.table_id == "table_01"


def test_solver_input_contract_can_be_created_with_defaults() -> None:
    from solver_postflop import SolverInput

    solver_input = SolverInput(table_id="table_01", hand_id="hand_001")

    assert solver_input.table_id == "table_01"
    assert solver_input.hand_id == "hand_001"
    assert solver_input.hero_cards == ()
    assert solver_input.board_cards == ()
    assert solver_input.players == ()
    assert solver_input.allowed_actions == ()
    assert solver_input.raw_clear_json_ref == {}


def test_solver_trace_contract_defaults_to_clear_json_input_kind() -> None:
    from solver_postflop import SolverTrace

    trace = SolverTrace(
        input_file="case.clear.json",
        mapping_version="v0.1.1",
        fields_used=("hero_cards", "board_cards"),
        fields_not_provided=("preflop_context",),
        module_chain_next_step="clear_json_input_loader",
        notes=("baseline contract",),
    )

    assert trace.input_kind == "clear_json"
    assert trace.fields_used == ("hero_cards", "board_cards")
    assert trace.fields_not_provided == ("preflop_context",)
    assert trace.module_chain_next_step == "clear_json_input_loader"


def test_contract_classes_have_stable_public_field_names() -> None:
    from solver_postflop import ClearJsonInput, SolverInput, SolverTrace

    assert tuple(ClearJsonInput.__dataclass_fields__) == (
        "source_file",
        "raw_data",
        "loaded_at",
        "case_id",
        "hand_id",
        "table_id",
    )

    assert tuple(SolverInput.__dataclass_fields__) == (
        "table_id",
        "hand_id",
        "hero_cards",
        "board_cards",
        "players",
        "pot",
        "to_call",
        "stacks",
        "committed_amounts",
        "positions",
        "button",
        "blinds",
        "allowed_actions",
        "action_context",
        "raw_clear_json_ref",
    )

    assert tuple(SolverTrace.__dataclass_fields__) == (
        "input_file",
        "mapping_version",
        "input_kind",
        "fields_used",
        "fields_not_provided",
        "module_chain_next_step",
        "notes",
    )


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
