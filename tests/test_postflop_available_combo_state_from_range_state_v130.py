from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from solver_postflop.blocker_filtering import build_available_combo_state
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

EXPECTED_DIR = Path("tests/fixtures/postflop_available_combo_state_v0134/expected")


CASE_INPUTS: dict[str, dict[str, Any]] = {
    "flop_blockers_top_pair_blocks_ax": {
        "spot_family": "srp_heads_up",
        "pot_type": "srp",
        "hero_position": "BTN",
        "opponent_positions": ("BB",),
        "hero_cards": ("As", "Qh"),
        "board_cards": ("Ah", "7d", "2c"),
        "players": (
            {
                "player_id": "hero",
                "position": "BTN",
                "role": "preflop_aggressor",
                "range_name": "top_pair_hero_baseline",
                "combo_groups": {
                    "top_pair_plus": ("AsKs", "QhJd", "KcKd"),
                },
            },
            {
                "player_id": "villain_1",
                "position": "BB",
                "role": "bb_defender",
                "range_name": "top_pair_villain_ax_baseline",
                "combo_groups": {
                    "ace_x_suited": ("As5s", "Ah5h", "Ac5c", "Ad5d"),
                    "strong_broadways": ("KhQh", "KcQc"),
                },
            },
        ),
    },
    "flop_blockers_flush_draw_blocks_suited_combos": {
        "spot_family": "srp_heads_up",
        "pot_type": "srp",
        "hero_position": "BTN",
        "opponent_positions": ("BB",),
        "hero_cards": ("Ks", "9s"),
        "board_cards": ("As", "7s", "2d"),
        "players": (
            {
                "player_id": "hero",
                "position": "BTN",
                "role": "preflop_aggressor",
                "range_name": "flush_draw_hero_baseline",
                "combo_groups": {
                    "suited_broadways": ("KsQs", "KhQh"),
                    "suited_connectors": ("9s8s", "9h8h"),
                },
            },
            {
                "player_id": "villain_1",
                "position": "BB",
                "role": "bb_defender",
                "range_name": "flush_draw_villain_baseline",
                "combo_groups": {
                    "suited_broadways": ("QsJs", "QhJh", "AsKs", "AdKd"),
                    "suited_connectors": ("Ts9s", "Th9h", "8s7s", "8h7h"),
                },
            },
        ),
    },
    "flop_blockers_paired_board_blocks_sets": {
        "spot_family": "srp_heads_up",
        "pot_type": "srp",
        "hero_position": "CO",
        "opponent_positions": ("BB",),
        "hero_cards": ("Qd", "Jh"),
        "board_cards": ("7c", "7d", "2s"),
        "players": (
            {
                "player_id": "hero",
                "position": "CO",
                "role": "preflop_aggressor",
                "range_name": "paired_board_hero_baseline",
                "combo_groups": {
                    "sets": ("7s7h", "7c7d", "2c2d"),
                    "overpair": ("AsAh", "QdQc"),
                },
            },
            {
                "player_id": "villain_1",
                "position": "BB",
                "role": "bb_defender",
                "range_name": "paired_board_villain_baseline",
                "combo_groups": {
                    "sets": ("7s7h", "7c7d", "2c2d", "JcJd"),
                    "two_pair_plus": ("7h2h", "Ah7h"),
                },
            },
        ),
    },
    "flop_blockers_monotone_board_blocks_flush_combos": {
        "spot_family": "threebet_pot_heads_up",
        "pot_type": "3bet_pot",
        "hero_position": "BTN",
        "opponent_positions": ("SB",),
        "hero_cards": ("Kd", "Qd"),
        "board_cards": ("Ad", "Td", "4d"),
        "players": (
            {
                "player_id": "hero",
                "position": "BTN",
                "role": "three_bet_caller_ip",
                "range_name": "monotone_hero_baseline",
                "combo_groups": {
                    "suited_broadways": ("AdKd", "AhKh", "KdQd", "KsQs"),
                    "suited_connectors": ("Td9d", "Th9h"),
                },
            },
            {
                "player_id": "villain_1",
                "position": "SB",
                "role": "three_bettor_oop",
                "range_name": "monotone_villain_baseline",
                "combo_groups": {
                    "suited_broadways": ("AdQd", "AhQh", "KdJd", "KhJh"),
                    "suited_connectors": ("Td9d", "9d8d", "9h8h"),
                },
            },
        ),
    },
    "flop_blockers_broadway_board_blocks_broadway_combos": {
        "spot_family": "srp_heads_up",
        "pot_type": "srp",
        "hero_position": "BTN",
        "opponent_positions": ("BB",),
        "hero_cards": ("Ac", "Js"),
        "board_cards": ("Kd", "Qh", "Tc"),
        "players": (
            {
                "player_id": "hero",
                "position": "BTN",
                "role": "preflop_aggressor",
                "range_name": "broadway_board_hero_baseline",
                "combo_groups": {
                    "strong_broadways": ("AcKc", "AsKs", "QhJd", "JsTs"),
                    "offsuit_broadways": ("AdQh", "KhJc"),
                },
            },
            {
                "player_id": "villain_1",
                "position": "BB",
                "role": "bb_defender",
                "range_name": "broadway_board_villain_baseline",
                "combo_groups": {
                    "strong_broadways": ("AsKs", "KcQc", "QhJh", "Tc9c"),
                    "offsuit_broadways": ("AcQd", "KdJh", "JsTd"),
                },
            },
        ),
    },
    "flop_blockers_multiway_combo_state": {
        "spot_family": "multiway_pot",
        "pot_type": "multiway_pot",
        "hero_position": "BTN",
        "opponent_positions": ("BB", "CO"),
        "hero_cards": ("Ah", "8h"),
        "board_cards": ("Kh", "Th", "2c"),
        "players": (
            {
                "player_id": "hero",
                "position": "BTN",
                "role": "multiway_participant",
                "range_name": "multiway_hero_baseline",
                "combo_groups": {
                    "strong_broadways": ("AhKh", "AsKs", "QhJh"),
                    "suited_connectors": ("8h7h", "8s7s"),
                },
            },
            {
                "player_id": "villain_1",
                "position": "BB",
                "role": "multiway_defender",
                "range_name": "multiway_villain_1_baseline",
                "combo_groups": {
                    "suited_broadways": ("QhJh", "AhQh", "KsQs", "KhQh"),
                    "ace_x_suited": ("Ah5h", "As5s"),
                },
            },
            {
                "player_id": "villain_2",
                "position": "CO",
                "role": "multiway_caller",
                "range_name": "multiway_villain_2_baseline",
                "combo_groups": {
                    "defense_range": ("KhJh", "Th9h", "8h7h", "Ac2c", "Ks2s", "Ah2h"),
                },
            },
        ),
    },
}


def _load_expected(case_id: str) -> dict[str, Any]:
    return json.loads((EXPECTED_DIR / f"{case_id}.expected.json").read_text(encoding="utf-8"))


def _bucket_tuple(combo_groups: dict[str, tuple[str, ...]]) -> tuple[RangeBucket, ...]:
    buckets: list[RangeBucket] = []
    for bucket_name in combo_groups:
        try:
            buckets.append(RangeBucket(bucket_name))
        except ValueError:
            continue
    return tuple(buckets)


def _build_range_state(case_id: str) -> RangeState:
    payload = CASE_INPUTS[case_id]
    player_states: list[PlayerRangeState] = []
    for player_payload in payload["players"]:
        combo_groups = player_payload["combo_groups"]
        player_states.append(
            PlayerRangeState(
                player_id=player_payload["player_id"],
                position=player_payload["position"],
                role=player_payload["role"],
                range_name=player_payload["range_name"],
                range_source=RangeSourceType.SYNTHETIC_TEST_RANGES,
                combo_groups=combo_groups,
                range_buckets=_bucket_tuple(combo_groups),
                weighting_mode=RangeWeightingMode.FLAT_BASELINE,
                confidence=RangeConfidenceClass.MEDIUM,
                notes=("v0134_fixture_range_state",),
            )
        )

    return RangeState(
        case_id=case_id,
        source_file=f"tests/fixtures/postflop_available_combo_state_v0134/source/{case_id}.range_state.json",
        spot_family=payload["spot_family"],
        pot_type=payload["pot_type"],
        hero_position=payload["hero_position"],
        opponent_positions=payload["opponent_positions"],
        hero_range_state=player_states[0],
        opponent_range_states=tuple(player_states[1:]),
        range_source_info=RangeSourceInfo(
            source_type=RangeSourceType.SYNTHETIC_TEST_RANGES,
            source_name="v0134_available_combo_state_fixture_ranges",
            source_file="tests/fixtures/postflop_available_combo_state_v0134/source",
            source_version="v0.13.4",
            is_synthetic_test_source=True,
            notes=("fixture_coverage_only",),
        ),
        range_confidence=RangeConfidenceClass.MEDIUM,
        range_import_status=RangeImportStatus.SYNTHETIC_IMPORTED,
        range_buckets=tuple(sorted({bucket for player in player_states for bucket in player.range_buckets}, key=lambda item: item.value)),
        next_module="blocker_filtering_later",
        notes=("v0134_fixture_range_state", "range_state_read_only_expected"),
    )


def _result_for_case(case_id: str):
    payload = CASE_INPUTS[case_id]
    return build_available_combo_state(
        _build_range_state(case_id),
        hero_cards=payload["hero_cards"],
        board_cards=payload["board_cards"],
        case_id=case_id,
    )


def test_available_combo_state_fixture_cases_match_expected_counts_and_statuses() -> None:
    for case_id in CASE_INPUTS:
        expected = _load_expected(case_id)
        result = _result_for_case(case_id)

        assert result.case_id == case_id
        assert result.spot_family == expected["expected_spot_family"]
        assert result.hero_cards_used_as_blockers == tuple(expected["expected_hero_cards_used_as_blockers"])
        assert result.board_cards_used_as_blockers == tuple(expected["expected_board_cards_used_as_blockers"])
        assert result.total_combo_count_before == expected["expected_combo_count_before"]
        assert result.total_combo_count_available == expected["expected_combo_count_available"]
        assert result.total_combo_count_blocked_by_hero == expected["expected_combo_count_blocked_by_hero"]
        assert result.total_combo_count_blocked_by_board == expected["expected_combo_count_blocked_by_board"]
        assert result.total_combo_count_blocked_by_hero_and_board == expected["expected_combo_count_blocked_by_hero_and_board"]
        assert result.availability_status.value == expected["expected_availability_status"]
        assert sorted({item.blocked_reason.value for player in result.player_combo_states for item in player.blocker_results}) == sorted(
            expected["expected_blocked_combo_reasons"]
        )


def test_available_combo_state_preserves_range_source_info_and_trace_ready_payload() -> None:
    result = _result_for_case("flop_blockers_top_pair_blocks_ax")
    payload = result.to_json_dict()

    assert result.range_source_info["source_type"] == "synthetic_test_ranges"
    assert result.range_source_info["source_name"] == "v0134_available_combo_state_fixture_ranges"
    assert result.next_module == "flop_action_model_later"
    assert "range_state" in result.fields_used
    assert "player_range_state.combo_groups" in result.fields_used
    assert payload["case_id"] == "flop_blockers_top_pair_blocks_ax"
    assert payload["range_source_info"]["source_version"] == "v0.13.4"
    json.dumps(payload, sort_keys=True)


def test_multiway_available_combo_state_keeps_players_separate() -> None:
    expected = _load_expected("flop_blockers_multiway_combo_state")
    result = _result_for_case("flop_blockers_multiway_combo_state")

    assert len(result.player_combo_states) == expected["expected_player_count"]
    player_ids = [player.player_id for player in result.player_combo_states]
    assert player_ids == ["hero", "villain_1", "villain_2"]

    counts = {player.player_id: player.to_json_dict() for player in result.player_combo_states}
    for player_id, player_expected in expected["expected_player_summaries"].items():
        assert counts[player_id]["combo_count_before"] == player_expected["combo_count_before"]
        assert counts[player_id]["combo_count_available"] == player_expected["combo_count_available"]
        assert counts[player_id]["combo_count_blocked"] == player_expected["combo_count_blocked"]


def test_range_state_is_not_mutated_by_v0134_fixture_filtering() -> None:
    state = _build_range_state("flop_blockers_monotone_board_blocks_flush_combos")
    before = copy.deepcopy(state.to_json_dict())

    result = build_available_combo_state(
        state,
        hero_cards=CASE_INPUTS["flop_blockers_monotone_board_blocks_flush_combos"]["hero_cards"],
        board_cards=CASE_INPUTS["flop_blockers_monotone_board_blocks_flush_combos"]["board_cards"],
    )

    assert state.to_json_dict() == before
    assert result.availability_status is ComboAvailabilityStatus.PARTIALLY_BLOCKED
    assert "range_state_read_only" in result.notes


def test_available_combo_state_fixture_output_is_json_safe_for_all_cases() -> None:
    for case_id in CASE_INPUTS:
        result = _result_for_case(case_id)
        payload = result.to_json_dict()
        assert payload["case_id"] == case_id
        assert payload["player_combo_states"]
        assert payload["total_combo_count_before"] >= payload["total_combo_count_available"]
        json.dumps(payload, sort_keys=True)


def test_v0134_fixture_coverage_does_not_execute_later_solver_layers() -> None:
    result = _result_for_case("flop_blockers_broadway_board_blocks_broadway_combos")
    payload = result.to_json_dict()

    assert payload["next_module"] == "flop_action_model_later"
    assert "no_range_narrowing" in payload["notes"]
    assert "no_equity_recalculation" in payload["notes"]
    assert "no_decision_runtime_click" in payload["notes"]
