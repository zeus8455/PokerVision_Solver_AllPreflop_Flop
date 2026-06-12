from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass

from solver_postflop import (
    COMBO_DRAW_CLASSES,
    DRAW_CLASSES,
    DRAW_CONTRACT_VERSION,
    DRAW_FUTURE_MODULES,
    DRAW_STRENGTH_TIERS,
    FLUSH_DRAW_CLASSES,
    OVERCARD_CLASSES,
    STRAIGHT_DRAW_CLASSES,
    ComboDrawClass,
    DrawClass,
    DrawFeatures,
    DrawStrengthTier,
    FlushDrawClass,
    OvercardClass,
    StraightDrawClass,
)


def test_draw_contract_version_is_fixed_for_v080() -> None:
    assert DRAW_CONTRACT_VERSION == "v0.8.0"


def test_draw_class_labels_are_fixed() -> None:
    assert {draw_class.value for draw_class in DrawClass} == {
        "no_draw",
        "backdoor_only",
        "flush_draw",
        "straight_draw",
        "combo_draw",
        "overcards_only",
        "pair_plus_draw",
        "unknown",
    }
    assert DRAW_CLASSES == tuple(DrawClass)


def test_flush_draw_class_labels_are_fixed() -> None:
    assert {flush_draw.value for flush_draw in FlushDrawClass} == {
        "no_flush_draw",
        "backdoor_flush_draw",
        "weak_flush_draw",
        "standard_flush_draw",
        "nut_flush_draw_candidate",
        "unknown",
    }
    assert FLUSH_DRAW_CLASSES == tuple(FlushDrawClass)


def test_straight_draw_class_labels_are_fixed() -> None:
    assert {straight_draw.value for straight_draw in StraightDrawClass} == {
        "no_straight_draw",
        "gutshot",
        "open_ended_straight_draw",
        "double_gutshot",
        "combo_straight_draw",
        "unknown",
    }
    assert STRAIGHT_DRAW_CLASSES == tuple(StraightDrawClass)


def test_overcard_class_labels_are_fixed() -> None:
    assert {overcard.value for overcard in OvercardClass} == {
        "no_overcards",
        "one_overcard",
        "two_overcards",
        "unknown",
    }
    assert OVERCARD_CLASSES == tuple(OvercardClass)


def test_combo_draw_class_labels_are_fixed() -> None:
    assert {combo_draw.value for combo_draw in ComboDrawClass} == {
        "no_combo_draw",
        "flush_plus_gutshot",
        "flush_plus_oesd",
        "pair_plus_flush_draw",
        "pair_plus_straight_draw",
        "pair_plus_combo_draw",
        "overcards_plus_draw",
        "premium_combo_draw",
        "unknown",
    }
    assert COMBO_DRAW_CLASSES == tuple(ComboDrawClass)


def test_draw_strength_tier_labels_are_fixed() -> None:
    assert {tier.value for tier in DrawStrengthTier} == {
        "no_draw",
        "backdoor_only",
        "weak_draw",
        "medium_draw",
        "strong_draw",
        "premium_combo_draw",
        "unknown",
    }
    assert DRAW_STRENGTH_TIERS == tuple(DrawStrengthTier)


def test_draw_features_can_be_created_and_serialized() -> None:
    features = DrawFeatures(
        case_id="draw_contract_case",
        source_file="tests/fixtures/postflop_clear_json/synthetic/flop/case.clear.json",
        hero_cards=("Ah", "Jh"),
        board_cards=("Kh", "Th", "2c"),
        draw_class=DrawClass.COMBO_DRAW,
        flush_draw_class=FlushDrawClass.NUT_FLUSH_DRAW_CANDIDATE,
        straight_draw_class=StraightDrawClass.GUTSHOT,
        overcard_class=OvercardClass.ONE_OVERCARD,
        combo_draw_class=ComboDrawClass.FLUSH_PLUS_GUTSHOT,
        draw_strength_tier=DrawStrengthTier.STRONG_DRAW,
        draw_tags=("nut_fd_gutshot_overcard",),
        features_used_by_future_modules=DRAW_FUTURE_MODULES[:3],
        notes=("contract_only",),
    )

    assert is_dataclass(features)
    assert asdict(features)["draw_class"] == DrawClass.COMBO_DRAW
    payload = features.to_json_dict()
    assert payload["hero_cards"] == ["Ah", "Jh"]
    assert payload["board_cards"] == ["Kh", "Th", "2c"]
    assert payload["draw_class"] == "combo_draw"
    assert payload["flush_draw_class"] == "nut_flush_draw_candidate"
    assert payload["straight_draw_class"] == "gutshot"
    assert payload["overcard_class"] == "one_overcard"
    assert payload["combo_draw_class"] == "flush_plus_gutshot"
    assert payload["draw_strength_tier"] == "strong_draw"
    assert payload["draw_tags"] == ["nut_fd_gutshot_overcard"]
    json.dumps(payload, sort_keys=True)


def test_draw_features_remain_feature_metadata_only() -> None:
    features = DrawFeatures(
        case_id="metadata_only_case",
        source_file="metadata_only.clear.json",
        hero_cards=("As", "Qd"),
        board_cards=("Kh", "7d", "2c"),
        draw_class=DrawClass.NO_DRAW,
        flush_draw_class=FlushDrawClass.NO_FLUSH_DRAW,
        straight_draw_class=StraightDrawClass.NO_STRAIGHT_DRAW,
        overcard_class=OvercardClass.ONE_OVERCARD,
        combo_draw_class=ComboDrawClass.NO_COMBO_DRAW,
        draw_strength_tier=DrawStrengthTier.NO_DRAW,
        draw_tags=("no_draw_one_overcard",),
    )
    payload = features.to_json_dict()

    forbidden_keys = {
        "equity",
        "range",
        "decision",
        "runtime_plan",
        "click_result",
        "action_sequence",
        "button_targets",
    }
    assert forbidden_keys.isdisjoint(payload)


def test_draw_future_modules_are_fixed_metadata_targets() -> None:
    assert DRAW_FUTURE_MODULES == (
        "equity_input_builder_later",
        "equity_module_later",
        "range_interaction_later",
        "decision_engine_later",
        "bet_sizing_policy_later",
        "runtime_plan_later",
    )


def test_draw_contracts_exported_from_public_package() -> None:
    import solver_postflop

    for public_name in (
        "COMBO_DRAW_CLASSES",
        "DRAW_CLASSES",
        "DRAW_CONTRACT_VERSION",
        "DRAW_FUTURE_MODULES",
        "DRAW_STRENGTH_TIERS",
        "FLUSH_DRAW_CLASSES",
        "OVERCARD_CLASSES",
        "STRAIGHT_DRAW_CLASSES",
        "ComboDrawClass",
        "DrawClass",
        "DrawFeatures",
        "DrawStrengthTier",
        "FlushDrawClass",
        "OvercardClass",
        "StraightDrawClass",
    ):
        assert public_name in solver_postflop.__all__
        assert hasattr(solver_postflop, public_name)
