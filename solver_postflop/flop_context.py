"""Build flop context objects from trusted SolverInput and branch metadata."""

from __future__ import annotations

from collections.abc import Mapping as MappingABC
from typing import Any, Mapping, Optional

from solver_postflop.branch_contracts import SolverBranch, SolverBranchResult
from solver_postflop.engine_contracts import SolverInput
from solver_postflop.flop_context_contracts import (
    DEFAULT_FLOP_NEXT_MODULE,
    FlopActionContext,
    FlopContext,
    FlopPlayerContext,
    FlopPositionContext,
    FlopPotContext,
    FlopSpotFamily,
)


def build_flop_context(solver_input: SolverInput, branch_result: SolverBranchResult) -> FlopContext:
    """Build baseline flop context from an already-routed flop SolverInput.

    This builder is a read-only grouping layer. It copies information already
    present in SolverInput/raw Clear JSON into FlopContext blocks without
    repairing cards, selecting seats, computing poker actions, or deriving a
    strategy. Spot-family classification is intentionally left as unknown in
    V0.5.2 and will be handled by the next subversion.
    """

    if _branch_value(branch_result.branch) != SolverBranch.FLOP.value:
        raise ValueError("FlopContext requires flop branch")

    raw_payload = solver_input.raw_clear_json_ref
    raw_mapping = raw_payload if isinstance(raw_payload, MappingABC) else {}

    context_fields_used: list[str] = []
    context_fields_not_provided: list[str] = []

    hero_cards = tuple(solver_input.hero_cards)
    board_cards = tuple(solver_input.board_cards)
    players = tuple(solver_input.players)
    allowed_actions = tuple(solver_input.allowed_actions)
    action_context_mapping = _as_mapping(solver_input.action_context)

    _mark_sequence_field("hero_cards", hero_cards, context_fields_used, context_fields_not_provided)
    _mark_sequence_field("board_cards", board_cards, context_fields_used, context_fields_not_provided)
    _mark_sequence_field("players", players, context_fields_used, context_fields_not_provided)
    _mark_scalar_field("pot", solver_input.pot, context_fields_used, context_fields_not_provided)
    _mark_scalar_field("to_call", solver_input.to_call, context_fields_used, context_fields_not_provided)
    _mark_sequence_field("allowed_actions", allowed_actions, context_fields_used, context_fields_not_provided)
    _mark_mapping_field("action_context", action_context_mapping, context_fields_used, context_fields_not_provided)

    hero_id = _first_available(raw_mapping, ("hero_id", "hero"))
    hero_position = _first_available(raw_mapping, ("hero_position",))
    if hero_position is None and hero_id is not None and isinstance(solver_input.positions, MappingABC):
        hero_position = solver_input.positions.get(str(hero_id))

    pot_type = _first_available(raw_mapping, ("pot_type",))
    preflop_context = raw_mapping.get("preflop_context") if isinstance(raw_mapping, MappingABC) else None
    if pot_type is None and isinstance(preflop_context, MappingABC):
        pot_type = preflop_context.get("pot_type")

    if hero_id is not None:
        context_fields_used.append("hero_id")
    else:
        context_fields_not_provided.append("hero_id")

    if hero_position is not None:
        context_fields_used.append("hero_position")
    else:
        context_fields_not_provided.append("hero_position")

    if pot_type is not None:
        context_fields_used.append("pot_type")
    else:
        context_fields_not_provided.append("pot_type")

    pot_context = _build_pot_context(
        pot=solver_input.pot,
        to_call=solver_input.to_call,
        pot_type=pot_type,
    )
    position_context = _build_position_context(hero_id=hero_id, hero_position=hero_position)
    action_context = _build_action_context(
        allowed_actions=allowed_actions,
        action_context_mapping=action_context_mapping,
    )
    player_context = _build_player_context(
        players=players,
        hero_id=hero_id,
        hero_position=hero_position,
    )

    context_fields_used.append("raw_clear_json_ref")
    context_fields_used = _dedupe(context_fields_used)
    context_fields_not_provided = _dedupe(context_fields_not_provided)

    return FlopContext(
        case_id=branch_result.case_id or _optional_str(raw_mapping.get("case_id")),
        source_file=branch_result.source_file,
        table_id=solver_input.table_id,
        hand_id=solver_input.hand_id,
        branch=SolverBranch.FLOP.value,
        spot_family=FlopSpotFamily.UNKNOWN_FLOP_SPOT,
        hero_cards=hero_cards,
        board_cards=board_cards,
        pot_context=pot_context,
        position_context=position_context,
        action_context=action_context,
        player_context=player_context,
        next_module=DEFAULT_FLOP_NEXT_MODULE,
        context_fields_used=tuple(context_fields_used),
        context_fields_not_provided=tuple(context_fields_not_provided),
        raw_clear_json_ref=raw_payload,
        notes=(
            "flop_context_builder_baseline_v0.5.2",
            "spot_family_classification_deferred_to_v0.5.3",
            "metadata_only_no_poker_decision",
        ),
    )


def _build_pot_context(pot: Any, to_call: Any, pot_type: Any) -> FlopPotContext:
    fields_used: list[str] = []
    fields_not_provided: list[str] = []

    _mark_scalar_field("pot", pot, fields_used, fields_not_provided)
    _mark_scalar_field("to_call", to_call, fields_used, fields_not_provided)
    _mark_scalar_field("pot_type", pot_type, fields_used, fields_not_provided)
    fields_not_provided.extend(["effective_stack", "spr"])

    return FlopPotContext(
        pot=pot,
        to_call=to_call,
        effective_stack=None,
        spr=None,
        pot_type=_optional_str(pot_type),
        fields_used=tuple(_dedupe(fields_used)),
        fields_not_provided=tuple(_dedupe(fields_not_provided)),
        notes=("effective_stack_and_spr_deferred",),
    )


def _build_position_context(hero_id: Any, hero_position: Any) -> FlopPositionContext:
    fields_used: list[str] = []
    fields_not_provided: list[str] = []

    _mark_scalar_field("hero_id", hero_id, fields_used, fields_not_provided)
    _mark_scalar_field("hero_position", hero_position, fields_used, fields_not_provided)
    fields_not_provided.extend(["is_in_position", "position_label"])

    return FlopPositionContext(
        hero_id=_optional_str(hero_id),
        hero_position=_optional_str(hero_position),
        is_in_position=None,
        position_label=None,
        fields_used=tuple(_dedupe(fields_used)),
        fields_not_provided=tuple(_dedupe(fields_not_provided)),
        notes=("position_classification_deferred",),
    )


def _build_action_context(
    allowed_actions: tuple[Any, ...],
    action_context_mapping: Mapping[str, Any],
) -> FlopActionContext:
    normalized_actions = tuple(str(action).lower() for action in allowed_actions)
    fields_used: list[str] = []
    fields_not_provided: list[str] = []

    _mark_sequence_field("allowed_actions", allowed_actions, fields_used, fields_not_provided)
    _mark_mapping_field("action_context", action_context_mapping, fields_used, fields_not_provided)

    current_actor = action_context_mapping.get("current_actor")
    facing_bet = action_context_mapping.get("facing_bet")
    facing_raise = action_context_mapping.get("facing_raise")
    action_context_label = _first_available(
        action_context_mapping,
        ("available_option", "facing_action", "action_context", "street"),
    )

    _mark_scalar_field("current_actor", current_actor, fields_used, fields_not_provided)
    _mark_scalar_field("facing_bet", facing_bet, fields_used, fields_not_provided)
    _mark_scalar_field("facing_raise", facing_raise, fields_used, fields_not_provided)

    has_allowed_actions = bool(normalized_actions)
    if has_allowed_actions:
        fields_used.extend(["can_check", "can_call", "can_bet", "can_raise"])
    else:
        fields_not_provided.extend(["can_check", "can_call", "can_bet", "can_raise"])

    return FlopActionContext(
        allowed_actions=allowed_actions,
        current_actor=_optional_str(current_actor),
        action_context_label=_optional_str(action_context_label),
        facing_bet=_optional_bool(facing_bet),
        facing_raise=_optional_bool(facing_raise),
        can_check=("check" in normalized_actions) if has_allowed_actions else None,
        can_call=("call" in normalized_actions) if has_allowed_actions else None,
        can_bet=("bet" in normalized_actions) if has_allowed_actions else None,
        can_raise=("raise" in normalized_actions) if has_allowed_actions else None,
        fields_used=tuple(_dedupe(fields_used)),
        fields_not_provided=tuple(_dedupe(fields_not_provided)),
        notes=("action_flags_derived_only_from_allowed_actions",),
    )


def _build_player_context(
    players: tuple[Any, ...],
    hero_id: Any,
    hero_position: Any,
) -> FlopPlayerContext:
    fields_used: list[str] = []
    fields_not_provided: list[str] = []

    _mark_sequence_field("players", players, fields_used, fields_not_provided)
    _mark_scalar_field("hero_id", hero_id, fields_used, fields_not_provided)
    _mark_scalar_field("hero_position", hero_position, fields_used, fields_not_provided)

    player_count = len(players)
    is_heads_up = player_count == 2 if player_count else None
    is_multiway = player_count > 2 if player_count else None
    if player_count:
        fields_used.extend(["is_heads_up", "is_multiway"])
    else:
        fields_not_provided.extend(["is_heads_up", "is_multiway"])

    return FlopPlayerContext(
        players=players,
        opponents=(),
        hero_id=_optional_str(hero_id),
        hero_position=_optional_str(hero_position),
        is_heads_up=is_heads_up,
        is_multiway=is_multiway,
        fields_used=tuple(_dedupe(fields_used)),
        fields_not_provided=tuple(_dedupe(fields_not_provided + ["opponents"])),
        notes=("players_copied_without_reselection", "opponents_derivation_deferred"),
    )


def _branch_value(branch: Any) -> str:
    if isinstance(branch, SolverBranch):
        return branch.value
    return str(branch)


def _first_available(mapping: Mapping[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return value
    return None


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, MappingABC):
        return value
    return {}


def _optional_str(value: Any) -> Optional[str]:
    if value in (None, ""):
        return None
    return str(value)


def _optional_bool(value: Any) -> Optional[bool]:
    if value is None:
        return None
    return bool(value)


def _mark_scalar_field(
    field_name: str,
    value: Any,
    fields_used: list[str],
    fields_not_provided: list[str],
) -> None:
    if value in (None, ""):
        fields_not_provided.append(field_name)
    else:
        fields_used.append(field_name)


def _mark_sequence_field(
    field_name: str,
    value: tuple[Any, ...],
    fields_used: list[str],
    fields_not_provided: list[str],
) -> None:
    if value:
        fields_used.append(field_name)
    else:
        fields_not_provided.append(field_name)


def _mark_mapping_field(
    field_name: str,
    value: Mapping[str, Any],
    fields_used: list[str],
    fields_not_provided: list[str],
) -> None:
    if value:
        fields_used.append(field_name)
    else:
        fields_not_provided.append(field_name)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
