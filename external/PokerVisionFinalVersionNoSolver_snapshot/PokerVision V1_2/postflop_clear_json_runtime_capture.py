"""Runtime mirror for postflop Clear_JSON files used by V0.9 live audit.

V0.9.7.3 extends the V0.9.7.2 live evidence fix:
real postflop frames are currently published as Clear_JSON_Pending, not as
Final Clear_JSON. This module therefore mirrors postflop Pending Clear_JSON and
Final Clear_JSON into solver-readable ``*.clear.json`` files for audit only.
It also adapts live-runtime Clear_JSON shape into top-level solver-compatible
aliases such as board_cards, hero_cards, hero_id, table_id, hand_id, and total_pot.

Safety rules:
- mirrors only Clear_JSON-derived payloads whose board.street is flop/turn/river;
- writes only under outputs/postflop_live_clear_json;
- marks pending captures as not final-confirmed and not decision-eligible;
- does not build postflop decisions, runtime plans, Action_Button payloads, or clicks;
- mirror failures are diagnostic-only and must not break the existing runtime/click-chain.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, Optional

POSTFLOP_CLEAR_JSON_CAPTURE_DIR_NAME = "postflop_live_clear_json"
POSTFLOP_CLEAR_JSON_CAPTURE_SCHEMA_VERSION = "postflop_clear_json_runtime_capture_v0_9_7_3"
POSTFLOP_STREETS = {"flop", "turn", "river"}


def _safe_text(value: object, fallback: str) -> str:
    text = str(value or "").strip() or fallback
    safe_chars = []
    for char in text:
        if char.isalnum() or char in {"_", "-", "."}:
            safe_chars.append(char)
        else:
            safe_chars.append("_")
    return "".join(safe_chars).strip("._") or fallback


def _clear_state_street(clear_state: Optional[Dict[str, Any]]) -> Optional[str]:
    if not isinstance(clear_state, dict):
        return None
    board = clear_state.get("board")
    if not isinstance(board, dict):
        return None
    street = board.get("street")
    text = str(street).strip().lower() if street is not None else ""
    return text or None


def is_postflop_clear_state(clear_state: Optional[Dict[str, Any]]) -> bool:
    """Return True only for flop/turn/river Clear_JSON-like payloads."""
    return _clear_state_street(clear_state) in POSTFLOP_STREETS


RANK_ALIASES: dict[str, str] = {
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "10": "T",
    "T": "T",
    "J": "J",
    "Q": "Q",
    "K": "K",
    "A": "A",
}

SUIT_ALIASES: dict[str, str] = {
    "s": "s",
    "spade": "s",
    "spades": "s",
    "♠": "s",
    "c": "c",
    "club": "c",
    "clubs": "c",
    "♣": "c",
    "h": "h",
    "heart": "h",
    "hearts": "h",
    "♥": "h",
    "d": "d",
    "diamond": "d",
    "diamonds": "d",
    "♦": "d",
}


def _normalize_card_token(card: Any) -> str:
    """Normalize live card labels into compact solver-friendly notation.

    Examples:
        ``10_clubs`` -> ``Tc``
        ``A_spades`` -> ``As``
        ``9_diamonds`` -> ``9d``

    Unknown formats are carried forward as text. This is not card validation; it is
    a schema adapter for known live-runtime labels.
    """
    text = str(card or "").strip()
    if not text:
        return text
    normalized = (
        text.replace("♠", "_spades")
        .replace("♣", "_clubs")
        .replace("♥", "_hearts")
        .replace("♦", "_diamonds")
        .replace("-", "_")
        .replace(" ", "_")
    )
    parts = [part for part in normalized.split("_") if part]
    if len(parts) >= 2:
        rank_raw = parts[0].upper()
        suit_raw = parts[-1].lower()
        rank = RANK_ALIASES.get(rank_raw)
        suit = SUIT_ALIASES.get(suit_raw)
        if rank and suit:
            return f"{rank}{suit}"
    # Compact forms such as As, 10c, Td.
    compact = normalized.strip()
    if len(compact) >= 2:
        suit_raw = compact[-1].lower()
        rank_raw = compact[:-1].upper()
        rank = RANK_ALIASES.get(rank_raw)
        suit = SUIT_ALIASES.get(suit_raw)
        if rank and suit:
            return f"{rank}{suit}"
    return text


def _normalize_cards(cards: Any) -> list[str]:
    if not isinstance(cards, (list, tuple)):
        return []
    return [_normalize_card_token(card) for card in cards if str(card or "").strip()]


def _parse_table_hand_from_frame_id(frame_id: Any) -> tuple[Optional[str], Optional[str]]:
    text = str(frame_id or "").strip()
    if not text:
        return None, None
    parts = text.split("_")
    table_id: Optional[str] = None
    hand_id: Optional[str] = None
    for idx in range(len(parts) - 1):
        if parts[idx].lower() == "table" and parts[idx + 1].isdigit():
            table_id = f"table_{parts[idx + 1]}"
        if parts[idx].lower() == "hand" and parts[idx + 1].isdigit():
            hand_id = f"hand_{parts[idx + 1]}"
    return table_id, hand_id


def _find_hero_from_players(players: Any) -> tuple[Optional[str], list[str]]:
    if not isinstance(players, dict):
        return None, []
    for seat, player in players.items():
        if isinstance(player, dict) and player.get("hero") is True:
            return str(seat), _normalize_cards(player.get("cards"))
    return None, []


def build_solver_compatible_live_clear_json(clear_state: Dict[str, Any]) -> Dict[str, Any]:
    """Return a solver-compatible audit payload built from live Clear_JSON shape.

    Live runtime currently stores useful postflop metadata under nested keys such
    as ``board.cards`` and ``players.<seat>.cards``. V0.1-V0.9 audit modules read
    contract-backed top-level aliases such as ``board_cards`` and ``hero_cards``.
    This adapter adds those aliases while preserving the original live payload
    under ``raw_live_clear_json``.
    """
    if not isinstance(clear_state, dict):
        raise TypeError("clear_state must be a dict")

    raw_live_clear_json = copy.deepcopy(clear_state)
    adapted: Dict[str, Any] = copy.deepcopy(clear_state)

    frame_id = adapted.get("frame_id") or adapted.get("case_id")
    parsed_table_id, parsed_hand_id = _parse_table_hand_from_frame_id(frame_id)
    table_id = adapted.get("table_id") or parsed_table_id
    hand_id = adapted.get("hand_id") or parsed_hand_id
    if frame_id is not None:
        adapted.setdefault("case_id", str(frame_id))
    if table_id is not None:
        adapted.setdefault("table_id", str(table_id))
    if hand_id is not None:
        adapted.setdefault("hand_id", str(hand_id))

    board = adapted.get("board")
    if isinstance(board, dict):
        board_cards = _normalize_cards(board.get("cards"))
        if board_cards:
            adapted.setdefault("board_cards", board_cards)
        street = board.get("street")
        if street not in (None, ""):
            adapted.setdefault("street", str(street).strip().lower())

    players = adapted.get("players")
    hero_id, hero_cards = _find_hero_from_players(players)
    if hero_id is not None:
        adapted.setdefault("hero_id", hero_id)
        adapted.setdefault("hero", hero_id)
        adapted.setdefault("hero_position", hero_id)
    if hero_cards:
        adapted.setdefault("hero_cards", hero_cards)

    if "Total_pot" in adapted and "total_pot" not in adapted:
        adapted["total_pot"] = adapted["Total_pot"]
    if "total_pot" in adapted and "pot" not in adapted:
        adapted["pot"] = adapted["total_pot"]

    adapted["raw_live_clear_json"] = raw_live_clear_json
    return adapted


def resolve_postflop_clear_json_capture_root(cycle_dir: Path) -> Path:
    """Return the live audit Clear_JSON capture root for a UI display cycle dir.

    Expected live cycle dir:
        <project>/outputs/ui_display_cycle/current_cycle

    Capture root:
        <project>/outputs/postflop_live_clear_json
    """
    cycle = Path(cycle_dir)
    if cycle.name == "current_cycle" and cycle.parent.name == "ui_display_cycle":
        return cycle.parent.parent / POSTFLOP_CLEAR_JSON_CAPTURE_DIR_NAME
    return cycle / POSTFLOP_CLEAR_JSON_CAPTURE_DIR_NAME


def _stem_without_runtime_suffix(path: Optional[Path], clear_state: Optional[Dict[str, Any]]) -> str:
    if path is not None:
        stem = Path(path).stem
        if stem.endswith(".pending"):
            stem = stem[: -len(".pending")]
        if stem.endswith(".complete"):
            stem = stem[: -len(".complete")]
        return stem
    if isinstance(clear_state, dict):
        return str(clear_state.get("frame_id") or clear_state.get("source_frame_id") or "clear_state")
    return "clear_state"


def build_postflop_clear_json_capture_path(
    *,
    cycle_dir: Path,
    table_id: str,
    source_clear_json_path: Optional[Path] = None,
    clear_state: Optional[Dict[str, Any]] = None,
) -> Path:
    """Build the mirror path for a solver-readable ``*.clear.json`` artifact."""
    capture_root = resolve_postflop_clear_json_capture_root(Path(cycle_dir))
    table_name = _safe_text(table_id, "unknown_table")
    stem = _stem_without_runtime_suffix(source_clear_json_path, clear_state)
    filename = _safe_text(stem, "clear_state") + ".clear.json"
    return capture_root / table_name / filename


def _write_json_atomic(path: Path, payload: Dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp_path, path)
    return path


def _build_capture_metadata(
    *,
    capture_stage: str,
    final_clear_confirmed: bool,
    source_clear_json_path: Optional[Path],
) -> Dict[str, Any]:
    return {
        "schema_version": POSTFLOP_CLEAR_JSON_CAPTURE_SCHEMA_VERSION,
        "capture_stage": str(capture_stage),
        "final_clear_confirmed": bool(final_clear_confirmed),
        "solver_input_allowed_for_v090_audit": True,
        "solver_input_allowed_for_decision": False,
        "source_path": str(source_clear_json_path) if source_clear_json_path is not None else None,
        "source_type": "clear_json_pending" if capture_stage == "pending_clear_json" else "clear_json_final",
        "behavior": "audit_only_no_postflop_decision_no_runtime_plan_no_click",
    }


def mirror_postflop_clear_json_for_v090_audit(
    *,
    clear_state: Dict[str, Any],
    cycle_dir: Path,
    table_id: str,
    source_clear_json_path: Optional[Path] = None,
    capture_stage: str,
    final_clear_confirmed: bool,
) -> Optional[Path]:
    """Mirror postflop Clear_JSON-like payload into the V0.9 live audit folder.

    Returns None when the payload is not flop/turn/river. This lets runtime call
    the function safely for every Pending/Final Clear_JSON save without changing
    preflop behavior.
    """
    if not isinstance(clear_state, dict):
        raise TypeError("clear_state must be a dict")
    if not is_postflop_clear_state(clear_state):
        return None

    mirror_payload: Dict[str, Any] = build_solver_compatible_live_clear_json(clear_state)
    mirror_payload["postflop_live_capture"] = _build_capture_metadata(
        capture_stage=capture_stage,
        final_clear_confirmed=final_clear_confirmed,
        source_clear_json_path=source_clear_json_path,
    )
    mirror_path = build_postflop_clear_json_capture_path(
        cycle_dir=Path(cycle_dir),
        table_id=str(table_id),
        source_clear_json_path=source_clear_json_path,
        clear_state=mirror_payload,
    )
    return _write_json_atomic(mirror_path, mirror_payload)


def mirror_postflop_pending_clear_json_for_audit(
    *,
    clear_state: Dict[str, Any],
    cycle_dir: Path,
    table_id: str,
    pending_clear_json_path: Optional[Path] = None,
) -> Optional[Path]:
    """Mirror postflop Clear_JSON_Pending as V0.9 audit input, not decision input."""
    return mirror_postflop_clear_json_for_v090_audit(
        clear_state=clear_state,
        cycle_dir=Path(cycle_dir),
        table_id=str(table_id),
        source_clear_json_path=Path(pending_clear_json_path) if pending_clear_json_path is not None else None,
        capture_stage="pending_clear_json",
        final_clear_confirmed=False,
    )


def mirror_postflop_final_clear_json_for_audit(
    *,
    clear_state: Dict[str, Any],
    cycle_dir: Path,
    table_id: str,
    final_clear_json_path: Optional[Path] = None,
) -> Optional[Path]:
    """Mirror postflop Final Clear_JSON as V0.9 audit input, not decision input."""
    return mirror_postflop_clear_json_for_v090_audit(
        clear_state=clear_state,
        cycle_dir=Path(cycle_dir),
        table_id=str(table_id),
        source_clear_json_path=Path(final_clear_json_path) if final_clear_json_path is not None else None,
        capture_stage="final_clear_json",
        final_clear_confirmed=True,
    )


# V0.9.7.1 compatibility alias.
def mirror_final_clear_json_for_postflop_audit(
    *,
    clear_state: Dict[str, Any],
    cycle_dir: Path,
    table_id: str,
    final_clear_json_path: Optional[Path] = None,
) -> Optional[Path]:
    return mirror_postflop_final_clear_json_for_audit(
        clear_state=clear_state,
        cycle_dir=cycle_dir,
        table_id=table_id,
        final_clear_json_path=final_clear_json_path,
    )


def install_postflop_clear_json_runtime_capture(
    display_analysis_cycle_module: ModuleType,
    *,
    logger: Optional[Callable[[str], None]] = None,
) -> bool:
    """Wrap Pending and Final Clear_JSON save functions once.

    The wrapper is audit-only. It does not alter the original return values, does
    not create decisions/runtime plans, and does not affect click execution.
    """
    log = logger or print
    installed_any = False

    pending_current = getattr(display_analysis_cycle_module, "save_pending_clear_table_frame_json", None)
    if callable(pending_current) and not bool(getattr(pending_current, "_postflop_clear_json_capture_installed", False)):
        pending_original = pending_current

        def _wrapped_save_pending_clear_table_frame_json(*, clear_state: Dict[str, Any], cycle_dir: Path, table_id: str) -> Path:
            pending_path = pending_original(clear_state=clear_state, cycle_dir=cycle_dir, table_id=table_id)
            try:
                mirror_path = mirror_postflop_pending_clear_json_for_audit(
                    clear_state=clear_state,
                    cycle_dir=Path(cycle_dir),
                    table_id=str(table_id),
                    pending_clear_json_path=Path(pending_path),
                )
                if mirror_path is not None:
                    log(f"[POSTFLOP_CLEAR_JSON_CAPTURE] mirrored Pending postflop Clear_JSON: {mirror_path}")
            except Exception as exc:  # pragma: no cover - live diagnostic fallback
                log(f"[POSTFLOP_CLEAR_JSON_CAPTURE] pending mirror failed: {exc}")
            return pending_path

        setattr(_wrapped_save_pending_clear_table_frame_json, "_postflop_clear_json_capture_installed", True)
        setattr(_wrapped_save_pending_clear_table_frame_json, "_postflop_clear_json_capture_original", pending_original)
        display_analysis_cycle_module.save_pending_clear_table_frame_json = _wrapped_save_pending_clear_table_frame_json
        installed_any = True
    elif callable(pending_current):
        installed_any = True

    final_current = getattr(display_analysis_cycle_module, "save_clear_table_frame_json", None)
    if callable(final_current) and not bool(getattr(final_current, "_postflop_clear_json_capture_installed", False)):
        final_original = final_current

        def _wrapped_save_clear_table_frame_json(*, clear_state: Dict[str, Any], cycle_dir: Path, table_id: str) -> Path:
            final_path = final_original(clear_state=clear_state, cycle_dir=cycle_dir, table_id=table_id)
            try:
                mirror_path = mirror_postflop_final_clear_json_for_audit(
                    clear_state=clear_state,
                    cycle_dir=Path(cycle_dir),
                    table_id=str(table_id),
                    final_clear_json_path=Path(final_path),
                )
                if mirror_path is not None:
                    log(f"[POSTFLOP_CLEAR_JSON_CAPTURE] mirrored Final postflop Clear_JSON: {mirror_path}")
            except Exception as exc:  # pragma: no cover - live diagnostic fallback
                log(f"[POSTFLOP_CLEAR_JSON_CAPTURE] final mirror failed: {exc}")
            return final_path

        setattr(_wrapped_save_clear_table_frame_json, "_postflop_clear_json_capture_installed", True)
        setattr(_wrapped_save_clear_table_frame_json, "_postflop_clear_json_capture_original", final_original)
        display_analysis_cycle_module.save_clear_table_frame_json = _wrapped_save_clear_table_frame_json
        installed_any = True
    elif callable(final_current):
        installed_any = True

    return installed_any
