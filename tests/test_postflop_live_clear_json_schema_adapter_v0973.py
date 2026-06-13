from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any, Dict

RUNTIME_ROOT = Path("external") / "PokerVisionFinalVersionNoSolver_snapshot" / "PokerVision V1_2"
CAPTURE_MODULE_PATH = RUNTIME_ROOT / "postflop_clear_json_runtime_capture.py"


def _load_capture_module():
    spec = importlib.util.spec_from_file_location("postflop_clear_json_runtime_capture_v0973_test", CAPTURE_MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _live_flop_payload() -> Dict[str, Any]:
    return {
        "frame_id": "table_01_hand_58_flop_02",
        "board": {
            "cards": ["10_clubs", "9_diamonds", "A_diamonds"],
            "street": "flop",
        },
        "Total_pot": 9.0,
        "players": {
            "BB": {
                "hero": True,
                "cards": ["A_spades", "3_diamonds"],
                "stack": 97.5,
                "fold": False,
                "chips": False,
            },
            "BTN": {"stack": 107.5, "fold": False, "chips": 3.5},
        },
    }


def test_v0973_live_schema_adapter_adds_solver_compatible_top_level_aliases() -> None:
    module = _load_capture_module()

    adapted = module.build_solver_compatible_live_clear_json(_live_flop_payload())

    assert adapted["case_id"] == "table_01_hand_58_flop_02"
    assert adapted["table_id"] == "table_01"
    assert adapted["hand_id"] == "hand_58"
    assert adapted["street"] == "flop"
    assert adapted["board_cards"] == ["Tc", "9d", "Ad"]
    assert adapted["hero_id"] == "BB"
    assert adapted["hero"] == "BB"
    assert adapted["hero_position"] == "BB"
    assert adapted["hero_cards"] == ["As", "3d"]
    assert adapted["total_pot"] == 9.0
    assert adapted["pot"] == 9.0
    assert adapted["raw_live_clear_json"] == _live_flop_payload()


def test_v0973_pending_mirror_writes_adapted_payload_with_pending_audit_metadata(tmp_path: Path) -> None:
    module = _load_capture_module()
    cycle_dir = tmp_path / "outputs" / "ui_display_cycle" / "current_cycle"
    pending_path = cycle_dir / "Clear_JSON_Pending" / "table_01" / "table_01_hand_58_flop_02.pending.json"

    mirror_path = module.mirror_postflop_pending_clear_json_for_audit(
        clear_state=_live_flop_payload(),
        cycle_dir=cycle_dir,
        table_id="table_01",
        pending_clear_json_path=pending_path,
    )

    assert mirror_path == tmp_path / "outputs" / "postflop_live_clear_json" / "table_01" / "table_01_hand_58_flop_02.clear.json"
    payload = json.loads(mirror_path.read_text(encoding="utf-8"))
    assert payload["board_cards"] == ["Tc", "9d", "Ad"]
    assert payload["hero_cards"] == ["As", "3d"]
    assert payload["hero_id"] == "BB"
    assert payload["total_pot"] == 9.0
    assert payload["postflop_live_capture"]["schema_version"] == "postflop_clear_json_runtime_capture_v0_9_7_3"
    assert payload["postflop_live_capture"]["capture_stage"] == "pending_clear_json"
    assert payload["postflop_live_capture"]["final_clear_confirmed"] is False
    assert payload["postflop_live_capture"]["solver_input_allowed_for_v090_audit"] is True
    assert payload["postflop_live_capture"]["solver_input_allowed_for_decision"] is False


def test_v0973_adapter_preserves_existing_solver_compatible_fields() -> None:
    module = _load_capture_module()
    payload = _live_flop_payload()
    payload.update(
        {
            "table_id": "table_custom",
            "hand_id": "hand_custom",
            "board_cards": ["Qh", "Jh", "2s"],
            "hero_id": "HERO_SLOT",
            "hero_cards": ["Ah", "Kh"],
            "total_pot": 99.0,
        }
    )

    adapted = module.build_solver_compatible_live_clear_json(payload)

    assert adapted["table_id"] == "table_custom"
    assert adapted["hand_id"] == "hand_custom"
    assert adapted["board_cards"] == ["Qh", "Jh", "2s"]
    assert adapted["hero_id"] == "HERO_SLOT"
    assert adapted["hero_cards"] == ["Ah", "Kh"]
    assert adapted["total_pot"] == 99.0


def test_v0973_preflop_payload_still_does_not_mirror(tmp_path: Path) -> None:
    module = _load_capture_module()
    cycle_dir = tmp_path / "outputs" / "ui_display_cycle" / "current_cycle"
    payload = _live_flop_payload()
    payload["frame_id"] = "table_01_hand_58_preflop"
    payload["board"] = {"cards": [], "street": "preflop"}

    mirror_path = module.mirror_postflop_pending_clear_json_for_audit(
        clear_state=payload,
        cycle_dir=cycle_dir,
        table_id="table_01",
        pending_clear_json_path=cycle_dir / "Clear_JSON_Pending" / "table_01" / "table_01_hand_58_preflop.pending.json",
    )

    assert mirror_path is None
    assert not (tmp_path / "outputs" / "postflop_live_clear_json").exists()


def test_v0973_capture_adapter_does_not_add_decision_runtime_or_click_logic() -> None:
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
