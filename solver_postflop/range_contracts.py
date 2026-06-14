"""Contracts for the postflop baseline range state layer.

V0.12.1 scope: JSON-safe contract objects only.
This module defines baseline range metadata that later importer modules will
produce from already-built FlopContext / spot context. It does not import range
files, remove blocked combos, narrow ranges by action, compute equity, build a
runtime plan, or issue UI commands.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any, Mapping, Optional


class RangeSourceType(str, Enum):
    """Supported baseline range source levels for future importer modules."""

    EXISTING_PROJECT_RANGES = "existing_project_ranges"
    POSTFLOP_DEFAULT_RANGES = "postflop_default_ranges"
    SYNTHETIC_TEST_RANGES = "synthetic_test_ranges"
    UNKNOWN_RANGE = "unknown_range"


class RangeImportStatus(str, Enum):
    """Structured status returned with a RangeState."""

    IMPORTED = "imported"
    SYNTHETIC_IMPORTED = "synthetic_imported"
    UNKNOWN_RANGE = "unknown_range"
    SOURCE_UNAVAILABLE = "source_unavailable"
    UNSUPPORTED_CONTEXT = "unsupported_context"


class RangeConfidenceClass(str, Enum):
    """Confidence bucket for the selected baseline range."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class RangeBucket(str, Enum):
    """Coarse baseline hand groups carried forward for future modules."""

    PREMIUM_PAIRS = "premium_pairs"
    STRONG_BROADWAYS = "strong_broadways"
    SUITED_BROADWAYS = "suited_broadways"
    SUITED_CONNECTORS = "suited_connectors"
    OFFSUIT_BROADWAYS = "offsuit_broadways"
    POCKET_PAIRS = "pocket_pairs"
    ACE_X_SUITED = "ace_x_suited"
    DEFENSE_RANGE = "defense_range"
    UNKNOWN_BUCKET = "unknown_bucket"


class RangeWeightingMode(str, Enum):
    """How combo groups are weighted in the baseline state."""

    FLAT_BASELINE = "flat_baseline"
    SOURCE_WEIGHTED = "source_weighted"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class RangeSourceInfo:
    """Metadata describing where a baseline range was selected from."""

    source_type: RangeSourceType = RangeSourceType.UNKNOWN_RANGE
    source_name: str = "unknown_range"
    source_file: Optional[str] = None
    source_version: Optional[str] = None
    is_existing_project_source: bool = False
    is_synthetic_test_source: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation of the source info."""

        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class PlayerRangeState:
    """Baseline range assigned to one player without later refinements.

    combo_groups stores canonical compact combos per bucket, for example
    {"suited_broadways": ("AsKs", "AhKh")}. V0.12.1 only carries these
    combos forward; later versions may use them as inputs.
    """

    player_id: str
    position: Optional[str] = None
    role: Optional[str] = None
    range_name: str = "unknown_range"
    range_source: RangeSourceType = RangeSourceType.UNKNOWN_RANGE
    combo_groups: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    hand_class_groups: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    range_buckets: tuple[RangeBucket, ...] = field(default_factory=tuple)
    weighting_mode: RangeWeightingMode = RangeWeightingMode.UNKNOWN
    confidence: RangeConfidenceClass = RangeConfidenceClass.UNKNOWN
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation of the player range."""

        return _json_safe(asdict(self))


@dataclass(frozen=True, slots=True)
class RangeState:
    """Baseline range state selected from already-built spot context."""

    case_id: Optional[str]
    source_file: str
    spot_family: Optional[str] = None
    pot_type: Optional[str] = None
    hero_position: Optional[str] = None
    opponent_positions: tuple[str, ...] = field(default_factory=tuple)
    hero_range_state: Optional[PlayerRangeState] = None
    opponent_range_states: tuple[PlayerRangeState, ...] = field(default_factory=tuple)
    range_source_info: RangeSourceInfo = field(default_factory=RangeSourceInfo)
    range_confidence: RangeConfidenceClass = RangeConfidenceClass.UNKNOWN
    range_import_status: RangeImportStatus = RangeImportStatus.UNKNOWN_RANGE
    range_buckets: tuple[RangeBucket, ...] = field(default_factory=tuple)
    next_module: str = "blocker_filtering_later"
    fields_used: tuple[str, ...] = field(default_factory=tuple)
    fields_not_provided: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation of the range state."""

        return _json_safe(asdict(self))


RANGE_CONTRACT_VERSION = "v0.12.1"
DEFAULT_RANGE_NEXT_MODULE = "blocker_filtering_later"
DEFAULT_UNKNOWN_RANGE_NAME = "unknown_range"
RANGE_SOURCE_TYPES: tuple[RangeSourceType, ...] = tuple(RangeSourceType)
RANGE_IMPORT_STATUSES: tuple[RangeImportStatus, ...] = tuple(RangeImportStatus)
RANGE_CONFIDENCE_CLASSES: tuple[RangeConfidenceClass, ...] = tuple(RangeConfidenceClass)
RANGE_BUCKETS: tuple[RangeBucket, ...] = tuple(RangeBucket)
RANGE_WEIGHTING_MODES: tuple[RangeWeightingMode, ...] = tuple(RangeWeightingMode)


__all__ = (
    "DEFAULT_RANGE_NEXT_MODULE",
    "DEFAULT_UNKNOWN_RANGE_NAME",
    "RANGE_BUCKETS",
    "RANGE_CONFIDENCE_CLASSES",
    "RANGE_CONTRACT_VERSION",
    "RANGE_IMPORT_STATUSES",
    "RANGE_SOURCE_TYPES",
    "RANGE_WEIGHTING_MODES",
    "PlayerRangeState",
    "RangeBucket",
    "RangeConfidenceClass",
    "RangeImportStatus",
    "RangeSourceInfo",
    "RangeSourceType",
    "RangeState",
    "RangeWeightingMode",
)


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
