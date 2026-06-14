"""Range source inventory probe for V0.12.2.

This tool audits existing range JSON files under the repository-local ranges/
directory. It is read-only for range sources and does not create RangeState,
block combos, calculate equity, create decisions, create runtime plans, or touch
any real PokerVision project directory.
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "pokervision_solver_postflop_range_source_inventory_v1"
VERSION_BLOCK = "V0.12.2"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RANGE_ROOT = PROJECT_ROOT / "ranges"
REPORT_DIR = PROJECT_ROOT / "outputs" / "postflop_range_inventory"
REPORT_PATH = REPORT_DIR / "latest_range_source_inventory_report.json"

RANGE_SHORTHAND_MARKERS = (
    "+",
    "-",
    "s",
    "o",
)
RANGE_ACTION_KEYS = {
    "open_raise",
    "limp",
    "iso_raise",
    "3bet",
    "4bet",
    "5bet_jam",
    "call",
}
KNOWN_RANGE_SECTION_KEYS = {
    "rfi",
    "sb_first_in",
    "vs_open",
    "opener_vs_3bet",
    "threebettor_vs_4bet",
    "cold_4bet",
    "iso_raise",
    "limper_vs_iso",
}


def _sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_safe_preview(value: Any, *, max_items: int = 12) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe_preview(item, max_items=max_items) for key, item in list(value.items())[:max_items]}
    if isinstance(value, list):
        return [_json_safe_preview(item, max_items=max_items) for item in value[:max_items]]
    if isinstance(value, tuple):
        return [_json_safe_preview(item, max_items=max_items) for item in value[:max_items]]
    return value


def _walk_json_values(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, dict):
        for item in value.values():
            yield from _walk_json_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_json_values(item)


def _walk_json_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from _walk_json_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_json_keys(item)


def _looks_like_range_shorthand(text: str) -> bool:
    tokens = [token.strip() for token in text.replace(",", " ").split() if token.strip()]
    if not tokens:
        return False
    rank_chars = set("AKQJT98765432")
    matched = 0
    for token in tokens:
        cleaned = token.strip()
        if len(cleaned) < 2:
            continue
        has_rank = any(char in rank_chars for char in cleaned.upper())
        has_marker = any(marker in cleaned for marker in RANGE_SHORTHAND_MARKERS)
        pair_or_hand = len(cleaned) in {2, 3, 4, 5} and has_rank
        if pair_or_hand and (has_marker or cleaned.upper() in {"AA", "KK", "QQ", "JJ", "TT", "AKS", "AKO", "AQO", "AQS"}):
            matched += 1
    return matched > 0


def _looks_like_compact_combo(text: str) -> bool:
    # Compact combo candidate used by future V0.13 blocker filtering, e.g. AsKh or QcQs.
    if len(text) != 4:
        return False
    ranks = set("AKQJT98765432")
    suits = set("cdhs")
    return text[0] in ranks and text[1] in suits and text[2] in ranks and text[3] in suits


def _analyze_json_payload(payload: Any) -> dict[str, Any]:
    values = list(_walk_json_values(payload))
    keys = list(_walk_json_keys(payload))
    string_values = [value for value in values if isinstance(value, str)]
    top_level_keys = list(payload.keys()) if isinstance(payload, dict) else []
    detected_action_keys = sorted(set(keys) & RANGE_ACTION_KEYS)
    detected_section_keys = sorted(set(keys) & KNOWN_RANGE_SECTION_KEYS)
    range_shorthand_values = [text for text in string_values if _looks_like_range_shorthand(text)]
    compact_combo_values = [text for text in string_values if _looks_like_compact_combo(text)]

    return {
        "top_level_type": type(payload).__name__,
        "top_level_keys": [str(key) for key in top_level_keys[:40]],
        "schema": payload.get("schema") if isinstance(payload, dict) else None,
        "source": payload.get("source") if isinstance(payload, dict) else None,
        "nested_dict_count": sum(1 for value in values if isinstance(value, dict)),
        "list_count": sum(1 for value in values if isinstance(value, list)),
        "string_value_count": len(string_values),
        "detected_section_keys": detected_section_keys,
        "detected_action_keys": detected_action_keys,
        "contains_range_shorthand_strings": bool(range_shorthand_values),
        "range_shorthand_string_count": len(range_shorthand_values),
        "contains_combo_level_compact_strings": bool(compact_combo_values),
        "combo_level_compact_string_count": len(compact_combo_values),
        "sample_range_shorthand_strings": range_shorthand_values[:8],
        "sample_combo_level_compact_strings": compact_combo_values[:8],
        "payload_preview": _json_safe_preview(payload),
    }


@dataclass(frozen=True)
class RangeFileInventory:
    relative_path: str
    exists: bool
    size_bytes: int | None
    sha256: str | None
    json_load_status: str
    json_error: str | None = None
    source_type_candidate: str = "existing_project_ranges"
    top_level_type: str | None = None
    top_level_keys: list[str] = field(default_factory=list)
    schema: str | None = None
    source: str | None = None
    nested_dict_count: int = 0
    list_count: int = 0
    string_value_count: int = 0
    detected_section_keys: list[str] = field(default_factory=list)
    detected_action_keys: list[str] = field(default_factory=list)
    contains_range_shorthand_strings: bool = False
    range_shorthand_string_count: int = 0
    contains_combo_level_compact_strings: bool = False
    combo_level_compact_string_count: int = 0
    sample_range_shorthand_strings: list[str] = field(default_factory=list)
    sample_combo_level_compact_strings: list[str] = field(default_factory=list)
    requires_expansion_before_v013: bool = False
    usable_as_existing_project_range_source: bool = False
    payload_preview: Any = None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RangeSourceInventoryReport:
    schema: str = SCHEMA
    version_block: str = VERSION_BLOCK
    status: str = "ok"
    project_root: str = str(PROJECT_ROOT)
    range_root: str = str(RANGE_ROOT)
    range_root_exists: bool = False
    json_files_total: int = 0
    range_files_total: int = 0
    hero_preflop_ranges_found: bool = False
    existing_project_ranges_detected: bool = False
    combo_level_source_available: bool = False
    shorthand_source_available: bool = False
    requires_combo_expansion_before_v013: bool = False
    files: list[RangeFileInventory] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    real_project_touched: bool = False
    range_files_mutated: bool = False
    range_importer_executed: bool = False
    range_state_created: bool = False
    blocker_filtering_executed: bool = False
    equity_recalculation_executed: bool = False
    decision_logic_executed: bool = False
    runtime_plan_created: bool = False
    physical_click_executed: bool = False

    def to_json_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["files"] = [item.to_json_dict() for item in self.files]
        return payload


def _inventory_file(path: Path) -> RangeFileInventory:
    relative_path = path.relative_to(PROJECT_ROOT).as_posix()
    size_bytes = path.stat().st_size if path.exists() else None
    digest_before = _sha256(path)

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return RangeFileInventory(
            relative_path=relative_path,
            exists=path.exists(),
            size_bytes=size_bytes,
            sha256=digest_before,
            json_load_status="error",
            json_error=f"{type(exc).__name__}: {exc}",
        )

    analysis = _analyze_json_payload(payload)
    contains_shorthand = bool(analysis["contains_range_shorthand_strings"])
    contains_combo = bool(analysis["contains_combo_level_compact_strings"])

    return RangeFileInventory(
        relative_path=relative_path,
        exists=True,
        size_bytes=size_bytes,
        sha256=digest_before,
        json_load_status="ok",
        top_level_type=analysis["top_level_type"],
        top_level_keys=analysis["top_level_keys"],
        schema=analysis["schema"],
        source=analysis["source"],
        nested_dict_count=analysis["nested_dict_count"],
        list_count=analysis["list_count"],
        string_value_count=analysis["string_value_count"],
        detected_section_keys=analysis["detected_section_keys"],
        detected_action_keys=analysis["detected_action_keys"],
        contains_range_shorthand_strings=contains_shorthand,
        range_shorthand_string_count=analysis["range_shorthand_string_count"],
        contains_combo_level_compact_strings=contains_combo,
        combo_level_compact_string_count=analysis["combo_level_compact_string_count"],
        sample_range_shorthand_strings=analysis["sample_range_shorthand_strings"],
        sample_combo_level_compact_strings=analysis["sample_combo_level_compact_strings"],
        requires_expansion_before_v013=contains_shorthand and not contains_combo,
        usable_as_existing_project_range_source=contains_shorthand or contains_combo,
        payload_preview=analysis["payload_preview"],
    )


def create_range_source_inventory_report(range_root: Path = RANGE_ROOT) -> RangeSourceInventoryReport:
    if not range_root.exists():
        return RangeSourceInventoryReport(
            status="range_root_missing",
            range_root_exists=False,
            notes=["ranges_directory_missing", "structured_empty_inventory"],
        )

    json_files = sorted(path for path in range_root.rglob("*.json") if path.is_file())
    if not json_files:
        return RangeSourceInventoryReport(
            status="no_json_range_files",
            range_root_exists=True,
            notes=["ranges_directory_present", "no_json_files_found", "structured_empty_inventory"],
        )

    inventories = [_inventory_file(path) for path in json_files]
    hero_found = any(item.relative_path == "ranges/hero_preflop_ranges.json" for item in inventories)
    shorthand = any(item.contains_range_shorthand_strings for item in inventories)
    combo = any(item.contains_combo_level_compact_strings for item in inventories)
    requires_expansion = any(item.requires_expansion_before_v013 for item in inventories)
    existing_detected = any(item.usable_as_existing_project_range_source for item in inventories)

    notes = ["ranges_directory_present", "json_range_files_scanned"]
    if hero_found:
        notes.append("hero_preflop_ranges_json_found")
    if shorthand:
        notes.append("range_shorthand_source_detected")
    if requires_expansion:
        notes.append("combo_expansion_needed_before_v013_blocker_filtering")
    if combo:
        notes.append("combo_level_source_detected")

    return RangeSourceInventoryReport(
        status="ok",
        range_root_exists=True,
        json_files_total=len(json_files),
        range_files_total=len(inventories),
        hero_preflop_ranges_found=hero_found,
        existing_project_ranges_detected=existing_detected,
        combo_level_source_available=combo,
        shorthand_source_available=shorthand,
        requires_combo_expansion_before_v013=requires_expansion,
        files=inventories,
        notes=notes,
    )


def write_report(report: RangeSourceInventoryReport, path: Path = REPORT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_json_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    report = create_range_source_inventory_report()
    write_report(report)
    print(json.dumps(report.to_json_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
