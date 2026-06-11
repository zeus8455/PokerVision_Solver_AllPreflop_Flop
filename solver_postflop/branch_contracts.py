"""Contracts for postflop solver branch routing results."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any, Mapping, Optional


class SolverBranch(str, Enum):
    """Supported branch labels for routing a trusted SolverInput."""

    PREFLOP_NOT_HANDLED = "preflop_not_handled"
    FLOP = "flop"
    TURN_NOT_IMPLEMENTED_YET = "turn_not_implemented_yet"
    RIVER_NOT_IMPLEMENTED_YET = "river_not_implemented_yet"
    UNSUPPORTED = "unsupported"


class SolverBranchFamily(str, Enum):
    """High-level family for the selected branch."""

    NON_POSTFLOP = "non_postflop"
    POSTFLOP_FLOP = "postflop_flop"
    POSTFLOP_TURN = "postflop_turn"
    POSTFLOP_RIVER = "postflop_river"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True, slots=True)
class SolverBranchResult:
    """Result produced by the future branch router.

    The result is metadata only. It does not contain a poker action,
    sizing instruction, executable plan, or UI command.
    """

    case_id: Optional[str]
    source_file: str
    branch: SolverBranch
    branch_family: SolverBranchFamily
    next_module: str
    branch_reason: str
    is_decision_branch_enabled: bool = False
    is_runtime_branch_enabled: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation of the branch result."""

        return _json_safe(asdict(self))


DEFAULT_NEXT_MODULE_BY_BRANCH: Mapping[SolverBranch, str] = {
    SolverBranch.PREFLOP_NOT_HANDLED: "preflop_solver_external_or_skip",
    SolverBranch.FLOP: "flop_context_builder",
    SolverBranch.TURN_NOT_IMPLEMENTED_YET: "turn_branch_not_implemented_yet",
    SolverBranch.RIVER_NOT_IMPLEMENTED_YET: "river_branch_not_implemented_yet",
    SolverBranch.UNSUPPORTED: "unsupported_branch_report",
}


DEFAULT_FAMILY_BY_BRANCH: Mapping[SolverBranch, SolverBranchFamily] = {
    SolverBranch.PREFLOP_NOT_HANDLED: SolverBranchFamily.NON_POSTFLOP,
    SolverBranch.FLOP: SolverBranchFamily.POSTFLOP_FLOP,
    SolverBranch.TURN_NOT_IMPLEMENTED_YET: SolverBranchFamily.POSTFLOP_TURN,
    SolverBranch.RIVER_NOT_IMPLEMENTED_YET: SolverBranchFamily.POSTFLOP_RIVER,
    SolverBranch.UNSUPPORTED: SolverBranchFamily.UNSUPPORTED,
}


def branch_family_for(branch: SolverBranch) -> SolverBranchFamily:
    """Return the default family for a branch label."""

    return DEFAULT_FAMILY_BY_BRANCH[branch]


def next_module_for(branch: SolverBranch) -> str:
    """Return the default next module for a branch label."""

    return DEFAULT_NEXT_MODULE_BY_BRANCH[branch]


def _json_safe(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value
