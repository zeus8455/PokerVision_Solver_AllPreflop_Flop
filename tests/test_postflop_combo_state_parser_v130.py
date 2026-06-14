"""Tests for V0.13.2 card/combo parser foundation."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from solver_postflop.combo_contracts import BlockedComboReason
from solver_postflop.combo_state import (
    ARCHITECTURE_FLAGS,
    COMBO_STATE_VERSION,
    CardParseStatus,
    ComboParseStatus,
    combo_contains_any_card,
    detect_combo_blockers,
    normalize_card,
    normalize_cards,
    parse_compact_combo,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMBO_STATE_SOURCE = PROJECT_ROOT / "solver_postflop" / "combo_state.py"


def test_combo_state_version_is_v0132() -> None:
    assert COMBO_STATE_VERSION == "v0.13.2"


def test_parse_compact_combo_returns_two_cards() -> None:
    parsed = parse_compact_combo("AsKs")

    assert parsed.status is ComboParseStatus.PARSED
    assert parsed.is_parseable is True
    assert parsed.combo_cards == ("As", "Ks")
    assert parsed.normalized_combo == "AsKs"
    assert parsed.to_json_dict()["combo_cards"] == ["As", "Ks"]


def test_parse_compact_combo_handles_pairs_and_ten_alias() -> None:
    assert parse_compact_combo("QcQd").combo_cards == ("Qc", "Qd")
    assert parse_compact_combo("10s9s").combo_cards == ("Ts", "9s")
    assert parse_compact_combo("Th 9h").normalized_combo == "Th9h"


def test_normalize_project_card_formats() -> None:
    assert normalize_card("A_spades").normalized_card == "As"
    assert normalize_card("10_spades").normalized_card == "Ts"
    assert normalize_card("K_hearts").normalized_card == "Kh"
    assert normalize_card("queen-diamonds").normalized_card == "Qd"
    assert normalize_card("J clubs").normalized_card == "Jc"


def test_normalize_cards_skips_unknown_values_without_raising() -> None:
    normalized = normalize_cards(["A_spades", None, "", "bad-card", "10_hearts"])

    assert normalized == ("As", "Th")
    assert normalize_card(None).status is CardParseStatus.EMPTY
    assert normalize_card("bad-card").status is CardParseStatus.UNRECOGNIZED


def test_malformed_combo_returns_structured_result_without_exception() -> None:
    parsed = parse_compact_combo("not_a_combo")

    assert parsed.status is ComboParseStatus.MALFORMED
    assert parsed.is_parseable is False
    assert parsed.to_json_dict()["status"] == "malformed"


def test_combo_contains_hero_blocker_card() -> None:
    assert combo_contains_any_card("AsKs", ["A_spades", "Q_hearts"]) is True
    assert combo_contains_any_card("AsKs", ["Q_hearts", "J_diamonds"]) is False


def test_combo_contains_board_blocker_card() -> None:
    assert combo_contains_any_card("QcQd", ["Q_diamonds", "2_clubs"]) is True
    assert combo_contains_any_card("Th9h", ["A_spades", "K_spades"]) is False


def test_detect_combo_blockers_returns_hero_reason() -> None:
    result = detect_combo_blockers("AsKs", hero_cards=["A_spades", "7_clubs"], board_cards=["Q_hearts"])

    assert result.blocked_reason is BlockedComboReason.BLOCKED_BY_HERO_CARD
    assert result.hero_blocker_cards == ("As",)
    assert result.board_blocker_cards == ()
    assert result.is_blocked is True


def test_detect_combo_blockers_returns_board_reason() -> None:
    result = detect_combo_blockers("QcQd", hero_cards=["A_spades"], board_cards=["Q_diamonds", "2_clubs"])

    assert result.blocked_reason is BlockedComboReason.BLOCKED_BY_BOARD_CARD
    assert result.hero_blocker_cards == ()
    assert result.board_blocker_cards == ("Qd",)


def test_detect_combo_blockers_returns_hero_and_board_reason() -> None:
    result = detect_combo_blockers("AsQd", hero_cards=["A_spades"], board_cards=["Q_diamonds"])

    assert result.blocked_reason is BlockedComboReason.BLOCKED_BY_HERO_AND_BOARD
    assert result.hero_blocker_cards == ("As",)
    assert result.board_blocker_cards == ("Qd",)


def test_detect_combo_blockers_returns_not_blocked_reason() -> None:
    result = detect_combo_blockers("Th9h", hero_cards=["A_spades"], board_cards=["Q_diamonds"])

    assert result.blocked_reason is BlockedComboReason.NOT_BLOCKED
    assert result.is_blocked is False
    assert result.parse_status is ComboParseStatus.PARSED


def test_detect_combo_blockers_malformed_combo_does_not_raise() -> None:
    result = detect_combo_blockers("broken", hero_cards=["A_spades"], board_cards=["Q_diamonds"])

    assert result.parse_status is ComboParseStatus.MALFORMED
    assert result.blocked_reason is BlockedComboReason.NOT_BLOCKED
    assert "combo_unparseable_no_blocker_decision" in result.notes


def test_parser_results_are_json_serializable() -> None:
    payload = {
        "card": normalize_card("A_spades").to_json_dict(),
        "combo": parse_compact_combo("AsKs").to_json_dict(),
        "match": detect_combo_blockers("AsKs", hero_cards=["A_spades"]).to_json_dict(),
    }

    dumped = json.dumps(payload, sort_keys=True)
    assert "blocked_by_hero_card" in dumped
    assert "AsKs" in dumped


def test_input_collections_are_not_mutated() -> None:
    hero_cards = ["A_spades", "K_hearts"]
    board_cards = ["Q_diamonds", "2_clubs", "7_hearts"]
    hero_before = copy.deepcopy(hero_cards)
    board_before = copy.deepcopy(board_cards)

    _ = detect_combo_blockers("AsQd", hero_cards=hero_cards, board_cards=board_cards)

    assert hero_cards == hero_before
    assert board_cards == board_before


def test_architecture_flags_remain_parser_only() -> None:
    assert ARCHITECTURE_FLAGS == {
        "available_combo_state_created": False,
        "range_state_mutated": False,
        "clear_json_validation_executed": False,
        "player_filtering_executed": False,
        "range_narrowing_executed": False,
        "equity_recalculation_executed": False,
        "decision_logic_executed": False,
        "runtime_plan_created": False,
        "physical_click_executed": False,
    }


def test_combo_state_source_has_no_engine_or_runtime_dependencies() -> None:
    source = COMBO_STATE_SOURCE.read_text(encoding="utf-8")

    forbidden_fragments = (
        "from solver_postflop.range_contracts import RangeState",
        "AvailableComboState(",
        "PlayerComboState(",
        "EquityResult",
        "Decision",
        "RuntimePlan",
        "click(",
        "mouse",
        "Dark_JSON",
        "Pending_JSON",
        "Service_JSON",
        "current_cycle",
    )
    for fragment in forbidden_fragments:
        assert fragment not in source


def test_public_api_is_small_and_parser_focused() -> None:
    import solver_postflop.combo_state as combo_state

    assert set(combo_state.__all__) == {
        "ARCHITECTURE_FLAGS",
        "COMBO_STATE_VERSION",
        "CardParseResult",
        "CardParseStatus",
        "ComboBlockerMatch",
        "ComboParseResult",
        "ComboParseStatus",
        "combo_contains_any_card",
        "detect_combo_blockers",
        "normalize_card",
        "normalize_cards",
        "parse_compact_combo",
    }
