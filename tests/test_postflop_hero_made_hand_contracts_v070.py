from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass

from solver_postflop import (
    MADE_HAND_CLASSES,
    MADE_HAND_CONTRACT_VERSION,
    MADE_HAND_FUTURE_MODULES,
    MADE_HAND_STRENGTH_TIERS,
    PAIR_CLASSES,
    SHOWDOWN_VALUE_CLASSES,
    MadeHandClass,
    MadeHandFeatures,
    MadeHandStrengthTier,
    PairClass,
    ShowdownValueClass,
)


def test_made_hand_contract_version_is_fixed_for_v070() -> None:
    assert MADE_HAND_CONTRACT_VERSION == "v0.7.0"


def test_made_hand_class_labels_are_fixed() -> None:
    assert {made_hand.value for made_hand in MadeHandClass} == {
        "no_made_hand",
        "high_card",
        "one_pair",
        "two_pair",
        "three_of_a_kind",
        "straight",
        "flush",
        "full_house",
        "quads",
        "unknown",
    }
    assert MADE_HAND_CLASSES == tuple(MadeHandClass)


def test_pair_class_labels_are_fixed() -> None:
    assert {pair_class.value for pair_class in PairClass} == {
        "top_pair",
        "second_pair",
        "middle_pair",
        "bottom_pair",
        "overpair",
        "underpair",
        "pocket_pair_below_board",
        "no_pair_class",
        "unknown",
    }
    assert PAIR_CLASSES == tuple(PairClass)


def test_showdown_value_class_labels_are_fixed() -> None:
    assert {showdown.value for showdown in ShowdownValueClass} == {
        "air",
        "weak_showdown",
        "medium_showdown",
        "strong_showdown",
        "value_hand",
        "unknown",
    }
    assert SHOWDOWN_VALUE_CLASSES == tuple(ShowdownValueClass)


def test_made_hand_strength_tier_labels_are_fixed() -> None:
    assert {tier.value for tier in MadeHandStrengthTier} == {
        "air",
        "weak_showdown",
        "medium_showdown",
        "strong_showdown",
        "value_hand",
        "very_strong_value",
        "nut_or_near_nut",
        "unknown",
    }
    assert MADE_HAND_STRENGTH_TIERS == tuple(MadeHandStrengthTier)


def test_made_hand_features_can_be_created_and_serialized() -> None:
    features = MadeHandFeatures(
        case_id="made_hand_contract_case",
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/case.clear.json",
        hero_cards=("Ah", "Qh"),
        board_cards=("As", "7d", "2c"),
        made_hand_class=MadeHandClass.ONE_PAIR,
        pair_class=PairClass.TOP_PAIR,
        showdown_value_class=ShowdownValueClass.STRONG_SHOWDOWN,
        strength_tier=MadeHandStrengthTier.STRONG_SHOWDOWN,
        kicker_relevance="high",
        board_interaction_tags=("top_pair_top_kicker_candidate",),
        features_used_by_future_modules=MADE_HAND_FUTURE_MODULES[:3],
        notes=("contract_only",),
    )

    assert is_dataclass(features)
    assert asdict(features)["made_hand_class"] == MadeHandClass.ONE_PAIR
    payload = features.to_json_dict()
    assert payload["hero_cards"] == ["Ah", "Qh"]
    assert payload["board_cards"] == ["As", "7d", "2c"]
    assert payload["made_hand_class"] == "one_pair"
    assert payload["pair_class"] == "top_pair"
    assert payload["showdown_value_class"] == "strong_showdown"
    assert payload["strength_tier"] == "strong_showdown"
    assert payload["kicker_relevance"] == "high"
    assert payload["board_interaction_tags"] == ["top_pair_top_kicker_candidate"]
    json.dumps(payload, sort_keys=True)


def test_made_hand_features_remain_feature_metadata_only() -> None:
    features = MadeHandFeatures(
        case_id="metadata_only_case",
        source_file="metadata_only.clear.json",
        hero_cards=("Kh", "Qs"),
        board_cards=("Ah", "7d", "2c"),
        made_hand_class=MadeHandClass.HIGH_CARD,
        pair_class=PairClass.NO_PAIR_CLASS,
        showdown_value_class=ShowdownValueClass.AIR,
        strength_tier=MadeHandStrengthTier.AIR,
        board_interaction_tags=("high_card_only",),
    )
    payload = features.to_json_dict()

    forbidden_keys = {
        "draw_class",
        "flush_draw_class",
        "straight_draw_class",
        "equity",
        "range",
        "decision",
        "runtime_plan",
        "click_result",
    }
    assert forbidden_keys.isdisjoint(payload)


def test_made_hand_future_modules_are_fixed_metadata_targets() -> None:
    assert MADE_HAND_FUTURE_MODULES == (
        "hero_draw_classifier_later",
        "equity_module_later",
        "range_interaction_later",
        "decision_engine_later",
        "bet_sizing_policy_later",
        "runtime_plan_later",
    )


def test_made_hand_contracts_exported_from_public_package() -> None:
    import solver_postflop

    for public_name in (
        "MADE_HAND_CLASSES",
        "MADE_HAND_CONTRACT_VERSION",
        "MADE_HAND_FUTURE_MODULES",
        "MADE_HAND_STRENGTH_TIERS",
        "PAIR_CLASSES",
        "SHOWDOWN_VALUE_CLASSES",
        "MadeHandClass",
        "MadeHandFeatures",
        "MadeHandStrengthTier",
        "PairClass",
        "ShowdownValueClass",
    ):
        assert public_name in solver_postflop.__all__
        assert hasattr(solver_postflop, public_name)
