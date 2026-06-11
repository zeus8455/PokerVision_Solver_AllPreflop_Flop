from __future__ import annotations

import copy

from solver_postflop import (
    FlopSpotFamily,
    SolverBranch,
    build_flop_context,
    build_solver_input,
    classify_flop_spot_family,
    load_clear_json_input,
    resolve_solver_branch,
)
from solver_postflop.engine_contracts import ClearJsonInput


def _clear_input_from_payload(payload: dict) -> ClearJsonInput:
    return ClearJsonInput(
        source_file=f"{payload.get('case_id', 'in_memory')}.clear.json",
        raw_data=payload,
        loaded_at="2026-06-11T00:00:00+00:00",
        case_id=payload.get("case_id"),
        hand_id=payload.get("hand_id"),
        table_id=payload.get("table_id"),
    )


def _base_payload(**overrides):  # noqa: ANN003
    payload = {
        "case_id": "flop_spot_family_case",
        "table_id": "table_01",
        "hand_id": "hand_flop_spot_family",
        "hero_cards": ["As", "Kh"],
        "board_cards": ["7c", "2d", "Jh"],
        "players": [
            {"player_id": "hero", "position": "BB", "is_hero": True, "folded": False},
            {"player_id": "villain_btn", "position": "BTN", "is_hero": False, "folded": False},
        ],
        "allowed_actions": ["check", "bet"],
        "action_context": {"street": "flop", "current_actor": "hero", "available_option": "check_option"},
        "pot_type": "srp",
        "preflop_context": {"pot_type": "srp", "hero_preflop_role": "bb_defender"},
    }
    payload.update(overrides)
    return payload


def _context_from_payload(payload: dict):
    clear_input = _clear_input_from_payload(payload)
    solver_input, solver_trace = build_solver_input(clear_input)
    branch_result = resolve_solver_branch(solver_input, solver_trace)
    assert branch_result.branch == SolverBranch.FLOP
    return clear_input, solver_input, branch_result, build_flop_context(solver_input, branch_result)


def test_srp_heads_up_spot_family_from_explicit_pot_type() -> None:
    _clear_input, solver_input, _branch_result, context = _context_from_payload(_base_payload())

    assert classify_flop_spot_family(solver_input) == FlopSpotFamily.SRP_HEADS_UP
    assert context.spot_family == FlopSpotFamily.SRP_HEADS_UP
    assert "spot_family_context" in context.context_fields_used


def test_threebet_pot_heads_up_spot_family_from_preflop_context() -> None:
    payload = _base_payload(
        pot_type="3bet_pot",
        preflop_context={"pot_type": "3bet_pot", "preflop_aggressor": "hero"},
    )
    _clear_input, solver_input, _branch_result, context = _context_from_payload(payload)

    assert classify_flop_spot_family(solver_input) == FlopSpotFamily.THREEBET_POT_HEADS_UP
    assert context.spot_family == FlopSpotFamily.THREEBET_POT_HEADS_UP


def test_fourbet_low_spr_spot_family_from_explicit_context() -> None:
    payload = _base_payload(
        pot_type="4bet_pot",
        preflop_context={"pot_type": "4bet_pot", "spr_context": "low_spr"},
    )
    _clear_input, solver_input, _branch_result, context = _context_from_payload(payload)

    assert classify_flop_spot_family(solver_input) == FlopSpotFamily.FOURBET_LOW_SPR
    assert context.spot_family == FlopSpotFamily.FOURBET_LOW_SPR


def test_limp_or_passive_pot_spot_family_from_explicit_context() -> None:
    payload = _base_payload(
        pot_type="limp_pot",
        preflop_context={"pot_type": "limp_pot", "preflop_line": "limped_passive_pot"},
    )
    _clear_input, solver_input, _branch_result, context = _context_from_payload(payload)

    assert classify_flop_spot_family(solver_input) == FlopSpotFamily.LIMP_OR_PASSIVE_POT
    assert context.spot_family == FlopSpotFamily.LIMP_OR_PASSIVE_POT


def test_multiway_pot_spot_family_from_player_shape_without_filtering() -> None:
    players = [
        {"player_id": "hero", "position": "BB", "is_hero": True, "folded": False},
        {"player_id": "villain_btn", "position": "BTN", "is_hero": False, "folded": False},
        {"player_id": "villain_co", "position": "CO", "is_hero": False, "folded": False},
    ]
    payload = _base_payload(players=players, pot_type="srp")
    _clear_input, solver_input, _branch_result, context = _context_from_payload(payload)

    assert classify_flop_spot_family(solver_input) == FlopSpotFamily.MULTIWAY_POT
    assert context.spot_family == FlopSpotFamily.MULTIWAY_POT
    assert context.player_context.players == solver_input.players
    assert context.player_context.players[2] is solver_input.players[2]


def test_unknown_flop_spot_when_context_is_not_provided() -> None:
    payload = _base_payload(pot_type=None, preflop_context={}, action_context={})
    payload.pop("pot_type")
    payload.pop("preflop_context")
    _clear_input, solver_input, _branch_result, context = _context_from_payload(payload)

    assert classify_flop_spot_family(solver_input) == FlopSpotFamily.UNKNOWN_FLOP_SPOT
    assert context.spot_family == FlopSpotFamily.UNKNOWN_FLOP_SPOT
    assert "spot_family_context" in context.context_fields_not_provided


def test_spot_family_classifier_uses_only_solver_input_and_clear_json_context() -> None:
    payload = _base_payload(
        case_id="classifier_readonly_case",
        pot_type="3bet_pot",
        preflop_context={"pot_type": "3bet_pot", "preflop_aggressor": "hero"},
    )
    original_payload = copy.deepcopy(payload)
    clear_input, solver_input, branch_result, context = _context_from_payload(payload)

    assert payload == original_payload
    assert clear_input.raw_data == original_payload
    assert solver_input.raw_clear_json_ref == original_payload
    assert context.raw_clear_json_ref is solver_input.raw_clear_json_ref
    assert branch_result.branch == SolverBranch.FLOP


def test_real_flop_fixture_is_classified_as_srp_heads_up() -> None:
    clear_input = load_clear_json_input(
        "tests/fixtures/postflop_clear_json/real/flop/real_flop_srp_btn_vs_bb_check_option.clear.json"
    )
    solver_input, solver_trace = build_solver_input(clear_input)
    branch_result = resolve_solver_branch(solver_input, solver_trace)
    context = build_flop_context(solver_input, branch_result)

    assert context.spot_family == FlopSpotFamily.SRP_HEADS_UP
    assert context.player_context.is_heads_up is True
    assert context.pot_context.pot_type == "srp"


def test_spot_family_classifier_exported_from_public_package() -> None:
    import solver_postflop

    assert "classify_flop_spot_family" in solver_postflop.__all__
    assert hasattr(solver_postflop, "classify_flop_spot_family")
