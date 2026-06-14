"""Architecture boundary tests for V0.12 postflop RangeState layer.

V0.12 scope is deliberately narrow:
FlopContext -> RangeImporter -> RangeState.

The range layer may select and carry baseline combo groups, but it must not
remove blockers, narrow ranges by flop action, recompute equity, build a
runtime plan, click UI buttons, validate Clear_JSON, or search temporary
PokerVision JSON sources.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RANGE_CONTRACTS_PATH = PROJECT_ROOT / "solver_postflop" / "range_contracts.py"
RANGE_IMPORTER_PATH = PROJECT_ROOT / "solver_postflop" / "range_importer.py"
RANGE_PACK_PATH = PROJECT_ROOT / "ranges" / "postflop_default_ranges.json"

RANGE_LAYER_PATHS = (RANGE_CONTRACTS_PATH, RANGE_IMPORTER_PATH)

FORBIDDEN_IMPORTED_MODULES = {
    "solver_postflop.blocker_filtering",
    "solver_postflop.combo_state",
    "solver_postflop.combo_contracts",
    "solver_postflop.equity_engine",
    "solver_postflop.equity_backend_pokerkit",
    "solver_postflop.equity_input",
    "solver_postflop.equity_contracts",
    "solver_postflop.flop_decision_engine",
    "solver_postflop.decision_engine",
    "solver_postflop.runtime_plan",
    "solver_postflop.click_runtime",
    "solver_postflop.action_button_snapshot",
    "solver_postflop.action_option_resolver",
    "solver_postflop.source_discovery",
    "solver_postflop.source_adapter",
    "solver_postflop.frame_normalizer",
    "solver_postflop.clear_json_input_loader",
}

FORBIDDEN_DEFINITION_FRAGMENTS = (
    "blocker_filter",
    "blocked_combo",
    "available_combo_state",
    "combo_availability",
    "range_narrow",
    "narrow_range",
    "action_narrow",
    "equity_recalculation",
    "decision_engine",
    "runtime_plan",
    "click_runtime",
    "clear_json_validation",
    "player_filter",
    "source_discovery",
)

FORBIDDEN_SOURCE_FALLBACK_MARKERS = (
    "Dark_JSON",
    "Pending_JSON",
    "Service_JSON",
    "Runtime_JSON",
    "Clear_JSON_Pending",
    "current_cycle",
    "ui_display_cycle",
    "outputs/ui_display_cycle",
    "outputs\\ui_display_cycle",
    "external/PokerVisionFinalVersionNoSolver_snapshot",
    "external\\PokerVisionFinalVersionNoSolver_snapshot",
)

REQUIRED_FALSE_RANGE_PACK_FLAGS = (
    "blocker_filtering_executed",
    "range_narrowing_executed",
    "equity_recalculation_executed",
    "decision_logic_executed",
    "runtime_plan_created",
    "physical_click_executed",
    "clear_json_validation_executed",
    "player_filtering_executed",
    "range_importer_executed",
    "range_state_created",
)


def _read_source(path: Path) -> str:
    assert path.exists(), f"Missing expected range-layer file: {path}"
    return path.read_text(encoding="utf-8")


def _parse_module(path: Path) -> ast.Module:
    return ast.parse(_read_source(path), filename=str(path))


def _imported_module_names(tree: ast.Module) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            modules.add(node.module or "")
    return modules


def _defined_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


def _called_attribute_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            names.add(func.id)
        elif isinstance(func, ast.Attribute):
            names.add(func.attr)
    return names


def _load_range_pack() -> dict:
    assert RANGE_PACK_PATH.exists(), "V0.12.3 postflop default range pack must exist before V0.12.6"
    payload = json.loads(RANGE_PACK_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_range_layer_does_not_import_future_logic_modules() -> None:
    for path in RANGE_LAYER_PATHS:
        imported_modules = _imported_module_names(_parse_module(path))
        forbidden = sorted(imported_modules & FORBIDDEN_IMPORTED_MODULES)
        assert forbidden == [], f"{path.name} imports future/out-of-scope modules: {forbidden}"


def test_range_layer_does_not_define_future_engines_or_side_effect_apis() -> None:
    for path in RANGE_LAYER_PATHS:
        tree = _parse_module(path)
        names = _defined_names(tree) | _called_attribute_names(tree)
        lowered_names = {name.lower() for name in names}
        matches = sorted(
            name
            for name in lowered_names
            if any(fragment in name for fragment in FORBIDDEN_DEFINITION_FRAGMENTS)
        )
        assert matches == [], f"{path.name} defines or calls out-of-scope future logic names: {matches}"


def test_range_layer_does_not_reference_temporary_pokervision_json_fallback_sources() -> None:
    for path in RANGE_LAYER_PATHS:
        source = _read_source(path)
        markers = [marker for marker in FORBIDDEN_SOURCE_FALLBACK_MARKERS if marker in source]
        assert markers == [], f"{path.name} references temporary source fallback markers: {markers}"


def test_postflop_default_range_pack_keeps_architecture_flags_false() -> None:
    payload = _load_range_pack()
    flags = payload.get("architecture_flags")
    assert isinstance(flags, dict)
    for flag_name in REQUIRED_FALSE_RANGE_PACK_FLAGS:
        assert flags.get(flag_name) is False, f"{flag_name} must remain false in V0.12 baseline range pack"


def test_postflop_default_range_pack_is_combo_level_but_not_filtered_or_narrowed() -> None:
    payload = _load_range_pack()
    assert payload["schema"] == "pokervision_solver_postflop_default_ranges_v1"
    assert payload["source_type"] == "postflop_default_ranges"
    assert payload["next_module"] == "range_importer_v0124"

    cases = payload.get("cases")
    assert isinstance(cases, dict)
    assert cases, "range pack must expose baseline cases"

    combo_count = 0
    for case_payload in cases.values():
        for player_key in ("hero_range_state",):
            combo_groups = case_payload[player_key]["combo_groups"]
            combo_count += sum(len(combos) for combos in combo_groups.values())
        for opponent_payload in case_payload.get("opponent_range_states", []):
            combo_groups = opponent_payload["combo_groups"]
            combo_count += sum(len(combos) for combos in combo_groups.values())

        notes = " ".join(case_payload.get("notes", []))
        assert "blocker" not in notes.lower()
        assert "narrow" not in notes.lower()

    assert combo_count > 0, "V0.12 pack must carry combo-level compact strings for future V0.13"


def test_range_contracts_and_importer_defer_to_future_blocker_filtering_without_running_it() -> None:
    from solver_postflop.range_contracts import DEFAULT_RANGE_NEXT_MODULE
    from solver_postflop.range_importer import DEFAULT_RANGE_IMPORTER_NEXT_MODULE

    assert DEFAULT_RANGE_NEXT_MODULE == "blocker_filtering_later"
    assert DEFAULT_RANGE_IMPORTER_NEXT_MODULE == "blocker_filtering_later"

    importer_imports = _imported_module_names(_parse_module(RANGE_IMPORTER_PATH))
    assert "solver_postflop.blocker_filtering" not in importer_imports
    assert "solver_postflop.combo_state" not in importer_imports


def test_range_layer_is_not_a_decision_runtime_or_click_layer() -> None:
    for path in RANGE_LAYER_PATHS:
        source = _read_source(path).lower()
        # These exact API markers would indicate an out-of-scope executable action layer.
        forbidden_api_markers = (
            "def build_runtime_plan",
            "def execute_click",
            "def click_button",
            "class runtimeplan",
            "class clickresult",
            "planned_action",
            "click_sequence",
        )
        found = [marker for marker in forbidden_api_markers if marker in source]
        assert found == [], f"{path.name} contains decision/runtime/click API markers: {found}"
