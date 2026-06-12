from __future__ import annotations

import importlib.util
import json
import types
from pathlib import Path
from typing import Any, Dict

RUNTIME_ROOT = Path("external") / "PokerVisionFinalVersionNoSolver_snapshot" / "PokerVision V1_2"
CAPTURE_MODULE_PATH = RUNTIME_ROOT / "postflop_clear_json_runtime_capture.py"
SITECUSTOMIZE_PATH = RUNTIME_ROOT / "sitecustomize.py"
FORBIDDEN_RUNTIME_ARTIFACT_DIRS = {
    "Decision_JSON",
    "Action_Decision_JSON",
    "Action_Runtime_Plan_JSON",
    "Action_Button_JSON",
    "Runtime_JSON",
}


def _load_capture_module():
    spec = importlib.util.spec_from_file_location("postflop_clear_json_runtime_capture_test", CAPTURE_MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sample_final_clear_json() -> Dict[str, Any]:
    return {
        "schema_version": "clear_json_v_test",
        "frame_id": "table_01_hand_12_flop",
        "table_id": "table_01",
        "hand_id": "hand_12",
        "board": {"street": "flop", "cards": ["As", "7d", "2c"]},
        "players": {
            "BTN": {"hero": True, "cards": ["Ah", "Kd"], "fold": False},
            "BB": {"hero": False, "cards": [], "fold": False},
        },
        "Total_pot": 6.5,
        "click_result": {"status": "dry_run", "dry_run": True},
    }


def test_v0971_runtime_capture_files_exist() -> None:
    assert CAPTURE_MODULE_PATH.exists()
    assert SITECUSTOMIZE_PATH.exists()


def test_v0971_capture_root_resolves_next_to_ui_display_cycle(tmp_path: Path) -> None:
    module = _load_capture_module()
    cycle_dir = tmp_path / "outputs" / "ui_display_cycle" / "current_cycle"

    root = module.resolve_postflop_clear_json_capture_root(cycle_dir)

    assert root == tmp_path / "outputs" / "postflop_live_clear_json"


def test_v0971_mirror_final_clear_json_writes_only_solver_readable_clear_json(tmp_path: Path) -> None:
    module = _load_capture_module()
    cycle_dir = tmp_path / "outputs" / "ui_display_cycle" / "current_cycle"
    final_path = cycle_dir / "Clear_JSON" / "table_01" / "table_01_hand_12_flop.json"
    clear_state = _sample_final_clear_json()

    mirror_path = module.mirror_final_clear_json_for_postflop_audit(
        clear_state=clear_state,
        cycle_dir=cycle_dir,
        table_id="table_01",
        final_clear_json_path=final_path,
    )

    assert mirror_path == tmp_path / "outputs" / "postflop_live_clear_json" / "table_01" / "table_01_hand_12_flop.clear.json"
    assert mirror_path.exists()
    assert json.loads(mirror_path.read_text(encoding="utf-8")) == clear_state
    assert mirror_path.name.endswith(".clear.json")

    created_dirs = {path.name for path in (tmp_path / "outputs").rglob("*") if path.is_dir()}
    assert not (created_dirs & FORBIDDEN_RUNTIME_ARTIFACT_DIRS)


def test_v0971_install_wrapper_preserves_original_final_clear_save_and_adds_mirror(tmp_path: Path) -> None:
    module = _load_capture_module()
    cycle_dir = tmp_path / "outputs" / "ui_display_cycle" / "current_cycle"
    logs: list[str] = []

    fake_display = types.ModuleType("display_analysis_cycle_fake")

    def original_save_clear_table_frame_json(*, clear_state: Dict[str, Any], cycle_dir: Path, table_id: str) -> Path:
        final_path = Path(cycle_dir) / "Clear_JSON" / table_id / "table_01_hand_12_flop.json"
        final_path.parent.mkdir(parents=True, exist_ok=True)
        final_path.write_text(json.dumps(clear_state, ensure_ascii=False, indent=2), encoding="utf-8")
        return final_path

    fake_display.save_clear_table_frame_json = original_save_clear_table_frame_json

    assert module.install_postflop_clear_json_runtime_capture(fake_display, logger=logs.append) is True
    assert module.install_postflop_clear_json_runtime_capture(fake_display, logger=logs.append) is True

    clear_state = _sample_final_clear_json()
    final_path = fake_display.save_clear_table_frame_json(
        clear_state=clear_state,
        cycle_dir=cycle_dir,
        table_id="table_01",
    )

    mirror_path = tmp_path / "outputs" / "postflop_live_clear_json" / "table_01" / "table_01_hand_12_flop.clear.json"
    assert final_path.exists()
    assert mirror_path.exists()
    assert json.loads(final_path.read_text(encoding="utf-8")) == clear_state
    assert json.loads(mirror_path.read_text(encoding="utf-8")) == clear_state
    assert any("mirrored Final Clear_JSON" in message for message in logs)


def test_v0971_sitecustomize_installs_capture_but_does_not_contain_click_or_decision_logic() -> None:
    text = SITECUSTOMIZE_PATH.read_text(encoding="utf-8")

    assert "install_postflop_clear_json_runtime_capture" in text
    assert "display_analysis_cycle" in text
    assert "Action_Button" not in text
    assert "runtime_plan" not in text.lower()
    assert "pyautogui" not in text
    assert "mouse" not in text.lower()
    assert "click(" not in text.lower()


def test_v0971_capture_module_does_not_import_action_or_click_runtime() -> None:
    text = CAPTURE_MODULE_PATH.read_text(encoding="utf-8")
    forbidden_fragments = [
        "Action_Button_Detector",
        "Action_Decision_JSON",
        "Action_Runtime_Plan_JSON",
        "pyautogui",
        "win32api",
        "mouse_event",
        "click_execution",
        "decision_json_builder",
        "action_runtime_plan_builder",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in text
