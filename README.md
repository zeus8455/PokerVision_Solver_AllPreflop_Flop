# PokerVision_Solver_AllPreflop_Flop

Postflop development line for PokerVision on top of the existing AllPreflop / Preflop Solver baseline.

Current closed block: **V0.2.0 - Source-Based Postflop Fixture Lab**
Current checkpoint: **01528aa - V0.2.5 add postflop fixture structure tests**
Previous checkpoint: **3d19268 - README V0.1.0 baseline audit update**

---

## Purpose

This repository starts from the previous PokerVision_Solver_Preflop baseline and becomes the new working line for:

```text
PokerVision_Solver_AllPreflop_Flop
```

The project goal is to build a safe postflop development chain without breaking the existing preflop/runtime baseline.

The current direction is source-first postflop development:

```text
V0.1.0 audit -> V0.2.0 fixture lab -> V0.3.0 contracts -> V0.4.0 source discovery + normalizer
```

The project must not jump directly into postflop solver, ranges, equity, player resolver, street detector, runtime click plan, or click-chain logic before the source/contract layers are stable.

---

## Development rule

Development is versioned by controlled blocks.

For every version/subversion:

1. discuss the scope first;
2. implement only after explicit approval;
3. deliver a ZIP with ready project structure;
4. integrate through one PowerShell command;
5. run the required checks;
6. commit and push a short Git checkpoint;
7. update README / VERSION when a full version block is closed;
8. document the version in Miro.

No runtime, click-chain, source-of-truth, player-state, or solver logic is changed without a separate approved version.

---

## Current repository status

The repository is still a controlled development shell:

```text
AllPreflop_Flop repository shell
+ existing PokerVision_Solver_Preflop baseline
+ external PokerVision snapshot
+ legacy/audit/live test history
+ runtime/output JSON history
+ postflop audit reports
+ postflop source-based fixture lab
```

This is expected. The postflop line is being built in strict layers.

---

# Closed version: V0.1.0 - Current Baseline / Test / Source Audit

**Status:** closed  
**Final checkpoint:** `c2723c3 - V0.1.5 add final baseline report`  
**README checkpoint:** `3d19268 - docs: update README for V0.1.0 baseline audit`  
**Ready for V0.2 design:** `True`

## Goal

Create a factual audit layer for the current repository before starting postflop development.

V0.1.0 did not create postflop solver logic. It created tools and reports for:

- project identity / baseline audit;
- test suite health audit;
- JSON source map audit;
- player-state / filtering audit;
- final V0.1 report and V0.2 plan.

## V0.1 subversions

### V0.1.1 - Repo Identity / Baseline Audit

**Commit:** `6bb90f8 - V0.1.1 add project baseline audit`

Added:

- `tools/audit_current_project_baseline_v010.py`
- `tests/test_baseline_audit_tools_v010.py`
- `docs/reports/current_project_baseline_audit_v010.md`
- `outputs/baseline_audit_v010/project_baseline_report.json`

Result:

- the repository is the new AllPreflop_Flop shell;
- the internal baseline still comes from PokerVision_Solver_Preflop;
- README / project identity mismatch was detected;
- external snapshot and preflop baseline were confirmed.

### V0.1.2 - Test Suite Health Audit

**Commit:** `c062077 - V0.1.2 add test suite health audit`

Added:

- `tools/audit_current_test_suite_health_v010.py`
- `docs/reports/current_test_suite_health_audit_v010.md`
- `outputs/baseline_audit_v010/test_suite_health_report.json`

Result:

- 81 test files found;
- tests classified into live/dry-run, core baseline, future postflop, legacy old audit, and static/dynamic map categories;
- legacy/live-only tests are not treated as automatic postflop blockers.

### V0.1.3 - JSON Source Map Audit

**Commit:** `00bfea3 - V0.1.3 add json source map audit`

Added:

- `tools/audit_current_json_source_map_v010.py`
- `docs/reports/current_json_source_map_v010.md`
- `outputs/baseline_audit_v010/json_source_map_report.json`

Result:

- 187 JSON files found;
- 78 before-click sources found;
- 109 after-click sources found;
- Final Clear_JSON is not the only valid future postflop source.

### V0.1.4 - Player-State / Filtering Audit

**Commit:** `077eb88 - V0.1.4 add player state filtering audit`

Added:

- `tools/audit_current_player_state_filtering_v010.py`
- `docs/reports/current_player_state_filtering_audit_v010.md`
- `outputs/baseline_audit_v010/player_state_filtering_report.json`

Result:

- 1015 files scanned;
- 1297 player-state / filtering mechanisms found;
- 1256 mechanisms marked as should_not_duplicate;
- future postflop player resolver must adapt to existing PokerVision filtering, not duplicate it.

### V0.1.5 - Final V0.1 Report / Plan to V0.2

**Commit:** `c2723c3 - V0.1.5 add final baseline report`

Added:

- `tools/build_v010_final_report.py`
- `tests/test_v010_final_report_builder.py`
- `docs/reports/v010_final_baseline_audit_report.md`
- `docs/reports/v010_plan_to_v020.md`
- `outputs/baseline_audit_v010/v010_final_report.json`

Result:

- V0.1 audit block finalized;
- V0.2 Source-Based Fixture Lab approved as the next development layer;
- `Ready for V0.2 design: True`.

---

# Closed version: V0.2.0 - Source-Based Postflop Fixture Lab

**Status:** closed  
**Final technical checkpoint:** `01528aa - V0.2.5 add postflop fixture structure tests`  
**Validation:** `30 passed in 0.25s`

## Goal

Create a controlled source-based postflop fixture lab tied to the real PokerVision JSON chain.

V0.2.0 does not create solver logic, source discovery, normalizer, contracts, player resolver, ranges, equity, poker decisions, runtime click plan, or click-chain changes.

It creates the fixture foundation for future versions:

```text
source JSON -> manifest case -> expected JSON -> future normalizer target
```

## Source types supported by V0.2.0

```text
dark_json
pending_json
service_json
current_cycle_json
runtime_json
solver_payload_json
final_clear_json
manual_live_like_json
unknown
```

Important rules:

- Final Clear_JSON is optional.
- Manual live-like JSON must not be presented as real project source.
- Expected JSON must not contain poker decisions.
- Normalized files may be future paths until the normalizer is implemented.

## V0.2 subversions

### V0.2.1 - Fixture Strategy / Source Type Docs

**Commit:** `8cd8240 - V0.2.1 add postflop fixture lab docs`

Added:

- `docs/POSTFLOP_FIXTURE_STRATEGY.md`
- `docs/POSTFLOP_SOURCE_TYPES.md`
- `docs/POSTFLOP_FIXTURE_MANIFEST_RULES.md`

Result:

- fixture strategy documented;
- source types documented;
- manifest rules documented;
- Final Clear_JSON optional rule fixed in docs;
- manual live-like separation rule fixed in docs.

### V0.2.2 - Fixture Directory Skeleton

**Commit:** `25981ad - V0.2.2 add postflop fixture skeleton`

Added:

- `tests/fixtures/postflop/manifest.json`
- `tests/fixtures/postflop/source_json/`
- `tests/fixtures/postflop/live_like_tree/`
- `tests/fixtures/postflop/normalized/`
- `tests/fixtures/postflop/expected/`

Created source_json subfolders:

- `current_cycle_json`
- `dark_json`
- `final_clear_json`
- `manual_live_like_json`
- `pending_json`
- `runtime_json`
- `service_json`
- `solver_payload_json`

Result:

- fixture directory skeleton created;
- `manifest.json` initialized;
- `cases: []` at skeleton stage;
- empty folders preserved with `.gitkeep`.

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

Result:

- first source-based flop fixture added;
- source JSON and expected JSON are linked through manifest;
- no poker decision is present;
- Final Clear_JSON is not required.

### V0.2.4 - Fixture Manifest Tests

**Commit:** `0b2d9d6 - V0.2.4 add postflop fixture manifest tests`

Added:

- `tests/test_postflop_fixture_manifest_v020.py`

Result:

- manifest existence is tested;
- top-level manifest fields are tested;
- required case fields are tested;
- duplicate case_id is forbidden;
- source_type must be valid;
- source_file and expected_file must exist;
- normalized_file may be a future path;
- manual and real source flags cannot conflict;
- expected JSON must not contain poker decisions.

Validation:

```text
11 passed in 0.15s
```

### V0.2.5 - Fixture Structure / Source Type Tests

**Commit:** `01528aa - V0.2.5 add postflop fixture structure tests`

Added:

- `tests/test_postflop_fixture_structure_v020.py`
- `tests/test_postflop_source_fixture_types_v020.py`

Result:

- fixture root structure is tested;
- source_json subfolders are tested;
- allowed source types are tested;
- source files must live in the correct source_type folder;
- expected files must live in expected/;
- Final Clear_JSON remains optional;
- unknown source_type is allowed only with explicit notes;
- manual live-like source is not treated as real source.

Validation:

```powershell
pytest tests/test_postflop_fixture_manifest_v020.py tests/test_postflop_fixture_structure_v020.py tests/test_postflop_source_fixture_types_v020.py -q
```

Result:

```text
30 passed in 0.25s
```

---

## Current V0.2 fixture lab structure

```text
tests/fixtures/postflop/
  manifest.json
  source_json/
    current_cycle_json/
    dark_json/
      flop_source_case_001.dark.json
    final_clear_json/
    manual_live_like_json/
    pending_json/
    runtime_json/
    service_json/
    solver_payload_json/
  live_like_tree/
  normalized/
  expected/
    flop_source_case_001.expected.json
```

---

## Current test commands

### V0.2 fixture lab gate

```powershell
cd "C:\PokerVision_Solver_AllPreflop_Flop"
C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe -m pytest `
  .\tests\test_postflop_fixture_manifest_v020.py `
  .\tests\test_postflop_fixture_structure_v020.py `
  .\tests\test_postflop_source_fixture_types_v020.py `
  -q
```

Expected result:

```text
30 passed
```

---

## Development rules going forward

Do not build postflop solver logic before contracts and source/normalizer layers exist.

Do not use Final Clear_JSON as the only source-of-truth.

Do not mix manual live-like JSON with real project sources.

Do not duplicate PokerVision player-state filtering.

Do not treat legacy/live-only tests as automatic postflop blockers.

Do not change runtime or click-chain without a separate approved version.

---

## Next version

Next development block:

```text
V0.3.0 - Postflop Source Contracts
```

Goal:

Create strict data contracts for the future postflop chain:

```text
SourceCandidate -> RawSource -> NormalizedPostflopFrame -> ModuleResult -> Trace
```

V0.3.0 still must not search folders, normalize real JSON, detect street, restore preflop history, filter players, calculate equity, build ranges, make poker decisions, or create runtime click plans.
