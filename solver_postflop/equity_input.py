"""Builder for postflop equity input scenarios.

V0.10.2 scope:
    FlopContext + BoardTextureFeatures + MadeHandFeatures + DrawFeatures
    -> EquityScenarioInput

This module is a metadata adapter only. It does not evaluate cards, create
players, choose poker actions, or execute any external backend.
"""
from __future__ import annotations

from dataclasses import is_dataclass, asdict
from enum import Enum
from typing import Any, Mapping, Optional

from .board_texture_contracts import BoardTextureFeatures
from .equity_input_contracts import (
    DEFAULT_EQUITY_INPUT_NEXT_MODULE,
    EquityBoardInput,
    EquityHeroInput,
    EquityOpponentModelInput,
    EquityRunMode,
    EquityScenarioInput,
)
from .flop_context_contracts import FlopContext, FlopSpotFamily
from .hero_draw_contracts import DrawFeatures
from .hero_made_hand_contracts import MadeHandFeatures


EQUITY_INPUT_BUILDER_VERSION = "v0.10.2"
EQUITY_INPUT_BUILDER_NEXT_MODULE = DEFAULT_EQUITY_INPUT_NEXT_MODULE


def build_equity_scenario_input(
    *,
    flop_context: FlopContext,
    board_texture_features: BoardTextureFeatures,
    made_hand_features: MadeHandFeatures,
    draw_features: DrawFeatures,
    force_range_based_later: bool = False,
) -> EquityScenarioInput:
    """Build a future equity scenario from already-produced flop-chain objects.

    The builder only copies and reshapes trusted upstream metadata. Opponent
    count is derived from existing FlopPlayerContext fields only.
    """
    fields_used: list[str] = []
    fields_not_provided: list[str] = []
    notes: list[str] = ["equity_input_builder_metadata_only"]

    hero = _build_hero_input(flop_context, fields_used, fields_not_provided)
    board = _build_board_input(
        flop_context=flop_context,
        board_texture_features=board_texture_features,
        fields_used=fields_used,
        fields_not_provided=fields_not_provided,
    )
    opponents = _build_opponents_input(
        flop_context=flop_context,
        fields_used=fields_used,
        fields_not_provided=fields_not_provided,
    )
    run_mode = _select_equity_run_mode(
        flop_context=flop_context,
        opponents=opponents,
        force_range_based_later=force_range_based_later,
    )

    if run_mode is EquityRunMode.UNKNOWN_CONTEXT_MODE:
        notes.append("unknown_context_mode_selected_without_creating_opponents")
    elif run_mode is EquityRunMode.RANGE_BASED_LATER:
        notes.append("range_based_later_selected_by_explicit_builder_flag")

    pot_context = flop_context.pot_context
    if pot_context.pot is not None:
        fields_used.append("flop_context.pot_context.pot")
    else:
        fields_not_provided.append("pot")

    if pot_context.to_call is not None:
        fields_used.append("flop_context.pot_context.to_call")
    else:
        fields_not_provided.append("to_call")

    if pot_context.effective_stack is not None:
        fields_used.append("flop_context.pot_context.effective_stack")
    else:
        fields_not_provided.append("effective_stack")

    if pot_context.spr is not None:
        fields_used.append("flop_context.pot_context.spr")
    else:
        fields_not_provided.append("spr")

    return EquityScenarioInput(
        case_id=flop_context.case_id,
        source_file=flop_context.source_file,
        hero=hero,
        board=board,
        opponents=opponents,
        spot_family=_enum_value(flop_context.spot_family),
        pot=pot_context.pot,
        to_call=pot_context.to_call,
        effective_stack=pot_context.effective_stack,
        spr=pot_context.spr,
        position_context=_to_json_mapping(flop_context.position_context),
        action_context=_to_json_mapping(flop_context.action_context),
        board_texture_features=_to_json_mapping(board_texture_features),
        made_hand_features=_to_json_mapping(made_hand_features),
        draw_features=_to_json_mapping(draw_features),
        equity_run_mode=run_mode,
        next_module=EQUITY_INPUT_BUILDER_NEXT_MODULE,
        fields_used=_dedupe_tuple(fields_used),
        fields_not_provided=_dedupe_tuple(fields_not_provided),
        notes=_dedupe_tuple(notes),
    )


def _build_hero_input(
    flop_context: FlopContext,
    fields_used: list[str],
    fields_not_provided: list[str],
) -> EquityHeroInput:
    if flop_context.hero_cards:
        fields_used.append("flop_context.hero_cards")
    else:
        fields_not_provided.append("hero_cards")

    position = flop_context.position_context.hero_position
    if position is not None:
        fields_used.append("flop_context.position_context.hero_position")
    else:
        fields_not_provided.append("hero_position")

    effective_stack = flop_context.pot_context.effective_stack
    if effective_stack is not None:
        fields_used.append("flop_context.pot_context.effective_stack")
    else:
        fields_not_provided.append("effective_stack")

    return EquityHeroInput(
        hero_cards=tuple(flop_context.hero_cards),
        position=position,
        stack=None,
        effective_stack=effective_stack,
        notes=("hero_stack_not_provided_by_flop_context",),
    )


def _build_board_input(
    *,
    flop_context: FlopContext,
    board_texture_features: BoardTextureFeatures,
    fields_used: list[str],
    fields_not_provided: list[str],
) -> EquityBoardInput:
    if flop_context.board_cards:
        fields_used.append("flop_context.board_cards")
    else:
        fields_not_provided.append("board_cards")

    texture_tags = tuple(board_texture_features.texture_tags)
    if texture_tags:
        fields_used.append("board_texture_features.texture_tags")
    else:
        fields_not_provided.append("board_texture_features.texture_tags")

    fields_used.extend(
        [
            "board_texture_features.paired_texture",
            "board_texture_features.suit_texture",
            "board_texture_features.connection_texture",
        ]
    )

    return EquityBoardInput(
        board_cards=tuple(flop_context.board_cards),
        street="flop",
        texture_tags=texture_tags,
        paired_status=_enum_value(board_texture_features.paired_texture),
        suit_structure=_enum_value(board_texture_features.suit_texture),
        straight_structure=_enum_value(board_texture_features.connection_texture),
        notes=("board_cards_carried_from_flop_context",),
    )


def _build_opponents_input(
    *,
    flop_context: FlopContext,
    fields_used: list[str],
    fields_not_provided: list[str],
) -> EquityOpponentModelInput:
    player_context = flop_context.player_context
    known_opponents = tuple(_to_plain_dict(item) for item in player_context.opponents)
    opponent_positions = tuple(
        str(item["position"])
        for item in known_opponents
        if item.get("position") not in (None, "")
    )

    opponents_count: Optional[int]
    if known_opponents:
        opponents_count = len(known_opponents)
        fields_used.append("flop_context.player_context.opponents")
    elif player_context.is_heads_up is True:
        opponents_count = 1
        fields_used.append("flop_context.player_context.is_heads_up")
    else:
        opponents_count = None
        fields_not_provided.append("opponents_count")

    is_heads_up = player_context.is_heads_up
    is_multiway = player_context.is_multiway

    if is_heads_up is None and opponents_count is not None:
        is_heads_up = opponents_count == 1
    if is_multiway is None and opponents_count is not None:
        is_multiway = opponents_count > 1

    if is_heads_up is not None:
        fields_used.append("flop_context.player_context.is_heads_up")
    else:
        fields_not_provided.append("is_heads_up")

    if is_multiway is not None:
        fields_used.append("flop_context.player_context.is_multiway")
    else:
        fields_not_provided.append("is_multiway")

    range_model_status = (
        "unknown_context" if opponents_count is None else "range_based_later"
    )

    return EquityOpponentModelInput(
        opponents_count=opponents_count,
        is_heads_up=is_heads_up,
        is_multiway=is_multiway,
        known_opponents=known_opponents,
        opponent_positions=opponent_positions,
        range_model_status=range_model_status,
        notes=("opponents_carried_from_existing_player_context_only",),
    )


def _select_equity_run_mode(
    *,
    flop_context: FlopContext,
    opponents: EquityOpponentModelInput,
    force_range_based_later: bool,
) -> EquityRunMode:
    if force_range_based_later:
        return EquityRunMode.RANGE_BASED_LATER

    if opponents.opponents_count == 1 or opponents.is_heads_up is True:
        return EquityRunMode.HEADS_UP_EXACT_OR_SAMPLED

    if opponents.opponents_count is not None and opponents.opponents_count > 1:
        return EquityRunMode.MULTIWAY_SAMPLED

    if opponents.is_multiway is True and opponents.opponents_count is not None:
        return EquityRunMode.MULTIWAY_SAMPLED

    if _enum_value(flop_context.spot_family) == FlopSpotFamily.UNKNOWN_FLOP_SPOT.value:
        return EquityRunMode.UNKNOWN_CONTEXT_MODE

    return EquityRunMode.UNKNOWN_CONTEXT_MODE


def _to_json_mapping(value: Any) -> dict[str, Any]:
    if hasattr(value, "to_json_dict"):
        mapped = value.to_json_dict()
        return dict(mapped) if isinstance(mapped, Mapping) else {"value": mapped}

    if is_dataclass(value):
        return _json_safe(asdict(value))

    if isinstance(value, Mapping):
        return _json_safe(dict(value))

    return {"value": _json_safe(value)}


def _to_plain_dict(value: Mapping[str, Any]) -> dict[str, Any]:
    return _json_safe(dict(value))


def _json_safe(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def _enum_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    return value


def _dedupe_tuple(items: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            output.append(item)
    return tuple(output)


__all__ = (
    "EQUITY_INPUT_BUILDER_NEXT_MODULE",
    "EQUITY_INPUT_BUILDER_VERSION",
    "build_equity_scenario_input",
)
