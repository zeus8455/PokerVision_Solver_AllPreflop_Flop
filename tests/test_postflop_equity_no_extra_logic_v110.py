"""Architecture gate for V0.11.0 raw equity layer.

The V0.11 equity layer is allowed to compute raw equity snapshots through the
PokerKit backend. It must not become a range engine, decision engine, runtime
planner, source-discovery layer, or click layer.
"""

from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EQUITY_IMPLEMENTATION_FILES = (
    PROJECT_ROOT / "solver_postflop" / "equity_contracts.py",
    PROJECT_ROOT / "solver_postflop" / "equity_backend_pokerkit.py",
    PROJECT_ROOT / "solver_postflop" / "equity_engine.py",
)


def _source(path: Path) -> str:
    assert path.exists(), f"missing equity layer source file: {path}"
    return path.read_text(encoding="utf-8").lower()


def _all_sources() -> dict[Path, str]:
    return {path: _source(path) for path in EQUITY_IMPLEMENTATION_FILES}


def _assert_absent(patterns: tuple[str, ...], *, reason: str) -> None:
    sources = _all_sources()
    for path, source in sources.items():
        for pattern in patterns:
            assert pattern not in source, f"{reason}: {pattern!r} found in {path}"


def _assert_regex_absent(patterns: tuple[str, ...], *, reason: str) -> None:
    sources = _all_sources()
    for path, source in sources.items():
        for pattern in patterns:
            assert re.search(pattern, source) is None, f"{reason}: /{pattern}/ found in {path}"


def test_v110_equity_layer_files_exist() -> None:
    for path in EQUITY_IMPLEMENTATION_FILES:
        assert path.exists(), path


def test_equity_engine_does_not_import_pokerkit_directly() -> None:
    engine_source = _source(PROJECT_ROOT / "solver_postflop" / "equity_engine.py")

    forbidden_direct_imports = (
        "import pokerkit",
        "from pokerkit import",
    )

    for forbidden in forbidden_direct_imports:
        assert forbidden not in engine_source


def test_equity_layer_has_no_range_engine_or_blocker_logic() -> None:
    _assert_absent(
        (
            "range_state",
            "range_importer",
            "range_contracts",
            "build_range_state",
            "build_player_range",
            "narrow_range",
            "action_history_range",
            "blocker_filter",
            "filter_blockers",
            "combo_removal",
            "range_weight",
        ),
        reason="V0.11 raw equity layer must not build or narrow ranges",
    )


def test_equity_layer_has_no_decision_runtime_or_click_logic() -> None:
    _assert_absent(
        (
            "decision_engine",
            "postflop_decision",
            "make_decision",
            "runtime_plan",
            "action_runtime",
            "action_button",
            "pyautogui",
            "mouse",
            "physical_click",
            "real_click",
            "button_sequence",
        ),
        reason="V0.11 raw equity layer must not create decisions, runtime plans, or clicks",
    )

    _assert_regex_absent(
        (
            r"\bclick\s*\(",
            r"\bmove_to\s*\(",
            r"\bpress\s*\(",
        ),
        reason="V0.11 raw equity layer must not call UI automation primitives",
    )


def test_equity_layer_has_no_clear_json_validation_or_player_filtering() -> None:
    _assert_absent(
        (
            "validate_clear_json",
            "clear_json_validator",
            "duplicate_card",
            "hero_board_collision",
            "dirty_source",
            "filter_players",
            "player_filter",
            "create_hero",
            "invent_hero",
            "create_opponent",
            "invent_opponent",
        ),
        reason="V0.11 raw equity layer must not validate Clear_JSON or refilter players",
    )


def test_equity_layer_has_no_live_source_discovery_or_temporary_json_fallback() -> None:
    _assert_absent(
        (
            "clear_json_pending",
            "dark_json",
            "pending_json",
            "current_cycle",
            "ui_display_cycle",
            "source_discovery",
            "runtime_json",
            "service_json",
            "final_clear_json",
        ),
        reason="V0.11 raw equity layer must consume EquityScenarioInput, not discover live JSON sources",
    )

    _assert_regex_absent(
        (
            r"\bglob\s*\(",
            r"\brglob\s*\(",
            r"\bos\.walk\s*\(",
        ),
        reason="V0.11 raw equity layer must not scan filesystem sources",
    )
