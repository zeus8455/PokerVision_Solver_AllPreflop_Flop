import json
from pathlib import Path

from solver_postflop.range_contracts import (
    DEFAULT_RANGE_NEXT_MODULE,
    DEFAULT_UNKNOWN_RANGE_NAME,
    RANGE_BUCKETS,
    RANGE_CONFIDENCE_CLASSES,
    RANGE_CONTRACT_VERSION,
    RANGE_IMPORT_STATUSES,
    RANGE_SOURCE_TYPES,
    RANGE_WEIGHTING_MODES,
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
CONTRACT_SOURCE = PROJECT_ROOT / "solver_postflop" / "range_contracts.py"


def test_range_contract_version_is_v0121() -> None:
    assert RANGE_CONTRACT_VERSION == "v0.12.1"


def test_range_source_types_contain_planned_sources() -> None:
    assert {source.value for source in RANGE_SOURCE_TYPES} == {
        "existing_project_ranges",
        "postflop_default_ranges",
        "synthetic_test_ranges",
        "unknown_range",
    }


def test_range_import_statuses_contain_unknown_range_without_failure() -> None:
    statuses = {status.value for status in RANGE_IMPORT_STATUSES}
    assert "imported" in statuses
    assert "synthetic_imported" in statuses
    assert "unknown_range" in statuses
    assert "source_unavailable" in statuses
    assert "unsupported_context" in statuses


def test_range_buckets_include_baseline_groups_for_future_combo_modules() -> None:
    buckets = {bucket.value for bucket in RANGE_BUCKETS}
    assert "premium_pairs" in buckets
    assert "strong_broadways" in buckets
    assert "suited_broadways" in buckets
    assert "suited_connectors" in buckets
    assert "offsuit_broadways" in buckets
    assert "pocket_pairs" in buckets
    assert "ace_x_suited" in buckets
    assert "defense_range" in buckets
    assert "unknown_bucket" in buckets


def test_range_confidence_and_weighting_modes_exist() -> None:
    assert {item.value for item in RANGE_CONFIDENCE_CLASSES} == {
        "high",
        "medium",
        "low",
        "unknown",
    }
    assert {item.value for item in RANGE_WEIGHTING_MODES} == {
        "flat_baseline",
        "source_weighted",
        "unknown",
    }


def test_range_source_info_serializes_to_json_safe_dict() -> None:
    source_info = RangeSourceInfo(
        source_type=RangeSourceType.SYNTHETIC_TEST_RANGES,
        source_name="srp_btn_vs_bb_synthetic",
        source_file="tests/fixtures/ranges/srp_btn_vs_bb.json",
        source_version="v0.12.1-test",
        is_synthetic_test_source=True,
        notes=("fixture_only",),
    )

    payload = source_info.to_json_dict()

    assert payload["source_type"] == "synthetic_test_ranges"
    assert payload["source_name"] == "srp_btn_vs_bb_synthetic"
    assert payload["is_synthetic_test_source"] is True
    json.dumps(payload)


def test_player_range_state_carries_combo_groups_without_processing() -> None:
    player_range = PlayerRangeState(
        player_id="villain_1",
        position="BB",
        role="bb_defender",
        range_name="srp_bb_defense_baseline",
        range_source=RangeSourceType.POSTFLOP_DEFAULT_RANGES,
        combo_groups={
            "premium_pairs": ("AsAh", "KsKh"),
            "suited_broadways": ("AsKs", "AhKh"),
            "ace_x_suited": ("As5s", "Ah5h"),
        },
        hand_class_groups={
            "pocket_pairs": ("AA", "KK"),
            "suited_aces": ("A5s",),
        },
        range_buckets=(
            RangeBucket.PREMIUM_PAIRS,
            RangeBucket.SUITED_BROADWAYS,
            RangeBucket.ACE_X_SUITED,
        ),
        weighting_mode=RangeWeightingMode.FLAT_BASELINE,
        confidence=RangeConfidenceClass.MEDIUM,
        notes=("baseline_only",),
    )

    payload = player_range.to_json_dict()

    assert payload["player_id"] == "villain_1"
    assert payload["range_source"] == "postflop_default_ranges"
    assert payload["combo_groups"]["premium_pairs"] == ["AsAh", "KsKh"]
    assert payload["combo_groups"]["suited_broadways"] == ["AsKs", "AhKh"]
    assert payload["range_buckets"] == [
        "premium_pairs",
        "suited_broadways",
        "ace_x_suited",
    ]
    assert payload["weighting_mode"] == "flat_baseline"
    json.dumps(payload)


def test_range_state_creates_full_json_safe_baseline_state() -> None:
    hero_range = PlayerRangeState(
        player_id="hero",
        position="BTN",
        role="hero",
        range_name="srp_btn_open_baseline",
        range_source=RangeSourceType.POSTFLOP_DEFAULT_RANGES,
        combo_groups={"strong_broadways": ("AsKs",)},
        range_buckets=(RangeBucket.STRONG_BROADWAYS,),
        weighting_mode=RangeWeightingMode.FLAT_BASELINE,
        confidence=RangeConfidenceClass.MEDIUM,
    )
    opponent_range = PlayerRangeState(
        player_id="villain_1",
        position="BB",
        role="bb_defender",
        range_name="srp_bb_defense_baseline",
        range_source=RangeSourceType.POSTFLOP_DEFAULT_RANGES,
        combo_groups={"defense_range": ("As5s", "KcQc")},
        range_buckets=(RangeBucket.DEFENSE_RANGE,),
        weighting_mode=RangeWeightingMode.FLAT_BASELINE,
        confidence=RangeConfidenceClass.MEDIUM,
    )

    range_state = RangeState(
        case_id="flop_range_srp_heads_up_btn_vs_bb",
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop.clear.json",
        spot_family="srp_heads_up",
        pot_type="srp",
        hero_position="BTN",
        opponent_positions=("BB",),
        hero_range_state=hero_range,
        opponent_range_states=(opponent_range,),
        range_source_info=RangeSourceInfo(
            source_type=RangeSourceType.POSTFLOP_DEFAULT_RANGES,
            source_name="postflop_default_srp_ranges",
        ),
        range_confidence=RangeConfidenceClass.MEDIUM,
        range_import_status=RangeImportStatus.IMPORTED,
        range_buckets=(RangeBucket.STRONG_BROADWAYS, RangeBucket.DEFENSE_RANGE),
        fields_used=("spot_family", "position_context.hero_position"),
        fields_not_provided=("source_weighting",),
        notes=("baseline_range_only",),
    )

    payload = range_state.to_json_dict()

    assert payload["case_id"] == "flop_range_srp_heads_up_btn_vs_bb"
    assert payload["spot_family"] == "srp_heads_up"
    assert payload["pot_type"] == "srp"
    assert payload["hero_position"] == "BTN"
    assert payload["opponent_positions"] == ["BB"]
    assert payload["hero_range_state"]["range_name"] == "srp_btn_open_baseline"
    assert payload["opponent_range_states"][0]["range_name"] == "srp_bb_defense_baseline"
    assert payload["range_source_info"]["source_type"] == "postflop_default_ranges"
    assert payload["range_import_status"] == "imported"
    assert payload["range_confidence"] == "medium"
    assert payload["next_module"] == DEFAULT_RANGE_NEXT_MODULE
    json.dumps(payload)


def test_unknown_range_state_is_structured_and_non_fatal() -> None:
    range_state = RangeState(
        case_id="flop_range_unknown_context",
        source_file="unknown.clear.json",
        spot_family="unknown_flop_spot",
        range_source_info=RangeSourceInfo(),
        range_confidence=RangeConfidenceClass.UNKNOWN,
        range_import_status=RangeImportStatus.UNKNOWN_RANGE,
        range_buckets=(RangeBucket.UNKNOWN_BUCKET,),
        notes=("range_source_not_selected",),
    )

    payload = range_state.to_json_dict()

    assert payload["range_source_info"]["source_type"] == "unknown_range"
    assert payload["range_source_info"]["source_name"] == DEFAULT_UNKNOWN_RANGE_NAME
    assert payload["range_import_status"] == "unknown_range"
    assert payload["range_confidence"] == "unknown"
    assert payload["range_buckets"] == ["unknown_bucket"]
    assert payload["next_module"] == "blocker_filtering_later"
    json.dumps(payload)


def test_range_contracts_do_not_import_backend_or_runtime_modules() -> None:
    source = CONTRACT_SOURCE.read_text(encoding="utf-8").lower()

    forbidden_terms = [
        "pokerkit",
        "calculate_equity",
        "monte_carlo",
        "run_simulation",
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
