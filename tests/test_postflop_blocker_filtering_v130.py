from __future__ import annotations

import copy
import json
from dataclasses import asdict

from solver_postflop.blocker_filtering import (
    ARCHITECTURE_FLAGS,
    BLOCKER_FILTERING_VERSION,
    build_available_combo_state,
    filter_range_state_blocked_combos,
)
from solver_postflop.combo_contracts import BlockedComboReason, ComboAvailabilityStatus
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


def _sample_range_state() -> RangeState:
    hero_range = PlayerRangeState(
        player_id="hero",
        position="BTN",
        role="preflop_aggressor",
        range_name="hero_test_baseline",
        range_source=RangeSourceType.POSTFLOP_DEFAULT_RANGES,
        combo_groups={
            "strong_broadways": ("AsKs", "QhJd", "10s9s"),
        },
        range_buckets=(RangeBucket.STRONG_BROADWAYS,),
        weighting_mode=RangeWeightingMode.FLAT_BASELINE,
        confidence=RangeConfidenceClass.MEDIUM,
    )
    villain_range = PlayerRangeState(
        player_id="villain_1",
        position="BB",
        role="bb_defender",
        range_name="villain_test_baseline",
        range_source=RangeSourceType.POSTFLOP_DEFAULT_RANGES,
        combo_groups={
            "premium_pairs": ("AsAh", "KcKd", "QcQd", "not_a_combo"),
            "strong_broadways": ("AsKd", "AhKh", "QcJc"),
        },
        range_buckets=(RangeBucket.PREMIUM_PAIRS, RangeBucket.STRONG_BROADWAYS),
        weighting_mode=RangeWeightingMode.FLAT_BASELINE,
        confidence=RangeConfidenceClass.MEDIUM,
    )
    return RangeState(
        case_id="v0133_sample_case",
        source_file="tests/fixtures/v0133/sample.range.json",
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
            notes=("synthetic_baseline",),
        ),
        range_confidence=RangeConfidenceClass.MEDIUM,
        range_import_status=RangeImportStatus.IMPORTED,
        range_buckets=(RangeBucket.PREMIUM_PAIRS, RangeBucket.STRONG_BROADWAYS),
    )


def test_build_available_combo_state_filters_hero_and_board_blocked_combos() -> None:
    state = _sample_range_state()

    result = build_available_combo_state(
        state,
        hero_cards=("As", "Qh"),
        board_cards=("Kd", "2c", "7h"),
    )

    assert result.case_id == "v0133_sample_case"
    assert result.spot_family == "srp_heads_up"
    assert result.hero_cards_used_as_blockers == ("As", "Qh")
    assert result.board_cards_used_as_blockers == ("Kd", "2c", "7h")
    assert result.availability_status is ComboAvailabilityStatus.PARTIALLY_BLOCKED

    assert result.total_combo_count_before == 10
    assert result.total_combo_count_available == 4
    assert result.total_combo_count_blocked == 6
    assert result.total_combo_count_blocked_by_hero == 4
    assert result.total_combo_count_blocked_by_board == 2
    assert result.total_combo_count_blocked_by_hero_and_board == 1


def test_player_combo_state_preserves_bucket_structure_after_filtering() -> None:
    result = build_available_combo_state(
        _sample_range_state(),
        hero_cards=("As", "Qh"),
        board_cards=("Kd", "2c", "7h"),
    )

    villain = next(player for player in result.player_combo_states if player.player_id == "villain_1")

    assert villain.combo_count_before == 7
    assert villain.combo_count_available == 3
    assert villain.combo_count_blocked == 4
    assert villain.blocked_by_hero_count == 2
    assert villain.blocked_by_board_count == 2
    assert villain.blocked_by_hero_and_board_count == 1
    assert villain.available_combo_groups == {
        "premium_pairs": ("QcQd",),
        "strong_broadways": ("AhKh", "QcJc"),
    }
    assert villain.blocked_combo_groups == {
        "premium_pairs": ("AsAh", "KcKd", "not_a_combo"),
        "strong_broadways": ("AsKd",),
    }

    group_by_name = {group.bucket_name: group for group in villain.combo_group_availability}
    assert group_by_name["premium_pairs"].combo_count_before == 4
    assert group_by_name["premium_pairs"].combo_count_available == 1
    assert group_by_name["premium_pairs"].combo_count_blocked == 3
    assert group_by_name["strong_broadways"].combo_count_before == 3
    assert group_by_name["strong_broadways"].combo_count_available == 2
    assert group_by_name["strong_broadways"].combo_count_blocked == 1


def test_blocker_results_keep_explicit_reasons() -> None:
    result = build_available_combo_state(
        _sample_range_state(),
        hero_cards=("As", "Qh"),
        board_cards=("Kd", "2c", "7h"),
    )
    villain = next(player for player in result.player_combo_states if player.player_id == "villain_1")
    by_combo = {combo.combo: combo for combo in villain.blocker_results}

    assert by_combo["AsAh"].blocked_reason is BlockedComboReason.BLOCKED_BY_HERO_CARD
    assert by_combo["AsAh"].blocking_hero_cards == ("As",)
    assert by_combo["KcKd"].blocked_reason is BlockedComboReason.BLOCKED_BY_BOARD_CARD
    assert by_combo["KcKd"].blocking_board_cards == ("Kd",)
    assert by_combo["AsKd"].blocked_reason is BlockedComboReason.BLOCKED_BY_HERO_AND_BOARD
    assert by_combo["AsKd"].blocking_hero_cards == ("As",)
    assert by_combo["AsKd"].blocking_board_cards == ("Kd",)
    assert by_combo["AhKh"].blocked_reason is BlockedComboReason.NOT_BLOCKED
    assert by_combo["AhKh"].is_available is True


def test_malformed_combo_does_not_break_pipeline_and_is_not_available() -> None:
    result = build_available_combo_state(
        _sample_range_state(),
        hero_cards=("As", "Qh"),
        board_cards=("Kd",),
    )
    villain = next(player for player in result.player_combo_states if player.player_id == "villain_1")
    malformed = next(combo for combo in villain.blocker_results if combo.combo == "not_a_combo")

    assert malformed.is_available is False
    assert malformed.blocked_reason is BlockedComboReason.NOT_BLOCKED
    assert "combo_unparseable_excluded_from_available_state" in malformed.notes


def test_project_card_format_is_normalized_for_blockers() -> None:
    result = build_available_combo_state(
        _sample_range_state(),
        hero_cards=("A_spades", "Q_hearts"),
        board_cards=("K_diamonds", "2_clubs", "7_hearts"),
    )

    assert result.hero_cards_used_as_blockers == ("As", "Qh")
    assert result.board_cards_used_as_blockers == ("Kd", "2c", "7h")
    assert result.total_combo_count_blocked_by_hero == 4
    assert result.total_combo_count_blocked_by_board == 2


def test_range_state_is_not_mutated_by_blocker_filtering() -> None:
    state = _sample_range_state()
    before = copy.deepcopy(state.to_json_dict())

    result = build_available_combo_state(state, hero_cards=("As",), board_cards=("Kd",))

    assert state.to_json_dict() == before
    assert result.notes
    assert "range_state_read_only" in result.notes


def test_filter_alias_matches_builder_result() -> None:
    state = _sample_range_state()

    direct = build_available_combo_state(state, hero_cards=("As",), board_cards=("Kd",)).to_json_dict()
    alias = filter_range_state_blocked_combos(state, hero_cards=("As",), board_cards=("Kd",)).to_json_dict()

    assert alias == direct


def test_unknown_empty_range_state_returns_structured_unknown_result() -> None:
    state = RangeState(
        case_id="unknown_case",
        source_file="unknown_range",
        spot_family=None,
        range_import_status=RangeImportStatus.UNKNOWN_RANGE,
    )

    result = build_available_combo_state(state, hero_cards=None, board_cards=None)

    assert result.case_id == "unknown_case"
    assert result.availability_status is ComboAvailabilityStatus.UNKNOWN
    assert result.total_combo_count_before == 0
    assert result.player_combo_states == ()
    assert "hero_cards" in result.fields_not_provided
    assert "board_cards" in result.fields_not_provided
    json.dumps(result.to_json_dict(), sort_keys=True)


def test_available_combo_state_is_json_serializable() -> None:
    result = build_available_combo_state(
        _sample_range_state(),
        hero_cards=("As", "Qh"),
        board_cards=("Kd", "2c", "7h"),
    )

    payload = result.to_json_dict()

    assert payload["availability_status"] == "partially_blocked"
    assert payload["player_combo_states"][0]["available_combo_groups"]
    json.dumps(payload, sort_keys=True)


def test_blocker_filtering_architecture_flags_do_not_execute_forbidden_layers() -> None:
    assert BLOCKER_FILTERING_VERSION == "v0.13.3"
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
