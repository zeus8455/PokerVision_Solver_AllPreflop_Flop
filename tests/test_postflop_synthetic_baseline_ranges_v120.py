from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RANGE_PACK_PATH = PROJECT_ROOT / "ranges" / "postflop_default_ranges.json"

EXPECTED_CASES = {
    "flop_range_srp_heads_up_btn_vs_bb",
    "flop_range_srp_oop_bb_vs_btn",
    "flop_range_3bet_pot_ip",
    "flop_range_3bet_pot_oop",
    "flop_range_4bet_low_spr",
    "flop_range_limp_passive",
    "flop_range_multiway",
    "flop_range_unknown_context",
}

EXPECTED_BUCKETS = {
    "premium_pairs",
    "strong_broadways",
    "suited_broadways",
    "suited_connectors",
    "offsuit_broadways",
    "pocket_pairs",
    "ace_x_suited",
    "defense_range",
    "unknown_bucket",
}

COMPACT_COMBO_RE = re.compile(r"^[AKQJT98765432][cdhs][AKQJT98765432][cdhs]$")


def _load_pack() -> dict:
    assert RANGE_PACK_PATH.exists(), "ranges/postflop_default_ranges.json must exist"
    return json.loads(RANGE_PACK_PATH.read_text(encoding="utf-8"))


def _iter_player_ranges(case: dict):
    hero = case.get("hero_range_state")
    if hero:
        yield hero
    for opponent in case.get("opponent_range_states", []):
        yield opponent


def _combo_values(player_range: dict) -> list[str]:
    combos: list[str] = []
    for bucket_values in player_range.get("combo_groups", {}).values():
        combos.extend(bucket_values)
    return combos


def test_postflop_default_range_pack_exists_with_v0123_schema() -> None:
    payload = _load_pack()

    assert payload["schema"] == "pokervision_solver_postflop_default_ranges_v1"
    assert payload["version_block"] == "V0.12.3"
    assert payload["source_type"] == "postflop_default_ranges"
    assert payload["source_name"] == "postflop_default_ranges_v0123"
    assert payload["combo_format"] == "compact_combo_rank_suit_rank_suit"
    assert payload["weighting_mode"] == "flat_baseline"
    assert payload["next_module"] == "range_importer_v0124"


def test_postflop_default_range_pack_contains_all_planned_baseline_cases() -> None:
    payload = _load_pack()
    cases = payload["cases"]

    assert set(cases) == EXPECTED_CASES
    assert cases["flop_range_srp_heads_up_btn_vs_bb"]["spot_family"] == "srp_heads_up"
    assert cases["flop_range_srp_oop_bb_vs_btn"]["spot_family"] == "srp_oop"
    assert cases["flop_range_3bet_pot_ip"]["spot_family"] == "three_bet_pot_ip"
    assert cases["flop_range_3bet_pot_oop"]["spot_family"] == "three_bet_pot_oop"
    assert cases["flop_range_4bet_low_spr"]["spot_family"] == "four_bet_low_spr"
    assert cases["flop_range_limp_passive"]["spot_family"] == "limp_passive"
    assert cases["flop_range_multiway"]["spot_family"] == "multiway"
    assert cases["flop_range_unknown_context"]["spot_family"] == "unknown_context"


def test_postflop_default_range_pack_declares_required_range_buckets() -> None:
    payload = _load_pack()

    assert set(payload["range_buckets_supported"]) == EXPECTED_BUCKETS

    for case_id, case in payload["cases"].items():
        assert case["next_module"] == "range_importer_v0124"
        assert set(case["range_buckets"]).issubset(EXPECTED_BUCKETS), case_id
        for player_range in _iter_player_ranges(case):
            assert set(player_range["range_buckets"]).issubset(EXPECTED_BUCKETS), case_id
            assert set(player_range["combo_groups"]).issubset(EXPECTED_BUCKETS), case_id


def test_postflop_default_range_pack_has_combo_level_compact_strings_for_supported_cases() -> None:
    payload = _load_pack()

    combo_count = 0
    for case_id, case in payload["cases"].items():
        if case_id == "flop_range_unknown_context":
            continue

        case_combo_count = 0
        for player_range in _iter_player_ranges(case):
            combos = _combo_values(player_range)
            assert combos, f"{case_id} / {player_range['range_name']} must carry combo-level data"
            for combo in combos:
                assert COMPACT_COMBO_RE.match(combo), f"Invalid compact combo: {combo}"
            case_combo_count += len(combos)

        assert case_combo_count > 0, case_id
        combo_count += case_combo_count

    assert combo_count >= 80


def test_postflop_default_range_pack_preserves_shorthand_source_for_future_expansion() -> None:
    payload = _load_pack()

    for case_id, case in payload["cases"].items():
        if case_id == "flop_range_unknown_context":
            continue
        for player_range in _iter_player_ranges(case):
            assert player_range["range_source"] == "postflop_default_ranges"
            assert player_range["weighting_mode"] == "flat_baseline"
            assert player_range["confidence"] in {"high", "medium", "low"}
            assert player_range["shorthand_source"], case_id
            assert isinstance(player_range["shorthand_source"], dict)


def test_postflop_default_unknown_context_is_structured_and_non_fatal() -> None:
    payload = _load_pack()
    unknown = payload["cases"]["flop_range_unknown_context"]

    assert unknown["source_type"] == "unknown_range"
    assert unknown["range_import_status"] == "unknown_range"
    assert unknown["range_confidence"] == "unknown"
    assert unknown["opponent_range_states"] == []
    assert unknown["hero_range_state"]["range_name"] == "unknown_range"
    assert unknown["hero_range_state"]["combo_groups"] == {"unknown_bucket": []}
    assert unknown["next_module"] == "range_importer_v0124"


def test_postflop_default_range_pack_is_json_serializable_and_read_only_data() -> None:
    payload = _load_pack()

    encoded = json.dumps(payload, sort_keys=True)
    decoded = json.loads(encoded)

    assert decoded == payload
    assert isinstance(payload["cases"], dict)
    assert RANGE_PACK_PATH.read_text(encoding="utf-8").endswith("\n")


def test_postflop_default_range_pack_has_no_importer_blocker_decision_runtime_or_click_execution() -> None:
    payload = _load_pack()
    flags = payload["architecture_flags"]

    assert flags["range_importer_executed"] is False
    assert flags["range_state_created"] is False
    assert flags["blocker_filtering_executed"] is False
    assert flags["range_narrowing_executed"] is False
    assert flags["equity_recalculation_executed"] is False
    assert flags["decision_logic_executed"] is False
    assert flags["runtime_plan_created"] is False
    assert flags["physical_click_executed"] is False
    assert flags["clear_json_validation_executed"] is False
    assert flags["player_filtering_executed"] is False
