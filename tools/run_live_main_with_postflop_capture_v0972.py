"""Run PokerVision main.py with V0.9.7.2 postflop Clear_JSON capture installed.

This wrapper is for local real-live audit only. It does not create postflop
decisions, runtime plans, Action_Button payloads, or clicks. It only installs a
file-mirror wrapper around the existing Pending/Final Clear_JSON save functions
before executing the existing snapshot main.py.
"""
from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path

DEFAULT_LIVE_ROOT = Path("external") / "PokerVisionFinalVersionNoSolver_snapshot" / "PokerVision V1_2"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run live main.py with V0.9.7.2 postflop Clear_JSON capture.")
    parser.add_argument("--live-root", default=str(DEFAULT_LIVE_ROOT), help="Path to the PokerVision V1_2 snapshot root.")
    args = parser.parse_args()

    repo_root = Path.cwd()
    live_root = (repo_root / args.live_root).resolve()
    live_main = live_root / "main.py"
    if not live_main.exists():
        raise FileNotFoundError(f"Live main.py not found: {live_main}")

    live_root_text = str(live_root)
    if live_root_text not in sys.path:
        sys.path.insert(0, live_root_text)

    import display_analysis_cycle  # type: ignore
    from postflop_clear_json_runtime_capture import install_postflop_clear_json_runtime_capture

    installed = install_postflop_clear_json_runtime_capture(display_analysis_cycle)
    print(f"[POSTFLOP_CLEAR_JSON_CAPTURE] V0.9.7.2 install status: {installed}")
    print(f"[POSTFLOP_CLEAR_JSON_CAPTURE] running existing main.py: {live_main}")

    runpy.run_path(str(live_main), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
