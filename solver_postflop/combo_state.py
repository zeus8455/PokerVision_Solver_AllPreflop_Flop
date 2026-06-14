"""Card and combo parser helpers for postflop combo-state work.

V0.13.2 scope: parse compact cards/combos and identify whether one combo
contains already-known HERO or board cards. This module does not create
AvailableComboState, does not iterate RangeState groups, does not validate
Clear_JSON, does not repair card data, and does not build decisions or runtime
plans.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
import re
from typing import Any, Iterable, Mapping, Optional

from solver_postflop.combo_contracts import BlockedComboReason


class CardParseStatus(str, Enum):
    """Syntax-level status for a single card token."""

    PARSED = "parsed"
    EMPTY = "empty"
    UNRECOGNIZED = "unrecognized"


class ComboParseStatus(str, Enum):
    """Syntax-level status for a two-card combo token."""

    PARSED = "parsed"
    EMPTY = "empty"
    MALFORMED = "malformed"


@dataclass(frozen=True, slots=True)
class CardParseResult:
    """JSON-safe single-card parse result.

    This is a syntax helper, not a poker-deck validator. It does not check
    whether the card conflicts with HERO, board, or another source field.
    """

    raw_card: Any
    normalized_card: Optional[str] = None
    status: CardParseStatus = CardParseStatus.UNRECOGNIZED
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_parseable(self) -> bool:
        return self.status is CardParseStatus.PARSED and self.normalized_card is not None

    def to_json_dict(self) -> dict[str, Any]:
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class ComboParseResult:
    """JSON-safe compact combo parse result."""

    raw_combo: Any
    normalized_combo: Optional[str] = None
    combo_cards: tuple[str, ...] = field(default_factory=tuple)
    status: ComboParseStatus = ComboParseStatus.MALFORMED
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_parseable(self) -> bool:
        return self.status is ComboParseStatus.PARSED and len(self.combo_cards) == 2

    def to_json_dict(self) -> dict[str, Any]:
        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class ComboBlockerMatch:
    """Single-combo blocker match result.

    The result tells later modules which known cards are present inside one
    parsed combo. It does not remove the combo from a player range by itself.
    """

    combo: str
    combo_cards: tuple[str, ...] = field(default_factory=tuple)
    hero_blocker_cards: tuple[str, ...] = field(default_factory=tuple)
    board_blocker_cards: tuple[str, ...] = field(default_factory=tuple)
    blocked_reason: BlockedComboReason = BlockedComboReason.NOT_BLOCKED
    parse_status: ComboParseStatus = ComboParseStatus.MALFORMED
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_blocked(self) -> bool:
        return self.blocked_reason is not BlockedComboReason.NOT_BLOCKED

    def to_json_dict(self) -> dict[str, Any]:
        return _json_safe(asdict(self))


RANK_ALIASES: Mapping[str, str] = {
    "A": "A",
    "ACE": "A",
    "K": "K",
    "KING": "K",
    "Q": "Q",
    "QUEEN": "Q",
    "J": "J",
    "JACK": "J",
    "T": "T",
    "10": "T",
    "TEN": "T",
    "9": "9",
    "NINE": "9",
    "8": "8",
    "EIGHT": "8",
    "7": "7",
    "SEVEN": "7",
    "6": "6",
    "SIX": "6",
    "5": "5",
    "FIVE": "5",
    "4": "4",
    "FOUR": "4",
    "3": "3",
    "THREE": "3",
    "2": "2",
    "TWO": "2",
}

SUIT_ALIASES: Mapping[str, str] = {
    "S": "s",
    "SPADE": "s",
    "SPADES": "s",
    "H": "h",
    "HEART": "h",
    "HEARTS": "h",
    "D": "d",
    "DIAMOND": "d",
    "DIAMONDS": "d",
    "C": "c",
    "CLUB": "c",
    "CLUBS": "c",
}

COMBO_STATE_VERSION = "v0.13.2"
COMPACT_CARD_PATTERN = re.compile(r"^(10|[AKQJT2-9])([SHDC])$", re.IGNORECASE)
PROJECT_CARD_PATTERN = re.compile(
    r"^(10|[AKQJT2-9]|ace|king|queen|jack|ten|nine|eight|seven|six|five|four|three|two)[_\-\s]+"
    r"(spades?|hearts?|diamonds?|clubs?|[shdc])$",
    re.IGNORECASE,
)
COMBO_SEPARATOR_PATTERN = re.compile(r"[\s,|/]+")
ARCHITECTURE_FLAGS: Mapping[str, bool] = {
    "available_combo_state_created": False,
    "range_state_mutated": False,
    "clear_json_validation_executed": False,
    "player_filtering_executed": False,
    "range_narrowing_executed": False,
    "equity_recalculation_executed": False,
    "decision_logic_executed": False,
    "runtime_plan_created": False,
    "physical_click_executed": False,
}

__all__ = (
    "ARCHITECTURE_FLAGS",
    "COMBO_STATE_VERSION",
    "CardParseResult",
    "CardParseStatus",
    "ComboBlockerMatch",
    "ComboParseResult",
    "ComboParseStatus",
    "combo_contains_any_card",
    "detect_combo_blockers",
    "normalize_card",
    "normalize_cards",
    "parse_compact_combo",
)


def normalize_card(raw_card: Any) -> CardParseResult:
    """Normalize one supported card token to compact form like ``As``.

    Supported examples: ``As``, ``10s``, ``A_spades``, ``10_spades``,
    ``K_hearts``. Unsupported input returns a structured result instead of
    raising.
    """

    if raw_card is None:
        return CardParseResult(raw_card=raw_card, status=CardParseStatus.EMPTY, notes=("card_missing",))

    token = str(raw_card).strip()
    if not token:
        return CardParseResult(raw_card=raw_card, status=CardParseStatus.EMPTY, notes=("card_empty",))

    compact_match = COMPACT_CARD_PATTERN.match(token)
    if compact_match:
        rank = RANK_ALIASES[compact_match.group(1).upper()]
        suit = SUIT_ALIASES[compact_match.group(2).upper()]
        return CardParseResult(
            raw_card=raw_card,
            normalized_card=f"{rank}{suit}",
            status=CardParseStatus.PARSED,
            notes=("compact_card",),
        )

    project_match = PROJECT_CARD_PATTERN.match(token)
    if project_match:
        rank = RANK_ALIASES[project_match.group(1).upper()]
        suit = SUIT_ALIASES[project_match.group(2).upper()]
        return CardParseResult(
            raw_card=raw_card,
            normalized_card=f"{rank}{suit}",
            status=CardParseStatus.PARSED,
            notes=("project_card",),
        )

    return CardParseResult(raw_card=raw_card, status=CardParseStatus.UNRECOGNIZED, notes=("card_unrecognized",))


def normalize_cards(raw_cards: Iterable[Any] | None) -> tuple[str, ...]:
    """Normalize parseable cards and silently skip unparseable tokens."""

    if raw_cards is None:
        return tuple()
    normalized: list[str] = []
    for raw_card in raw_cards:
        result = normalize_card(raw_card)
        if result.is_parseable and result.normalized_card is not None:
            normalized.append(result.normalized_card)
    return tuple(normalized)


def parse_compact_combo(raw_combo: Any) -> ComboParseResult:
    """Parse a two-card compact combo into normalized card tokens.

    The parser accepts compact forms like ``AsKs`` and separator forms like
    ``As Ks``. It returns ``ComboParseResult`` for malformed values rather than
    throwing.
    """

    if raw_combo is None:
        return ComboParseResult(raw_combo=raw_combo, status=ComboParseStatus.EMPTY, notes=("combo_missing",))

    token = str(raw_combo).strip()
    if not token:
        return ComboParseResult(raw_combo=raw_combo, status=ComboParseStatus.EMPTY, notes=("combo_empty",))

    cards = _split_combo_token(token)
    if len(cards) != 2:
        return ComboParseResult(raw_combo=raw_combo, status=ComboParseStatus.MALFORMED, notes=("combo_not_two_cards",))

    parsed_cards: list[str] = []
    for card in cards:
        result = normalize_card(card)
        if not result.is_parseable or result.normalized_card is None:
            return ComboParseResult(raw_combo=raw_combo, status=ComboParseStatus.MALFORMED, notes=("combo_card_unrecognized",))
        parsed_cards.append(result.normalized_card)

    normalized_combo = "".join(parsed_cards)
    return ComboParseResult(
        raw_combo=raw_combo,
        normalized_combo=normalized_combo,
        combo_cards=tuple(parsed_cards),
        status=ComboParseStatus.PARSED,
        notes=("combo_parsed",),
    )


def combo_contains_any_card(raw_combo: Any, blocker_cards: Iterable[Any] | None) -> bool:
    """Return whether one parsed combo contains at least one blocker card."""

    parsed_combo = parse_compact_combo(raw_combo)
    if not parsed_combo.is_parseable:
        return False
    normalized_blockers = set(normalize_cards(blocker_cards))
    return any(card in normalized_blockers for card in parsed_combo.combo_cards)


def detect_combo_blockers(
    raw_combo: Any,
    *,
    hero_cards: Iterable[Any] | None = None,
    board_cards: Iterable[Any] | None = None,
) -> ComboBlockerMatch:
    """Detect which known HERO/board cards are present in a single combo.

    This helper produces one-combo metadata only. Later modules decide how to
    aggregate the result into player-level availability counts.
    """

    parsed_combo = parse_compact_combo(raw_combo)
    if not parsed_combo.is_parseable:
        return ComboBlockerMatch(
            combo=str(raw_combo),
            parse_status=parsed_combo.status,
            notes=("combo_unparseable_no_blocker_decision",),
        )

    combo_cards = set(parsed_combo.combo_cards)
    hero_blockers = tuple(card for card in normalize_cards(hero_cards) if card in combo_cards)
    board_blockers = tuple(card for card in normalize_cards(board_cards) if card in combo_cards)

    if hero_blockers and board_blockers:
        reason = BlockedComboReason.BLOCKED_BY_HERO_AND_BOARD
    elif hero_blockers:
        reason = BlockedComboReason.BLOCKED_BY_HERO_CARD
    elif board_blockers:
        reason = BlockedComboReason.BLOCKED_BY_BOARD_CARD
    else:
        reason = BlockedComboReason.NOT_BLOCKED

    return ComboBlockerMatch(
        combo=parsed_combo.normalized_combo or str(raw_combo),
        combo_cards=parsed_combo.combo_cards,
        hero_blocker_cards=hero_blockers,
        board_blocker_cards=board_blockers,
        blocked_reason=reason,
        parse_status=parsed_combo.status,
        notes=("single_combo_blocker_match",),
    )


def _split_combo_token(token: str) -> tuple[str, ...]:
    split_tokens = tuple(part for part in COMBO_SEPARATOR_PATTERN.split(token.strip()) if part)
    if len(split_tokens) == 2:
        return split_tokens

    compact = token.replace("_", "").replace("-", "").replace(" ", "")
    cards: list[str] = []
    index = 0
    while index < len(compact):
        if compact[index : index + 2].upper() == "10":
            rank = compact[index : index + 2]
            index += 2
        else:
            rank = compact[index : index + 1]
            index += 1
        if index >= len(compact):
            return tuple()
        suit = compact[index : index + 1]
        index += 1
        cards.append(f"{rank}{suit}")
    return tuple(cards)


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
