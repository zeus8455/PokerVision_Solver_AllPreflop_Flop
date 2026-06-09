# PokerVision_Solver_AllPreflop_Flop

Postflop development line for PokerVision on top of the existing AllPreflop / Preflop Solver baseline.

Current closed block: **V0.3.0 - Postflop Source Contracts**
Current technical checkpoint: **8f238b9 - V0.3.4 add postflop module result contracts**
Current close step: **V0.3.5 - Contract Test Gate / Version Close**
Previous closed block: **V0.2.0 - Source-Based Postflop Fixture Lab**

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
+ postflop contract layer
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

- project baseline audit;
- test suite health audit;
- JSON source map audit;
- player-state / filtering audit;
- final V0.1 report and plan to V0.2.

## Key findings

- The repository is an AllPreflop_Flop shell over the previous PokerVision_Solver_Preflop baseline.
- Test history is mixed: core baseline, legacy/audit, live/dry-run, future postflop.
- Final Clear_JSON is not the only usable source.
- Existing player-state/filtering logic must not be duplicated by future postflop modules.

---

# Closed version: V0.2.0 - Source-Based Postflop Fixture Lab

**Status:** closed  
**Final technical checkpoint:** `01528aa - V0.2.5 add postflop fixture structure tests`  
**Documentation checkpoint:** `c4276ef - docs: close V0.2.0 fixture lab`  
**Validation:** `30 passed`

## Goal

Create a controlled source-based postflop fixture lab connected to the real PokerVision JSON/source structure.

V0.2.0 did not create solver logic, source discovery, normalizer, contracts, player resolver, ranges, equity, poker decisions, runtime click plan, or click-chain changes.

## Subversions

### V0.2.1 - Fixture Strategy / Source Type Docs

**Commit:** `8cd8240 - V0.2.1 add postflop fixture lab docs`

Added:

- `docs/POSTFLOP_FIXTURE_STRATEGY.md`
- `docs/POSTFLOP_SOURCE_TYPES.md`
- `docs/POSTFLOP_FIXTURE_MANIFEST_RULES.md`

### V0.2.2 - Fixture Directory Skeleton

**Commit:** `25981ad - V0.2.2 add postflop fixture skeleton`

Added:

- `tests/fixtures/postflop/manifest.json`
- `tests/fixtures/postflop/source_json/`
- `tests/fixtures/postflop/live_like_tree/`
- `tests/fixtures/postflop/normalized/`
- `tests/fixtures/postflop/expected/`

### V0.2.3 - First Source-Based Flop Fixture Case

**Commit:** `db9c2c4 - V0.2.3 add first postflop source fixture`

Added first fixture case:

- `tests/fixtures/postflop/source_json/dark_json/flop_source_case_001.dark.json`
- `tests/fixtures/postflop/expected/flop_source_case_001.expected.json`

Case properties:

```text
source_type = dark_json
street_candidate = flop
is_real_project_source = false
is_manual_live_like_source = true
requires_click_cycle = false
```

### V0.2.4 - Fixture Manifest Tests

**Commit:** `0b2d9d6 - V0.2.4 add postflop fixture manifest tests`

Added:

- `tests/test_postflop_fixture_manifest_v020.py`

### V0.2.5 - Fixture Structure / Source Type Tests

**Commit:** `01528aa - V0.2.5 add postflop fixture structure tests`

Added:

- `tests/test_postflop_fixture_structure_v020.py`
- `tests/test_postflop_source_fixture_types_v020.py`

Validation:

```text
pytest tests/test_postflop_fixture_manifest_v020.py tests/test_postflop_fixture_structure_v020.py tests/test_postflop_source_fixture_types_v020.py -q
30 passed
```

---

# Closed version: V0.3.0 - Postflop Source Contracts

**Status:** closed  
**Final technical checkpoint:** `8f238b9 - V0.3.4 add postflop module result contracts`  
**Close gate:** `V0.3.5 - Contract Test Gate / Version Close`  
**Validation:** `51 passed`

## Goal

Create strict data contracts for the future postflop chain:

```text
source JSON -> source candidate -> raw source -> normalized frame -> module result -> warnings/errors -> future trace
```

V0.3.0 does not search JSON files, normalize real JSON, detect street, reconstruct preflop history, filter players, calculate equity, build ranges, make poker decisions, create runtime click plans, click, or modify the main PokerVision runtime.

## Subversions

### V0.3.1 - Postflop Module Skeleton / Base Types

**Commit:** `61b16e1 - V0.3.1 add postflop contract base types`

Added:

- `solver_postflop/__init__.py`
- `solver_postflop/contracts.py`
- `tests/test_postflop_contracts_v030.py`

Contract types:

- `PostflopSourceType`
- `ContractSeverity`
- `ContractValidationError`
- `ModuleWarning`
- `ModuleError`

Validation:

```text
8 passed
```

### V0.3.2 - Source Candidate / Raw Source Contracts

**Commit:** `b83874e - V0.3.2 add postflop source contracts`

Added:

- `PostflopConfidence`
- `RawSourceLoadStatus`
- `DiscoveryStatus`
- `PostflopSourceCandidate`
- `PostflopRawSource`
- `PostflopSourceDiscoveryResult`
- `tests/test_postflop_source_contracts_v030.py`

Validation:

```text
21 passed
```

### V0.3.3 - Normalized Frame Contracts

**Commit:** `645c110 - V0.3.3 add postflop normalized frame contracts`

Added:

- `NormalizationStatus`
- `PostflopPlayerSnapshot`
- `PostflopBoardSnapshot`
- `PostflopActionSnapshot`
- `NormalizedPostflopFrame`
- `tests/test_postflop_normalized_frame_contract_v030.py`

Validation:

```text
37 passed
```

### V0.3.4 - Module Result / Future Runtime Contracts

**Commit:** `8f238b9 - V0.3.4 add postflop module result contracts`

Added:

- `StreetName`
- `ModuleResultStatus`
- `PreflopHistoryStatus`
- `PostflopDecisionAction`
- `RuntimeGuardStatus`
- `ProbeReportStatus`
- `StreetDetectionResult`
- `PreflopHistoryResult`
- `PostflopDecision`
- `PostflopRuntimePlan`
- `PostflopTrace`
- `PostflopProbeReport`
- `tests/test_postflop_module_result_contracts_v030.py`

Validation:

```text
51 passed
```

### V0.3.5 - Contract Test Gate / Version Close

Adds:

- `tools/run_v030_contract_gate.py`
- `outputs/postflop_contracts_v030/contract_gate_report.json`

Purpose:

- run all V0.3 contract tests together;
- write a machine-readable contract gate report;
- close V0.3.0 in README / VERSION;
- mark the project ready for V0.4.0 design.

## Final V0.3.0 contract chain

```text
PostflopSourceType
-> PostflopSourceCandidate
-> PostflopRawSource
-> PostflopSourceDiscoveryResult
-> NormalizedPostflopFrame
-> StreetDetectionResult
-> PreflopHistoryResult
-> PostflopDecision
-> PostflopRuntimePlan
-> PostflopTrace
-> PostflopProbeReport
```

---

# Next planned block: V0.4.0 - Source Discovery + Postflop Normalizer

V0.4.0 will create the first working source/normalizer layer:

- `solver_postflop/source_discovery.py`
- `solver_postflop/source_adapter.py`
- `solver_postflop/frame_normalizer.py`
- `docs/POSTFLOP_SOURCE_DISCOVERY.md`
- `docs/POSTFLOP_NORMALIZER.md`
- `tests/test_postflop_source_discovery_v040.py`
- `tests/test_postflop_source_adapter_v040.py`
- `tests/test_postflop_frame_normalizer_v040.py`

V0.4.0 will not make poker decisions, determine street finally, reconstruct preflop history, filter players again, create runtime click plans, click, or modify the main runtime.
