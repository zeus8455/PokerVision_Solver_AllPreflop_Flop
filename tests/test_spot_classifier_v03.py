import json
from pathlib import Path

from solver_preflop import solve_clear_json
from solver_preflop.clear_json_adapter import parse_clear_json_preflop
from solver_preflop.spot_classifier import classify_preflop_spot


def _base():
    path = Path("examples/clear_json/table_02_hand_29_preflop_01_preclick.json")
    return json.loads(path.read_text(encoding="utf-8"))


def _move_hero(data, pos, cards=("A_spades", "Q_hearts"), chips=False):
    for player in data["players"].values():
        player.pop("hero", None)
        player.pop("cards", None)
    data["players"][pos]["hero"] = True
    data["players"][pos]["cards"] = list(cards)
    data["players"][pos]["fold"] = False
    data["players"][pos]["chips"] = chips


def test_sb_first_in_classified():
    data = _base()

    for pos in ["UTG", "MP", "CO", "BTN"]:
        data["players"][pos]["fold"] = True
        data["players"][pos]["chips"] = False

    data["players"]["BB"].pop("hero", None)
    data["players"]["BB"].pop("cards", None)
    data["players"]["BB"]["fold"] = False
    data["players"]["BB"]["chips"] = 1.0

    _move_hero(data, "SB", cards=("A_spades", "Q_hearts"), chips=0.5)

    decision = solve_clear_json(data)

    assert decision.node_type == "sb_first_in"
    assert decision.raw_action == "open_raise"
    assert decision.click_sequence == ["Raise"]


def test_btn_facing_open_classified():
    data = _base()

    data["players"]["UTG"]["fold"] = True
    data["players"]["UTG"]["chips"] = False
    data["players"]["MP"]["fold"] = True
    data["players"]["MP"]["chips"] = False
    data["players"]["CO"]["fold"] = False
    data["players"]["CO"]["chips"] = 2.5

    data["players"]["BB"].pop("hero", None)
    data["players"]["BB"].pop("cards", None)
    data["players"]["BB"]["fold"] = False
    data["players"]["BB"]["chips"] = 1.0

    _move_hero(data, "BTN", chips=False)

    frame = parse_clear_json_preflop(data)
    spot = classify_preflop_spot(frame)

    assert spot.node_type == "facing_open"
    assert spot.opener_pos == "CO"
    assert spot.to_call_bb == 2.5


def test_bb_blind_vs_open_classified():
    data = _base()

    data["players"]["UTG"]["fold"] = True
    data["players"]["UTG"]["chips"] = False
    data["players"]["MP"]["fold"] = True
    data["players"]["MP"]["chips"] = False
    data["players"]["CO"]["fold"] = True
    data["players"]["CO"]["chips"] = False
    data["players"]["BTN"]["fold"] = False
    data["players"]["BTN"]["chips"] = 2.5

    decision = solve_clear_json(data)

    assert decision.node_type == "blind_vs_open"
    assert decision.debug["to_call_bb"] == 1.5
    assert decision.raw_action in {"fold", "call", "3bet"}


def test_limper_vs_iso_classified():
    data = _base()

    data["players"]["BB"].pop("hero", None)
    data["players"]["BB"].pop("cards", None)
    data["players"]["BB"]["fold"] = False
    data["players"]["BB"]["chips"] = 1.0

    _move_hero(data, "MP", cards=("K_spades", "Q_hearts"), chips=1.0)

    data["players"]["UTG"]["fold"] = True
    data["players"]["UTG"]["chips"] = False
    data["players"]["CO"]["fold"] = True
    data["players"]["CO"]["chips"] = False
    data["players"]["BTN"]["fold"] = False
    data["players"]["BTN"]["chips"] = 4.5

    decision = solve_clear_json(data)

    assert decision.node_type == "limper_vs_iso"
    assert decision.debug["to_call_bb"] == 3.5
    assert decision.raw_action in {"fold", "call", "3bet"}


def test_opener_vs_small_3bet_classified():
    data = _base()

    for pos in ["UTG", "MP"]:
        data["players"][pos]["fold"] = True
        data["players"][pos]["chips"] = False

    data["players"]["BB"].pop("hero", None)
    data["players"]["BB"].pop("cards", None)
    data["players"]["BB"]["fold"] = False
    data["players"]["BB"]["chips"] = 1.0

    _move_hero(data, "CO", cards=("A_spades", "J_hearts"), chips=2.0)

    data["players"]["BTN"]["fold"] = False
    data["players"]["BTN"]["chips"] = 4.0

    decision = solve_clear_json(data)

    assert decision.node_type == "opener_vs_small_3bet"
    assert decision.debug["sizing_category"] == "small_3bet"
    assert decision.debug["sizing_ratio"] == 2.0
    assert decision.debug["to_call_bb"] == 2.0
    assert decision.raw_action in {"call", "4bet"}


def test_opener_vs_normal_3bet_classified():
    data = _base()

    for pos in ["UTG", "MP", "BTN"]:
        data["players"][pos]["fold"] = True
        data["players"][pos]["chips"] = False

    data["players"]["BB"].pop("hero", None)
    data["players"]["BB"].pop("cards", None)
    data["players"]["BB"]["fold"] = False
    data["players"]["BB"]["chips"] = 1.0

    _move_hero(data, "CO", cards=("A_spades", "J_hearts"), chips=2.5)

    data["players"]["SB"]["fold"] = False
    data["players"]["SB"]["chips"] = 8.0

    decision = solve_clear_json(data)

    assert decision.node_type == "opener_vs_normal_3bet"
    assert decision.debug["sizing_category"] == "normal_3bet"
    assert round(decision.debug["sizing_ratio"], 2) == 3.2


def test_threebettor_vs_4bet_classified():
    data = _base()

    for pos in ["UTG", "MP"]:
        data["players"][pos]["fold"] = True
        data["players"][pos]["chips"] = False

    data["players"]["BB"].pop("hero", None)
    data["players"]["BB"].pop("cards", None)
    data["players"]["BB"]["fold"] = False
    data["players"]["BB"]["chips"] = 1.0

    data["players"]["CO"]["fold"] = False
    data["players"]["CO"]["chips"] = 2.5

    _move_hero(data, "BTN", cards=("A_spades", "K_hearts"), chips=8.0)

    data["players"]["SB"]["fold"] = False
    data["players"]["SB"]["chips"] = 20.0

    decision = solve_clear_json(data)

    assert decision.node_type == "threebettor_vs_normal_4bet"
    assert decision.debug["sizing_category"] == "normal_4bet"
    assert decision.debug["three_bettor_pos"] == "BTN"
    assert decision.debug["four_bettor_pos"] == "SB"
    assert decision.debug["to_call_bb"] == 12.0
