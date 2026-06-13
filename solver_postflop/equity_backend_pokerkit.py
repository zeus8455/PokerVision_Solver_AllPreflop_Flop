"""PokerKit backend adapter for raw postflop equity snapshots.

V0.11.6 scope: first numeric heads-up raw equity result.
The adapter remains import-safe when PokerKit is absent and returns structured
backend data instead of raising into the solver pipeline.
"""

from __future__ import annotations

import importlib
import importlib.util
import itertools
import math
import time
from typing import Any, Iterable, Optional

from solver_postflop.equity_contracts import (
    DEFAULT_EQUITY_BACKEND_NAME,
    EquityBackendResult,
    EquityBackendStatus,
    EquityComputationMode,
    EquityConfidenceClass,
    EquityPlayerResult,
)

POKERKIT_BACKEND_ADAPTER_VERSION = "v0.11.6"
POKERKIT_PACKAGE_NAME = "pokerkit"
POKERKIT_NOT_INSTALLED_NOTE = "pokerkit_not_installed"
POKERKIT_CALCULATION_DEFERRED_NOTE = "pokerkit_backend_calculation_deferred_v0112"
POKERKIT_NUMERIC_HEADS_UP_NOTE = "pokerkit_numeric_heads_up_raw_equity_v0116"
POKERKIT_INPUT_NOT_READY_NOTE = "pokerkit_numeric_input_not_ready_v0116"
POKERKIT_MULTIWAY_DEFERRED_NOTE = "pokerkit_multiway_raw_equity_deferred_v0116"
DEFAULT_NUMERIC_SAMPLE_COUNT = 512
RANK_MAP = {
    "a": "A",
    "ace": "A",
    "k": "K",
    "king": "K",
    "q": "Q",
    "queen": "Q",
    "j": "J",
    "jack": "J",
    "t": "T",
    "ten": "T",
    "10": "T",
    "9": "9",
    "8": "8",
    "7": "7",
    "6": "6",
    "5": "5",
    "4": "4",
    "3": "3",
    "2": "2",
}
SUIT_MAP = {
    "s": "s",
    "spade": "s",
    "spades": "s",
    "h": "h",
    "heart": "h",
    "hearts": "h",
    "d": "d",
    "diamond": "d",
    "diamonds": "d",
    "c": "c",
    "club": "c",
    "clubs": "c",
}
DECK_RANKS = ("A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2")
DECK_SUITS = ("s", "h", "d", "c")
FULL_DECK_COMPACTS = tuple(f"{rank}{suit}" for rank in DECK_RANKS for suit in DECK_SUITS)


def is_pokerkit_available() -> bool:
    """Return True when the local Python environment can import PokerKit.

    The function uses importlib metadata discovery instead of a direct package
    import. This keeps module import safe in environments where PokerKit is
    absent.
    """
    return importlib.util.find_spec(POKERKIT_PACKAGE_NAME) is not None


def build_backend_unavailable_result(
    *,
    reason: str = POKERKIT_NOT_INSTALLED_NOTE,
    runtime_ms: Optional[float] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> EquityBackendResult:
    """Build a structured backend-unavailable result without raising."""
    backend_metadata = {
        "adapter_version": POKERKIT_BACKEND_ADAPTER_VERSION,
        "backend_available": False,
        "requires_local_install": True,
    }
    if metadata:
        backend_metadata.update(metadata)

    return EquityBackendResult(
        backend_name=DEFAULT_EQUITY_BACKEND_NAME,
        backend_status=EquityBackendStatus.UNAVAILABLE,
        computation_mode=EquityComputationMode.BACKEND_UNAVAILABLE,
        hero_equity=None,
        hero_win_rate=None,
        hero_tie_rate=None,
        player_results=(),
        sample_count_used=None,
        runtime_ms=runtime_ms,
        backend_metadata=backend_metadata,
        error_message=reason,
        notes=(reason,),
    )


def build_backend_error_result(
    *,
    error_message: str,
    runtime_ms: Optional[float] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> EquityBackendResult:
    """Build a structured backend-error result without breaking the pipeline."""
    backend_metadata = {
        "adapter_version": POKERKIT_BACKEND_ADAPTER_VERSION,
        "backend_available": is_pokerkit_available(),
    }
    if metadata:
        backend_metadata.update(metadata)

    return EquityBackendResult(
        backend_name=DEFAULT_EQUITY_BACKEND_NAME,
        backend_status=EquityBackendStatus.ERROR,
        computation_mode=EquityComputationMode.BACKEND_ERROR,
        hero_equity=None,
        hero_win_rate=None,
        hero_tie_rate=None,
        player_results=(),
        sample_count_used=None,
        runtime_ms=runtime_ms,
        backend_metadata=backend_metadata,
        error_message=error_message,
        notes=("pokerkit_backend_error",),
    )


def run_pokerkit_backend(
    scenario_input: Any,
    *,
    sample_count: Optional[int] = None,
) -> EquityBackendResult:
    """Run the PokerKit backend and return structured raw equity metadata.

    V0.11.6 implements numeric heads-up raw equity only. Multiway and
    incomplete contexts are represented as structured not-run results.
    """
    started = time.perf_counter()
    requested_sample_count = sample_count

    if not is_pokerkit_available():
        return build_backend_unavailable_result(
            runtime_ms=_elapsed_ms(started),
            metadata={
                "sample_count_requested": requested_sample_count,
                "scenario_case_id": _get_attr(scenario_input, "case_id"),
            },
        )

    try:
        pokerkit = importlib.import_module(POKERKIT_PACKAGE_NAME)
        hero_cards = _scenario_hero_cards(scenario_input)
        board_cards = _scenario_board_cards(scenario_input)
        opponents_count = _scenario_opponents_count(scenario_input)

        context_check = _raw_heads_up_context_check(
            hero_cards=hero_cards,
            board_cards=board_cards,
            opponents_count=opponents_count,
        )
        if context_check is not None:
            return _build_not_run_result(
                started=started,
                scenario_input=scenario_input,
                sample_count_requested=requested_sample_count,
                computation_mode=context_check["computation_mode"],
                note=context_check["note"],
                extra_metadata=context_check["metadata"],
            )

        sample_limit = _normalize_sample_count(requested_sample_count)
        numeric = _compute_heads_up_raw_equity(
            pokerkit=pokerkit,
            hero_cards=tuple(_compact_card(card) for card in hero_cards),
            board_cards=tuple(_compact_card(card) for card in board_cards),
            sample_limit=sample_limit,
        )

        player_result = EquityPlayerResult(
            player_id="hero",
            position=_get_attr(_get_attr(scenario_input, "hero"), "position"),
            role="hero",
            equity=numeric["hero_equity"],
            win_rate=numeric["hero_win_rate"],
            tie_rate=numeric["hero_tie_rate"],
            confidence=EquityConfidenceClass.LOW,
            notes=(POKERKIT_NUMERIC_HEADS_UP_NOTE,),
        )

        return EquityBackendResult(
            backend_name=DEFAULT_EQUITY_BACKEND_NAME,
            backend_status=EquityBackendStatus.OK,
            computation_mode=EquityComputationMode.HEADS_UP_RAW_EQUITY,
            hero_equity=numeric["hero_equity"],
            hero_win_rate=numeric["hero_win_rate"],
            hero_tie_rate=numeric["hero_tie_rate"],
            player_results=(player_result,),
            sample_count_used=numeric["sample_count_used"],
            runtime_ms=_elapsed_ms(started),
            backend_metadata={
                "adapter_version": POKERKIT_BACKEND_ADAPTER_VERSION,
                "backend_available": True,
                "sample_count_requested": requested_sample_count,
                "sample_count_normalized": sample_limit,
                "scenario_case_id": _get_attr(scenario_input, "case_id"),
                "opponents_count": opponents_count,
                "hero_compact": "".join(numeric["hero_cards"]),
                "board_compact": "".join(numeric["board_cards"]),
                "missing_board_cards": numeric["missing_board_cards"],
                "total_possibilities": numeric["total_possibilities"],
                "exact_enumeration": numeric["exact_enumeration"],
            },
            error_message=None,
            notes=tuple(numeric["notes"]),
        )
    except Exception as exc:  # pragma: no cover - defensive backend boundary
        return build_backend_error_result(
            error_message=f"{type(exc).__name__}: {exc}",
            runtime_ms=_elapsed_ms(started),
            metadata={
                "sample_count_requested": requested_sample_count,
                "scenario_case_id": _get_attr(scenario_input, "case_id"),
            },
        )


def _build_not_run_result(
    *,
    started: float,
    scenario_input: Any,
    sample_count_requested: Optional[int],
    computation_mode: EquityComputationMode,
    note: str,
    extra_metadata: Optional[dict[str, Any]] = None,
) -> EquityBackendResult:
    metadata = {
        "adapter_version": POKERKIT_BACKEND_ADAPTER_VERSION,
        "backend_available": True,
        "sample_count_requested": sample_count_requested,
        "scenario_case_id": _get_attr(scenario_input, "case_id"),
    }
    if extra_metadata:
        metadata.update(extra_metadata)
    return EquityBackendResult(
        backend_name=DEFAULT_EQUITY_BACKEND_NAME,
        backend_status=EquityBackendStatus.NOT_RUN,
        computation_mode=computation_mode,
        hero_equity=None,
        hero_win_rate=None,
        hero_tie_rate=None,
        player_results=(),
        sample_count_used=None,
        runtime_ms=_elapsed_ms(started),
        backend_metadata=metadata,
        error_message=None,
        notes=(note,),
    )


def _raw_heads_up_context_check(
    *,
    hero_cards: tuple[Any, ...],
    board_cards: tuple[Any, ...],
    opponents_count: Optional[int],
) -> Optional[dict[str, Any]]:
    metadata = {
        "hero_cards_count": len(hero_cards),
        "board_cards_count": len(board_cards),
        "opponents_count": opponents_count,
    }
    if opponents_count is None:
        return {
            "computation_mode": EquityComputationMode.UNKNOWN_CONTEXT_EQUITY,
            "note": POKERKIT_INPUT_NOT_READY_NOTE,
            "metadata": metadata,
        }
    if opponents_count != 1:
        return {
            "computation_mode": EquityComputationMode.MULTIWAY_RAW_EQUITY,
            "note": POKERKIT_MULTIWAY_DEFERRED_NOTE,
            "metadata": metadata,
        }
    if len(hero_cards) != 2:
        return {
            "computation_mode": EquityComputationMode.UNKNOWN_CONTEXT_EQUITY,
            "note": POKERKIT_INPUT_NOT_READY_NOTE,
            "metadata": metadata,
        }
    if len(board_cards) not in {3, 4, 5}:
        return {
            "computation_mode": EquityComputationMode.UNKNOWN_CONTEXT_EQUITY,
            "note": POKERKIT_INPUT_NOT_READY_NOTE,
            "metadata": metadata,
        }
    return None


def _compute_heads_up_raw_equity(
    *,
    pokerkit: Any,
    hero_cards: tuple[str, str],
    board_cards: tuple[str, ...],
    sample_limit: int,
) -> dict[str, Any]:
    known_cards = tuple(hero_cards) + tuple(board_cards)
    available_cards = tuple(card for card in FULL_DECK_COMPACTS if card not in set(known_cards))
    missing_board_cards = 5 - len(board_cards)
    opponent_combos = tuple(itertools.combinations(available_cards, 2))
    runout_count_per_opponent = math.comb(len(available_cards) - 2, missing_board_cards)
    total_possibilities = len(opponent_combos) * runout_count_per_opponent

    if total_possibilities <= 0:
        raise ValueError("no_raw_equity_possibilities")

    target_samples = min(total_possibilities, sample_limit)
    selected_indexes = _selected_index_set(total_possibilities, target_samples)
    exact_enumeration = target_samples == total_possibilities

    wins = 0
    ties = 0
    losses = 0
    sample_index = 0
    evaluated = 0
    hero_compact = "".join(hero_cards)

    for opponent_cards in opponent_combos:
        remaining_after_opponent = tuple(card for card in available_cards if card not in opponent_cards)
        for runout_cards in itertools.combinations(remaining_after_opponent, missing_board_cards):
            if sample_index not in selected_indexes:
                sample_index += 1
                continue
            final_board = tuple(board_cards) + tuple(runout_cards)
            board_compact = "".join(final_board)
            opponent_compact = "".join(opponent_cards)
            hero_hand = pokerkit.StandardHighHand.from_game(hero_compact, board_compact)
            opponent_hand = pokerkit.StandardHighHand.from_game(opponent_compact, board_compact)
            if hero_hand > opponent_hand:
                wins += 1
            elif hero_hand == opponent_hand:
                ties += 1
            else:
                losses += 1
            evaluated += 1
            sample_index += 1

    if evaluated <= 0:
        raise ValueError("raw_equity_sample_empty")

    win_rate = wins / evaluated
    tie_rate = ties / evaluated
    hero_equity = win_rate + (tie_rate / 2.0)
    notes = [POKERKIT_NUMERIC_HEADS_UP_NOTE]
    if exact_enumeration:
        notes.append("exact_raw_equity_enumeration")
    else:
        notes.append("sampled_raw_equity_enumeration")

    return {
        "hero_cards": hero_cards,
        "board_cards": board_cards,
        "missing_board_cards": missing_board_cards,
        "total_possibilities": total_possibilities,
        "exact_enumeration": exact_enumeration,
        "sample_count_used": evaluated,
        "hero_equity": round(hero_equity, 6),
        "hero_win_rate": round(win_rate, 6),
        "hero_tie_rate": round(tie_rate, 6),
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "notes": notes,
    }


def _selected_index_set(total_count: int, target_count: int) -> set[int]:
    if target_count >= total_count:
        return set(range(total_count))
    if target_count <= 1:
        return {0}
    return {
        int(round(index * (total_count - 1) / (target_count - 1)))
        for index in range(target_count)
    }


def _normalize_sample_count(sample_count: Optional[int]) -> int:
    if sample_count is None:
        return DEFAULT_NUMERIC_SAMPLE_COUNT
    if sample_count <= 0:
        return DEFAULT_NUMERIC_SAMPLE_COUNT
    return int(sample_count)


def _scenario_hero_cards(scenario_input: Any) -> tuple[Any, ...]:
    hero = _get_attr(scenario_input, "hero")
    return tuple(_get_attr(hero, "hero_cards") or ())


def _scenario_board_cards(scenario_input: Any) -> tuple[Any, ...]:
    board = _get_attr(scenario_input, "board")
    return tuple(_get_attr(board, "board_cards") or ())


def _scenario_opponents_count(scenario_input: Any) -> Optional[int]:
    opponents = _get_attr(scenario_input, "opponents")
    count = _get_attr(opponents, "opponents_count")
    if count is None:
        return None
    return int(count)


def _compact_card(card: Any) -> str:
    raw = str(card).strip()
    if not raw:
        raise ValueError("empty_card")
    normalized = raw.replace("-", "_").replace(" ", "_").lower()
    if "_" in normalized:
        rank_raw, suit_raw = normalized.split("_", 1)
    elif len(normalized) in {2, 3}:
        rank_raw = normalized[:-1]
        suit_raw = normalized[-1]
    else:
        raise ValueError("unsupported_card_format")
    rank = RANK_MAP.get(rank_raw)
    suit = SUIT_MAP.get(suit_raw)
    if rank is None or suit is None:
        raise ValueError("unsupported_card_token")
    return f"{rank}{suit}"


def _elapsed_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000.0, 6)


def _get_attr(value: Any, name: str) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name, None)


__all__ = (
    "DEFAULT_NUMERIC_SAMPLE_COUNT",
    "POKERKIT_BACKEND_ADAPTER_VERSION",
    "POKERKIT_CALCULATION_DEFERRED_NOTE",
    "POKERKIT_INPUT_NOT_READY_NOTE",
    "POKERKIT_MULTIWAY_DEFERRED_NOTE",
    "POKERKIT_NOT_INSTALLED_NOTE",
    "POKERKIT_NUMERIC_HEADS_UP_NOTE",
    "POKERKIT_PACKAGE_NAME",
    "build_backend_error_result",
    "build_backend_unavailable_result",
    "is_pokerkit_available",
    "run_pokerkit_backend",
)
