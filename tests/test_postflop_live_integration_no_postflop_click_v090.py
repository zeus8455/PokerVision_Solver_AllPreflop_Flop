from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from solver_postflop.live_clear_json_capture_hook import (
    audit_default_clear_json_capture_hook,
    capture_hook_rejects_solver_input_path,
    is_solver_readable_clear_json_capture_path,
)
from solver_postflop.live_clear_json_integration import (
    audit_live_clear_json_file,
    audit_live_clear_json_root,
)
from solver_postflop.live_module_audit_report import RuntimeClickChainStatus
from tools.run_postflop_live_clear_json_audit_v090 import (
    LIVE_CLEAR_JSON_AUDIT_OUTPUT_SUBFOLDERS,
    _parse_args,
    run_postflop_live_clear_json_audit,
)

V096_GUARDED_SOURCE_FILES = (
    Path("solver_postflop/live_clear_json_integration.py"),
    Path("solver_postflop/live_clear_json_capture_hook.py"),
    Path("solver_postflop/live_module_audit_report.py"),
    Path("tools/run_postflop_live_clear_json_audit_v090.py"),
)

V096_FORBIDDEN_IMPORT_ROOTS = {
    "subprocess",
    "pyautogui",
    "win32api",
    "win32con",
    "win32gui",
    "ctypes",
    "pynput",
    "mouse",
    "keyboard",
}

V096_FORBIDDEN_EXECUTION_TOKENS = (
    "pyautogui.click",
    "pyautogui.moveTo",
    "mouseDown",
    "mouseUp",
    "win32api.mouse_event",
    "win32api.SetCursorPos",
    "ctypes.windll",
    "SendInput",
    "pynput.mouse",
    "subprocess.run",
    "subprocess.Popen",
    "os.system(",
    "main.py",
    "ui_display_launch",
    "run_ui_display_analysis_cycle",
)

V096_FORBIDDEN_ACTION_MODEL_TOKENS = (
    "PostflopDecision",
    "ActionDecision",
    "ActionRuntimePlan",
    "RuntimePlan",
    "target_sequence",
    "button_sequence",
    "ActionButtonDetector",
    "action_button_detector",
    "click_result",
    "physical_click",
)

V096_FORBIDDEN_OUTPUT_FOLDERS = {
    "action_decision_json",
    "action_runtime_plan_json",
    "runtime_plans",
    "action_button",
    "click_results",
    "postflop_decisions",
}


def _write_json(path: Path, payload: dict[str, object] | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload or {"ok": True}), encoding="utf-8")
    return path


def _flop_clear_json_payload() -> dict[str, object]:
    return {
        "case_id": "v096_no_click_flop_case",
        "table_id": "table_01",
        "hand_id": "hand_960",
        "hero_id": "hero",
        "hero_position": "BTN",
        "hero_cards": ["As", "Ks"],
        "board_cards": ["Qs", "Js", "2d"],
        "players": [
            {"id": "hero", "position": "BTN", "hero": True},
            {"id": "villain_1", "position": "BB", "hero": False},
        ],
        "positions": {"hero": "BTN", "villain_1": "BB"},
        "total_pot": 7.5,
        "to_call": 0,
        "stacks": {"hero": 95.0, "villain_1": 92.0},
        "allowed_actions": ["check", "bet"],
        "action_context": {
            "spot_family": "srp heads_up",
            "current_actor": "hero",
            "can_check": True,
            "can_bet": True,
        },
    }


def _read_source(path: Path) -> str:
    assert path.is_file(), f"Missing guarded source file: {path}"
    return path.read_text(encoding="utf-8")


def _import_roots(path: Path) -> set[str]:
    tree = ast.parse(_read_source(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def _collect_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        keys = {str(key) for key in value}
        for item in value.values():
            keys.update(_collect_keys(item))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for item in value:
            keys.update(_collect_keys(item))
        return keys
    return set()


def test_v096_guarded_live_audit_files_exist() -> None:
    for source_file in V096_GUARDED_SOURCE_FILES:
        assert source_file.is_file()


def test_v096_guarded_modules_do_not_import_click_or_process_launch_libraries() -> None:
    for source_file in V096_GUARDED_SOURCE_FILES:
        imports = _import_roots(source_file)
        assert imports.isdisjoint(V096_FORBIDDEN_IMPORT_ROOTS), (source_file, imports)


def test_v096_guarded_modules_do_not_contain_click_execution_calls() -> None:
    for source_file in V096_GUARDED_SOURCE_FILES:
        source_text = _read_source(source_file)
        for token in V096_FORBIDDEN_EXECUTION_TOKENS:
            assert token not in source_text, f"{source_file} must not contain {token!r}"


def test_v096_guarded_modules_do_not_define_postflop_action_or_runtime_plan_models() -> None:
    combined_source = "\n".join(_read_source(path) for path in V096_GUARDED_SOURCE_FILES)
    for token in V096_FORBIDDEN_ACTION_MODEL_TOKENS:
        assert token not in combined_source, f"V0.9 live audit layer must not define/use {token!r}"


def test_v096_file_audit_marks_runtime_click_chain_not_invoked(tmp_path: Path) -> None:
    source = _write_json(tmp_path / "clear_json" / "table_01_hand_960.clear.json", _flop_clear_json_payload())

    report = audit_live_clear_json_file(source)
    payload = report.to_json_dict()

    assert report.runtime_click_chain_status is RuntimeClickChainStatus.EXISTING_PROJECT_CHAIN_NOT_INVOKED_BY_AUDIT
    assert payload["runtime_click_chain_status"] == "existing_project_chain_not_invoked_by_audit"
    assert "postflop_decision" not in payload
    assert "runtime_plan" not in payload


def test_v096_root_audit_marks_runtime_click_chain_not_invoked(tmp_path: Path) -> None:
    _write_json(tmp_path / "clear_json" / "table_01_hand_960.clear.json", _flop_clear_json_payload())

    envelope = audit_live_clear_json_root(tmp_path)
    payload = envelope.to_json_dict()

    assert envelope.runtime_click_chain_status is RuntimeClickChainStatus.EXISTING_PROJECT_CHAIN_NOT_INVOKED_BY_AUDIT
    assert payload["runtime_click_chain_status"] == "existing_project_chain_not_invoked_by_audit"
    assert payload["total_clear_json_processed"] == 1


def test_v096_runner_output_structure_excludes_action_and_runtime_plan_folders(tmp_path: Path) -> None:
    clear_root = tmp_path / "clear_root"
    output_root = tmp_path / "audit_output"
    _write_json(clear_root / "clear_json" / "table_01_hand_960.clear.json", _flop_clear_json_payload())

    result = run_postflop_live_clear_json_audit(clear_json_root=clear_root, output_root=output_root)
    actual_subfolders = {path.name for path in output_root.iterdir() if path.is_dir()}

    assert result.output_subfolders == LIVE_CLEAR_JSON_AUDIT_OUTPUT_SUBFOLDERS
    assert actual_subfolders == set(LIVE_CLEAR_JSON_AUDIT_OUTPUT_SUBFOLDERS)
    assert actual_subfolders.isdisjoint(V096_FORBIDDEN_OUTPUT_FOLDERS)


def test_v096_runner_writes_no_action_decision_or_runtime_plan_json_files(tmp_path: Path) -> None:
    clear_root = tmp_path / "clear_root"
    output_root = tmp_path / "audit_output"
    _write_json(clear_root / "clear_json" / "table_01_hand_960.clear.json", _flop_clear_json_payload())

    run_postflop_live_clear_json_audit(clear_json_root=clear_root, output_root=output_root)
    written_files = [path.name.lower() for path in output_root.rglob("*.json")]

    assert written_files
    assert not any("action_decision" in name for name in written_files)
    assert not any("action_runtime_plan" in name for name in written_files)
    assert not any("runtime_plan" in name for name in written_files)
    assert not any("click_result" in name for name in written_files)


def test_v096_runner_status_confirms_existing_project_chain_is_not_invoked_by_audit(tmp_path: Path) -> None:
    clear_root = tmp_path / "clear_root"
    output_root = tmp_path / "audit_output"
    _write_json(clear_root / "clear_json" / "table_01_hand_960.clear.json", _flop_clear_json_payload())

    result = run_postflop_live_clear_json_audit(clear_json_root=clear_root, output_root=output_root)
    tool_result = json.loads((output_root / "tool_result.json").read_text(encoding="utf-8"))
    latest_report = json.loads((output_root / "latest_report.json").read_text(encoding="utf-8"))

    assert result.runtime_click_chain_status == "existing_project_chain_not_invoked_by_audit"
    assert tool_result["runtime_click_chain_status"] == "existing_project_chain_not_invoked_by_audit"
    assert latest_report["runtime_click_chain_status"] == "existing_project_chain_not_invoked_by_audit"


def test_v096_module_result_payloads_do_not_contain_action_or_click_keys(tmp_path: Path) -> None:
    source = _write_json(tmp_path / "clear_json" / "table_01_hand_960.clear.json", _flop_clear_json_payload())
    report = audit_live_clear_json_file(source).to_json_dict()

    feature_payload_keys = set()
    for result_key in ("board_texture_result", "made_hand_result", "draw_result"):
        feature_payload_keys.update(_collect_keys(report[result_key]["payload"]))

    forbidden_keys = {
        "decision",
        "postflop_decision",
        "runtime_plan",
        "action_decision_json",
        "action_runtime_plan_json",
        "button_sequence",
        "target_sequence",
        "click_result",
    }
    assert feature_payload_keys.isdisjoint(forbidden_keys)


def test_v096_capture_hook_audit_is_metadata_only_and_does_not_enable_postflop_clicks(tmp_path: Path) -> None:
    audit = audit_default_clear_json_capture_hook(tmp_path)
    payload = audit.to_json_dict()

    assert audit.runtime_click_chain_status is RuntimeClickChainStatus.EXISTING_PROJECT_CHAIN_NOT_INVOKED_BY_AUDIT
    assert payload["runtime_click_chain_status"] == "existing_project_chain_not_invoked_by_audit"
    assert "capture_hook_audit_only" in payload["notes"]
    assert "existing_runtime_click_chain_not_modified" in payload["notes"]


def test_v096_capture_hook_rejects_action_runtime_and_button_paths_as_solver_input(tmp_path: Path) -> None:
    clear_path = tmp_path / "outputs" / "postflop_live_clear_json" / "table_01_hand_960.clear.json"
    forbidden_paths = (
        tmp_path / "action_decision_json" / "table_01.json",
        tmp_path / "action_runtime_plan_json" / "table_01.json",
        tmp_path / "button_detector" / "table_01.json",
        tmp_path / "runtime_json" / "table_01.runtime.json",
    )

    assert is_solver_readable_clear_json_capture_path(clear_path) is True
    for path in forbidden_paths:
        assert capture_hook_rejects_solver_input_path(path) is True


def test_v096_tool_cli_has_no_live_or_click_execution_flags() -> None:
    args = _parse_args(["--project-root", ".", "--clear-json-root", "clear", "--output-root", "out", "--max-files", "1"])

    assert vars(args) == {
        "project_root": ".",
        "clear_json_root": "clear",
        "output_root": "out",
        "max_files": 1,
        "non_recursive": False,
    }
    assert "live" not in vars(args)
    assert "click" not in vars(args)
    assert "action_button" not in vars(args)
