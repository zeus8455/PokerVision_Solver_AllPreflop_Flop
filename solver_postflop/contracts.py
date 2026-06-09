from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


class ContractValidationError(ValueError):
    """Raised when a postflop contract receives invalid data."""


class _StringEnum(str, Enum):
    @classmethod
    def values(cls) -> List[str]:
        return [item.value for item in cls]

    @classmethod
    def from_value(cls, value: Any):
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise ContractValidationError(f"Unsupported {cls.__name__}: {value!r}") from exc
        raise ContractValidationError(f"Unsupported {cls.__name__}: {value!r}")


class PostflopSourceType(_StringEnum):
    DARK_JSON = "dark_json"
    PENDING_JSON = "pending_json"
    SERVICE_JSON = "service_json"
    CURRENT_CYCLE_JSON = "current_cycle_json"
    RUNTIME_JSON = "runtime_json"
    SOLVER_PAYLOAD_JSON = "solver_payload_json"
    FINAL_CLEAR_JSON = "final_clear_json"
    MANUAL_LIVE_LIKE_JSON = "manual_live_like_json"
    UNKNOWN = "unknown"

    @property
    def is_manual_live_like(self) -> bool:
        return self is PostflopSourceType.MANUAL_LIVE_LIKE_JSON

    @property
    def can_be_real_project_source(self) -> bool:
        return self not in {PostflopSourceType.MANUAL_LIVE_LIKE_JSON, PostflopSourceType.UNKNOWN}

    @property
    def requires_click_cycle_by_type(self) -> bool:
        return self is PostflopSourceType.FINAL_CLEAR_JSON


class ContractSeverity(_StringEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class PostflopConfidence(_StringEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class RawSourceLoadStatus(_StringEnum):
    LOADED = "loaded"
    INVALID_JSON = "invalid_json"
    MISSING_FILE = "missing_file"
    UNREADABLE = "unreadable"
    EMPTY = "empty"

class DiscoveryStatus(_StringEnum):
    OK = "ok"
    PARTIAL = "partial"
    FAILED = "failed"
    EMPTY = "empty"

class NormalizationStatus(_StringEnum):
    OK = "ok"
    PARTIAL = "partial"
    INVALID = "invalid"
    UNKNOWN = "unknown"


def _require_non_empty_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractValidationError(f"{field_name} must be a non-empty string")
    return value


def _ensure_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ContractValidationError(f"{field_name} must be a bool")
    return value


def _ensure_dict(value: Any, field_name: str) -> Dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ContractValidationError(f"{field_name} must be a dict")
    return value


def _ensure_list(value: Any, field_name: str) -> List[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ContractValidationError(f"{field_name} must be a list")
    return value


def _ensure_non_negative_number(value: Any, field_name: str, *, allow_none: bool = False) -> Optional[float]:
    if value is None and allow_none:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractValidationError(f"{field_name} must be a non-negative number")
    numeric = float(value)
    if numeric < 0:
        raise ContractValidationError(f"{field_name} must be non-negative")
    return numeric


def _warning_from_any(value: Any) -> "ModuleWarning":
    if isinstance(value, ModuleWarning):
        return value
    if isinstance(value, dict):
        return ModuleWarning.from_dict(value)
    raise ContractValidationError("warnings must contain ModuleWarning or dict items")


def _error_from_any(value: Any) -> "ModuleError":
    if isinstance(value, ModuleError):
        return value
    if isinstance(value, dict):
        return ModuleError.from_dict(value)
    raise ContractValidationError("errors must contain ModuleError or dict items")


@dataclass
class ModuleWarning:
    code: str
    message: str
    severity: ContractSeverity | str = ContractSeverity.WARNING
    source_file: Optional[str] = None
    field_name: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.code = _require_non_empty_string(self.code, "code")
        self.message = _require_non_empty_string(self.message, "message")
        self.severity = ContractSeverity.from_value(self.severity)
        if self.severity is ContractSeverity.ERROR:
            raise ContractValidationError("ModuleWarning cannot use error severity")
        self.context = _ensure_dict(self.context, "context")

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ModuleWarning":
        return cls(
            code=payload.get("code", ""),
            message=payload.get("message", ""),
            severity=payload.get("severity", ContractSeverity.WARNING.value),
            source_file=payload.get("source_file"),
            field_name=payload.get("field_name"),
            context=payload.get("context") or {},
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "source_file": self.source_file,
            "field_name": self.field_name,
            "context": dict(self.context),
        }


@dataclass
class ModuleError:
    code: str
    message: str
    severity: ContractSeverity | str = ContractSeverity.ERROR
    source_file: Optional[str] = None
    field_name: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    is_fatal: bool = True

    def __post_init__(self) -> None:
        self.code = _require_non_empty_string(self.code, "code")
        self.message = _require_non_empty_string(self.message, "message")
        self.severity = ContractSeverity.from_value(self.severity)
        if self.severity is not ContractSeverity.ERROR:
            raise ContractValidationError("ModuleError must use error severity")
        self.context = _ensure_dict(self.context, "context")
        self.is_fatal = _ensure_bool(self.is_fatal, "is_fatal")

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ModuleError":
        return cls(
            code=payload.get("code", ""),
            message=payload.get("message", ""),
            severity=payload.get("severity", ContractSeverity.ERROR.value),
            source_file=payload.get("source_file"),
            field_name=payload.get("field_name"),
            context=payload.get("context") or {},
            is_fatal=payload.get("is_fatal", True),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "source_file": self.source_file,
            "field_name": self.field_name,
            "context": dict(self.context),
            "is_fatal": self.is_fatal,
        }


@dataclass
class PostflopSourceCandidate:
    source_file: str
    source_type: PostflopSourceType | str
    table_id: str = "unknown"
    hand_id: str = "unknown"
    detected_at: Optional[str] = None
    has_board_cards: bool = False
    has_hero_cards: bool = False
    has_players: bool = False
    has_actions: bool = False
    can_be_normalized: bool = False
    confidence: PostflopConfidence | str = PostflopConfidence.UNKNOWN
    warnings: List[ModuleWarning | Dict[str, Any]] = field(default_factory=list)
    is_real_project_source: bool = False
    is_manual_live_like_source: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.source_file = _require_non_empty_string(self.source_file, "source_file")
        self.source_type = PostflopSourceType.from_value(self.source_type)
        self.confidence = PostflopConfidence.from_value(self.confidence)
        self.table_id = self.table_id if isinstance(self.table_id, str) and self.table_id.strip() else "unknown"
        self.hand_id = self.hand_id if isinstance(self.hand_id, str) and self.hand_id.strip() else "unknown"
        self.has_board_cards = _ensure_bool(self.has_board_cards, "has_board_cards")
        self.has_hero_cards = _ensure_bool(self.has_hero_cards, "has_hero_cards")
        self.has_players = _ensure_bool(self.has_players, "has_players")
        self.has_actions = _ensure_bool(self.has_actions, "has_actions")
        self.can_be_normalized = _ensure_bool(self.can_be_normalized, "can_be_normalized")
        self.is_real_project_source = _ensure_bool(self.is_real_project_source, "is_real_project_source")
        self.is_manual_live_like_source = _ensure_bool(self.is_manual_live_like_source, "is_manual_live_like_source")
        if self.source_type.is_manual_live_like:
            self.is_manual_live_like_source = True
        if self.is_manual_live_like_source and self.is_real_project_source:
            raise ContractValidationError("manual live-like source cannot also be marked as real project source")
        if self.source_type.is_manual_live_like and self.is_real_project_source:
            raise ContractValidationError("manual_live_like_json cannot be a real project source")
        self.metadata = _ensure_dict(self.metadata, "metadata")
        self.warnings = [_warning_from_any(w) for w in self.warnings]
        if self.table_id == "unknown":
            self.warnings.append(ModuleWarning(
                code="missing_table_id",
                message="table_id is unknown for source candidate.",
                source_file=self.source_file,
                field_name="table_id",
                context={"source_type": self.source_type.value},
            ))
        if self.hand_id == "unknown":
            self.warnings.append(ModuleWarning(
                code="missing_hand_id",
                message="hand_id is unknown for source candidate.",
                source_file=self.source_file,
                field_name="hand_id",
                context={"source_type": self.source_type.value},
            ))

    @property
    def is_real_source_allowed_by_type(self) -> bool:
        return self.source_type.can_be_real_project_source

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_file": self.source_file,
            "source_type": self.source_type.value,
            "table_id": self.table_id,
            "hand_id": self.hand_id,
            "detected_at": self.detected_at,
            "has_board_cards": self.has_board_cards,
            "has_hero_cards": self.has_hero_cards,
            "has_players": self.has_players,
            "has_actions": self.has_actions,
            "can_be_normalized": self.can_be_normalized,
            "confidence": self.confidence.value,
            "warnings": [warning.to_dict() for warning in self.warnings],
            "is_real_project_source": self.is_real_project_source,
            "is_manual_live_like_source": self.is_manual_live_like_source,
            "metadata": dict(self.metadata),
        }


@dataclass
class PostflopRawSource:
    candidate: PostflopSourceCandidate
    raw_data: Dict[str, Any] = field(default_factory=dict)
    load_status: RawSourceLoadStatus | str = RawSourceLoadStatus.LOADED
    warnings: List[ModuleWarning | Dict[str, Any]] = field(default_factory=list)
    errors: List[ModuleError | Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.candidate, PostflopSourceCandidate):
            raise ContractValidationError("candidate must be a PostflopSourceCandidate")
        self.raw_data = _ensure_dict(self.raw_data, "raw_data")
        self.load_status = RawSourceLoadStatus.from_value(self.load_status)
        self.warnings = [_warning_from_any(w) for w in self.warnings]
        self.errors = [_error_from_any(e) for e in self.errors]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate": self.candidate.to_dict(),
            "raw_data": dict(self.raw_data),
            "load_status": self.load_status.value,
            "warnings": [warning.to_dict() for warning in self.warnings],
            "errors": [error.to_dict() for error in self.errors],
        }


@dataclass
class PostflopSourceDiscoveryResult:
    input_root: str
    candidates: List[PostflopSourceCandidate] = field(default_factory=list)
    raw_sources: List[PostflopRawSource] = field(default_factory=list)
    warnings: List[ModuleWarning | Dict[str, Any]] = field(default_factory=list)
    errors: List[ModuleError | Dict[str, Any]] = field(default_factory=list)
    status: DiscoveryStatus | str = DiscoveryStatus.OK

    def __post_init__(self) -> None:
        self.input_root = _require_non_empty_string(self.input_root, "input_root")
        self.status = DiscoveryStatus.from_value(self.status)
        if not all(isinstance(candidate, PostflopSourceCandidate) for candidate in self.candidates):
            raise ContractValidationError("candidates must contain only PostflopSourceCandidate items")
        if not all(isinstance(raw_source, PostflopRawSource) for raw_source in self.raw_sources):
            raise ContractValidationError("raw_sources must contain only PostflopRawSource items")
        self.warnings = [_warning_from_any(w) for w in self.warnings]
        self.errors = [_error_from_any(e) for e in self.errors]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_root": self.input_root,
            "status": self.status.value,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "raw_sources": [raw_source.to_dict() for raw_source in self.raw_sources],
            "warnings": [warning.to_dict() for warning in self.warnings],
            "errors": [error.to_dict() for error in self.errors],
        }


@dataclass
class PostflopPlayerSnapshot:
    seat_id: str
    player_name: str = "unknown"
    stack: Optional[float] = None
    committed: float = 0.0
    position: Optional[str] = None
    is_hero: bool = False
    is_active: bool = False
    is_folded: bool = False
    is_sitout: bool = False
    is_all_in: bool = False
    raw_state: Dict[str, Any] = field(default_factory=dict)
    warnings: List[ModuleWarning | Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.seat_id = _require_non_empty_string(str(self.seat_id), "seat_id")
        self.player_name = self.player_name if isinstance(self.player_name, str) and self.player_name.strip() else "unknown"
        self.stack = _ensure_non_negative_number(self.stack, "stack", allow_none=True)
        self.committed = _ensure_non_negative_number(self.committed, "committed")
        self.is_hero = _ensure_bool(self.is_hero, "is_hero")
        self.is_active = _ensure_bool(self.is_active, "is_active")
        self.is_folded = _ensure_bool(self.is_folded, "is_folded")
        self.is_sitout = _ensure_bool(self.is_sitout, "is_sitout")
        self.is_all_in = _ensure_bool(self.is_all_in, "is_all_in")
        self.raw_state = _ensure_dict(self.raw_state, "raw_state")
        self.warnings = [_warning_from_any(w) for w in self.warnings]
        if self.player_name == "unknown":
            self.warnings.append(ModuleWarning(
                code="missing_player_name",
                message="player_name is unknown for player snapshot.",
                field_name="player_name",
                context={"seat_id": self.seat_id},
            ))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seat_id": self.seat_id,
            "player_name": self.player_name,
            "stack": self.stack,
            "committed": self.committed,
            "position": self.position,
            "is_hero": self.is_hero,
            "is_active": self.is_active,
            "is_folded": self.is_folded,
            "is_sitout": self.is_sitout,
            "is_all_in": self.is_all_in,
            "raw_state": dict(self.raw_state),
            "warnings": [warning.to_dict() for warning in self.warnings],
        }


@dataclass
class PostflopBoardSnapshot:
    cards: List[str] = field(default_factory=list)
    declared_street: Optional[str] = None
    raw_board: Dict[str, Any] = field(default_factory=dict)
    warnings: List[ModuleWarning | Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.cards = [str(card) for card in _ensure_list(self.cards, "cards")]
        if len(self.cards) > 5:
            raise ContractValidationError("board cards cannot contain more than 5 cards")
        self.raw_board = _ensure_dict(self.raw_board, "raw_board")
        self.warnings = [_warning_from_any(w) for w in self.warnings]
        if len(set(self.cards)) != len(self.cards):
            self.warnings.append(ModuleWarning(
                code="duplicate_board_cards",
                message="board contains duplicate cards; final validation belongs to street detector.",
                field_name="cards",
                context={"cards": list(self.cards)},
            ))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cards": list(self.cards),
            "declared_street": self.declared_street,
            "raw_board": dict(self.raw_board),
            "warnings": [warning.to_dict() for warning in self.warnings],
        }


@dataclass
class PostflopActionSnapshot:
    allowed_actions: List[str] = field(default_factory=list)
    to_call: float = 0.0
    min_raise: Optional[float] = None
    bet_size_options: List[Any] = field(default_factory=list)
    raw_action_context: Dict[str, Any] = field(default_factory=dict)
    warnings: List[ModuleWarning | Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.allowed_actions = [str(action) for action in _ensure_list(self.allowed_actions, "allowed_actions")]
        self.to_call = _ensure_non_negative_number(self.to_call, "to_call")
        self.min_raise = _ensure_non_negative_number(self.min_raise, "min_raise", allow_none=True)
        self.bet_size_options = _ensure_list(self.bet_size_options, "bet_size_options")
        self.raw_action_context = _ensure_dict(self.raw_action_context, "raw_action_context")
        self.warnings = [_warning_from_any(w) for w in self.warnings]
        if not self.allowed_actions:
            self.warnings.append(ModuleWarning(
                code="missing_allowed_actions",
                message="allowed_actions are missing or empty.",
                field_name="allowed_actions",
            ))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed_actions": list(self.allowed_actions),
            "to_call": self.to_call,
            "min_raise": self.min_raise,
            "bet_size_options": list(self.bet_size_options),
            "raw_action_context": dict(self.raw_action_context),
            "warnings": [warning.to_dict() for warning in self.warnings],
        }


@dataclass
class NormalizedPostflopFrame:
    source_type: PostflopSourceType | str
    source_file: str
    table_id: str = "unknown"
    hand_id: str = "unknown"
    street_candidate: str = "unknown"
    hero_cards: List[str] = field(default_factory=list)
    board_cards: List[str] = field(default_factory=list)
    pot: float = 0.0
    to_call: float = 0.0
    players: List[PostflopPlayerSnapshot] = field(default_factory=list)
    raw_players: Any = field(default_factory=list)
    allowed_actions: List[str] = field(default_factory=list)
    raw_action_context: Dict[str, Any] = field(default_factory=dict)
    normalization_status: NormalizationStatus | str = NormalizationStatus.UNKNOWN
    normalization_warnings: List[ModuleWarning | Dict[str, Any]] = field(default_factory=list)
    board_snapshot: Optional[PostflopBoardSnapshot] = None
    action_snapshot: Optional[PostflopActionSnapshot] = None
    raw_frame: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.source_type = PostflopSourceType.from_value(self.source_type)
        self.source_file = _require_non_empty_string(self.source_file, "source_file")
        self.table_id = self.table_id if isinstance(self.table_id, str) and self.table_id.strip() else "unknown"
        self.hand_id = self.hand_id if isinstance(self.hand_id, str) and self.hand_id.strip() else "unknown"
        self.street_candidate = self.street_candidate if isinstance(self.street_candidate, str) and self.street_candidate.strip() else "unknown"
        self.hero_cards = [str(card) for card in _ensure_list(self.hero_cards, "hero_cards")]
        self.board_cards = [str(card) for card in _ensure_list(self.board_cards, "board_cards")]
        if len(self.hero_cards) > 2:
            raise ContractValidationError("hero_cards cannot contain more than 2 cards")
        if len(self.board_cards) > 5:
            raise ContractValidationError("board_cards cannot contain more than 5 cards")
        self.pot = _ensure_non_negative_number(self.pot, "pot")
        self.to_call = _ensure_non_negative_number(self.to_call, "to_call")
        if not all(isinstance(player, PostflopPlayerSnapshot) for player in self.players):
            raise ContractValidationError("players must contain only PostflopPlayerSnapshot items")
        self.allowed_actions = [str(action) for action in _ensure_list(self.allowed_actions, "allowed_actions")]
        self.raw_action_context = _ensure_dict(self.raw_action_context, "raw_action_context")
        self.normalization_status = NormalizationStatus.from_value(self.normalization_status)
        self.normalization_warnings = [_warning_from_any(w) for w in self.normalization_warnings]
        if self.board_snapshot is None:
            self.board_snapshot = PostflopBoardSnapshot(cards=list(self.board_cards), declared_street=self.street_candidate)
        elif not isinstance(self.board_snapshot, PostflopBoardSnapshot):
            raise ContractValidationError("board_snapshot must be a PostflopBoardSnapshot")
        if self.action_snapshot is None:
            self.action_snapshot = PostflopActionSnapshot(
                allowed_actions=list(self.allowed_actions),
                to_call=self.to_call,
                raw_action_context=dict(self.raw_action_context),
            )
        elif not isinstance(self.action_snapshot, PostflopActionSnapshot):
            raise ContractValidationError("action_snapshot must be a PostflopActionSnapshot")
        self.raw_frame = _ensure_dict(self.raw_frame, "raw_frame")
        if self.table_id == "unknown":
            self.normalization_warnings.append(ModuleWarning(
                code="missing_table_id",
                message="table_id is unknown for normalized frame.",
                source_file=self.source_file,
                field_name="table_id",
            ))
        if self.hand_id == "unknown":
            self.normalization_warnings.append(ModuleWarning(
                code="missing_hand_id",
                message="hand_id is unknown for normalized frame.",
                source_file=self.source_file,
                field_name="hand_id",
            ))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_type": self.source_type.value,
            "source_file": self.source_file,
            "table_id": self.table_id,
            "hand_id": self.hand_id,
            "street_candidate": self.street_candidate,
            "hero_cards": list(self.hero_cards),
            "board_cards": list(self.board_cards),
            "pot": self.pot,
            "to_call": self.to_call,
            "players": [player.to_dict() for player in self.players],
            "raw_players": self.raw_players,
            "allowed_actions": list(self.allowed_actions),
            "raw_action_context": dict(self.raw_action_context),
            "normalization_status": self.normalization_status.value,
            "normalization_warnings": [warning.to_dict() for warning in self.normalization_warnings],
            "board_snapshot": self.board_snapshot.to_dict() if self.board_snapshot else None,
            "action_snapshot": self.action_snapshot.to_dict() if self.action_snapshot else None,
            "raw_frame": dict(self.raw_frame),
        }
