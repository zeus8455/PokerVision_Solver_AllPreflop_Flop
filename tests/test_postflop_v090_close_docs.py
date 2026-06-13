from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_readme_closes_v090_with_live_evidence() -> None:
    text = _read("README.md")
    assert "V0.9.0 — Main Live Clear_JSON Audit / Postflop Capture Evidence" in text
    assert "V0.9.8 — Close V0.9.0 / Live Audit Checkpoint" in text
    assert "evidence_status = passed" in text
    assert "module_chain_status = flop_features_completed" in text
    assert "runtime_click_chain_status = existing_project_chain_not_invoked_by_audit" in text


def test_version_tracks_v090_subversion_chain() -> None:
    text = _read("VERSION.md")
    required = [
        "bf062c5",
        "6928575",
        "0fabc40",
        "54e4f55",
        "813dd5f",
        "3b17f9f",
        "eb7fed5",
        "cca11f0",
        "52738bc",
        "14289f5",
        "5e315c8",
        "V0.9.8",
    ]
    for marker in required:
        assert marker in text


def test_checkpoint_records_v090_evidence_gate() -> None:
    text = _read("docs/checkpoints/V0_9_0_LIVE_AUDIT_CLOSE.md")
    assert "total_files_seen = 5" in text
    assert "total_clear_json_processed = 5" in text
    assert "artifacts_written.board_texture = 1" in text
    assert "artifacts_written.made_hand = 1" in text
    assert "artifacts_written.draw_features = 1" in text
    assert "errors = []" in text


def test_checkpoint_preserves_no_postflop_click_boundary() -> None:
    text = _read("docs/checkpoints/V0_9_0_LIVE_AUDIT_CLOSE.md")
    forbidden_boundaries = [
        "postflop poker decisions",
        "postflop Action_Decision_JSON",
        "postflop Action_Runtime_Plan_JSON",
        "postflop physical clicks",
        "Action_Button detector calls from the postflop solver",
        "equity calculation",
        "range construction",
        "bet sizing policy",
    ]
    for boundary in forbidden_boundaries:
        assert boundary in text


def test_miro_card_contains_copy_ready_close_summary() -> None:
    text = _read("docs/miro/V0_9_0_LIVE_AUDIT_MIRO_CARD.md")
    assert "Main goal" in text
    assert "Final evidence" in text
    assert "Important boundary" in text
    assert "Next discussion" in text
    assert "postflop solver remains **audit-only**" in text


def test_gitignore_ignores_generated_live_audit_outputs() -> None:
    text = _read(".gitignore")
    assert "outputs/postflop_live_clear_json_audit_v090/" in text
    assert "external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/postflop_live_clear_json/" in text
    assert "TABLE_03_HAND_49_DEEP_DUMP.txt" in text
