# V0.1.1 — Repo Identity / Baseline Audit

Generated at UTC: `2026-06-09T11:31:11+00:00`

## Summary

This report is the first baseline audit artifact for the V0.1.0 audit block. It does not validate postflop poker logic. It records the current repository identity, Git state, directory layout, README/VERSION identity signals, preflop baseline presence, and external snapshot presence.

## Repository identity

- Expected repo name: `PokerVision_Solver_AllPreflop_Flop`
- Project root name: `PokerVision_Solver_AllPreflop_Flop`
- Root name matches expected: **yes**
- Project root: `C:\PokerVision_Solver_AllPreflop_Flop`

## Git state

- Branch: `main`
- HEAD short: `db16abd`
- Origin: `https://github.com/zeus8455/PokerVision_Solver_AllPreflop_Flop.git`
- Working tree clean: **no**

### Git status --short

- `?? tests/test_baseline_audit_tools_v010.py`
- `?? tools/audit_current_project_baseline_v010.py`

## README identity check

- README exists: **yes**
- Contains expected repo name: **no**
- Contains legacy preflop name: **yes**
- Contains legacy preflop path: **yes**
- Identity mismatch detected: **yes**

## Directory presence

### Present

- `solver_preflop`
- `external`
- `tests`
- `tools`
- `outputs`
- `ranges`
- `examples/clear_json`
- `docs`
- `docs/checkpoints`

### Missing

- none

## Preflop baseline presence

Present modules: **11** / **11**

- `solver_preflop/__init__.py`
- `solver_preflop/clear_json_adapter.py`
- `solver_preflop/contracts.py`
- `solver_preflop/decision_engine.py`
- `solver_preflop/output_files.py`
- `solver_preflop/pokervision_bridge.py`
- `solver_preflop/range_engine.py`
- `solver_preflop/range_loader.py`
- `solver_preflop/range_parser.py`
- `solver_preflop/sizing_policy.py`
- `solver_preflop/spot_classifier.py`

## Postflop core presence

Dedicated postflop core candidates detected: **0**

- none

## External snapshot presence

- `external/PokerVisionFinalVersionNoSolver_snapshot`
- `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2`

## VERSION.md signals

- VERSION.md exists: **yes**
- Mentions V2.60: **yes**
- Mentions fixture review: **yes**

### First detected version headings/signals

- ## V2.34.0 - enable Solver_Preflop controlled raise branch
- - Remove the old V1.1 simple-button blocker only for Solver_Preflop-adapted preflop raise-family actions.
- - V2.34 audit status ok
- - V2.34 allows Solver_Preflop-controlled raise-family plans while preserving all runtime click guards.
- ## V2.32.0 - inject Solver_Preflop bridge before live runtime
- - V2.32 audit status ok
- - After V2.31, v11_stage1_runtime could accept ok/fallback Solver_Preflop bridge.
- - V2.32 injects the bridge before runtime, so the live click path can use Solver_Preflop instead of legacy stub.
- ## V2.31.0 - accept Solver_Preflop fallback bridge in live runtime
- - V2.31 audit status ok
- - V2.23 live runtime solver bridge audit updated for ok|fallback contract
- - After V2.30, duplicate Active retry reached action runtime.
- - V2.31 accepts fallback bridge when bridge_payload.action_decision exists, so live runtime uses Solver_Preflop instead of legacy stub.
- ## V2.30.0 - duplicate Active runtime retry when no runtime/final artifact exists
- - V2.30 audit status ok

## Risk flags

- **README_IDENTITY_MISMATCH** [medium]: Repository is AllPreflop_Flop, but README still identifies the project as PokerVision_Solver_Preflop.
- **PREFLOP_BASELINE_PRESENT** [info]: Preflop solver baseline modules are present and should be treated as source baseline, not postflop implementation.
- **POSTFLOP_CORE_NOT_PRESENT** [info]: No dedicated postflop solver/core directories were detected yet.
- **EXTERNAL_SNAPSHOT_PRESENT** [info]: External PokerVision NoSolver snapshot is present; do not modify it casually during V0.1.x audit.
- **WORKING_TREE_NOT_CLEAN** [medium]: Git working tree has uncommitted changes; commit/stash before development steps if needed.

## V0.1.1 conclusion

Current project state should be treated as an **AllPreflop_Flop repository identity with a legacy/preflop README and preflop solver baseline still present**. This is expected for V0.1.x and should not be fixed blindly before test, JSON-source, and player-state audits are complete.

## Recommended next action

Run V0.1.2 Test Suite Health Audit after this baseline identity audit is committed.
