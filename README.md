# PokerVision_Solver_AllPreflop_Flop

Postflop development line for PokerVision on top of the existing **AllPreflop / Preflop Solver baseline**.

Current closed block: **V0.1.0 — Current Baseline / Test / Source Audit**  
Current checkpoint: **c2723c3 — V0.1.5 add final baseline report**

---

## Purpose

This repository starts from the previous **PokerVision_Solver_Preflop** baseline and becomes the new working line for:

```text
PokerVision_Solver_AllPreflop_Flop
```

The project goal is to build a safe postflop development chain without breaking the existing preflop/runtime baseline.

Before writing any postflop solver, normalizer, source discovery, player resolver, ranges, equity, or click-chain logic, the project must first understand:

- what is already present in the repository;
- which tests are current, legacy, audit-only, or live-only;
- which JSON files are actually created by the current project;
- which JSON sources are available before click-cycle and after click-cycle;
- which player-state/filtering logic already exists and must not be duplicated;
- where future postflop source discovery can safely attach.

---

## Current development rule

Development is versioned by controlled blocks.

For every version/subversion:

1. discuss the scope first;
2. implement only after explicit approval;
3. deliver a ZIP with ready project structure;
4. integrate through one PowerShell command;
5. run the required checks;
6. commit and push a short Git checkpoint;
7. update README/version documentation when a full version block is closed;
8. document the version in Miro.

No runtime/click-chain/source-of-truth logic is changed without a separate approved version.

---

## Repository status after V0.1.0

The current repository is **not yet a clean postflop solver**.

It is currently:

```text
AllPreflop_Flop repository shell
+ existing PokerVision_Solver_Preflop baseline
+ external PokerVision snapshot
+ legacy/audit/live test history
+ runtime/output JSON history
```

This is expected. V0.1.0 was created specifically to audit and document that baseline before new postflop modules are added.

---

## Closed version: V0.1.0 — Current Baseline / Test / Source Audit

**Status:** closed  
**Final checkpoint:** `c2723c3 — V0.1.5 add final baseline report`  
**Ready for V0.2 design:** `True`

### Goal

Create a factual audit layer for the current repository before starting postflop development.

V0.1.0 did **not** create postflop solver logic.

It created tools and reports for:

- project baseline audit;
- test suite health audit;
- JSON source map audit;
- player-state/filtering audit;
- final V0.1 report and V0.2 plan.

---

## V0.1 subversions

### V0.1.1 — Repo Identity / Baseline Audit

**Commit:** `6bb90f8 — V0.1.1 add project baseline audit`

Created:

- `tools/audit_current_project_baseline_v010.py`
- `tests/test_baseline_audit_tools_v010.py`
- `docs/reports/current_project_baseline_audit_v010.md`
- `outputs/baseline_audit_v010/project_baseline_report.json`

Result:

- repository identity was captured;
- mismatch was detected: repository is now `PokerVision_Solver_AllPreflop_Flop`, but old README/project identity still described `PokerVision_Solver_Preflop`;
- current base was confirmed as preflop baseline + external snapshot + legacy/audit/test history.

---

### V0.1.2 — Test Suite Health Audit

**Commit:** `c062077 — V0.1.2 add test suite health audit`

Created:

- `tools/audit_current_test_suite_health_v010.py`
- `docs/reports/current_test_suite_health_audit_v010.md`
- `outputs/baseline_audit_v010/test_suite_health_report.json`

Updated:

- `tests/test_baseline_audit_tools_v010.py`

Result:

- total test files found: `81`
- categories:
  - `live_dry_run`: `55`
  - `core_baseline`: `4`
  - `future_postflop`: `11`
  - `legacy_old_audit`: `10`
  - `static_dynamic_map`: `1`

Main conclusion:

```text
Do not treat old live/legacy/audit tests as automatic blockers for postflop development.
```

---

### V0.1.3 — JSON Source Map Audit

**Commit:** `00bfea3 — V0.1.3 add json source map audit`

Created:

- `tools/audit_current_json_source_map_v010.py`
- `docs/reports/current_json_source_map_v010.md`
- `outputs/baseline_audit_v010/json_source_map_report.json`

Updated:

- `tests/test_baseline_audit_tools_v010.py`

Result:

- total JSON files found: `187`
- source types:
  - `current_cycle_json`: `36`
  - `dark_json`: `1`
  - `final_clear_json`: `10`
  - `pending_json`: `28`
  - `runtime_json`: `2`
  - `solver_payload_json`: `101`
  - `unknown`: `9`
- before-click sources: `78`
- after-click sources: `109`

Main conclusion:

```text
Final Clear_JSON must not be the only source for future postflop source discovery.
```

Future postflop source handling must support intermediate JSON sources such as:

- `dark_json`
- `pending_json`
- `current_cycle_json`
- `runtime_json`
- `solver_payload_json`
- `final_clear_json`
- `manual_live_like_json`
- `unknown`

---

### V0.1.4 — Player-State / Filtering Audit

**Commit:** `077eb88 — V0.1.4 add player state filtering audit`

Created:

- `tools/audit_current_player_state_filtering_v010.py`
- `docs/reports/current_player_state_filtering_audit_v010.md`
- `outputs/baseline_audit_v010/player_state_filtering_report.json`

Updated:

- `tests/test_baseline_audit_tools_v010.py`

Result:

- files scanned: `1015`
- mechanisms found: `1297`
- mechanisms marked `should_not_duplicate`: `1256`
- logic types:
  - `hero_detection`: `449`
  - `sitout_filtering`: `284`
  - `clear_json_filtering`: `193`
  - `all_in_state`: `112`
  - `active_player_state`: `107`
  - `trigger_service_state`: `65`
  - `final_clear_json_filtering`: `39`
  - `unknown_player_state_logic`: `41`
  - `player_exclusion_logic`: `7`

Main conclusion:

```text
Future postflop player resolver must not duplicate existing PokerVision player-state/filtering logic.
```

The future postflop layer must adapt to already-cleaned data where possible and explicitly detect raw/partially-cleaned sources where needed.

---

### V0.1.5 — Final V0.1 Report / Plan to V0.2

**Commit:** `c2723c3 — V0.1.5 add final baseline report`

Created:

- `tools/build_v010_final_report.py`
- `tests/test_v010_final_report_builder.py`
- `docs/reports/v010_final_baseline_audit_report.md`
- `docs/reports/v010_plan_to_v020.md`
- `outputs/baseline_audit_v010/v010_final_report.json`

Result:

- final V0.1 report was generated;
- V0.2 plan was generated;
- `Ready for V0.2 design: True` was confirmed.

Main conclusion:

```text
The project is ready to design V0.2.0 — Source-Based Postflop Fixture Lab.
```

---

## Key V0.1.0 conclusions

### 1. The repository is still preflop-baseline based

The repository name and direction are now AllPreflop/Flop, but the internal baseline still comes from the preflop solver line.

This is not an error. It is the expected starting point for the new postflop development line.

### 2. Tests must be classified, not blindly treated as one gate

The current test suite contains core tests, live/dry-run tests, old audit tests, snapshot-dependent tests, and future postflop placeholders.

Postflop development needs its own quality gate.

### 3. Final Clear_JSON is optional for postflop source discovery

A future postflop source discovery layer must support intermediate project JSON files, because postflop Final Clear_JSON can be absent without click-cycle.

### 4. Player-state filtering already exists

The project already contains large logic areas for HERO, sitout, all-in, active player, trigger/service state, Clear_JSON filtering, and Final Clear_JSON filtering.

Postflop logic must not duplicate that blindly.

---

## Next version: V0.2.0 — Source-Based Postflop Fixture Lab

V0.2.0 will create a controlled fixture laboratory for postflop source JSON.

It will not create solver logic.

Planned outputs:

- `docs/POSTFLOP_FIXTURE_STRATEGY.md`
- `docs/POSTFLOP_SOURCE_TYPES.md`
- `docs/POSTFLOP_FIXTURE_MANIFEST_RULES.md`
- `tests/fixtures/postflop/manifest.json`
- `tests/fixtures/postflop/source_json/`
- `tests/fixtures/postflop/live_like_tree/`
- `tests/fixtures/postflop/normalized/`
- `tests/fixtures/postflop/expected/`

Supported source types:

- `dark_json`
- `pending_json`
- `service_json`
- `current_cycle_json`
- `runtime_json`
- `solver_payload_json`
- `final_clear_json`
- `manual_live_like_json`
- `unknown`

Important rule:

```text
manual_live_like_json must never be treated as a real project source.
```

---

## Useful report files

- `docs/reports/current_project_baseline_audit_v010.md`
- `docs/reports/current_test_suite_health_audit_v010.md`
- `docs/reports/current_json_source_map_v010.md`
- `docs/reports/current_player_state_filtering_audit_v010.md`
- `docs/reports/v010_final_baseline_audit_report.md`
- `docs/reports/v010_plan_to_v020.md`

---

## Current Git checkpoints

```text
db16abd initial snapshot: Real_Version_SolverPreflop as AllPreflop_Flop baseline
6bb90f8 V0.1.1 add project baseline audit
c062077 V0.1.2 add test suite health audit
00bfea3 V0.1.3 add json source map audit
077eb88 V0.1.4 add player state filtering audit
c2723c3 V0.1.5 add final baseline report
```
