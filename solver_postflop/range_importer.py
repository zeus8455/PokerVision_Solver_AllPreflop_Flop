"""Import baseline postflop ranges from already-built FlopContext.

V0.12.4 scope: select a baseline range pack entry and convert it into
RangeState contracts. This module only selects and converts baseline range data from an already-built context.
It has no executable action side effects and performs no card or player repair.
"""

from __future__ import annotations

import json
from collections.abc import Mapping as MappingABC
from pathlib import Path
from typing import Any, Mapping, Optional

from solver_postflop.flop_context_contracts import FlopContext, FlopSpotFamily
from solver_postflop.range_contracts import (
    DEFAULT_UNKNOWN_RANGE_NAME,
    PlayerRangeState,
    RangeBucket,
    RangeConfidenceClass,
    RangeImportStatus,
    RangeSourceInfo,
    RangeSourceType,
    RangeState,
    RangeWeightingMode,
)

RANGE_IMPORTER_VERSION = "v0.12.4"
DEFAULT_POSTFLOP_RANGE_FILE = Path("ranges/postflop_default_ranges.json")
DEFAULT_RANGE_IMPORTER_NEXT_MODULE = "blocker_filtering_later"
POSTFLOP_DEFAULT_RANGE_SCHEMA = "pokervision_solver_postflop_default_ranges_v1"


class RangeImporterError(RuntimeError):
    """Raised only for invalid importer configuration, not for unknown spots."""


def build_range_state_from_flop_context(
    flop_context: FlopContext,
    *,
    project_root: Optional[Path] = None,
    range_file: Optional[Path] = None,
) -> RangeState:
    """Build a baseline RangeState from FlopContext.

    Unknown or unsupported context is represented as a structured unknown_range
    RangeState. The trusted FlopContext object is never mutated.
    """

    root = Path.cwd() if project_root is None else Path(project_root)
    selected_range_file = range_file or (root / DEFAULT_POSTFLOP_RANGE_FILE)
    fields_used, fields_not_provided = _collect_available_context_fields(flop_context)

    if not selected_range_file.exists():
        return _unknown_range_state(
            flop_context,
            source_file=str(flop_context.source_file),
            fields_used=fields_used,
            fields_not_provided=fields_not_provided + ("range_file",),
            notes=(
                "range_importer_v0.12.4",
                "postflop_default_range_file_missing",
                "structured_unknown_range_without_pipeline_failure",
            ),
            source_file_for_info=str(selected_range_file),
        )

    payload = _load_range_pack(selected_range_file)
    case_id = select_range_case_id(flop_context)
    cases = payload.get("cases") if isinstance(payload, MappingABC) else None

    if not isinstance(cases, MappingABC) or case_id not in cases:
        return _unknown_range_state(
            flop_context,
            source_file=str(flop_context.source_file),
            fields_used=fields_used,
            fields_not_provided=fields_not_provided + ("range_case",),
            notes=(
                "range_importer_v0.12.4",
                "range_case_not_found",
                "structured_unknown_range_without_pipeline_failure",
            ),
            source_file_for_info=str(selected_range_file),
        )

    case_payload = cases[case_id]
    if not isinstance(case_payload, MappingABC):
        return _unknown_range_state(
            flop_context,
            source_file=str(flop_context.source_file),
            fields_used=fields_used,
            fields_not_provided=fields_not_provided + ("range_case_payload",),
            notes=(
                "range_importer_v0.12.4",
                "range_case_payload_not_mapping",
                "structured_unknown_range_without_pipeline_failure",
            ),
            source_file_for_info=str(selected_range_file),
        )

    if str(case_payload.get("range_import_status") or "") == RangeImportStatus.UNKNOWN_RANGE.value:
        return _range_state_from_unknown_case(
            flop_context,
            case_payload=case_payload,
            selected_range_file=selected_range_file,
            fields_used=fields_used,
            fields_not_provided=fields_not_provided,
        )

    hero_range_state = _player_range_state_from_payload(case_payload.get("hero_range_state"), default_player_id="hero")
    opponent_range_states = tuple(
        _player_range_state_from_payload(item, default_player_id=f"villain_{index + 1}")
        for index, item in enumerate(_sequence_of_mappings(case_payload.get("opponent_range_states")))
    )
    opponent_positions = _string_tuple(case_payload.get("opponent_positions"))
    range_buckets = _range_bucket_tuple(case_payload.get("range_buckets"))

    source_type = _range_source_type(case_payload.get("source_type") or payload.get("source_type"))
    range_confidence = _range_confidence(case_payload.get("range_confidence"))
    range_import_status = _range_import_status(case_payload.get("range_import_status"))

    return RangeState(
        case_id=_optional_str(case_payload.get("case_id")) or _optional_str(flop_context.case_id) or case_id,
        source_file=str(flop_context.source_file),
        spot_family=_spot_family_value(flop_context.spot_family),
        pot_type=_optional_str(case_payload.get("pot_type")) or _optional_str(getattr(flop_context.pot_context, "pot_type", None)),
        hero_position=_optional_str(case_payload.get("hero_position")) or _optional_str(getattr(flop_context.position_context, "hero_position", None)),
        opponent_positions=opponent_positions,
        hero_range_state=hero_range_state,
        opponent_range_states=opponent_range_states,
        range_source_info=RangeSourceInfo(
            source_type=source_type,
            source_name=_optional_str(case_payload.get("source_name")) or _optional_str(payload.get("source_name")) or "postflop_default_ranges_v0123",
            source_file=str(selected_range_file),
            source_version=_optional_str(payload.get("source_version")),
            is_existing_project_source=False,
            is_synthetic_test_source=False,
            notes=(
                "range_importer_v0.12.4",
                "baseline_range_selected_from_postflop_default_pack",
                "baseline_selection_only",
            ),
        ),
        range_confidence=range_confidence,
        range_import_status=range_import_status,
        range_buckets=range_buckets,
        next_module=DEFAULT_RANGE_IMPORTER_NEXT_MODULE,
        fields_used=fields_used + ("range_file", "range_case"),
        fields_not_provided=fields_not_provided,
        notes=(
            "range_importer_v0.12.4",
            "baseline_range_only",
            "flop_context_read_only",
            "baseline_combo_groups_not_filtered",
            "baseline_combo_groups_not_refined",
        ),
    )


def select_range_case_id(flop_context: FlopContext) -> str:
    """Return the default range-pack case id for the supplied FlopContext."""

    spot_family = _spot_family_value(flop_context.spot_family)
    hero_position = (_optional_str(getattr(flop_context.position_context, "hero_position", None)) or "").upper()
    pot_type = (_optional_str(getattr(flop_context.pot_context, "pot_type", None)) or "").lower()

    if spot_family == FlopSpotFamily.SRP_HEADS_UP.value:
        if hero_position == "BB":
            return "flop_range_srp_oop_bb_vs_btn"
        return "flop_range_srp_heads_up_btn_vs_bb"

    if spot_family == FlopSpotFamily.THREEBET_POT_HEADS_UP.value:
        if hero_position in {"SB", "BB"} or "oop" in pot_type:
            return "flop_range_3bet_pot_oop"
        return "flop_range_3bet_pot_ip"

    if spot_family == FlopSpotFamily.FOURBET_LOW_SPR.value:
        return "flop_range_4bet_low_spr"

    if spot_family == FlopSpotFamily.LIMP_OR_PASSIVE_POT.value:
        return "flop_range_limp_passive"

    if spot_family == FlopSpotFamily.MULTIWAY_POT.value:
        return "flop_range_multiway"

    return "flop_range_unknown_context"


def _load_range_pack(path: Path) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RangeImporterError(f"Invalid range pack JSON: {path}") from exc

    if not isinstance(payload, MappingABC):
        raise RangeImporterError(f"Range pack must be a JSON object: {path}")
    return payload


def _range_state_from_unknown_case(
    flop_context: FlopContext,
    *,
    case_payload: Mapping[str, Any],
    selected_range_file: Path,
    fields_used: tuple[str, ...],
    fields_not_provided: tuple[str, ...],
) -> RangeState:
    hero_payload = case_payload.get("hero_range_state")
    hero_range_state = _player_range_state_from_payload(hero_payload, default_player_id="hero") if isinstance(hero_payload, MappingABC) else None

    return RangeState(
        case_id=_optional_str(case_payload.get("case_id")) or _optional_str(flop_context.case_id) or "flop_range_unknown_context",
        source_file=str(flop_context.source_file),
        spot_family=_spot_family_value(flop_context.spot_family),
        pot_type=_optional_str(getattr(flop_context.pot_context, "pot_type", None)),
        hero_position=_optional_str(getattr(flop_context.position_context, "hero_position", None)),
        opponent_positions=(),
        hero_range_state=hero_range_state,
        opponent_range_states=(),
        range_source_info=RangeSourceInfo(
            source_type=RangeSourceType.UNKNOWN_RANGE,
            source_name=DEFAULT_UNKNOWN_RANGE_NAME,
            source_file=str(selected_range_file),
            notes=(
                "range_importer_v0.12.4",
                "unknown_context_non_fatal",
            ),
        ),
        range_confidence=RangeConfidenceClass.UNKNOWN,
        range_import_status=RangeImportStatus.UNKNOWN_RANGE,
        range_buckets=(RangeBucket.UNKNOWN_BUCKET,),
        next_module=DEFAULT_RANGE_IMPORTER_NEXT_MODULE,
        fields_used=fields_used + ("range_file", "range_case"),
        fields_not_provided=fields_not_provided,
        notes=(
            "range_importer_v0.12.4",
            "structured_unknown_range_without_pipeline_failure",
        ),
    )


def _unknown_range_state(
    flop_context: FlopContext,
    *,
    source_file: str,
    fields_used: tuple[str, ...],
    fields_not_provided: tuple[str, ...],
    notes: tuple[str, ...],
    source_file_for_info: Optional[str] = None,
) -> RangeState:
    return RangeState(
        case_id=_optional_str(flop_context.case_id) or "flop_range_unknown_context",
        source_file=source_file,
        spot_family=_spot_family_value(flop_context.spot_family),
        pot_type=_optional_str(getattr(flop_context.pot_context, "pot_type", None)),
        hero_position=_optional_str(getattr(flop_context.position_context, "hero_position", None)),
        opponent_positions=(),
        hero_range_state=PlayerRangeState(
            player_id="hero",
            position=_optional_str(getattr(flop_context.position_context, "hero_position", None)),
            role="hero",
            range_name=DEFAULT_UNKNOWN_RANGE_NAME,
            range_source=RangeSourceType.UNKNOWN_RANGE,
            combo_groups={RangeBucket.UNKNOWN_BUCKET.value: ()},
            range_buckets=(RangeBucket.UNKNOWN_BUCKET,),
            weighting_mode=RangeWeightingMode.UNKNOWN,
            confidence=RangeConfidenceClass.UNKNOWN,
            notes=("unknown_range_non_fatal",),
        ),
        opponent_range_states=(),
        range_source_info=RangeSourceInfo(
            source_type=RangeSourceType.UNKNOWN_RANGE,
            source_name=DEFAULT_UNKNOWN_RANGE_NAME,
            source_file=source_file_for_info,
            notes=("range_source_not_selected",),
        ),
        range_confidence=RangeConfidenceClass.UNKNOWN,
        range_import_status=RangeImportStatus.UNKNOWN_RANGE,
        range_buckets=(RangeBucket.UNKNOWN_BUCKET,),
        next_module=DEFAULT_RANGE_IMPORTER_NEXT_MODULE,
        fields_used=fields_used,
        fields_not_provided=fields_not_provided,
        notes=notes,
    )


def _player_range_state_from_payload(payload: Any, *, default_player_id: str) -> PlayerRangeState:
    if not isinstance(payload, MappingABC):
        return PlayerRangeState(
            player_id=default_player_id,
            range_name=DEFAULT_UNKNOWN_RANGE_NAME,
            range_source=RangeSourceType.UNKNOWN_RANGE,
            combo_groups={RangeBucket.UNKNOWN_BUCKET.value: ()},
            range_buckets=(RangeBucket.UNKNOWN_BUCKET,),
            weighting_mode=RangeWeightingMode.UNKNOWN,
            confidence=RangeConfidenceClass.UNKNOWN,
            notes=("missing_player_range_payload",),
        )

    return PlayerRangeState(
        player_id=_optional_str(payload.get("player_id")) or default_player_id,
        position=_optional_str(payload.get("position")),
        role=_optional_str(payload.get("role")),
        range_name=_optional_str(payload.get("range_name")) or DEFAULT_UNKNOWN_RANGE_NAME,
        range_source=_range_source_type(payload.get("range_source")),
        combo_groups=_combo_groups(payload.get("combo_groups")),
        hand_class_groups=_string_tuple_mapping(payload.get("hand_class_groups")),
        range_buckets=_range_bucket_tuple(payload.get("range_buckets")),
        weighting_mode=_range_weighting_mode(payload.get("weighting_mode")),
        confidence=_range_confidence(payload.get("confidence")),
        notes=_string_tuple(payload.get("notes")),
    )


def _collect_available_context_fields(flop_context: FlopContext) -> tuple[tuple[str, ...], tuple[str, ...]]:
    fields_used: list[str] = []
    fields_not_provided: list[str] = []

    _mark_field("spot_family", _spot_family_value(flop_context.spot_family), fields_used, fields_not_provided)
    _mark_field("pot_context.pot_type", getattr(flop_context.pot_context, "pot_type", None), fields_used, fields_not_provided)
    _mark_field("position_context.hero_position", getattr(flop_context.position_context, "hero_position", None), fields_used, fields_not_provided)
    _mark_field("player_context.players", getattr(flop_context.player_context, "players", None), fields_used, fields_not_provided)

    return tuple(_dedupe(fields_used)), tuple(_dedupe(fields_not_provided))


def _mark_field(field_name: str, value: Any, fields_used: list[str], fields_not_provided: list[str]) -> None:
    if value in (None, "", (), [], {}):
        fields_not_provided.append(field_name)
    else:
        fields_used.append(field_name)


def _combo_groups(value: Any) -> dict[str, tuple[str, ...]]:
    return _string_tuple_mapping(value)


def _string_tuple_mapping(value: Any) -> dict[str, tuple[str, ...]]:
    if not isinstance(value, MappingABC):
        return {}
    return {str(key): _string_tuple(item) for key, item in value.items()}


def _sequence_of_mappings(value: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(item for item in value if isinstance(item, MappingABC))


def _string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(str(item) for item in value if item is not None)
    return (str(value),)


def _range_bucket_tuple(value: Any) -> tuple[RangeBucket, ...]:
    buckets: list[RangeBucket] = []
    for item in _string_tuple(value):
        try:
            buckets.append(RangeBucket(item))
        except ValueError:
            continue
    return tuple(buckets)


def _range_source_type(value: Any) -> RangeSourceType:
    try:
        return RangeSourceType(str(value))
    except (TypeError, ValueError):
        return RangeSourceType.UNKNOWN_RANGE


def _range_confidence(value: Any) -> RangeConfidenceClass:
    try:
        return RangeConfidenceClass(str(value))
    except (TypeError, ValueError):
        return RangeConfidenceClass.UNKNOWN


def _range_import_status(value: Any) -> RangeImportStatus:
    try:
        return RangeImportStatus(str(value))
    except (TypeError, ValueError):
        return RangeImportStatus.UNKNOWN_RANGE


def _range_weighting_mode(value: Any) -> RangeWeightingMode:
    try:
        return RangeWeightingMode(str(value))
    except (TypeError, ValueError):
        return RangeWeightingMode.UNKNOWN


def _spot_family_value(value: Any) -> Optional[str]:
    if isinstance(value, FlopSpotFamily):
        return value.value
    if value in (None, ""):
        return None
    return str(value)


def _optional_str(value: Any) -> Optional[str]:
    if value in (None, ""):
        return None
    return str(value)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


__all__ = (
    "DEFAULT_POSTFLOP_RANGE_FILE",
    "DEFAULT_RANGE_IMPORTER_NEXT_MODULE",
    "POSTFLOP_DEFAULT_RANGE_SCHEMA",
    "RANGE_IMPORTER_VERSION",
    "RangeImporterError",
    "build_range_state_from_flop_context",
    "select_range_case_id",
)
