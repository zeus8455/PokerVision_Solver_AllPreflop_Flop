"""Best-effort startup installer for V0.9.7.2 postflop Clear_JSON capture.

This file is intentionally not the only supported install path. The reliable
V0.9.7.2 live-audit path is tools/run_live_main_with_postflop_capture_v0972.py,
which imports display_analysis_cycle, installs the wrapper, then runs main.py.
"""
from __future__ import annotations

try:
    import display_analysis_cycle as _display_analysis_cycle
    from postflop_clear_json_runtime_capture import install_postflop_clear_json_runtime_capture

    install_postflop_clear_json_runtime_capture(_display_analysis_cycle)
except Exception as _exc:  # pragma: no cover - startup diagnostic only
    print(f"[POSTFLOP_CLEAR_JSON_CAPTURE] sitecustomize install failed: {_exc}")
