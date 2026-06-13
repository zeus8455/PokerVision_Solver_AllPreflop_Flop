"""PokerKit card API capability probe for V0.11.5.

This tool intentionally performs only local PokerKit API checks:
- import/capability inspection;
- PokerVision-style card string mapping;
- Card.parse smoke checks;
- StandardHighHand evaluation smoke check.

It does not compute equity, run simulations, build ranges, create decisions,
or touch PokerVision runtime/live/click infrastructure.
"""

from __future__ import annotations

import importlib
import importlib.metadata
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "postflop_pokerkit_card_api"
    / "latest_pokerkit_card_api_report.json"
)

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

SAMPLE_POKERVISION_CARDS = [
    "A_spades",
    "K_hearts",
    "Q_diamonds",
    "J_clubs",
    "10_spades",
    "2_clubs",
]


@dataclass(frozen=True)
class CardMappingResult:
    source: str
    compact: str | None
    ok: bool
    error: str | None = None


@dataclass(frozen=True)
class CardApiProbeReport:
    schema: str = "pokervision_solver_postflop_pokerkit_card_api_probe_v1"
    version_block: str = "V0.11.5"
    backend_name: str = "pokerkit"
    status: str = "backend_unavailable"
    package_version: str | None = None
    module_file: str | None = None
    importable: bool = False
    available_symbols: list[str] = field(default_factory=list)
    missing_symbols: list[str] = field(default_factory=list)
    sample_mapping_results: list[dict[str, Any]] = field(default_factory=list)
    hero_compact: str | None = None
    board_compact: str | None = None
    parsed_card_strings: list[str] = field(default_factory=list)
    parsed_card_compacts: list[str] = field(default_factory=list)
    standard_high_hand_created: bool = False
    standard_high_hand_repr: str | None = None
    standard_high_hand_cards: list[str] = field(default_factory=list)
    standard_high_comparison_ok: bool = False
    card_parse_error: str | None = None
    hand_evaluation_error: str | None = None
    real_project_touched: bool = False
    equity_calculation_executed: bool = False
    simulation_executed: bool = False
    monte_carlo_executed: bool = False
    range_logic_executed: bool = False
    decision_logic_executed: bool = False
    runtime_plan_created: bool = False
    physical_click_executed: bool = False
    notes: list[str] = field(default_factory=list)


def poker_vision_card_to_compact(card: str) -> str:
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
        raise ValueError(f"unsupported_card_format:{raw}")

    rank = RANK_MAP.get(rank_raw)
    suit = SUIT_MAP.get(suit_raw)

    if rank is None:
        raise ValueError(f"unsupported_rank:{rank_raw}")
    if suit is None:
        raise ValueError(f"unsupported_suit:{suit_raw}")

    return f"{rank}{suit}"


def _safe_version() -> str | None:
    try:
        return importlib.metadata.version("pokerkit")
    except importlib.metadata.PackageNotFoundError:
        return None


def _mapping_results() -> list[CardMappingResult]:
    results: list[CardMappingResult] = []
    for source in SAMPLE_POKERVISION_CARDS:
        try:
            compact = poker_vision_card_to_compact(source)
        except Exception as exc:  # pragma: no cover - defensive probe branch
            results.append(
                CardMappingResult(
                    source=source,
                    compact=None,
                    ok=False,
                    error=f"{type(exc).__name__}: {exc}",
                )
            )
        else:
            results.append(CardMappingResult(source=source, compact=compact, ok=True))
    return results



def _split_compact_cards(compact_cards: str) -> list[str]:
    if len(compact_cards) % 2 != 0:
        raise ValueError(f"invalid_compact_card_sequence:{compact_cards}")
    return [compact_cards[index : index + 2] for index in range(0, len(compact_cards), 2)]


def run_probe() -> CardApiProbeReport:
    notes: list[str] = []
    package_version = _safe_version()

    try:
        pokerkit = importlib.import_module("pokerkit")
    except Exception as exc:
        return CardApiProbeReport(
            package_version=package_version,
            status="backend_unavailable",
            notes=["pokerkit_not_importable", f"{type(exc).__name__}: {exc}"],
        )

    required_symbols = ["Card", "Rank", "Suit", "StandardHighHand"]
    available_symbols = [name for name in required_symbols if hasattr(pokerkit, name)]
    missing_symbols = [name for name in required_symbols if not hasattr(pokerkit, name)]

    if missing_symbols:
        return CardApiProbeReport(
            status="symbol_mismatch",
            package_version=package_version,
            module_file=str(getattr(pokerkit, "__file__", "")),
            importable=True,
            available_symbols=available_symbols,
            missing_symbols=missing_symbols,
            notes=["pokerkit_importable", "required_card_api_symbols_missing"],
        )

    mapping_results = _mapping_results()
    mapping_payload = [asdict(result) for result in mapping_results]
    notes.append("pokerkit_importable")
    notes.append("card_api_symbols_available")

    hero_cards = ["A_spades", "K_hearts"]
    board_cards = ["Q_diamonds", "J_clubs", "10_spades", "2_clubs", "3_diamonds"]
    hero_compact = "".join(poker_vision_card_to_compact(card) for card in hero_cards)
    board_compact = "".join(poker_vision_card_to_compact(card) for card in board_cards)

    parsed_card_strings: list[str] = []
    parsed_card_compacts: list[str] = []
    card_parse_error: str | None = None
    try:
        compact_sequence = hero_compact + board_compact
        parsed_cards = tuple(pokerkit.Card.parse(compact_sequence))
        parsed_card_strings = [str(card) for card in parsed_cards]
        parsed_card_compacts = _split_compact_cards(compact_sequence)
        notes.append("card_parse_ok")
    except Exception as exc:  # pragma: no cover - depends on external package behavior
        card_parse_error = f"{type(exc).__name__}: {exc}"
        notes.append("card_parse_failed")

    standard_high_hand_created = False
    standard_high_hand_repr: str | None = None
    standard_high_hand_cards: list[str] = []
    standard_high_comparison_ok = False
    hand_evaluation_error: str | None = None

    try:
        hero_hand = pokerkit.StandardHighHand.from_game(hero_compact, board_compact)
        weaker_hand = pokerkit.StandardHighHand.from_game("7c2d", "QsJcTs2c3d")
        stronger_hand = pokerkit.StandardHighHand.from_game("AsKs", "QsJsTs2c3d")
        standard_high_hand_created = True
        standard_high_hand_repr = str(hero_hand)
        standard_high_hand_cards = [str(card) for card in getattr(hero_hand, "cards", ())]
        standard_high_comparison_ok = weaker_hand < stronger_hand
        notes.append("standard_high_hand_evaluation_ok")
    except Exception as exc:  # pragma: no cover - depends on external package behavior
        hand_evaluation_error = f"{type(exc).__name__}: {exc}"
        notes.append("standard_high_hand_evaluation_failed")

    status = "available"
    if card_parse_error or hand_evaluation_error:
        status = "api_probe_partial"

    return CardApiProbeReport(
        status=status,
        package_version=package_version,
        module_file=str(getattr(pokerkit, "__file__", "")),
        importable=True,
        available_symbols=available_symbols,
        missing_symbols=missing_symbols,
        sample_mapping_results=mapping_payload,
        hero_compact=hero_compact,
        board_compact=board_compact,
        parsed_card_strings=parsed_card_strings,
        parsed_card_compacts=parsed_card_compacts,
        standard_high_hand_created=standard_high_hand_created,
        standard_high_hand_repr=standard_high_hand_repr,
        standard_high_hand_cards=standard_high_hand_cards,
        standard_high_comparison_ok=standard_high_comparison_ok,
        card_parse_error=card_parse_error,
        hand_evaluation_error=hand_evaluation_error,
        notes=notes,
    )


def write_report(report: CardApiProbeReport) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(asdict(report), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    report = run_probe()
    write_report(report)
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2, sort_keys=True))
    if report.status in {"available", "api_probe_partial", "backend_unavailable", "symbol_mismatch"}:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
