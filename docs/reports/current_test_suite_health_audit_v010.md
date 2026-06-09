# V0.1.2 — Test Suite Health Audit

## Overview

This report classifies the current pytest suite before any postflop solver, normalizer, player resolver, ranges, equity, runtime, or click-chain changes.

The audit is intentionally conservative: legacy, live, external snapshot, and old-output tests are not deleted or treated as automatic blockers for postflop development.

## Run Metadata

- Schema version: `v0.1.2-test-suite-health`
- Generated at UTC: `2026-06-09T11:51:05+00:00`
- Project root: `C:\PokerVision_Solver_AllPreflop_Flop`
- Run mode: `safe`
- Timeout per pytest call: `35s`

## Summary

- **total_test_files**: `81`
- **by_category**: `{'live_dry_run': 55, 'core_baseline': 4, 'future_postflop': 11, 'legacy_old_audit': 10, 'static_dynamic_map': 1}`
- **by_collect_status**: `{'passed': 81}`
- **by_run_status**: `{'not_run_guarded': 78, 'passed': 2, 'timeout': 1}`
- **by_recommended_action**: `{'keep_but_not_blocking': 67, 'keep_as_required_baseline': 3, 'fix_before_postflop': 1, 'mark_legacy': 10}`
- **requires_live_environment**: `64`
- **requires_external_snapshot**: `27`
- **requires_old_outputs**: `60`
- **blocking_for_postflop_dev**: `4`

## Test File Classification

| test_file | category | collect | run | live | external | old_outputs | blocking | action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `tests/test_allin_logic_v06.py` | live_dry_run | passed | not_run_guarded | yes | no | no | no | keep_but_not_blocking |
| `tests/test_baseline_audit_tools_v010.py` | live_dry_run | passed | not_run_guarded | no | yes | no | no | keep_but_not_blocking |
| `tests/test_cards.py` | core_baseline | passed | passed | no | no | no | yes | keep_as_required_baseline |
| `tests/test_clear_json_adapter.py` | live_dry_run | passed | not_run_guarded | yes | no | no | no | keep_but_not_blocking |
| `tests/test_clear_json_adapter_v02.py` | live_dry_run | passed | not_run_guarded | yes | no | no | no | keep_but_not_blocking |
| `tests/test_cold_4bet_range_support_v15.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_cold_blind_vs_3bet_v14.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_defensive_ranges_v05.py` | live_dry_run | passed | not_run_guarded | yes | no | no | no | keep_but_not_blocking |
| `tests/test_display_cycle_bridge_embedding_v16.py` | live_dry_run | passed | not_run_guarded | yes | no | no | no | keep_but_not_blocking |
| `tests/test_output_files_v08.py` | live_dry_run | passed | not_run_guarded | yes | no | no | no | keep_but_not_blocking |
| `tests/test_pokervision_bridge_v09.py` | live_dry_run | passed | not_run_guarded | yes | no | no | no | keep_but_not_blocking |
| `tests/test_preintegration_v10.py` | core_baseline | passed | timeout | no | no | no | yes | fix_before_postflop |
| `tests/test_range_engine_v04.py` | live_dry_run | passed | not_run_guarded | yes | no | no | no | keep_but_not_blocking |
| `tests/test_range_parser_v04.py` | core_baseline | passed | passed | no | no | no | yes | keep_as_required_baseline |
| `tests/test_response_contract_v07.py` | live_dry_run | passed | not_run_guarded | yes | no | no | no | keep_but_not_blocking |
| `tests/test_snapshot_bridge_check_v13.py` | core_baseline | passed | not_run_guarded | no | yes | no | yes | keep_as_required_baseline |
| `tests/test_snapshot_cycle_bridge_smoke_v19.py` | live_dry_run | passed | not_run_guarded | yes | yes | no | no | keep_but_not_blocking |
| `tests/test_snapshot_main_startup_smoke_v18.py` | live_dry_run | passed | not_run_guarded | yes | yes | no | no | keep_but_not_blocking |
| `tests/test_solver_decision.py` | live_dry_run | passed | not_run_guarded | yes | no | no | no | keep_but_not_blocking |
| `tests/test_solver_preflop_bridge_publication_v17.py` | future_postflop | passed | not_run_guarded | yes | yes | no | no | keep_but_not_blocking |
| `tests/test_solver_preflop_dryrun_bridge_v12.py` | future_postflop | passed | not_run_guarded | yes | yes | no | no | keep_but_not_blocking |
| `tests/test_spot_classifier_v02.py` | live_dry_run | passed | not_run_guarded | yes | no | no | no | keep_but_not_blocking |
| `tests/test_spot_classifier_v03.py` | live_dry_run | passed | not_run_guarded | yes | no | no | no | keep_but_not_blocking |
| `tests/test_v2_0_snapshot_runtime_source_switch.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_v2_10_snapshot_transaction_source_audit.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_v2_11_snapshot_transaction_lifecycle_audit.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_v2_12_snapshot_display_transaction_integration_audit.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_v2_13_snapshot_final_action_publication_regression.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_v2_14_snapshot_final_solver_source_regression.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_v2_15_snapshot_all_preflop_e2e.py` | future_postflop | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_v2_16_snapshot_6slot_preflop_e2e.py` | future_postflop | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_v2_17_pre_live_config_audit.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_18_startup_audit_only_readiness.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_19_live_no_click_capture_probe.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_1_snapshot_solver_source_dryrun.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_v2_21_real_click_stub_blocker_audit.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_22_strict_real_click_source_guard_audit.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_23_live_runtime_solver_bridge_audit.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_24_snapshot_live_runtime_e2e.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_v2_25_real_startup_readiness_after_v224.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_26_live_no_click_probe_after_v225.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_28_live_transaction_gate_unlock_audit.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_29_early_gate_stale_lifecycle_release_audit.py` | legacy_old_audit | passed | not_run_guarded | no | no | yes | no | mark_legacy |
| `tests/test_v2_2_snapshot_solver_source_multicase.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_v2_30_duplicate_active_runtime_retry_audit.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_31_accept_solver_preflop_fallback_contract_audit.py` | future_postflop | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_32_pre_runtime_solver_bridge_injection_audit.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_34_enable_solver_preflop_raise_branch_audit.py` | future_postflop | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_35_synthetic_real_click_gate_e2e.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_36_synthetic_clear_json_runtime_chain.py` | future_postflop | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_37_lineage_cleanup_audit.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_38_synthetic_lifecycle_regression.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_39_spot_classifier_no_raise_audit.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_3_snapshot_runtime_publication.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_v2_40_real_clear_json_adapter_audit.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_41_safe_fallback_runtime_fold_audit.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_42_full_preflop_spot_matrix_e2e.py` | future_postflop | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_43_allin_semantic_cleanup_audit.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_44_premium_fold_guard_e2e.py` | legacy_old_audit | passed | not_run_guarded | no | no | yes | no | mark_legacy |
| `tests/test_v2_45_allin_taxonomy_audit.py` | future_postflop | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_46_clear_json_allin_propagation_audit.py` | legacy_old_audit | passed | not_run_guarded | no | no | yes | no | mark_legacy |
| `tests/test_v2_47_allin_stack_policy_audit.py` | legacy_old_audit | passed | not_run_guarded | no | no | yes | no | mark_legacy |
| `tests/test_v2_48_unknown_amount_allin_audit.py` | legacy_old_audit | passed | not_run_guarded | no | no | yes | no | mark_legacy |
| `tests/test_v2_49_dark_clear_solver_runtime_chain.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_4_snapshot_click_guard_eligibility.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_v2_50_remove_game_service_policy_audit.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_51_postflop_runtime_fallback_audit.py` | future_postflop | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_52_invalid_hero_runtime_fallback_audit.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_53_bridge_payload_fallback_audit.py` | future_postflop | passed | not_run_guarded | no | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_54_project_static_logic_map.py` | static_dynamic_map | passed | not_run_guarded | no | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_55_project_dynamic_execution_map.py` | legacy_old_audit | passed | not_run_guarded | no | no | yes | no | mark_legacy |
| `tests/test_v2_56_project_logic_coverage_report.py` | live_dry_run | passed | not_run_guarded | yes | no | yes | no | keep_but_not_blocking |
| `tests/test_v2_57_cleanup_review_report.py` | legacy_old_audit | passed | not_run_guarded | no | yes | yes | no | mark_legacy |
| `tests/test_v2_58_delete_candidate_inspection.py` | legacy_old_audit | passed | not_run_guarded | no | no | yes | no | mark_legacy |
| `tests/test_v2_59_fixture_json_trust_review.py` | legacy_old_audit | passed | not_run_guarded | no | no | yes | no | mark_legacy |
| `tests/test_v2_5_snapshot_click_result_publication.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_v2_60_fixture_review_inspection.py` | legacy_old_audit | passed | not_run_guarded | no | no | yes | no | mark_legacy |
| `tests/test_v2_6_snapshot_final_clear_embedding.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_v2_7_snapshot_display_finalization_audit.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_v2_8_snapshot_6slot_isolation_audit.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |
| `tests/test_v2_9_snapshot_finalization_blocker_audit.py` | live_dry_run | passed | not_run_guarded | yes | yes | yes | no | keep_but_not_blocking |

## Failure / Guard Notes

### `tests/test_allin_logic_v06.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: safe mode avoided executing this file

### `tests/test_baseline_audit_tools_v010.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains external snapshot references
- Note: safe mode avoided executing this file

### `tests/test_clear_json_adapter.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: safe mode avoided executing this file

### `tests/test_clear_json_adapter_v02.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: safe mode avoided executing this file

### `tests/test_cold_4bet_range_support_v15.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_cold_blind_vs_3bet_v14.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_defensive_ranges_v05.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: safe mode avoided executing this file

### `tests/test_display_cycle_bridge_embedding_v16.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: safe mode avoided executing this file

### `tests/test_output_files_v08.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: safe mode avoided executing this file

### `tests/test_pokervision_bridge_v09.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: safe mode avoided executing this file

### `tests/test_preintegration_v10.py`
- Failure / guard reason: `run_timeout: .`

### `tests/test_range_engine_v04.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: safe mode avoided executing this file

### `tests/test_response_contract_v07.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: safe mode avoided executing this file

### `tests/test_snapshot_bridge_check_v13.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains external snapshot references
- Note: safe mode avoided executing this file

### `tests/test_snapshot_cycle_bridge_smoke_v19.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: safe mode avoided executing this file

### `tests/test_snapshot_main_startup_smoke_v18.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: safe mode avoided executing this file

### `tests/test_solver_decision.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: safe mode avoided executing this file

### `tests/test_solver_preflop_bridge_publication_v17.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: safe mode avoided executing this file

### `tests/test_solver_preflop_dryrun_bridge_v12.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: safe mode avoided executing this file

### `tests/test_spot_classifier_v02.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: safe mode avoided executing this file

### `tests/test_spot_classifier_v03.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: safe mode avoided executing this file

### `tests/test_v2_0_snapshot_runtime_source_switch.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_10_snapshot_transaction_source_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_11_snapshot_transaction_lifecycle_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_12_snapshot_display_transaction_integration_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_13_snapshot_final_action_publication_regression.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_14_snapshot_final_solver_source_regression.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_15_snapshot_all_preflop_e2e.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_16_snapshot_6slot_preflop_e2e.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_17_pre_live_config_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_18_startup_audit_only_readiness.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_19_live_no_click_capture_probe.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_1_snapshot_solver_source_dryrun.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_21_real_click_stub_blocker_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_22_strict_real_click_source_guard_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_23_live_runtime_solver_bridge_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_24_snapshot_live_runtime_e2e.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_25_real_startup_readiness_after_v224.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_26_live_no_click_probe_after_v225.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_28_live_transaction_gate_unlock_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_29_early_gate_stale_lifecycle_release_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_2_snapshot_solver_source_multicase.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_30_duplicate_active_runtime_retry_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_31_accept_solver_preflop_fallback_contract_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_32_pre_runtime_solver_bridge_injection_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_34_enable_solver_preflop_raise_branch_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_35_synthetic_real_click_gate_e2e.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_36_synthetic_clear_json_runtime_chain.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_37_lineage_cleanup_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_38_synthetic_lifecycle_regression.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_39_spot_classifier_no_raise_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_3_snapshot_runtime_publication.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_40_real_clear_json_adapter_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_41_safe_fallback_runtime_fold_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_42_full_preflop_spot_matrix_e2e.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_43_allin_semantic_cleanup_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_44_premium_fold_guard_e2e.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_45_allin_taxonomy_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_46_clear_json_allin_propagation_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_47_allin_stack_policy_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_48_unknown_amount_allin_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_49_dark_clear_solver_runtime_chain.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_4_snapshot_click_guard_eligibility.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_50_remove_game_service_policy_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_51_postflop_runtime_fallback_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_52_invalid_hero_runtime_fallback_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_53_bridge_payload_fallback_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_54_project_static_logic_map.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_55_project_dynamic_execution_map.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_56_project_logic_coverage_report.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_57_cleanup_review_report.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_58_delete_candidate_inspection.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_59_fixture_json_trust_review.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_5_snapshot_click_result_publication.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_60_fixture_review_inspection.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_6_snapshot_final_clear_embedding.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_7_snapshot_display_finalization_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_8_snapshot_6slot_isolation_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

### `tests/test_v2_9_snapshot_finalization_blocker_audit.py`
- Failure / guard reason: `run skipped by safe audit guard`
- Note: contains live/runtime/click/screen related references
- Note: contains external snapshot references
- Note: contains outputs/fixture/current_cycle related references
- Note: safe mode avoided executing this file

## V0.1.2 Conclusion

This report is the test-suite baseline for the new postflop direction. The next version should continue with JSON source mapping, not with direct postflop decision logic.

Next step: **V0.1.3 — JSON Source Map Audit**.
