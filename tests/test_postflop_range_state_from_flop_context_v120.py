import json
from pathlib import Path

import pytest

from solver_postflop.flop_context_contracts import (
    FlopActionContext,
    FlopContext,
    FlopPlayerContext,
    FlopPositionContext,
    FlopPotContext,
    FlopSpotFamily,
)
from solver_postflop.range_importer import build_range_state_from_flop_context


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIR = PROJECT_ROOT / "tests" / "fixtures" / "postflop_range_state_v0125" / "expected"
RANGE_PACK = PROJECT_ROOT / "ranges" / "postflop_default_ranges.json"

EXPECTED_FIXTURE_NAMES = {
    "flop_range_srp_heads_up_btn_vs_bb.expected.json",
    "flop_range_srp_oop_bb_vs_btn.expected.json",
    "flop_range_3bet_pot_ip.expected.json",
    "flop_range_3bet_pot_oop.expected.json",
    "flop_range_4bet_low_spr.expected.json",
    "flop_range_limp_passive.expected.json",
    "flop_range_multiway.expected.json",
    "flop_range_unknown_context.expected.json",
}


def _load_expected_fixture(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _expected_paths() -> list[Path]:
    return sorted(EXPECTED_DIR.glob("*.expected.json"))


def _flop_context_from_expected(expected: dict[str, object]) -> FlopContext:
    case_id = str(expected["input_case_id"])
    players = tuple(expected.get("input_players") or ())
    hero_position = expected.get("input_hero_position")
    pot_type = expected.get("input_pot_type")

    return FlopContext(
        case_id=case_id,
        source_file=f"tests/fixtures/postflop_range_state_v0125/source/{case_id}.clear.json",
        table_id="table_01",
        hand_id=f"hand_v0125_{case_id}",
        branch="flop",
        spot_family=FlopSpotFamily(str(expected["input_spot_family"])),
        hero_cards=("As", "Ks"),
        board_cards=("Qh", "Jd", "2c"),
        pot_context=FlopPotContext(
            pot=7.5,
            to_call=0.0,
            pot_type=str(pot_type) if pot_type is not None else None,
            fields_used=("pot_type",),
        ),
        position_context=FlopPositionContext(
            hero_id="hero",
            hero_position=str(hero_position) if hero_position is not None else None,
            fields_used=("hero_position",),
        ),
        action_context=FlopActionContext(
            allowed_actions=("check", "bet"),
            fields_used=("allowed_actions",),
        ),
        player_context=FlopPlayerContext(
            players=players,
            hero_id="hero",
            hero_position=str(hero_position) if hero_position is not None else None,
            is_heads_up=(len(players) == 2),
            is_multiway=(len(players) > 2),
            fields_used=("players", "hero_id", "hero_position"),
        ),
        context_fields_used=("spot_family_context", "pot_type", "hero_position", "players"),
        raw_clear_json_ref={
            "case_id": case_id,
            "pot_type": pot_type,
            "hero_position": hero_position,
            "source": "synthetic_range_state_fixture_v0125",
        },
        notes=("range_state_fixture_v0125",),
    )


def _build_range_state_payload(expected: dict[str, object]) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    context = _flop_context_from_expected(expected)
    before = context.to_json_dict()
    result = build_range_state_from_flop_context(context, project_root=PROJECT_ROOT)
    after = context.to_json_dict()
    return result.to_json_dict(), before, after


def _assert_combo_groups_are_json_safe_and_combo_level(player_range: dict[str, object], *, allow_empty: bool = False) -> None:
    combo_groups = player_range["combo_groups"]
    assert isinstance(combo_groups, dict)

    all_combos: list[str] = []
    for bucket, combos in combo_groups.items():
        assert isinstance(bucket, str)
        assert isinstance(combos, list)
        for combo in combos:
            assert isinstance(combo, str)
            assert len(combo) == 4
            assert combo[0] in "AKQJT98765432"
            assert combo[1] in "shcd"
            assert combo[2] in "AKQJT98765432"
            assert combo[3] in "shcd"
            all_combos.append(combo)

    if not allow_empty:
        assert all_combos, f"Expected combo-level compact strings in {player_range['range_name']}"



def test_v0125_expected_fixture_set_is_complete() -> None:
    assert EXPECTED_DIR.exists()
    assert {path.name for path in _expected_paths()} == EXPECTED_FIXTURE_NAMES


@pytest.mark.parametrize("expected_path", _expected_paths(), ids=lambda path: path.stem)
def test_range_state_from_flop_context_matches_expected_fixture(expected_path: Path) -> None:
    expected = _load_expected_fixture(expected_path)
    actual, before_context, after_context = _build_range_state_payload(expected)

    assert before_context == after_context
    assert actual["case_id"] == expected["expected_range_case_id"]
    assert actual["spot_family"] == expected["expected_spot_family"]
    assert actual["pot_type"] == expected["expected_pot_type"]
    assert actual["hero_position"] == expected["expected_hero_position"]
    assert actual["opponent_positions"] == expected["expected_opponent_positions"]
    assert actual["range_import_status"] == expected["expected_range_import_status"]
    assert actual["range_source_info"]["source_type"] == expected["expected_range_source_type"]
    assert actual["range_confidence"] == expected["expected_range_confidence"]
    assert actual["next_module"] == expected["expected_next_module"]
    assert actual["source_file"].endswith(f"{expected['input_case_id']}.clear.json")

    assert actual["hero_range_state"]["range_name"] == expected["expected_hero_range_name"]
    assert actual["hero_range_state"]["role"] == expected["expected_hero_role"]
    assert actual["hero_range_state"]["position"] == expected["expected_hero_position"]

    actual_opponents = actual["opponent_range_states"]
    assert [opponent["range_name"] for opponent in actual_opponents] == expected["expected_opponent_range_names"]
    assert [opponent["role"] for opponent in actual_opponents] == expected["expected_opponent_roles"]

    for bucket in expected["expected_required_buckets"]:
        assert bucket in actual["range_buckets"]

    allow_empty_hero = actual["range_import_status"] == "unknown_range"
    _assert_combo_groups_are_json_safe_and_combo_level(actual["hero_range_state"], allow_empty=allow_empty_hero)
    for opponent in actual_opponents:
        _assert_combo_groups_are_json_safe_and_combo_level(opponent)

    json.dumps(actual)


@pytest.mark.parametrize("expected_path", _expected_paths(), ids=lambda path: path.stem)
def test_range_source_info_is_preserved_from_default_pack(expected_path: Path) -> None:
    expected = _load_expected_fixture(expected_path)
    actual, _before_context, _after_context = _build_range_state_payload(expected)

    source_info = actual["range_source_info"]
    if actual["range_import_status"] == "unknown_range":
        assert source_info["source_name"] == "unknown_range"
        assert source_info["source_type"] == "unknown_range"
    else:
        assert source_info["source_type"] == "postflop_default_ranges"
        assert source_info["source_name"].startswith("postflop_default_flop_range_")
        assert source_info["source_file"].endswith("ranges/postflop_default_ranges.json") or source_info[
            "source_file"
        ].endswith("ranges\\postflop_default_ranges.json")
        assert source_info["source_version"] == "v0.12.3"
        assert "baseline_range_selected_from_postflop_default_pack" in source_info["notes"]


@pytest.mark.parametrize("expected_path", _expected_paths(), ids=lambda path: path.stem)
def test_range_state_payload_is_trace_append_ready(expected_path: Path) -> None:
    expected = _load_expected_fixture(expected_path)
    actual, _before_context, _after_context = _build_range_state_payload(expected)

    trace_record = {
        "case_id": expected["input_case_id"],
        "module_results": [
            {
                "module": "range_importer",
                "version": "v0.12.5_fixture_coverage",
                "result": actual,
            }
        ],
    }

    encoded = json.dumps(trace_record)
    decoded = json.loads(encoded)
    assert decoded["module_results"][0]["result"]["case_id"] == expected["expected_range_case_id"]
    assert decoded["module_results"][0]["result"]["next_module"] == "blocker_filtering_later"


def test_range_state_fixture_coverage_uses_default_range_pack_without_mutating_it() -> None:
    before = RANGE_PACK.read_text(encoding="utf-8")
    for expected_path in _expected_paths():
        expected = _load_expected_fixture(expected_path)
        _build_range_state_payload(expected)
    after = RANGE_PACK.read_text(encoding="utf-8")

    assert before == after


def test_v0125_does_not_execute_future_range_or_runtime_logic() -> None:
    importer_source = (PROJECT_ROOT / "solver_postflop" / "range_importer.py").read_text(encoding="utf-8").lower()

    forbidden_terms = [
        "filter_blockers(",
        "blocked_by_hero_card",
        "blocked_by_board_card",
        "range_narrowing",
        "narrow_range",
        "calculate_equity",
        "monte_carlo",
        "decision_engine",
        "runtime_plan(",
        "click(",
        "clear_json_pending",
        "dark_json",
        "current_cycle",
        "display_analysis_cycle",
    ]

    for forbidden in forbidden_terms:
        assert forbidden not in importer_source
