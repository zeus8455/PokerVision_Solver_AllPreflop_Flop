from __future__ import annotations

import json
from pathlib import Path

from solver_postflop import ModuleChainStatus
from tools.run_postflop_live_clear_json_audit_v090 import (
    LIVE_CLEAR_JSON_AUDIT_DEFAULT_CLEAR_ROOT,
    LIVE_CLEAR_JSON_AUDIT_DEFAULT_OUTPUT_ROOT,
    LIVE_CLEAR_JSON_AUDIT_LATEST_REPORT_NAME,
    LIVE_CLEAR_JSON_AUDIT_OUTPUT_SUBFOLDERS,
    LIVE_CLEAR_JSON_AUDIT_TOOL_VERSION,
    LiveClearJsonAuditToolConfig,
    LiveClearJsonAuditToolResult,
    build_live_clear_json_audit_config,
    build_live_clear_json_audit_output_structure,
    main,
    run_postflop_live_clear_json_audit,
)


def _write_json(path: Path, payload: dict[str, object] | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload or {"ok": True}), encoding="utf-8")
    return path


def _flop_clear_json_payload(
    *,
    case_id: str = "flop_live_audit_case",
    board_cards: list[str] | None = None,
    players: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return {
        "case_id": case_id,
        "table_id": "table_01",
        "hand_id": "hand_300",
        "hero_id": "hero",
        "hero_position": "BTN",
        "hero_cards": ["As", "Ks"],
        "board_cards": board_cards if board_cards is not None else ["Qs", "Js", "2d"],
        "players": players
        if players is not None
        else [
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


def test_v095_tool_version_and_default_output_contract_are_fixed() -> None:
    assert LIVE_CLEAR_JSON_AUDIT_TOOL_VERSION == "v0.9.5"
    assert LIVE_CLEAR_JSON_AUDIT_DEFAULT_OUTPUT_ROOT == "outputs/postflop_live_clear_json_audit_v090"
    assert LIVE_CLEAR_JSON_AUDIT_DEFAULT_CLEAR_ROOT == "outputs/postflop_live_clear_json"
    assert LIVE_CLEAR_JSON_AUDIT_LATEST_REPORT_NAME == "latest_report.json"
    assert LIVE_CLEAR_JSON_AUDIT_OUTPUT_SUBFOLDERS == (
        "processed_clear_json",
        "solver_inputs",
        "branch_results",
        "flop_contexts",
        "board_texture",
        "made_hand",
        "draw_features",
        "module_chain_reports",
    )


def test_v095_config_uses_project_relative_defaults(tmp_path: Path) -> None:
    config = build_live_clear_json_audit_config(project_root=tmp_path)
    payload = config.to_json_dict()

    assert isinstance(config, LiveClearJsonAuditToolConfig)
    assert payload["project_root"] == str(tmp_path)
    assert Path(payload["clear_json_root"]).parts[-2:] == ("outputs", "postflop_live_clear_json")
    assert Path(payload["output_root"]).parts[-2:] == ("outputs", "postflop_live_clear_json_audit_v090")
    assert payload["max_files"] is None
    assert payload["recursive"] is True
    json.dumps(payload, sort_keys=True)


def test_v095_output_structure_creates_all_expected_subfolders(tmp_path: Path) -> None:
    output_root = tmp_path / "audit_output"
    structure = build_live_clear_json_audit_output_structure(output_root)

    assert set(structure) == set(LIVE_CLEAR_JSON_AUDIT_OUTPUT_SUBFOLDERS)
    for subfolder in LIVE_CLEAR_JSON_AUDIT_OUTPUT_SUBFOLDERS:
        assert (output_root / subfolder).is_dir()
        assert structure[subfolder] == str(output_root / subfolder)


def test_v095_runner_writes_latest_report_and_tool_result(tmp_path: Path) -> None:
    clear_root = tmp_path / "clear_root"
    output_root = tmp_path / "audit_output"
    source = _write_json(clear_root / "clear_json" / "table_01_hand_300.clear.json", _flop_clear_json_payload())
    _write_json(clear_root / "dark_json" / "table_01.dark.json", {"not_solver_input": True})

    result = run_postflop_live_clear_json_audit(
        project_root=tmp_path,
        clear_json_root=clear_root,
        output_root=output_root,
    )
    payload = result.to_json_dict()
    latest_report = json.loads((output_root / "latest_report.json").read_text(encoding="utf-8"))

    assert isinstance(result, LiveClearJsonAuditToolResult)
    assert payload["tool_version"] == "v0.9.5"
    assert payload["latest_report_file"] == str(output_root / "latest_report.json")
    assert latest_report["total_files_seen"] == 2
    assert latest_report["total_clear_json_processed"] == 1
    assert latest_report["reports"][0]["source_file"] == str(source)
    assert (output_root / "tool_result.json").is_file()
    assert json.loads((output_root / "tool_result.json").read_text(encoding="utf-8"))["tool_version"] == "v0.9.5"


def test_v095_runner_writes_per_module_artifacts_for_flop_clear_json(tmp_path: Path) -> None:
    clear_root = tmp_path / "clear_root"
    output_root = tmp_path / "audit_output"
    _write_json(clear_root / "clear_json" / "table_01_hand_300.clear.json", _flop_clear_json_payload())

    result = run_postflop_live_clear_json_audit(clear_json_root=clear_root, output_root=output_root)

    assert result.module_chain_status == ModuleChainStatus.FLOP_FEATURES_COMPLETED.value
    assert result.artifacts_written["processed_clear_json"] == 1
    assert result.artifacts_written["module_chain_reports"] == 1
    assert result.artifacts_written["solver_inputs"] == 1
    assert result.artifacts_written["branch_results"] == 1
    assert result.artifacts_written["flop_contexts"] == 1
    assert result.artifacts_written["board_texture"] == 1
    assert result.artifacts_written["made_hand"] == 1
    assert result.artifacts_written["draw_features"] == 1
    assert (output_root / "processed_clear_json" / "table_01_hand_300.clear.json").is_file()
    assert (output_root / "solver_inputs" / "table_01_hand_300.solver_input.json").is_file()
    assert (output_root / "branch_results" / "table_01_hand_300.branch_result.json").is_file()
    assert (output_root / "flop_contexts" / "table_01_hand_300.flop_context.json").is_file()
    assert (output_root / "board_texture" / "table_01_hand_300.board_texture.json").is_file()
    assert (output_root / "made_hand" / "table_01_hand_300.made_hand.json").is_file()
    assert (output_root / "draw_features" / "table_01_hand_300.draw_features.json").is_file()
    assert (output_root / "module_chain_reports" / "table_01_hand_300.module_report.json").is_file()


def test_v095_runner_handles_bad_clear_json_without_breaking_latest_report(tmp_path: Path) -> None:
    clear_root = tmp_path / "clear_root"
    output_root = tmp_path / "audit_output"
    _write_json(clear_root / "clear_json" / "table_01_hand_300.clear.json", _flop_clear_json_payload())
    bad = clear_root / "clear_json" / "table_02_hand_301.clear.json"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text("{bad json", encoding="utf-8")

    result = run_postflop_live_clear_json_audit(clear_json_root=clear_root, output_root=output_root)
    latest_report = json.loads((output_root / "latest_report.json").read_text(encoding="utf-8"))

    assert result.total_clear_json_processed == 2
    assert result.module_chain_status == ModuleChainStatus.MODULE_ERROR.value
    assert {report["module_chain_status"] for report in latest_report["reports"]} == {
        "flop_features_completed",
        "module_error",
    }
    assert result.artifacts_written["module_chain_reports"] == 2
    assert result.artifacts_written["processed_clear_json"] == 2


def test_v095_runner_respects_max_files_and_keeps_deterministic_order(tmp_path: Path) -> None:
    clear_root = tmp_path / "clear_root"
    output_root = tmp_path / "audit_output"
    _write_json(clear_root / "clear_json" / "a_table_01_hand_1.clear.json", _flop_clear_json_payload(case_id="a"))
    _write_json(clear_root / "clear_json" / "b_table_02_hand_2.clear.json", _flop_clear_json_payload(case_id="b"))

    result = run_postflop_live_clear_json_audit(clear_json_root=clear_root, output_root=output_root, max_files=1)
    latest_report = json.loads((output_root / "latest_report.json").read_text(encoding="utf-8"))

    assert result.total_files_seen == 1
    assert result.total_clear_json_processed == 1
    assert Path(latest_report["reports"][0]["source_file"]).name == "a_table_01_hand_1.clear.json"


def test_v095_runner_missing_default_clear_root_writes_structured_empty_report(tmp_path: Path) -> None:
    output_root = tmp_path / "audit_output"

    result = run_postflop_live_clear_json_audit(project_root=tmp_path, output_root=output_root)
    latest_report = json.loads((output_root / "latest_report.json").read_text(encoding="utf-8"))

    assert result.total_files_seen == 0
    assert result.total_clear_json_processed == 0
    assert latest_report["source_root"].endswith("postflop_live_clear_json")
    assert latest_report["reports"] == []
    assert latest_report["notes"]


def test_v095_runner_does_not_turn_forbidden_project_json_into_artifacts(tmp_path: Path) -> None:
    clear_root = tmp_path / "clear_root"
    output_root = tmp_path / "audit_output"
    _write_json(clear_root / "clear_json" / "table_01_hand_300.clear.json", _flop_clear_json_payload())
    _write_json(clear_root / "pending_json" / "table_01.pending.json", _flop_clear_json_payload())
    _write_json(clear_root / "service_json" / "table_01.service.json", _flop_clear_json_payload())
    _write_json(clear_root / "action_runtime_plan_json" / "table_01.json", {"runtime_plan": "forbidden"})

    result = run_postflop_live_clear_json_audit(clear_json_root=clear_root, output_root=output_root)
    latest_report = json.loads((output_root / "latest_report.json").read_text(encoding="utf-8"))

    assert result.total_files_seen == 4
    assert result.total_clear_json_processed == 1
    assert len(latest_report["reports"]) == 1
    assert result.artifacts_written["processed_clear_json"] == 1


def test_v095_tool_result_serializes_to_json(tmp_path: Path) -> None:
    clear_root = tmp_path / "clear_root"
    output_root = tmp_path / "audit_output"
    _write_json(clear_root / "clear_json" / "table_01_hand_300.clear.json", _flop_clear_json_payload())

    result = run_postflop_live_clear_json_audit(clear_json_root=clear_root, output_root=output_root)
    payload = result.to_json_dict()

    assert payload["config"]["clear_json_root"] == str(clear_root)
    assert payload["output_subfolders"] == list(LIVE_CLEAR_JSON_AUDIT_OUTPUT_SUBFOLDERS)
    assert "offline_clear_json_audit_tool_runner_v095" in payload["notes"]
    assert payload["runtime_click_chain_status"] == "existing_project_chain_not_invoked_by_audit"
    json.dumps(payload, sort_keys=True)


def test_v095_tool_source_has_no_main_live_or_postflop_action_execution_markers() -> None:
    source_text = Path("tools/run_postflop_live_clear_json_audit_v090.py").read_text(encoding="utf-8")

    forbidden_tokens = (
        "subprocess",
        "pyautogui",
        "win32api",
        "mouseDown",
        "mouseUp",
        "ActionButtonDetector",
        "send_click",
        "physical_click",
        "main.py",
        "action_decision_json",
        "action_runtime_plan_json",
        "pokerkit",
    )
    for token in forbidden_tokens:
        assert token not in source_text

    required_tokens = (
        "audit_live_clear_json_root",
        "latest_report.json",
        "module_chain_reports",
        "build_solver_input",
        "build_draw_features",
    )
    for token in required_tokens:
        assert token in source_text


def test_v095_cli_main_returns_zero_and_writes_outputs(tmp_path: Path, capsys) -> None:
    clear_root = tmp_path / "clear_root"
    output_root = tmp_path / "audit_output"
    _write_json(clear_root / "clear_json" / "table_01_hand_300.clear.json", _flop_clear_json_payload())

    exit_code = main([
        "--project-root",
        str(tmp_path),
        "--clear-json-root",
        str(clear_root),
        "--output-root",
        str(output_root),
        "--max-files",
        "1",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "v0.9.5" in captured.out
    assert (output_root / "latest_report.json").is_file()
