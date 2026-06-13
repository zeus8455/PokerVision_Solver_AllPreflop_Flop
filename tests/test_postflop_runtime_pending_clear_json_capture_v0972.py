from __future__ import annotations

import importlib.util
import json
import types
from pathlib import Path
from typing import Any, Dict

RUNTIME_ROOT = Path("external") / "PokerVisionFinalVersionNoSolver_snapshot" / "PokerVision V1_2"
CAPTURE_MODULE_PATH = RUNTIME_ROOT / "postflop_clear_json_runtime_capture.py"
SITECUSTOMIZE_PATH = RUNTIME_ROOT / "sitecustomize.py"
RUNNER_PATH = Path("tools/run_live_main_with_postflop_capture_v0972.py")


def _load_capture_module():
    spec = importlib.util.spec_from_file_location("postflop_clear_json_runtime_capture_v0972_test", CAPTURE_MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sample_clear_json(street: str = "flop") -> Dict[str, Any]:
    return {
        "schema_version": "clear_json_v_test",
        "frame_id": f"table_01_hand_12_{street}",
        "table_id": "table_01",
        "hand_id": "hand_12",
        "board": {"street": street, "cards": ["As", "7d", "2c"] if street == "flop" else ["As", "7d", "2c", "4h"]},
        "players": {
            "BTN": {"hero": True, "cards": ["Ah", "Kd"], "fold": False},
            "BB": {"hero": False, "cards": [], "fold": False},
        },
        "Total_pot": 6.5,
    }


def test_v0972_capture_files_exist() -> None:
    assert CAPTURE_MODULE_PATH.exists()
    assert SITECUSTOMIZE_PATH.exists()
    assert RUNNER_PATH.exists()


def test_v0972_pending_postflop_clear_json_is_mirrored_with_pending_metadata(tmp_path: Path) -> None:
    module = _load_capture_module()
    cycle_dir = tmp_path / "outputs" / "ui_display_cycle" / "current_cycle"
    pending_path = cycle_dir / "Clear_JSON_Pending" / "table_01" / "table_01_hand_12_flop.pending.json"

    mirror_path = module.mirror_postflop_pending_clear_json_for_audit(
        clear_state=_sample_clear_json("flop"),
        cycle_dir=cycle_dir,
        table_id="table_01",
        pending_clear_json_path=pending_path,
    )

    expected = tmp_path / "outputs" / "postflop_live_clear_json" / "table_01" / "table_01_hand_12_flop.clear.json"
    assert mirror_path == expected
    assert expected.exists()
    payload = json.loads(expected.read_text(encoding="utf-8"))
    metadata = payload["postflop_live_capture"]
    assert metadata["schema_version"] == "postflop_clear_json_runtime_capture_v0_9_7_2"
    assert metadata["capture_stage"] == "pending_clear_json"
    assert metadata["final_clear_confirmed"] is False
    assert metadata["solver_input_allowed_for_v090_audit"] is True
    assert metadata["solver_input_allowed_for_decision"] is False
    assert metadata["source_type"] == "clear_json_pending"
    assert metadata["source_path"].endswith("table_01_hand_12_flop.pending.json")


def test_v0972_preflop_pending_clear_json_is_not_mirrored(tmp_path: Path) -> None:
    module = _load_capture_module()
    cycle_dir = tmp_path / "outputs" / "ui_display_cycle" / "current_cycle"

    mirror_path = module.mirror_postflop_pending_clear_json_for_audit(
        clear_state=_sample_clear_json("preflop"),
        cycle_dir=cycle_dir,
        table_id="table_01",
        pending_clear_json_path=cycle_dir / "Clear_JSON_Pending" / "table_01" / "table_01_hand_12_preflop.pending.json",
    )

    assert mirror_path is None
    assert not (tmp_path / "outputs" / "postflop_live_clear_json").exists()


def test_v0972_final_postflop_clear_json_is_mirrored_with_final_metadata(tmp_path: Path) -> None:
    module = _load_capture_module()
    cycle_dir = tmp_path / "outputs" / "ui_display_cycle" / "current_cycle"
    final_path = cycle_dir / "Clear_JSON" / "table_01" / "table_01_hand_12_turn_01.json"

    mirror_path = module.mirror_postflop_final_clear_json_for_audit(
        clear_state=_sample_clear_json("turn"),
        cycle_dir=cycle_dir,
        table_id="table_01",
        final_clear_json_path=final_path,
    )

    assert mirror_path == tmp_path / "outputs" / "postflop_live_clear_json" / "table_01" / "table_01_hand_12_turn_01.clear.json"
    payload = json.loads(mirror_path.read_text(encoding="utf-8"))
    metadata = payload["postflop_live_capture"]
    assert metadata["capture_stage"] == "final_clear_json"
    assert metadata["final_clear_confirmed"] is True
    assert metadata["solver_input_allowed_for_v090_audit"] is True
    assert metadata["solver_input_allowed_for_decision"] is False
    assert metadata["source_type"] == "clear_json_final"


def test_v0972_install_wrapper_preserves_pending_and_final_saves(tmp_path: Path) -> None:
    module = _load_capture_module()
    cycle_dir = tmp_path / "outputs" / "ui_display_cycle" / "current_cycle"
    logs: list[str] = []
    fake_display = types.ModuleType("display_analysis_cycle_fake")

    def original_pending(*, clear_state: Dict[str, Any], cycle_dir: Path, table_id: str) -> Path:
        path = Path(cycle_dir) / "Clear_JSON_Pending" / table_id / f"{clear_state['frame_id']}.pending.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(clear_state, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def original_final(*, clear_state: Dict[str, Any], cycle_dir: Path, table_id: str) -> Path:
        path = Path(cycle_dir) / "Clear_JSON" / table_id / f"{clear_state['frame_id']}_01.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(clear_state, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    fake_display.save_pending_clear_table_frame_json = original_pending
    fake_display.save_clear_table_frame_json = original_final

    assert module.install_postflop_clear_json_runtime_capture(fake_display, logger=logs.append) is True
    assert module.install_postflop_clear_json_runtime_capture(fake_display, logger=logs.append) is True

    pending_source = fake_display.save_pending_clear_table_frame_json(
        clear_state=_sample_clear_json("flop"),
        cycle_dir=cycle_dir,
        table_id="table_01",
    )
    final_source = fake_display.save_clear_table_frame_json(
        clear_state=_sample_clear_json("river"),
        cycle_dir=cycle_dir,
        table_id="table_01",
    )

    assert pending_source.exists()
    assert final_source.exists()
    assert (tmp_path / "outputs" / "postflop_live_clear_json" / "table_01" / "table_01_hand_12_flop.clear.json").exists()
    assert (tmp_path / "outputs" / "postflop_live_clear_json" / "table_01" / "table_01_hand_12_river_01.clear.json").exists()
    assert any("mirrored Pending postflop Clear_JSON" in message for message in logs)
    assert any("mirrored Final postflop Clear_JSON" in message for message in logs)


def test_v0972_runner_installs_capture_before_running_existing_main() -> None:
    text = RUNNER_PATH.read_text(encoding="utf-8")
    assert "install_postflop_clear_json_runtime_capture" in text
    assert "display_analysis_cycle" in text
    assert "runpy.run_path" in text
    assert "main.py" in text
    assert "sys.path.insert" in text


def test_v0972_capture_code_does_not_import_decision_runtime_or_click_modules() -> None:
    combined = CAPTURE_MODULE_PATH.read_text(encoding="utf-8") + "\n" + RUNNER_PATH.read_text(encoding="utf-8")
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
        assert fragment not in combined
