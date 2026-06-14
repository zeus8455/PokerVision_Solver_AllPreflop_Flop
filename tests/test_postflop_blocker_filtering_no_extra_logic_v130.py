from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from solver_postflop.blocker_filtering import ARCHITECTURE_FLAGS, build_available_combo_state
from solver_postflop.combo_contracts import ComboAvailabilityStatus
from solver_postflop.range_contracts import (
    PlayerRangeState,
    RangeBucket,
    RangeConfidenceClass,
    RangeImportStatus,
    RangeSourceInfo,
    RangeSourceType,
    RangeState,
    RangeWeightingMode,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BLOCKER_MODULES = (
    PROJECT_ROOT / "solver_postflop" / "blocker_filtering.py",
    PROJECT_ROOT / "solver_postflop" / "combo_state.py",
    PROJECT_ROOT / "solver_postflop" / "combo_contracts.py",
)
FORBIDDEN_IMPORT_PREFIXES = (
    "solver_postflop.equity",
    "solver_postflop.equity_engine",
    "solver_postflop.equity_backend_pokerkit",
    "solver_postflop.decision",
    "solver_postflop.runtime",
    "solver_postflop.source_discovery",
    "solver_postflop.source_adapter",
    "solver_postflop.frame_normalizer",
    "solver_postflop.clear_json",
    "solver_postflop.input_loader",
    "action_button",
    "runtime",
    "pyautogui",
)
FORBIDDEN_PUBLIC_NAME_FRAGMENTS = (
    "validate_clear_json",
    "repair_clear_json",
    "card_collision",
    "hero_board_collision",
    "filter_player",
    "player_filter",
    "narrow_range",
    "range_narrowing",
    "recalculate_equity",
    "equity_recalculation",
    "make_decision",
    "decision_engine",
    "runtime_plan",
    "click",
)
FORBIDDEN_RESULT_KEYS = {
    "decision",
    "solver_decision",
    "runtime_plan",
    "click_sequence",
    "click_result",
    "clear_json_validation_result",
    "player_filtering_result",
    "range_narrowing_result",
    "equity_recalculation_result",
}


def _sample_range_state() -> RangeState:
    hero_range = PlayerRangeState(
        player_id="hero",
        position="BTN",
        role="preflop_aggressor",
        range_name="hero_v0135_baseline",
        range_source=RangeSourceType.POSTFLOP_DEFAULT_RANGES,
        combo_groups={
            "strong_broadways": ("AsKs", "QhJd"),
            "pocket_pairs": ("QcQd",),
        },
        range_buckets=(RangeBucket.STRONG_BROADWAYS, RangeBucket.POCKET_PAIRS),
        weighting_mode=RangeWeightingMode.FLAT_BASELINE,
        confidence=RangeConfidenceClass.MEDIUM,
    )
    villain_range = PlayerRangeState(
        player_id="villain_1",
        position="BB",
        role="bb_defender",
        range_name="villain_v0135_baseline",
        range_source=RangeSourceType.POSTFLOP_DEFAULT_RANGES,
        combo_groups={
            "ace_x_suited": ("As5s", "Ah5h", "Ac5c"),
            "suited_connectors": ("Ts9s", "Th9h"),
        },
        range_buckets=(RangeBucket.ACE_X_SUITED, RangeBucket.SUITED_CONNECTORS),
        weighting_mode=RangeWeightingMode.FLAT_BASELINE,
        confidence=RangeConfidenceClass.MEDIUM,
    )
    return RangeState(
        case_id="v0135_architecture_case",
        source_file="tests/fixtures/v0135/no_extra_logic.range.json",
        spot_family="srp_heads_up",
        pot_type="srp",
        hero_position="BTN",
        opponent_positions=("BB",),
        hero_range_state=hero_range,
        opponent_range_states=(villain_range,),
        range_source_info=RangeSourceInfo(
            source_type=RangeSourceType.POSTFLOP_DEFAULT_RANGES,
            source_name="postflop_default_ranges_v0123",
            source_file="ranges/postflop_default_ranges.json",
            source_version="v0.12.3",
        ),
        range_confidence=RangeConfidenceClass.MEDIUM,
        range_import_status=RangeImportStatus.IMPORTED,
        range_buckets=(
            RangeBucket.STRONG_BROADWAYS,
            RangeBucket.POCKET_PAIRS,
            RangeBucket.ACE_X_SUITED,
            RangeBucket.SUITED_CONNECTORS,
        ),
    )


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def _defined_public_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not node.name.startswith("_"):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    names.add(target.id)
    return names


def _walk_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        keys = {str(key) for key in value.keys()}
        for item in value.values():
            keys.update(_walk_keys(item))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for item in value:
            keys.update(_walk_keys(item))
        return keys
    return set()


def test_blocker_filtering_architecture_flags_block_forbidden_layers() -> None:
    assert ARCHITECTURE_FLAGS["available_combo_state_created"] is True
    assert ARCHITECTURE_FLAGS["range_state_mutated"] is False
    assert ARCHITECTURE_FLAGS["clear_json_validation_executed"] is False
    assert ARCHITECTURE_FLAGS["card_collision_check_executed"] is False
    assert ARCHITECTURE_FLAGS["player_filtering_executed"] is False
    assert ARCHITECTURE_FLAGS["range_rebuild_executed"] is False
    assert ARCHITECTURE_FLAGS["range_creation_executed"] is False
    assert ARCHITECTURE_FLAGS["range_narrowing_executed"] is False
    assert ARCHITECTURE_FLAGS["equity_recalculation_executed"] is False
    assert ARCHITECTURE_FLAGS["decision_logic_executed"] is False
    assert ARCHITECTURE_FLAGS["runtime_plan_created"] is False
    assert ARCHITECTURE_FLAGS["physical_click_executed"] is False


def test_blocker_filtering_modules_do_not_import_decision_runtime_click_or_source_fallback_layers() -> None:
    for path in BLOCKER_MODULES:
        imports = _imports_from(path)
        for module_name in imports:
            assert not any(
                module_name == forbidden or module_name.startswith(f"{forbidden}.")
                for forbidden in FORBIDDEN_IMPORT_PREFIXES
            ), f"{path} imports forbidden dependency {module_name}"


def test_blocker_filtering_public_api_does_not_expose_forbidden_pipeline_actions() -> None:
    for path in BLOCKER_MODULES:
        public_names = _defined_public_names(path)
        lowered_names = {name.lower() for name in public_names}
        for name in lowered_names:
            assert not any(fragment in name for fragment in FORBIDDEN_PUBLIC_NAME_FRAGMENTS), (
                f"{path} exposes forbidden public name {name}"
            )


def test_available_combo_state_result_has_no_decision_runtime_click_or_validation_payloads() -> None:
    result = build_available_combo_state(
        _sample_range_state(),
        hero_cards=("As", "Qh"),
        board_cards=("Ah", "7d", "2c"),
    )
    payload = result.to_json_dict()
    keys = _walk_keys(payload)

    assert result.availability_status is ComboAvailabilityStatus.PARTIALLY_BLOCKED
    assert result.next_module == "flop_action_model_later"
    assert FORBIDDEN_RESULT_KEYS.isdisjoint(keys)
    json.dumps(payload, sort_keys=True)


def test_blocker_filtering_keeps_range_state_read_only_without_rebuilding_or_narrowing_ranges() -> None:
    state = _sample_range_state()
    before = state.to_json_dict()

    result = build_available_combo_state(
        state,
        hero_cards=("As", "Qh"),
        board_cards=("Ah", "7d", "2c"),
    )

    assert state.to_json_dict() == before
    assert result.range_source_info["source_type"] == "postflop_default_ranges"
    assert "range_state_read_only" in result.notes
    assert "no_range_narrowing" in result.notes
    assert "no_equity_recalculation" in result.notes
    assert "no_decision_runtime_click" in result.notes
