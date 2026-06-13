from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EQUITY_INPUT_FILES = (
    PROJECT_ROOT / "solver_postflop" / "equity_input.py",
    PROJECT_ROOT / "solver_postflop" / "equity_input_contracts.py",
)
DOC_PATH = PROJECT_ROOT / "docs" / "POSTFLOP_EQUITY_INPUT.md"


BACKEND_OR_LIVE_IMPORT_ROOTS = {
    "pokerkit",
    "treys",
    "deuces",
    "random",
    "numpy",
    "scipy",
    "solver_preflop",
    "display_analysis_cycle",
    "source_discovery",
    "action_button",
    "Action_Button",
    "pyautogui",
}

FORBIDDEN_CALL_NAMES = {
    "calculate_equity",
    "compute_equity",
    "run_equity",
    "simulate",
    "run_simulation",
    "monte_carlo",
    "sample_turn_river",
    "evaluate_hand",
    "rank_hand",
    "create_state",
    "deal_hole",
    "deal_board",
    "build_ranges",
    "narrow_ranges",
    "blocker_filter",
    "filter_blockers",
    "validate_cards",
    "validate_clear_json",
    "check_duplicate_cards",
    "filter_players",
    "create_players",
    "build_decision",
    "make_decision",
    "build_runtime_plan",
    "click_button",
    "perform_click",
}

FORBIDDEN_SOURCE_TOKENS = {
    "import pokerkit",
    "from pokerkit",
    "monte_carlo",
    "run_simulation",
    "calculate_equity",
    "compute_equity",
    "evaluate_hand",
    "build_ranges",
    "narrow_ranges",
    "blocker_filter",
    "validate_clear_json",
    "check_duplicate_cards",
    "filter_players",
    "build_runtime_plan",
    "perform_click",
    "pyautogui",
    "clear_json_pending",
    "dark_json",
    "current_cycle",
    "source_discovery",
}

FORBIDDEN_DECLARATION_FRAGMENTS = {
    "pokerkit",
    "monte_carlo",
    "simulation",
    "equity_engine_backend",
    "range_builder",
    "range_narrow",
    "blocker_filter",
    "card_validator",
    "player_filter",
    "decision_engine",
    "runtime_plan",
    "click",
    "source_discovery",
}


def _parse(path: Path) -> ast.Module:
    assert path.exists(), f"Missing source file: {path}"
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _source(path: Path) -> str:
    assert path.exists(), f"Missing source file: {path}"
    return path.read_text(encoding="utf-8").lower()


def _import_roots(tree: ast.Module) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


def _call_name(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        parts = [func.attr]
        value = func.value
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        if isinstance(value, ast.Name):
            parts.append(value.id)
        return ".".join(reversed(parts))
    return None


def _declared_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
    return names


def test_equity_input_layer_imports_no_backend_or_live_modules() -> None:
    for path in EQUITY_INPUT_FILES:
        imported_roots = _import_roots(_parse(path))
        forbidden = imported_roots & BACKEND_OR_LIVE_IMPORT_ROOTS
        assert not forbidden, f"{path.name} imports forbidden modules: {sorted(forbidden)}"


def test_equity_input_layer_declares_no_extra_logic_symbols() -> None:
    for path in EQUITY_INPUT_FILES:
        declared = {name.lower() for name in _declared_names(_parse(path))}
        offenders = sorted(
            name
            for name in declared
            for fragment in FORBIDDEN_DECLARATION_FRAGMENTS
            if fragment in name
        )
        assert not offenders, f"{path.name} declares forbidden symbols: {offenders}"


def test_equity_input_layer_calls_no_equity_range_validation_decision_or_click_logic() -> None:
    for path in EQUITY_INPUT_FILES:
        tree = _parse(path)
        calls = {
            name.lower()
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            for name in [_call_name(node)]
            if name
        }
        offenders = sorted(
            call
            for call in calls
            if call in FORBIDDEN_CALL_NAMES or call.rsplit(".", 1)[-1] in FORBIDDEN_CALL_NAMES
        )
        assert not offenders, f"{path.name} calls forbidden logic: {offenders}"


def test_equity_input_layer_has_no_live_json_source_fallback_tokens() -> None:
    for path in EQUITY_INPUT_FILES:
        source = _source(path)
        offenders = sorted(token for token in FORBIDDEN_SOURCE_TOKENS if token in source)
        assert not offenders, f"{path.name} contains forbidden source tokens: {offenders}"


def test_equity_input_layer_does_not_read_files_or_discover_sources() -> None:
    forbidden_file_calls = {"open", "glob", "rglob", "read_text", "read_bytes", "load", "loads"}
    forbidden_imports = {"json", "pathlib", "glob", "os"}

    for path in EQUITY_INPUT_FILES:
        tree = _parse(path)
        imported_roots = _import_roots(tree)
        assert not (imported_roots & forbidden_imports), (
            f"{path.name} imports file/source-discovery modules: "
            f"{sorted(imported_roots & forbidden_imports)}"
        )

        calls = {
            name.lower().rsplit(".", 1)[-1]
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            for name in [_call_name(node)]
            if name
        }
        offenders = sorted(calls & forbidden_file_calls)
        assert not offenders, f"{path.name} reads/discovers files: {offenders}"


def test_equity_input_documentation_freezes_v010_boundary() -> None:
    assert DOC_PATH.exists(), "Missing docs/POSTFLOP_EQUITY_INPUT.md"
    text = DOC_PATH.read_text(encoding="utf-8")

    required_phrases = (
        "EquityScenarioInput",
        "does not calculate equity",
        "does not import PokerKit",
        "unknown_context_mode is not an error",
        "next_module = equity_engine",
        "V0.11.0",
    )
    for phrase in required_phrases:
        assert phrase in text
