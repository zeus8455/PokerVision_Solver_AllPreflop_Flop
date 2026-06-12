"""Auto-install V0.9.7.1 postflop Clear_JSON mirror for live main.py runs.

Python imports sitecustomize at interpreter startup when this snapshot directory is
on sys.path. The hook wraps only Final Clear_JSON publication and is deliberately
limited to file mirroring.
"""
from __future__ import annotations

try:
    import display_analysis_cycle as _display_analysis_cycle
    from postflop_clear_json_runtime_capture import install_postflop_clear_json_runtime_capture

    install_postflop_clear_json_runtime_capture(_display_analysis_cycle)
except Exception as _exc:  # pragma: no cover - startup diagnostic only
    print(f"[POSTFLOP_CLEAR_JSON_CAPTURE] sitecustomize install failed: {_exc}")
