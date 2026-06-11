from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass

from solver_postflop import (
    DEFAULT_FLOP_NEXT_MODULE,
    FLOP_SPOT_FAMILIES,
    FlopActionContext,
    FlopContext,
    FlopPlayerContext,
    FlopPositionContext,
    FlopPotContext,
    FlopSpotFamily,
)


def test_flop_spot_family_labels_are_fixed() -> None:
    assert {family.value for family in FlopSpotFamily} == {
        "srp_heads_up",
        "threebet_pot_heads_up",
        "fourbet_low_spr",
        "limp_or_passive_pot",
        "multiway_pot",
        "unknown_flop_spot",
    }
    assert FLOP_SPOT_FAMILIES == tuple(FlopSpotFamily)


def test_flop_pot_context_can_be_created_and_serialized() -> None:
    context = FlopPotContext(
        pot=6.5,
        to_call=0.0,
        effective_stack=97.5,
        spr=15.0,
        pot_type="srp",
        fields_used=("pot", "to_call", "stacks"),
        fields_not_provided=("preflop_aggressor",),
    )

    assert context.pot == 6.5
    assert context.to_json_dict()["pot_type"] == "srp"
    json.dumps(context.to_json_dict(), sort_keys=True)


def test_flop_action_context_can_be_created_and_serialized() -> None:
    context = FlopActionContext(
        allowed_actions=("check", "bet"),
        current_actor="hero",
        action_context_label="check_option",
        facing_bet=False,
        facing_raise=False,
        can_check=True,
        can_call=False,
        can_bet=True,
        can_raise=False,
        fields_used=("allowed_actions", "action_context"),
    )

    payload = context.to_json_dict()
    assert payload["allowed_actions"] == ["check", "bet"]
    assert payload["can_check"] is True
    json.dumps(payload, sort_keys=True)


def test_flop_position_and_player_contexts_can_be_created() -> None:
    position_context = FlopPositionContext(
        hero_id="hero",
        hero_position="BB",
        is_in_position=False,
        position_label="out_of_position",
        fields_used=("players", "positions"),
    )
    player_context = FlopPlayerContext(
        players=(
            {"id": "hero", "position": "BB", "stack": 97.5},
            {"id": "villain", "position": "BTN", "stack": 101.0},
        ),
        opponents=({"id": "villain", "position": "BTN", "stack": 101.0},),
        hero_id="hero",
        hero_position="BB",
        is_heads_up=True,
        is_multiway=False,
        fields_used=("players",),
    )

    assert position_context.hero_position == "BB"
    assert player_context.is_heads_up is True
    assert player_context.to_json_dict()["opponents"][0]["id"] == "villain"


def test_flop_context_can_be_created_for_srp_heads_up() -> None:
    raw_payload = {"case_id": "flop_contract_case", "board_cards": ["Ah", "7d", "2c"]}
    context = FlopContext(
        case_id="flop_contract_case",
        source_file="tests/fixtures/postflop_clear_json/real/flop/case.clear.json",
        table_id="table_01",
        hand_id="hand_01",
        branch="flop",
        spot_family=FlopSpotFamily.SRP_HEADS_UP,
        hero_cards=("As", "Kd"),
        board_cards=("Ah", "7d", "2c"),
        pot_context=FlopPotContext(pot=6.5, to_call=0.0, pot_type="srp"),
        position_context=FlopPositionContext(hero_id="hero", hero_position="BB"),
        action_context=FlopActionContext(allowed_actions=("check", "bet"), can_check=True, can_bet=True),
        player_context=FlopPlayerContext(is_heads_up=True, is_multiway=False),
        next_module=DEFAULT_FLOP_NEXT_MODULE,
        context_fields_used=("hero_cards", "board_cards", "players", "pot", "allowed_actions"),
        context_fields_not_provided=("preflop_aggressor",),
        raw_clear_json_ref=raw_payload,
        notes=("contract_only",),
    )

    assert context.branch == "flop"
    assert context.spot_family == FlopSpotFamily.SRP_HEADS_UP
    assert context.next_module == "flop_board_texture_builder"
    assert context.raw_clear_json_ref is raw_payload


def test_flop_context_serializes_to_json_safe_dict() -> None:
    context = FlopContext(
        case_id="flop_json_case",
        source_file="flop_json_case.clear.json",
        table_id=None,
        hand_id=None,
        branch="flop",
        spot_family=FlopSpotFamily.UNKNOWN_FLOP_SPOT,
        hero_cards=("Qh", "Qs"),
        board_cards=("Ah", "7d", "2c"),
        notes=("json_safe",),
    )

    payload = context.to_json_dict()

    assert payload["spot_family"] == "unknown_flop_spot"
    assert payload["hero_cards"] == ["Qh", "Qs"]
    assert payload["pot_context"]["fields_used"] == []
    json.dumps(payload, sort_keys=True)


def test_flop_context_is_frozen_dataclass() -> None:
    context = FlopContext(
        case_id=None,
        source_file="contract_only.clear.json",
        table_id=None,
        hand_id=None,
        branch="flop",
        spot_family=FlopSpotFamily.UNKNOWN_FLOP_SPOT,
    )

    assert is_dataclass(context)
    assert asdict(context)["spot_family"] == FlopSpotFamily.UNKNOWN_FLOP_SPOT


def test_flop_context_contracts_exported_from_public_package() -> None:
    import solver_postflop

    for public_name in (
        "DEFAULT_FLOP_NEXT_MODULE",
        "FLOP_SPOT_FAMILIES",
        "FlopActionContext",
        "FlopContext",
        "FlopPlayerContext",
        "FlopPositionContext",
        "FlopPotContext",
        "FlopSpotFamily",
    ):
        assert public_name in solver_postflop.__all__
        assert hasattr(solver_postflop, public_name)
