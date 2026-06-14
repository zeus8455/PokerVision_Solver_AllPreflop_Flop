"""First blocker filtering engine for postflop combo availability.

V0.13.3 scope: convert an existing RangeState plus already-known HERO and
board cards into AvailableComboState. This module treats Clear_JSON-derived
cards as trusted poker blockers only. It does not validate card correctness,
repair player state, rebuild ranges, narrow ranges by action, recalculate
equity, create a decision, create a runtime plan, or click.
"""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any, Iterable, Mapping, Optional

from solver_postflop.combo_contracts import (
    AvailableComboState,
    BlockedComboReason,
    ComboAvailabilityStatus,
    ComboBlockerResult,
    ComboGroupAvailability,
    PlayerComboState,
)
from solver_postflop.combo_state import detect_combo_blockers, normalize_cards, parse_compact_combo
from solver_postflop.range_contracts import PlayerRangeState, RangeState


BLOCKER_FILTERING_VERSION = "v0.13.3"
ARCHITECTURE_FLAGS: Mapping[str, bool] = {
    "available_combo_state_created": True,
    "range_state_mutated": False,
    "clear_json_validation_executed": False,
    "card_collision_check_executed": False,
    "player_filtering_executed": False,
    "range_rebuild_executed": False,
    "range_creation_executed": False,
    "range_narrowing_executed": False,
    "equity_recalculation_executed": False,
    "decision_logic_executed": False,
    "runtime_plan_created": False,
    "physical_click_executed": False,
}

__all__ = (
    "ARCHITECTURE_FLAGS",
    "BLOCKER_FILTERING_VERSION",
    "build_available_combo_state",
    "filter_range_state_blocked_combos",
)


def build_available_combo_state(
    range_state: RangeState,
    *,
    hero_cards: Iterable[Any] | None = None,
    board_cards: Iterable[Any] | None = None,
    case_id: Optional[str] = None,
    source_file: Optional[str] = None,
) -> AvailableComboState:
    """Build an AvailableComboState from an existing RangeState.

    The function is intentionally read-only with respect to ``range_state``.
    It uses parsed HERO/board cards as blockers against each PlayerRangeState's
    existing combo_groups. Unsupported combo strings are excluded from available
    combos in a structured way instead of raising.
    """

    normalized_hero_cards = normalize_cards(hero_cards)
    normalized_board_cards = normalize_cards(board_cards)

    player_ranges = _iter_player_ranges(range_state)
    player_combo_states = tuple(
        _build_player_combo_state(
            player_range,
            hero_cards=normalized_hero_cards,
            board_cards=normalized_board_cards,
        )
        for player_range in player_ranges
    )

    total_before = sum(player.combo_count_before for player in player_combo_states)
    total_available = sum(player.combo_count_available for player in player_combo_states)
    total_blocked = sum(player.combo_count_blocked for player in player_combo_states)
    total_blocked_by_hero = sum(player.blocked_by_hero_count for player in player_combo_states)
    total_blocked_by_board = sum(player.blocked_by_board_count for player in player_combo_states)
    total_blocked_by_both = sum(player.blocked_by_hero_and_board_count for player in player_combo_states)

    fields_not_provided: list[str] = []
    if not normalized_hero_cards:
        fields_not_provided.append("hero_cards")
    if not normalized_board_cards:
        fields_not_provided.append("board_cards")

    return AvailableComboState(
        case_id=case_id if case_id is not None else range_state.case_id,
        source_file=source_file if source_file is not None else range_state.source_file,
        spot_family=range_state.spot_family,
        hero_cards_used_as_blockers=normalized_hero_cards,
        board_cards_used_as_blockers=normalized_board_cards,
        player_combo_states=player_combo_states,
        total_combo_count_before=total_before,
        total_combo_count_available=total_available,
        total_combo_count_blocked=total_blocked,
        total_combo_count_blocked_by_hero=total_blocked_by_hero,
        total_combo_count_blocked_by_board=total_blocked_by_board,
        total_combo_count_blocked_by_hero_and_board=total_blocked_by_both,
        availability_status=_availability_status(total_before, total_available, total_blocked),
        range_source_info=_to_mapping(range_state.range_source_info),
        next_module="flop_action_model_later",
        fields_used=(
            "range_state",
            "range_state.hero_range_state",
            "range_state.opponent_range_states",
            "player_range_state.combo_groups",
            "hero_cards",
            "board_cards",
        ),
        fields_not_provided=tuple(fields_not_provided),
        notes=(
            "v0133_first_blocker_filtering_engine",
            "hero_and_board_cards_used_as_poker_blockers_only",
            "range_state_read_only",
            "no_range_narrowing",
            "no_equity_recalculation",
            "no_decision_runtime_click",
        ),
    )


def filter_range_state_blocked_combos(
    range_state: RangeState,
    *,
    hero_cards: Iterable[Any] | None = None,
    board_cards: Iterable[Any] | None = None,
    case_id: Optional[str] = None,
    source_file: Optional[str] = None,
) -> AvailableComboState:
    """Alias for build_available_combo_state with explicit filtering wording."""

    return build_available_combo_state(
        range_state,
        hero_cards=hero_cards,
        board_cards=board_cards,
        case_id=case_id,
        source_file=source_file,
    )


def _iter_player_ranges(range_state: RangeState) -> tuple[PlayerRangeState, ...]:
    player_ranges: list[PlayerRangeState] = []
    if range_state.hero_range_state is not None:
        player_ranges.append(range_state.hero_range_state)
    player_ranges.extend(range_state.opponent_range_states)
    return tuple(player_ranges)


def _build_player_combo_state(
    player_range: PlayerRangeState,
    *,
    hero_cards: tuple[str, ...],
    board_cards: tuple[str, ...],
) -> PlayerComboState:
    available_groups: dict[str, tuple[str, ...]] = {}
    blocked_groups: dict[str, tuple[str, ...]] = {}
    group_availability: list[ComboGroupAvailability] = []
    blocker_results: list[ComboBlockerResult] = []

    for bucket_name, raw_combos in player_range.combo_groups.items():
        bucket = str(bucket_name)
        available_in_bucket: list[str] = []
        blocked_in_bucket: list[str] = []

        for raw_combo in tuple(raw_combos):
            result = _evaluate_combo(bucket, raw_combo, hero_cards=hero_cards, board_cards=board_cards)
            blocker_results.append(result)
            if result.is_available:
                available_in_bucket.append(result.combo)
            else:
                blocked_in_bucket.append(result.combo)

        if available_in_bucket:
            available_groups[bucket] = tuple(available_in_bucket)
        if blocked_in_bucket:
            blocked_groups[bucket] = tuple(blocked_in_bucket)
        group_availability.append(
            ComboGroupAvailability(
                bucket_name=bucket,
                combo_count_before=len(tuple(raw_combos)),
                combo_count_available=len(available_in_bucket),
                combo_count_blocked=len(blocked_in_bucket),
                available_combos=tuple(available_in_bucket),
                blocked_combos=tuple(blocked_in_bucket),
                notes=("bucket_structure_preserved",),
            )
        )

    combo_count_before = len(blocker_results)
    combo_count_available = sum(1 for result in blocker_results if result.is_available)
    combo_count_blocked = combo_count_before - combo_count_available
    blocked_by_hero = sum(
        1
        for result in blocker_results
        if result.blocked_reason
        in (BlockedComboReason.BLOCKED_BY_HERO_CARD, BlockedComboReason.BLOCKED_BY_HERO_AND_BOARD)
    )
    blocked_by_board = sum(
        1
        for result in blocker_results
        if result.blocked_reason
        in (BlockedComboReason.BLOCKED_BY_BOARD_CARD, BlockedComboReason.BLOCKED_BY_HERO_AND_BOARD)
    )
    blocked_by_both = sum(
        1 for result in blocker_results if result.blocked_reason is BlockedComboReason.BLOCKED_BY_HERO_AND_BOARD
    )

    return PlayerComboState(
        player_id=player_range.player_id,
        position=player_range.position,
        range_name=player_range.range_name,
        combo_count_before=combo_count_before,
        combo_count_available=combo_count_available,
        combo_count_blocked=combo_count_blocked,
        blocked_by_hero_count=blocked_by_hero,
        blocked_by_board_count=blocked_by_board,
        blocked_by_hero_and_board_count=blocked_by_both,
        available_combo_groups=available_groups,
        blocked_combo_groups=blocked_groups,
        combo_group_availability=tuple(group_availability),
        blocker_results=tuple(blocker_results),
        availability_status=_availability_status(combo_count_before, combo_count_available, combo_count_blocked),
        availability_confidence=_enum_value(player_range.confidence),
        notes=(
            "player_combo_state_from_range_state",
            "combo_groups_filtered_by_hero_and_board_blockers",
            "player_range_state_read_only",
        ),
    )


def _evaluate_combo(
    bucket_name: str,
    raw_combo: Any,
    *,
    hero_cards: tuple[str, ...],
    board_cards: tuple[str, ...],
) -> ComboBlockerResult:
    parsed_combo = parse_compact_combo(raw_combo)
    if not parsed_combo.is_parseable:
        return ComboBlockerResult(
            combo=str(raw_combo),
            bucket_name=bucket_name,
            combo_cards=tuple(),
            blocked_reason=BlockedComboReason.NOT_BLOCKED,
            is_available=False,
            notes=("combo_unparseable_excluded_from_available_state",),
        )

    match = detect_combo_blockers(parsed_combo.normalized_combo, hero_cards=hero_cards, board_cards=board_cards)
    is_available = match.blocked_reason is BlockedComboReason.NOT_BLOCKED
    return ComboBlockerResult(
        combo=parsed_combo.normalized_combo or str(raw_combo),
        bucket_name=bucket_name,
        combo_cards=parsed_combo.combo_cards,
        blocked_reason=match.blocked_reason,
        is_available=is_available,
        blocking_hero_cards=match.hero_blocker_cards,
        blocking_board_cards=match.board_blocker_cards,
        notes=("combo_available" if is_available else "combo_blocked_by_known_cards",),
    )


def _availability_status(
    total_before: int,
    total_available: int,
    total_blocked: int,
) -> ComboAvailabilityStatus:
    if total_before <= 0:
        return ComboAvailabilityStatus.UNKNOWN
    if total_available == total_before and total_blocked == 0:
        return ComboAvailabilityStatus.AVAILABLE
    if total_available == 0:
        return ComboAvailabilityStatus.FULLY_BLOCKED
    return ComboAvailabilityStatus.PARTIALLY_BLOCKED


def _enum_value(value: Any) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    if value is None:
        return "unknown"
    return str(value)


def _to_mapping(value: Any) -> dict[str, Any]:
    if hasattr(value, "to_json_dict"):
        return value.to_json_dict()
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    return {}


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
