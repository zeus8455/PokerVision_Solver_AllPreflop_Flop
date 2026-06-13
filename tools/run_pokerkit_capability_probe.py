"""PokerKit capability probe for V0.11.3.

This tool only checks whether the local PokerKit package can be imported and
whether the core symbols planned for later equity backend work are present.
It does not compute equity, run simulations, build ranges, create decisions,
create runtime plans, or touch the real PokerVision project.
"""

from __future__ import annotations

import importlib
import json
import sys
from dataclasses import asdict, dataclass, field
from importlib import metadata
from pathlib import Path
from typing import Any

SCHEMA = "pokervision_solver_postflop_pokerkit_capability_probe_v1"
VERSION_BLOCK = "V0.11.3"
BACKEND_NAME = "pokerkit"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "outputs" / "postflop_pokerkit_capability"
REPORT_PATH = REPORT_DIR / "latest_pokerkit_capability_report.json"

CORE_SYMBOL_CANDIDATES = (
    "NoLimitTexasHoldem",
    "Automation",
    "Mode",
    "State",
    "StandardHighHand",
    "Card",
    "Rank",
    "Suit",
    "Deck",
)


@dataclass(frozen=True)
class PokerKitCapabilityReport:
    schema: str = SCHEMA
    version_block: str = VERSION_BLOCK
    backend_name: str = BACKEND_NAME
    status: str = "backend_unavailable"
    importable: bool = False
    package_version: str | None = None
    module_file: str | None = None
    available_symbols: list[str] = field(default_factory=list)
    missing_symbols: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    real_project_touched: bool = False
    equity_calculation_executed: bool = False
    monte_carlo_executed: bool = False
    simulation_executed: bool = False
    range_logic_executed: bool = False
    decision_logic_executed: bool = False
    runtime_plan_created: bool = False
    physical_click_executed: bool = False

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


def _package_version() -> str | None:
    try:
        return metadata.version(BACKEND_NAME)
    except metadata.PackageNotFoundError:
        return None


def build_pokerkit_capability_report() -> PokerKitCapabilityReport:
    try:
        pokerkit_module = importlib.import_module(BACKEND_NAME)
    except Exception as exc:  # pragma: no cover - depends on local environment
        return PokerKitCapabilityReport(
            status="backend_unavailable",
            importable=False,
            package_version=_package_version(),
            available_symbols=[],
            missing_symbols=list(CORE_SYMBOL_CANDIDATES),
            notes=["pokerkit_not_importable", f"import_error:{type(exc).__name__}"],
        )

    available_symbols = [
        symbol for symbol in CORE_SYMBOL_CANDIDATES if hasattr(pokerkit_module, symbol)
    ]
    missing_symbols = [
        symbol for symbol in CORE_SYMBOL_CANDIDATES if symbol not in available_symbols
    ]

    status = "available" if not missing_symbols else "partial"
    notes = ["pokerkit_importable"]
    if not missing_symbols:
        notes.append("core_symbol_candidates_available")
    else:
        notes.append("core_symbol_candidates_partial")

    return PokerKitCapabilityReport(
        status=status,
        importable=True,
        package_version=_package_version(),
        module_file=str(getattr(pokerkit_module, "__file__", "")) or None,
        available_symbols=available_symbols,
        missing_symbols=missing_symbols,
        notes=notes,
    )


def write_report(report: PokerKitCapabilityReport, path: Path = REPORT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report.to_json_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    report = build_pokerkit_capability_report()
    write_report(report)
    print(json.dumps(report.to_json_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
