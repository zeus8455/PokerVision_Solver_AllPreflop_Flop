import pytest

from solver_postflop.contracts import (
    ContractValidationError,
    DiscoveryStatus,
    ModuleError,
    ModuleWarning,
    PostflopConfidence,
    PostflopRawSource,
    PostflopSourceCandidate,
    PostflopSourceDiscoveryResult,
    PostflopSourceType,
    RawSourceLoadStatus,
)


def test_v032_source_candidate_is_structured_and_serializable():
    candidate = PostflopSourceCandidate(
        source_file="tests/fixtures/postflop/source_json/dark_json/flop_source_case_001.dark.json",
        source_type="dark_json",
        table_id="table_01",
        hand_id="hand_001",
        detected_at="2026-06-09T00:00:00Z",
        has_board_cards=True,
        has_hero_cards=True,
        has_players=True,
        has_actions=True,
        can_be_normalized=True,
        confidence="high",
        warnings=[
            ModuleWarning(
                code="manual_fixture",
                message="Manual fixture source used for contract test.",
                context={"case_id": "flop_source_case_001"},
            )
        ],
    )

    data = candidate.to_dict()

    assert data["source_type"] == "dark_json"
    assert data["confidence"] == "high"
    assert data["has_board_cards"] is True
    assert data["can_be_normalized"] is True
    assert data["warnings"][0]["code"] == "manual_fixture"


def test_v032_source_candidate_requires_source_file():
    with pytest.raises(ContractValidationError):
        PostflopSourceCandidate(source_file="", source_type="dark_json")


def test_v032_source_candidate_rejects_bad_source_type():
    with pytest.raises(ContractValidationError):
        PostflopSourceCandidate(source_file="bad.json", source_type="not_supported")


def test_v032_confidence_accepts_only_allowed_values():
    assert PostflopConfidence.values() == ["high", "medium", "low", "unknown"]

    with pytest.raises(ContractValidationError):
        PostflopSourceCandidate(
            source_file="tests/fixtures/postflop/source_json/dark_json/flop_source_case_001.dark.json",
            source_type="dark_json",
            confidence="certain",
        )


def test_v032_table_id_and_hand_id_can_be_unknown_but_emit_warnings():
    candidate = PostflopSourceCandidate(
        source_file="tests/fixtures/postflop/source_json/dark_json/flop_source_case_001.dark.json",
        source_type=PostflopSourceType.DARK_JSON,
    )

    warning_codes = {warning.code for warning in candidate.warnings}

    assert candidate.table_id == "unknown"
    assert candidate.hand_id == "unknown"
    assert "missing_table_id" in warning_codes
    assert "missing_hand_id" in warning_codes


def test_v032_manual_live_like_candidate_cannot_be_real_source():
    with pytest.raises(ContractValidationError):
        PostflopSourceCandidate(
            source_file="tests/fixtures/postflop/source_json/manual_live_like_json/example.json",
            source_type="manual_live_like_json",
            is_real_project_source=True,
        )

    candidate = PostflopSourceCandidate(
        source_file="tests/fixtures/postflop/source_json/manual_live_like_json/example.json",
        source_type="manual_live_like_json",
        is_manual_live_like_source=True,
    )

    assert candidate.is_manual_live_like_source is True
    assert candidate.is_real_project_source is False


def test_v032_raw_source_preserves_raw_data_without_normalization():
    candidate = PostflopSourceCandidate(
        source_file="tests/fixtures/postflop/source_json/dark_json/flop_source_case_001.dark.json",
        source_type="dark_json",
        table_id="table_01",
        hand_id="hand_001",
    )
    raw_payload = {
        "weird_nested_field": {"kept": True},
        "board_cards": ["Ah", "Kd", "2c"],
    }

    raw_source = PostflopRawSource(
        candidate=candidate,
        raw_data=raw_payload,
        load_status=RawSourceLoadStatus.LOADED,
    )

    data = raw_source.to_dict()

    assert data["load_status"] == "loaded"
    assert data["raw_data"] == raw_payload
    assert data["candidate"]["source_file"].endswith("flop_source_case_001.dark.json")


def test_v032_raw_source_rejects_non_candidate():
    with pytest.raises(ContractValidationError):
        PostflopRawSource(candidate="not_candidate", raw_data={})  # type: ignore[arg-type]


def test_v032_raw_source_supports_warning_and_error_lists():
    candidate = PostflopSourceCandidate(
        source_file="tests/fixtures/postflop/source_json/unknown/bad.json",
        source_type="unknown",
    )

    raw_source = PostflopRawSource(
        candidate=candidate,
        raw_data={},
        load_status="invalid_json",
        warnings=[ModuleWarning(code="unknown_source", message="source_type unknown")],
        errors=[ModuleError(code="invalid_json", message="JSON could not be parsed")],
    )

    data = raw_source.to_dict()

    assert data["load_status"] == "invalid_json"
    assert data["warnings"][0]["code"] == "unknown_source"
    assert data["errors"][0]["severity"] == "error"


def test_v032_discovery_result_collects_candidates_raw_sources_warnings_and_errors():
    candidate = PostflopSourceCandidate(
        source_file="tests/fixtures/postflop/source_json/dark_json/flop_source_case_001.dark.json",
        source_type="dark_json",
        table_id="table_01",
        hand_id="hand_001",
        confidence="medium",
    )
    raw_source = PostflopRawSource(candidate=candidate, raw_data={"source": "kept"})

    result = PostflopSourceDiscoveryResult(
        input_root="tests/fixtures/postflop",
        candidates=[candidate],
        raw_sources=[raw_source],
        warnings=[ModuleWarning(code="partial_scan", message="Only fixture folder scanned.")],
        errors=[],
        status=DiscoveryStatus.PARTIAL,
    )

    data = result.to_dict()

    assert data["input_root"] == "tests/fixtures/postflop"
    assert data["status"] == "partial"
    assert data["candidates"][0]["confidence"] == "medium"
    assert data["raw_sources"][0]["raw_data"] == {"source": "kept"}
    assert data["warnings"][0]["code"] == "partial_scan"


def test_v032_discovery_result_requires_input_root():
    with pytest.raises(ContractValidationError):
        PostflopSourceDiscoveryResult(input_root="")


def test_v032_discovery_result_rejects_wrong_candidate_collection_item():
    with pytest.raises(ContractValidationError):
        PostflopSourceDiscoveryResult(input_root="tests/fixtures/postflop", candidates=["bad"])  # type: ignore[list-item]


def test_v032_status_enums_are_stable():
    assert RawSourceLoadStatus.values() == [
        "loaded",
        "invalid_json",
        "missing_file",
        "unreadable",
        "empty",
    ]
    assert DiscoveryStatus.values() == ["ok", "partial", "failed", "empty"]
