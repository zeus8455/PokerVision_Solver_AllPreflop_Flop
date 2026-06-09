# PokerVision_Solver_AllPreflop_Flop - Version History

This file tracks the new AllPreflop_Flop postflop development line.

The repository was created from the earlier PokerVision_Solver_Preflop baseline. Legacy preflop history remains available in Git history, but the active version log below starts from the AllPreflop_Flop line.

---

## V0.2.0 - Source-Based Postflop Fixture Lab

**Status:** closed  
**Final technical checkpoint:** `01528aa - V0.2.5 add postflop fixture structure tests`  
**Validation:** `30 passed in 0.25s`

### Goal

Create a controlled source-based postflop fixture lab connected to the real PokerVision JSON/source structure.

This version does not create solver logic, source discovery, normalizer, contracts, player resolver, ranges, equity, poker decisions, runtime click plan, or click-chain changes.

### V0.2.1 - Fixture Strategy / Source Type Docs

**Commit:** `8cd8240 - V0.2.1 add postflop fixture lab docs`

Added:

- `docs/POSTFLOP_FIXTURE_STRATEGY.md`
- `docs/POSTFLOP_SOURCE_TYPES.md`
- `docs/POSTFLOP_FIXTURE_MANIFEST_RULES.md`

Purpose:

- document fixture lab strategy;
- document allowed source types;
- document manifest rules;
- document that Final Clear_JSON is optional;
- document manual live-like vs real-source separation.

### V0.2.2 - Fixture Directory Skeleton

**Commit:** `25981ad - V0.2.2 add postflop fixture skeleton`

Added:

- `tests/fixtures/postflop/manifest.json`
- `tests/fixtures/postflop/source_json/`
- `tests/fixtures/postflop/live_like_tree/`
- `tests/fixtures/postflop/normalized/`
- `tests/fixtures/postflop/expected/`

Added source_json subfolders:

- `current_cycle_json`
- `dark_json`
- `final_clear_json`
- `manual_live_like_json`
- `pending_json`
- `runtime_json`
- `service_json`
- `solver_payload_json`

Purpose:

- create the fixture lab directory skeleton;
- initialize manifest with allowed source types;
- keep fixture cases empty until V0.2.3.

### V0.2.3 - First Source-Based Flop Fixture Case

**Commit:** `db9c2c4 - V0.2.3 add first postflop source fixture`

Added / updated:

- `tests/fixtures/postflop/manifest.json`
- `tests/fixtures/postflop/source_json/dark_json/flop_source_case_001.dark.json`
- `tests/fixtures/postflop/expected/flop_source_case_001.expected.json`

Fixture case:

```text
case_id: flop_source_case_001
source_type: dark_json
street_candidate: flop
is_real_project_source: false
is_manual_live_like_source: true
requires_click_cycle: false
```

Purpose:

- add the first minimal postflop source-based fixture case;
- prove fixture lab can link source JSON, expected JSON, and manifest entry;
- keep poker decision absent;
- keep Final Clear_JSON optional.

### V0.2.4 - Fixture Manifest Tests

**Commit:** `0b2d9d6 - V0.2.4 add postflop fixture manifest tests`

Added:

- `tests/test_postflop_fixture_manifest_v020.py`

Validation:

```text
11 passed in 0.15s
```

Purpose:

- protect manifest structure;
- require all mandatory case fields;
- prevent duplicate case_id;
- validate source_type;
- require source_file and expected_file to exist;
- allow normalized_file as a future path;
- prevent manual/real source flag conflicts;
- confirm expected JSON does not contain poker decisions.

### V0.2.5 - Fixture Structure / Source Type Tests

**Commit:** `01528aa - V0.2.5 add postflop fixture structure tests`

Added:

- `tests/test_postflop_fixture_structure_v020.py`
- `tests/test_postflop_source_fixture_types_v020.py`

Validation:

```text
30 passed in 0.25s
```

Purpose:

- protect fixture root structure;
- require all source_json subfolders;
- validate allowed source types;
- require source_file to live in the matching source_type folder;
- require expected_file to live in expected/;
- keep Final Clear_JSON optional;
- allow unknown only with explicit notes;
- prevent manual live-like source from being treated as real-source.

---

## V0.1.0 - Current Baseline / Test / Source Audit

**Status:** closed  
**Final checkpoint:** `c2723c3 - V0.1.5 add final baseline report`  
**README checkpoint:** `3d19268 - docs: update README for V0.1.0 baseline audit`  
**Ready for V0.2 design:** `True`

### Goal

Create a factual audit layer for the current repository before starting postflop development.

This version does not create postflop solver logic.

### V0.1.1 - Repo Identity / Baseline Audit

**Commit:** `6bb90f8 - V0.1.1 add project baseline audit`

Added:

- `tools/audit_current_project_baseline_v010.py`
- `tests/test_baseline_audit_tools_v010.py`
- `docs/reports/current_project_baseline_audit_v010.md`
- `outputs/baseline_audit_v010/project_baseline_report.json`

Purpose:

- identify repo baseline;
- detect project identity mismatch;
- confirm preflop baseline and external snapshot.

### V0.1.2 - Test Suite Health Audit

**Commit:** `c062077 - V0.1.2 add test suite health audit`

Added:

- `tools/audit_current_test_suite_health_v010.py`
- `docs/reports/current_test_suite_health_audit_v010.md`
- `outputs/baseline_audit_v010/test_suite_health_report.json`

Purpose:

- classify current tests;
- separate core baseline, legacy, live/dry-run, static/dynamic map, and future postflop tests;
- avoid treating legacy/live-only tests as automatic postflop blockers.

### V0.1.3 - JSON Source Map Audit

**Commit:** `00bfea3 - V0.1.3 add json source map audit`

Added:

- `tools/audit_current_json_source_map_v010.py`
- `docs/reports/current_json_source_map_v010.md`
- `outputs/baseline_audit_v010/json_source_map_report.json`

Purpose:

- map JSON files and JSON-producing code references;
- classify before-click and after-click sources;
- prove Final Clear_JSON must not be the only future source.

### V0.1.4 - Player-State / Filtering Audit

**Commit:** `077eb88 - V0.1.4 add player state filtering audit`

Added:

- `tools/audit_current_player_state_filtering_v010.py`
- `docs/reports/current_player_state_filtering_audit_v010.md`
- `outputs/baseline_audit_v010/player_state_filtering_report.json`

Purpose:

- find existing HERO, sitout, all-in, active state, trigger/service state, Clear_JSON filtering, and Final Clear_JSON filtering logic;
- mark logic that must not be duplicated by future postflop modules.

### V0.1.5 - Final V0.1 Report / Plan to V0.2

**Commit:** `c2723c3 - V0.1.5 add final baseline report`

Added:

- `tools/build_v010_final_report.py`
- `tests/test_v010_final_report_builder.py`
- `docs/reports/v010_final_baseline_audit_report.md`
- `docs/reports/v010_plan_to_v020.md`
- `outputs/baseline_audit_v010/v010_final_report.json`

Purpose:

- close V0.1 audit block;
- combine V0.1 reports;
- approve V0.2 Source-Based Fixture Lab as the next development block.

---

## Initial imported baseline

### Initial snapshot

**Commit:** `db16abd - initial snapshot: Real_Version_SolverPreflop as AllPreflop_Flop baseline`

Purpose:

- import the previous Real_Version_SolverPreflop baseline into the new AllPreflop_Flop development repository.
