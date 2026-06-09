import pytest

from solver_postflop.contracts import (
    ContractValidationError,
    ModuleWarning,
    NormalizationStatus,
    NormalizedPostflopFrame,
    PostflopActionSnapshot,
    PostflopBoardSnapshot,
    PostflopPlayerSnapshot,
    PostflopSourceType,
)

SOURCE_FILE = "tests/fixtures/postflop/source_json/dark_json/flop_source_case_001.dark.json"


def test_v033_player_snapshot_preserves_state_without_refiltering():
    player = PostflopPlayerSnapshot(
        seat_id="seat_01",
        player_name="Hero",
        stack=97.5,
        committed=2.5,
        position="BTN",
        is_hero=True,
        is_active=True,
        is_folded=False,
        is_sitout=False,
        is_all_in=False,
        raw_state={"chips": 2.5, "source": "dark_json"},
    )

    payload = player.to_dict()

    assert payload["seat_id"] == "seat_01"
    assert payload["is_hero"] is True
    assert payload["raw_state"]["source"] == "dark_json"
    assert payload["stack"] == 97.5
    assert payload["committed"] == 2.5


@pytest.mark.parametrize(
    "field_name, kwargs",
    [
        ("stack", {"stack": -1}),
        ("committed", {"committed": -0.01}),
    ],
)
def test_v033_player_snapshot_rejects_negative_amounts(field_name, kwargs):
    with pytest.raises(ContractValidationError, match=field_name):
        PostflopPlayerSnapshot(seat_id="seat_02", **kwargs)


def test_v033_board_snapshot_accepts_zero_to_five_cards():
    empty_board = PostflopBoardSnapshot(cards=[])
    river_board = PostflopBoardSnapshot(cards=["As", "Kd", "7c", "2h", "9s"], declared_street="river")

    assert empty_board.to_dict()["cards"] == []
    assert river_board.to_dict()["declared_street"] == "river"
    assert len(river_board.cards) == 5


def test_v033_board_snapshot_rejects_more_than_five_cards():
    with pytest.raises(ContractValidationError, match="more than 5"):
        PostflopBoardSnapshot(cards=["As", "Kd", "7c", "2h", "9s", "Tc"])


def test_v033_duplicate_board_cards_are_warning_not_final_street_error():
    board = PostflopBoardSnapshot(cards=["As", "As", "7c"], declared_street="flop")

    warnings = board.to_dict()["warnings"]

    assert any(warning["code"] == "duplicate_board_cards" for warning in warnings)


def test_v033_action_snapshot_preserves_allowed_actions_and_raw_context():
    action = PostflopActionSnapshot(
        allowed_actions=["Check", "Bet"],
        to_call=0,
        min_raise=2.5,
        bet_size_options=["50%", "75%"],
        raw_action_context={"buttons_detected": ["Check", "Bet"]},
    )

    payload = action.to_dict()

    assert payload["allowed_actions"] == ["Check", "Bet"]
    assert payload["min_raise"] == 2.5
    assert payload["raw_action_context"]["buttons_detected"] == ["Check", "Bet"]


@pytest.mark.parametrize(
    "field_name, kwargs",
    [
        ("to_call", {"to_call": -1}),
        ("min_raise", {"min_raise": -1}),
    ],
)
def test_v033_action_snapshot_rejects_negative_amounts(field_name, kwargs):
    with pytest.raises(ContractValidationError, match=field_name):
        PostflopActionSnapshot(**kwargs)


def test_v033_normalized_frame_preserves_normalized_and_raw_layers():
    players = [
        PostflopPlayerSnapshot(seat_id="seat_01", player_name="Hero", stack=100, committed=1, is_hero=True),
        PostflopPlayerSnapshot(seat_id="seat_02", player_name="Villain", stack=90, committed=1),
    ]
    warning = ModuleWarning(code="partial_actions", message="Only partial action context was extracted.")

    frame = NormalizedPostflopFrame(
        source_type=PostflopSourceType.DARK_JSON,
        source_file=SOURCE_FILE,
        table_id="table_01",
        hand_id="hand_001",
        street_candidate="flop",
        hero_cards=["Ah", "Kd"],
        board_cards=["As", "7d", "2c"],
        pot=3.5,
        to_call=0,
        players=players,
        raw_players=[{"seat_id": "seat_01"}, {"seat_id": "seat_02"}],
        allowed_actions=["Check", "Bet"],
        raw_action_context={"buttons": ["Check", "Bet"]},
        normalization_status=NormalizationStatus.PARTIAL,
        normalization_warnings=[warning],
        raw_frame={"source_schema": "manual_live_like_dark_json"},
    )

    payload = frame.to_dict()

    assert payload["source_type"] == "dark_json"
    assert payload["street_candidate"] == "flop"
    assert payload["hero_cards"] == ["Ah", "Kd"]
    assert payload["board_cards"] == ["As", "7d", "2c"]
    assert len(payload["players"]) == 2
    assert payload["raw_players"] == [{"seat_id": "seat_01"}, {"seat_id": "seat_02"}]
    assert payload["raw_frame"]["source_schema"] == "manual_live_like_dark_json"
    assert payload["normalization_warnings"][0]["code"] == "partial_actions"


def test_v033_normalized_frame_creates_board_and_action_snapshots():
    frame = NormalizedPostflopFrame(
        source_type="dark_json",
        source_file=SOURCE_FILE,
        table_id="table_01",
        hand_id="hand_001",
        street_candidate="flop",
        hero_cards=["Ah", "Kd"],
        board_cards=["As", "7d", "2c"],
        allowed_actions=["Check"],
        to_call=0,
    )

    payload = frame.to_dict()

    assert payload["board_snapshot"]["cards"] == ["As", "7d", "2c"]
    assert payload["action_snapshot"]["allowed_actions"] == ["Check"]


@pytest.mark.parametrize(
    "field_name, kwargs",
    [
        ("hero_cards", {"hero_cards": ["Ah", "Kd", "Qs"]}),
        ("board_cards", {"board_cards": ["As", "Kd", "7c", "2h", "9s", "Tc"]}),
        ("pot", {"pot": -0.01}),
        ("to_call", {"to_call": -0.01}),
    ],
)
def test_v033_normalized_frame_rejects_invalid_card_counts_and_negative_amounts(field_name, kwargs):
    base_kwargs = {
        "source_type": "dark_json",
        "source_file": SOURCE_FILE,
    }
    base_kwargs.update(kwargs)

    with pytest.raises(ContractValidationError, match=field_name):
        NormalizedPostflopFrame(**base_kwargs)


def test_v033_normalized_frame_allows_missing_optional_table_and_hand_with_warnings():
    frame = NormalizedPostflopFrame(
        source_type="dark_json",
        source_file=SOURCE_FILE,
        hero_cards=["Ah", "Kd"],
        board_cards=["As", "7d", "2c"],
    )

    warning_codes = {warning["code"] for warning in frame.to_dict()["normalization_warnings"]}

    assert "missing_table_id" in warning_codes
    assert "missing_hand_id" in warning_codes
