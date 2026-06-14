import json
from pathlib import Path

from solver_postflop.combo_contracts import (
    BLOCKED_COMBO_REASONS,
    COMBO_AVAILABILITY_STATUSES,
    COMBO_CONTRACT_VERSION,
    DEFAULT_COMBO_NEXT_MODULE,
    AvailableComboState,
    BlockedComboReason,
    ComboAvailabilityStatus,
    ComboBlockerResult,
    ComboGroupAvailability,
    PlayerComboState,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_SOURCE = PROJECT_ROOT / "solver_postflop" / "combo_contracts.py"


def test_combo_contract_version_is_v0131() -> None:
    assert COMBO_CONTRACT_VERSION == "v0.13.1"


def test_blocked_combo_reasons_match_v013_plan() -> None:
    assert {reason.value for reason in BLOCKED_COMBO_REASONS} == {
        "not_blocked",
        "blocked_by_hero_card",
        "blocked_by_board_card",
        "blocked_by_hero_and_board",
    }


def test_combo_availability_statuses_exist() -> None:
    assert {status.value for status in COMBO_AVAILABILITY_STATUSES} == {
        "available",
        "partially_blocked",
        "fully_blocked",
        "unknown",
    }


def test_combo_blocker_result_serializes_to_json_safe_dict() -> None:
    result = ComboBlockerResult(
        combo="AsKs",
        bucket_name="strong_broadways",
        combo_cards=("As", "Ks"),
        blocked_reason=BlockedComboReason.BLOCKED_BY_HERO_CARD,
        is_available=False,
        blocking_hero_cards=("As",),
        blocking_board_cards=(),
        notes=("contract_only",),
    )

    payload = result.to_json_dict()

    assert payload["combo"] == "AsKs"
    assert payload["combo_cards"] == ["As", "Ks"]
    assert payload["bucket_name"] == "strong_broadways"
    assert payload["blocked_reason"] == "blocked_by_hero_card"
    assert payload["is_available"] is False
    assert payload["blocking_hero_cards"] == ["As"]
    json.dumps(payload)


def test_combo_group_availability_serializes_bucket_counts() -> None:
    bucket_state = ComboGroupAvailability(
        bucket_name="suited_broadways",
        combo_count_before=3,
        combo_count_available=2,
        combo_count_blocked=1,
        available_combos=("AhKh", "AcKc"),
        blocked_combos=("AsKs",),
        notes=("bucket_contract_only",),
    )

    payload = bucket_state.to_json_dict()

    assert payload["bucket_name"] == "suited_broadways"
    assert payload["combo_count_before"] == 3
    assert payload["combo_count_available"] == 2
    assert payload["combo_count_blocked"] == 1
    assert payload["available_combos"] == ["AhKh", "AcKc"]
    assert payload["blocked_combos"] == ["AsKs"]
    json.dumps(payload)


def test_player_combo_state_serializes_available_and_blocked_groups() -> None:
    player_state = PlayerComboState(
        player_id="villain_1",
        position="BB",
        range_name="srp_bb_defense_baseline",
        combo_count_before=4,
        combo_count_available=2,
        combo_count_blocked=2,
        blocked_by_hero_count=1,
        blocked_by_board_count=1,
        blocked_by_hero_and_board_count=0,
        available_combo_groups={"suited_broadways": ("AhKh", "AcKc")},
        blocked_combo_groups={"suited_broadways": ("AsKs",), "ace_x_suited": ("As5s",)},
        combo_group_availability=(
            ComboGroupAvailability(
                bucket_name="suited_broadways",
                combo_count_before=3,
                combo_count_available=2,
                combo_count_blocked=1,
                available_combos=("AhKh", "AcKc"),
                blocked_combos=("AsKs",),
            ),
        ),
        blocker_results=(
            ComboBlockerResult(
                combo="AsKs",
                bucket_name="suited_broadways",
                combo_cards=("As", "Ks"),
                blocked_reason=BlockedComboReason.BLOCKED_BY_HERO_CARD,
                is_available=False,
                blocking_hero_cards=("As",),
            ),
        ),
        availability_status=ComboAvailabilityStatus.PARTIALLY_BLOCKED,
        availability_confidence="medium",
        notes=("player_combo_contract_only",),
    )

    payload = player_state.to_json_dict()

    assert payload["player_id"] == "villain_1"
    assert payload["position"] == "BB"
    assert payload["range_name"] == "srp_bb_defense_baseline"
    assert payload["combo_count_before"] == 4
    assert payload["combo_count_available"] == 2
    assert payload["combo_count_blocked"] == 2
    assert payload["blocked_by_hero_count"] == 1
    assert payload["blocked_by_board_count"] == 1
    assert payload["available_combo_groups"]["suited_broadways"] == ["AhKh", "AcKc"]
    assert payload["blocked_combo_groups"]["ace_x_suited"] == ["As5s"]
    assert payload["availability_status"] == "partially_blocked"
    json.dumps(payload)


def test_available_combo_state_serializes_full_table_state() -> None:
    player_state = PlayerComboState(
        player_id="villain_1",
        position="BB",
        range_name="srp_bb_defense_baseline",
        combo_count_before=3,
        combo_count_available=1,
        combo_count_blocked=2,
        blocked_by_hero_count=1,
        blocked_by_board_count=1,
        available_combo_groups={"defense_range": ("KcQc",)},
        blocked_combo_groups={"defense_range": ("As9s", "QhTh")},
        availability_status=ComboAvailabilityStatus.PARTIALLY_BLOCKED,
        availability_confidence="medium",
    )

    state = AvailableComboState(
        case_id="flop_blockers_top_pair_blocks_ax",
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop.clear.json",
        spot_family="srp_heads_up",
        hero_cards_used_as_blockers=("As", "Kd"),
        board_cards_used_as_blockers=("Qh", "Jh", "2c"),
        player_combo_states=(player_state,),
        total_combo_count_before=3,
        total_combo_count_available=1,
        total_combo_count_blocked=2,
        total_combo_count_blocked_by_hero=1,
        total_combo_count_blocked_by_board=1,
        total_combo_count_blocked_by_hero_and_board=0,
        availability_status=ComboAvailabilityStatus.PARTIALLY_BLOCKED,
        range_source_info={"source_type": "postflop_default_ranges"},
        fields_used=("range_state", "hero_cards", "board_cards"),
        notes=("available_combo_contract_only",),
    )

    payload = state.to_json_dict()

    assert payload["case_id"] == "flop_blockers_top_pair_blocks_ax"
    assert payload["spot_family"] == "srp_heads_up"
    assert payload["hero_cards_used_as_blockers"] == ["As", "Kd"]
    assert payload["board_cards_used_as_blockers"] == ["Qh", "Jh", "2c"]
    assert payload["player_combo_states"][0]["player_id"] == "villain_1"
    assert payload["total_combo_count_before"] == 3
    assert payload["total_combo_count_available"] == 1
    assert payload["total_combo_count_blocked"] == 2
    assert payload["availability_status"] == "partially_blocked"
    assert payload["next_module"] == DEFAULT_COMBO_NEXT_MODULE
    json.dumps(payload)


def test_unknown_available_combo_state_is_structured_and_non_fatal() -> None:
    state = AvailableComboState(
        case_id="flop_blockers_unknown_context",
        source_file="unknown.clear.json",
        spot_family=None,
        availability_status=ComboAvailabilityStatus.UNKNOWN,
        fields_not_provided=("range_state", "hero_cards", "board_cards"),
        notes=("structured_unknown_combo_state",),
    )

    payload = state.to_json_dict()

    assert payload["case_id"] == "flop_blockers_unknown_context"
    assert payload["availability_status"] == "unknown"
    assert payload["player_combo_states"] == []
    assert payload["total_combo_count_before"] == 0
    assert payload["next_module"] == "flop_action_model_later"
    json.dumps(payload)


def test_combo_contracts_do_not_import_solver_execution_layers() -> None:
    source = CONTRACT_SOURCE.read_text(encoding="utf-8").lower()
    forbidden_terms = [
        "pokerkit",
        "calculate_equity",
        "monte_carlo",
        "range_narrowing",
        "decision_engine",
        "runtime_plan(",
        "click(",
        "mouse",
        "clear_json_pending",
        "dark_json",
        "current_cycle",
        "display_analysis_cycle",
    ]

    for forbidden in forbidden_terms:
        assert forbidden not in source
