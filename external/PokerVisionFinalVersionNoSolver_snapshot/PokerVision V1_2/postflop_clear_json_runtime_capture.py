"""Runtime mirror for Final Clear_JSON files used by V0.9 live postflop audit.

This module is intentionally narrow:
- it mirrors only Final Clear_JSON files written by save_clear_table_frame_json;
- it writes solver-readable *.clear.json files under outputs/postflop_live_clear_json;
- it does not build decisions, runtime plans, Action_Button payloads, or clicks;
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
POSTFLOP_CLEAR_JSON_CAPTURE_SCHEMA_VERSION = "postflop_clear_json_runtime_capture_v0_9_7_1"


def _safe_text(value: object, fallback: str) -> str:
    text = str(value or "").strip() or fallback
    safe_chars = []
    for char in text:
        if char.isalnum() or char in {"_", "-", "."}:
            safe_chars.append(char)
        else:
            safe_chars.append("_")
    return "".join(safe_chars).strip("._") or fallback


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


def build_postflop_clear_json_capture_path(
    *,
    cycle_dir: Path,
    table_id: str,
    final_clear_json_path: Optional[Path] = None,
    clear_state: Optional[Dict[str, Any]] = None,
) -> Path:
    """Build the mirror path for a solver-readable *.clear.json artifact."""
    capture_root = resolve_postflop_clear_json_capture_root(Path(cycle_dir))
    table_name = _safe_text(table_id, "unknown_table")

    if final_clear_json_path is not None:
        stem = Path(final_clear_json_path).stem
    elif isinstance(clear_state, dict):
        stem = str(clear_state.get("frame_id") or clear_state.get("source_frame_id") or "clear_state")
    else:
        stem = "clear_state"

    filename = _safe_text(stem, "clear_state") + ".clear.json"
    return capture_root / table_name / filename


def _write_json_atomic(path: Path, payload: Dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp_path, path)
    return path


def mirror_final_clear_json_for_postflop_audit(
    *,
    clear_state: Dict[str, Any],
    cycle_dir: Path,
    table_id: str,
    final_clear_json_path: Optional[Path] = None,
) -> Path:
    """Mirror a Final Clear_JSON payload into the postflop live audit folder."""
    if not isinstance(clear_state, dict):
        raise TypeError("clear_state must be a dict")

    mirror_payload: Dict[str, Any] = copy.deepcopy(clear_state)
    mirror_path = build_postflop_clear_json_capture_path(
        cycle_dir=Path(cycle_dir),
        table_id=str(table_id),
        final_clear_json_path=final_clear_json_path,
        clear_state=mirror_payload,
    )
    return _write_json_atomic(mirror_path, mirror_payload)


def install_postflop_clear_json_runtime_capture(
    display_analysis_cycle_module: ModuleType,
    *,
    logger: Optional[Callable[[str], None]] = None,
) -> bool:
    """Wrap display_analysis_cycle.save_clear_table_frame_json once.

    Returns True when the wrapper was installed or already present.
    It never installs decision/runtime/click behavior.
    """
    log = logger or print
    current = getattr(display_analysis_cycle_module, "save_clear_table_frame_json", None)
    if not callable(current):
        return False
    if bool(getattr(current, "_postflop_clear_json_capture_installed", False)):
        return True

    original = current

    def _wrapped_save_clear_table_frame_json(*, clear_state: Dict[str, Any], cycle_dir: Path, table_id: str) -> Path:
        final_path = original(clear_state=clear_state, cycle_dir=cycle_dir, table_id=table_id)
        try:
            mirror_path = mirror_final_clear_json_for_postflop_audit(
                clear_state=clear_state,
                cycle_dir=Path(cycle_dir),
                table_id=str(table_id),
                final_clear_json_path=Path(final_path),
            )
            log(f"[POSTFLOP_CLEAR_JSON_CAPTURE] mirrored Final Clear_JSON: {mirror_path}")
        except Exception as exc:  # pragma: no cover - live diagnostic fallback
            log(f"[POSTFLOP_CLEAR_JSON_CAPTURE] mirror failed: {exc}")
        return final_path

    setattr(_wrapped_save_clear_table_frame_json, "_postflop_clear_json_capture_installed", True)
    setattr(_wrapped_save_clear_table_frame_json, "_postflop_clear_json_capture_original", original)
    display_analysis_cycle_module.save_clear_table_frame_json = _wrapped_save_clear_table_frame_json
    return True
