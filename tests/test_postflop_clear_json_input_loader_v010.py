from __future__ import annotations

import copy
import json
from pathlib import Path

from solver_postflop import ClearJsonInput, load_clear_json_input


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_load_clear_json_input_reads_explicit_file(tmp_path: Path) -> None:
    source_file = tmp_path / "flop_case_001.clear.json"
    payload = {
        "case_id": "flop_case_001",
        "hand_id": "hand_77",
        "table_id": "table_03",
        "hero_cards": ["As", "Kd"],
        "board_cards": ["Ah", "7c", "2d"],
    }
    _write_json(source_file, payload)

    result = load_clear_json_input(source_file)

    assert isinstance(result, ClearJsonInput)
    assert Path(result.source_file) == source_file
    assert result.raw_data == payload
    assert result.case_id == "flop_case_001"
    assert result.hand_id == "hand_77"
    assert result.table_id == "table_03"
    assert result.loaded_at


def test_load_clear_json_input_accepts_metadata_container(tmp_path: Path) -> None:
    source_file = tmp_path / "metadata_case.clear.json"
    payload = {
        "metadata": {
            "caseId": "case_from_metadata",
            "handId": "hand_from_metadata",
            "tableId": "table_from_metadata",
        },
        "players": [],
    }
    _write_json(source_file, payload)

    result = load_clear_json_input(str(source_file))

    assert result.case_id == "case_from_metadata"
    assert result.hand_id == "hand_from_metadata"
    assert result.table_id == "table_from_metadata"


def test_load_clear_json_input_allows_missing_optional_metadata(tmp_path: Path) -> None:
    source_file = tmp_path / "minimal.clear.json"
    payload = {"hero_cards": ["Qs", "Qh"], "board_cards": []}
    _write_json(source_file, payload)

    result = load_clear_json_input(source_file)

    assert result.case_id is None
    assert result.hand_id is None
    assert result.table_id is None
    assert result.raw_data == payload


def test_load_clear_json_input_does_not_mutate_loaded_payload(tmp_path: Path) -> None:
    source_file = tmp_path / "read_only.clear.json"
    payload = {
        "case_id": "read_only_case",
        "players": [{"id": "hero", "stack": 100}],
        "action_context": {"allowed_actions": ["check", "bet"]},
    }
    expected_payload = copy.deepcopy(payload)
    _write_json(source_file, payload)

    result = load_clear_json_input(source_file)
    result.raw_data["players"][0]["stack"] = 50

    reloaded_from_disk = json.loads(source_file.read_text(encoding="utf-8"))
    assert payload == expected_payload
    assert reloaded_from_disk == expected_payload


def test_clear_json_input_loader_rejects_non_object_json(tmp_path: Path) -> None:
    source_file = tmp_path / "array.clear.json"
    source_file.write_text('[{"case_id": "bad"}]', encoding="utf-8")

    try:
        load_clear_json_input(source_file)
    except TypeError as exc:
        assert "root" in str(exc)
    else:
        raise AssertionError("expected TypeError for non-object JSON root")


def test_clear_json_input_loader_has_no_automatic_fallback_code() -> None:
    source_text = Path("solver_postflop/clear_json_input.py").read_text(encoding="utf-8")

    forbidden_markers = (
        "glob(",
        "rglob(",
        "os.walk",
        "solver_preflop",
        "external.",
        "display_analysis_cycle",
        "Action_Button",
        "Dark_JSON",
        "Pending_JSON",
        "Service JSON",
        "Runtime JSON",
    )

    for marker in forbidden_markers:
        assert marker not in source_text
