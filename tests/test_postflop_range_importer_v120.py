import json
from pathlib import Path

from solver_postflop.flop_context_contracts import (
    FlopActionContext,
    FlopContext,
    FlopPlayerContext,
    FlopPositionContext,
    FlopPotContext,
    FlopSpotFamily,
)
from solver_postflop.range_contracts import RangeImportStatus, RangeSourceType
from solver_postflop.range_importer import (
    RANGE_IMPORTER_VERSION,
    build_range_state_from_flop_context,
    select_range_case_id,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMPORTER_SOURCE = PROJECT_ROOT / "solver_postflop" / "range_importer.py"
RANGE_PACK = PROJECT_ROOT / "ranges" / "postflop_default_ranges.json"


def _flop_context(
    *,
    case_id: str,
    spot_family: FlopSpotFamily,
    hero_position: str | None,
    pot_type: str | None,
    players: tuple[dict[str, object], ...] = (
        {"player_id": "hero", "position": "BTN"},
        {"player_id": "villain_1", "position": "BB"},
    ),
) -> FlopContext:
    return FlopContext(
        case_id=case_id,
        source_file=f"tests/fixtures/postflop_clear_json/synthetic/{case_id}.clear.json",
        table_id="table_01",
        hand_id="hand_v0124",
        branch="flop",
        spot_family=spot_family,
        hero_cards=("As", "Ks"),
        board_cards=("Qh", "Jd", "2c"),
        pot_context=FlopPotContext(pot=7.5, to_call=0.0, pot_type=pot_type),
        position_context=FlopPositionContext(hero_id="hero", hero_position=hero_position),
        action_context=FlopActionContext(allowed_actions=("check", "bet")),
        player_context=FlopPlayerContext(
            players=players,
            hero_id="hero",
            hero_position=hero_position,
            is_heads_up=(len(players) == 2),
            is_multiway=(len(players) > 2),
        ),
        context_fields_used=("spot_family_context", "pot_type", "hero_position"),
        raw_clear_json_ref={"case_id": case_id, "pot_type": pot_type, "hero_position": hero_position},
        notes=("test_context",),
    )


def _build(context: FlopContext):
    return build_range_state_from_flop_context(context, project_root=PROJECT_ROOT)


def test_range_importer_version_is_v0124() -> None:
    assert RANGE_IMPORTER_VERSION == "v0.12.4"


def test_srp_heads_up_btn_vs_bb_gets_postflop_default_baseline_range() -> None:
    context = _flop_context(
        case_id="srp_btn_vs_bb",
        spot_family=FlopSpotFamily.SRP_HEADS_UP,
        hero_position="BTN",
        pot_type="srp",
    )

    assert select_range_case_id(context) == "flop_range_srp_heads_up_btn_vs_bb"

    result = _build(context)
    payload = result.to_json_dict()

    assert payload["range_import_status"] == RangeImportStatus.IMPORTED.value
    assert payload["range_source_info"]["source_type"] == RangeSourceType.POSTFLOP_DEFAULT_RANGES.value
    assert payload["case_id"] == "flop_range_srp_heads_up_btn_vs_bb"
    assert payload["spot_family"] == FlopSpotFamily.SRP_HEADS_UP.value
    assert payload["pot_type"] == "srp"
    assert payload["hero_position"] == "BTN"
    assert payload["hero_range_state"]["range_name"] == "srp_btn_open_baseline"
    assert payload["opponent_range_states"][0]["range_name"] == "srp_bb_defense_baseline"
    assert payload["hero_range_state"]["combo_groups"]["premium_pairs"]
    assert payload["next_module"] == "blocker_filtering_later"
    json.dumps(payload)


def test_srp_oop_bb_vs_btn_selects_oop_baseline_range() -> None:
    context = _flop_context(
        case_id="srp_bb_vs_btn",
        spot_family=FlopSpotFamily.SRP_HEADS_UP,
        hero_position="BB",
        pot_type="srp",
    )

    result = _build(context)
    payload = result.to_json_dict()

    assert payload["case_id"] == "flop_range_srp_oop_bb_vs_btn"
    assert payload["hero_range_state"]["range_name"] == "srp_bb_defense_baseline"
    assert payload["opponent_range_states"][0]["range_name"] == "srp_btn_open_baseline"
    assert payload["opponent_positions"] == ["BTN"]


def test_three_bet_pot_ip_and_oop_get_distinct_baselines() -> None:
    ip_context = _flop_context(
        case_id="threebet_ip",
        spot_family=FlopSpotFamily.THREEBET_POT_HEADS_UP,
        hero_position="BTN",
        pot_type="3bet_pot",
    )
    oop_context = _flop_context(
        case_id="threebet_oop",
        spot_family=FlopSpotFamily.THREEBET_POT_HEADS_UP,
        hero_position="SB",
        pot_type="3bet_pot",
    )

    ip_result = _build(ip_context).to_json_dict()
    oop_result = _build(oop_context).to_json_dict()

    assert ip_result["case_id"] == "flop_range_3bet_pot_ip"
    assert ip_result["hero_range_state"]["role"] == "three_bet_caller_ip"
    assert ip_result["opponent_range_states"][0]["role"] == "three_bettor_oop"
    assert oop_result["case_id"] == "flop_range_3bet_pot_oop"
    assert oop_result["hero_range_state"]["role"] == "three_bettor_oop"
    assert oop_result["opponent_range_states"][0]["role"] == "three_bet_caller_ip"


def test_four_bet_low_spr_gets_four_bet_source() -> None:
    context = _flop_context(
        case_id="fourbet_low_spr",
        spot_family=FlopSpotFamily.FOURBET_LOW_SPR,
        hero_position="CO",
        pot_type="4bet_pot",
    )

    payload = _build(context).to_json_dict()

    assert payload["case_id"] == "flop_range_4bet_low_spr"
    assert payload["range_confidence"] == "high"
    assert payload["hero_range_state"]["range_name"] == "four_bet_low_spr_aggressor_baseline"
    assert payload["opponent_range_states"][0]["range_name"] == "four_bet_low_spr_caller_baseline"


def test_limp_or_passive_spot_gets_limp_passive_source() -> None:
    context = _flop_context(
        case_id="limp_passive",
        spot_family=FlopSpotFamily.LIMP_OR_PASSIVE_POT,
        hero_position="BB",
        pot_type="limped_pot",
    )

    payload = _build(context).to_json_dict()

    assert payload["case_id"] == "flop_range_limp_passive"
    assert payload["hero_range_state"]["role"] == "bb_option_vs_limp"
    assert payload["opponent_range_states"][0]["role"] == "limper"
    assert "defense_range" in payload["range_buckets"]


def test_multiway_spot_gets_multiway_range_mode() -> None:
    players = (
        {"player_id": "hero", "position": "BTN"},
        {"player_id": "villain_1", "position": "BB"},
        {"player_id": "villain_2", "position": "CO"},
    )
    context = _flop_context(
        case_id="multiway",
        spot_family=FlopSpotFamily.MULTIWAY_POT,
        hero_position="BTN",
        pot_type="multiway_pot",
        players=players,
    )

    payload = _build(context).to_json_dict()

    assert payload["case_id"] == "flop_range_multiway"
    assert payload["range_confidence"] == "low"
    assert len(payload["opponent_range_states"]) == 2
    assert payload["opponent_positions"] == ["BB", "CO"]


def test_unknown_spot_returns_structured_unknown_range_without_failure() -> None:
    context = _flop_context(
        case_id="unknown_context",
        spot_family=FlopSpotFamily.UNKNOWN_FLOP_SPOT,
        hero_position=None,
        pot_type=None,
        players=(),
    )

    payload = _build(context).to_json_dict()

    assert payload["case_id"] == "flop_range_unknown_context"
    assert payload["range_import_status"] == RangeImportStatus.UNKNOWN_RANGE.value
    assert payload["range_source_info"]["source_type"] == RangeSourceType.UNKNOWN_RANGE.value
    assert payload["range_confidence"] == "unknown"
    assert payload["hero_range_state"]["range_name"] == "unknown_range"
    assert payload["opponent_range_states"] == []
    assert payload["next_module"] == "blocker_filtering_later"


def test_missing_range_file_returns_structured_unknown_range() -> None:
    context = _flop_context(
        case_id="missing_range_file",
        spot_family=FlopSpotFamily.SRP_HEADS_UP,
        hero_position="BTN",
        pot_type="srp",
    )

    result = build_range_state_from_flop_context(
        context,
        project_root=PROJECT_ROOT,
        range_file=PROJECT_ROOT / "ranges" / "missing_postflop_ranges.json",
    )
    payload = result.to_json_dict()

    assert payload["range_import_status"] == RangeImportStatus.UNKNOWN_RANGE.value
    assert payload["range_source_info"]["source_type"] == RangeSourceType.UNKNOWN_RANGE.value
    assert "range_file" in payload["fields_not_provided"]


def test_range_importer_preserves_context_and_source_read_only() -> None:
    context = _flop_context(
        case_id="srp_btn_vs_bb_read_only",
        spot_family=FlopSpotFamily.SRP_HEADS_UP,
        hero_position="BTN",
        pot_type="srp",
    )
    before = context.to_json_dict()

    result = _build(context)
    after = context.to_json_dict()
    payload = result.to_json_dict()

    assert before == after
    assert payload["source_file"] == context.source_file
    assert payload["range_source_info"]["source_file"].endswith("ranges/postflop_default_ranges.json") or payload["range_source_info"]["source_file"].endswith("ranges\\postflop_default_ranges.json")
    assert RANGE_PACK.exists()


def test_range_importer_does_not_add_non_range_pipeline_logic() -> None:
    source = IMPORTER_SOURCE.read_text(encoding="utf-8").lower()

    forbidden_terms = [
        "pokerkit",
        "calculate_equity",
        "monte_carlo",
        "run_simulation",
        "decision_engine",
        "runtime_plan(",
        "click(",
        "mouse",
        "clear_json_pending",
        "dark_json",
        "current_cycle",
        "display_analysis_cycle",
        "action_button",
    ]

    for forbidden in forbidden_terms:
        assert forbidden not in source
