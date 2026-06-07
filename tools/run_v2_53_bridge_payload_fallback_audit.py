from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOT = PROJECT_ROOT / "external" / "PokerVisionFinalVersionNoSolver_snapshot" / "PokerVision V1_2"

for path in (PROJECT_ROOT, SNAPSHOT_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import runtime.v11_stage1_runtime as v11


def _bridge_contract(kind: str) -> dict[str, Any]:
    if kind == "active_invalid_hero_cards":
        return {
            "schema_version": "solver_preflop_dryrun_bridge_v2_52",
            "source": "PokerVision_Solver_Preflop",
            "status": "ok",
            "reason": "v252_active_invalid_hero_cards_safe_runtime_fallback",
            "fallback_reason": "invalid_hero_count_0",
            "table_id": "table_01",
            "street": "preflop",
            "node_type": "active_invalid_hero_cards",
            "raw_action": "safe_runtime_fallback",
            "engine_action": "fold",
            "target_sequence": ["FOLD"],
            "bridge_payload": {
                "action_decision": {
                    "schema_version": "action_decision_v1",
                    "source": "Decision_JSON",
                    "source_decision_frame_id": "frame_v253_invalid_hero",
                    "status": "ok",
                    "action": "fold",
                    "size_policy": {"type": "none", "value": None},
                    "target_button_classes": ["FOLD"],
                    "reason": "v252_active_invalid_hero_cards_safe_runtime_fallback:invalid_hero_count_0",
                    "dry_run_safe": True,
                    "solver_stub": True,
                    "decision_context": {
                        "street": "preflop",
                        "source_frame_id": "frame_v253_invalid_hero",
                        "solver_preflop_runtime_source": True,
                        "solver_stub_legacy_compat": True,
                        "solver_decision_id": "v253_invalid_hero_decision",
                        "solver_fingerprint": "v253_invalid_hero_decision",
                        "solver_raw_action": "safe_runtime_fallback",
                        "solver_engine_action": "fold",
                        "node_type": "active_invalid_hero_cards",
                        "active_invalid_hero_cards": True,
                        "safe_runtime_fallback": True,
                        "target_sequence": ["FOLD"],
                    },
                }
            },
        }

    if kind == "postflop_solver_missing":
        return {
            "schema_version": "solver_preflop_dryrun_bridge_v2_51",
            "source": "PokerVision_Solver_Preflop",
            "status": "ok",
            "reason": "v251_postflop_solver_missing_safe_runtime_fallback",
            "table_id": "table_01",
            "street": "flop",
            "node_type": "postflop_solver_missing",
            "raw_action": "safe_runtime_fallback",
            "engine_action": "check_fold",
            "target_sequence": ["Check", "Check/fold", "FOLD"],
            "bridge_payload": {
                "action_decision": {
                    "schema_version": "action_decision_v1",
                    "source": "Decision_JSON",
                    "source_decision_frame_id": "frame_v253_postflop_missing",
                    "status": "ok",
                    "action": "check_fold",
                    "size_policy": {"type": "none", "value": None},
                    "target_button_classes": ["Check", "Check/fold", "FOLD"],
                    "reason": "v251_postflop_solver_missing_safe_runtime_fallback",
                    "dry_run_safe": True,
                    "solver_stub": True,
                    "decision_context": {
                        "street": "flop",
                        "source_frame_id": "frame_v253_postflop_missing",
                        "solver_preflop_runtime_source": True,
                        "solver_stub_legacy_compat": True,
                        "solver_decision_id": "v253_postflop_missing_decision",
                        "solver_fingerprint": "v253_postflop_missing_decision",
                        "solver_raw_action": "safe_runtime_fallback",
                        "solver_engine_action": "check_fold",
                        "node_type": "postflop_solver_missing",
                        "postflop_solver_missing": True,
                        "safe_runtime_fallback": True,
                        "target_sequence": ["Check", "Check/fold", "FOLD"],
                    },
                }
            },
        }

    raise ValueError(kind)


def _full_state(kind: str) -> dict[str, Any]:
    frame_name = "frame_v253_invalid_hero" if kind == "active_invalid_hero_cards" else "frame_v253_postflop_missing"
    return {
        "table": {
            "table_id": "table_01",
            "hand_id": "hand_v253",
            "frame_name": frame_name,
        },
        "pipeline_meta": {
            "frame_name": frame_name,
            "processing_time_ms": 1,
        },
        "solver_preflop_bridge_contract": _bridge_contract(kind),
    }


def _run_case(kind: str, tmp_dir: Path) -> dict[str, Any]:
    original = v11._V253_ORIGINAL_BUILD_AND_SAVE_SOLVER_PAYLOAD

    def _forced_failure(full_state: dict[str, Any], *, cycle_dir: Path):
        raise RuntimeError("forced_clear_json_payload_failure_for_v253_audit")

    v11._V253_ORIGINAL_BUILD_AND_SAVE_SOLVER_PAYLOAD = _forced_failure
    try:
        full_state = _full_state(kind)
        payload, payload_path = v11.build_and_save_solver_payload(full_state, cycle_dir=tmp_dir)
        decision = v11._extract_solver_preflop_decision_from_state(
            full_state=full_state,
            solver_payload=payload,
            solver_payload_path=payload_path,
        )
    finally:
        v11._V253_ORIGINAL_BUILD_AND_SAVE_SOLVER_PAYLOAD = original

    return {
        "payload": payload,
        "payload_path": str(payload_path),
        "payload_path_exists": Path(payload_path).exists(),
        "decision": decision,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--report-json", default="outputs/v2_53_bridge_payload_fallback_audit.json")
    args = parser.parse_args()

    out = Path(args.report_json)
    tmp_dir = out.parent / "v2_53_payload_fallback_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    cases = {
        "active_invalid_hero_cards": _run_case("active_invalid_hero_cards", tmp_dir),
        "postflop_solver_missing": _run_case("postflop_solver_missing", tmp_dir),
    }

    checks: dict[str, bool] = {}

    inv = cases["active_invalid_hero_cards"]
    inv_decision = inv["decision"] or {}
    inv_payload = inv["payload"] or {}
    checks["invalid_hero_payload_status_ok"] = inv_payload.get("status") == "ok"
    checks["invalid_hero_payload_source_bridge"] = inv_payload.get("source") == "solver_preflop_bridge_contract"
    checks["invalid_hero_payload_file_written"] = inv["payload_path_exists"] is True
    checks["invalid_hero_decision_extracted"] = isinstance(inv_decision, dict)
    checks["invalid_hero_decision_action_fold"] = inv_decision.get("action") == "fold"
    checks["invalid_hero_decision_sequence_fold"] = list(inv_decision.get("click_sequence") or []) == ["FOLD"]
    checks["invalid_hero_decision_not_stub"] = not str(inv_decision.get("decision_id") or "").startswith("v12_stub_")

    post = cases["postflop_solver_missing"]
    post_decision = post["decision"] or {}
    post_payload = post["payload"] or {}
    checks["postflop_payload_status_ok"] = post_payload.get("status") == "ok"
    checks["postflop_payload_source_bridge"] = post_payload.get("source") == "solver_preflop_bridge_contract"
    checks["postflop_payload_file_written"] = post["payload_path_exists"] is True
    checks["postflop_decision_extracted"] = isinstance(post_decision, dict)
    checks["postflop_decision_action_check_fold"] = post_decision.get("action") == "check_fold"
    checks["postflop_decision_sequence_check_fold"] = list(post_decision.get("click_sequence") or []) == ["Check", "Check/fold", "FOLD"]
    checks["postflop_decision_not_stub"] = not str(post_decision.get("decision_id") or "").startswith("v12_stub_")

    report = {
        "schema": "v2_53_bridge_payload_fallback_audit_v1",
        "ok": all(checks.values()),
        "checks": checks,
        "cases": cases,
    }

    print("V2.53 BRIDGE PAYLOAD FALLBACK AUDIT")
    for key, value in checks.items():
        print(f"{key:64} {value}")
    print("-" * 100)
    print(f"V2.53_BRIDGE_PAYLOAD_FALLBACK_AUDIT_OK = {report['ok']}")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
