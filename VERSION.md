# PokerVision_Solver_AllPreflop_Flop - Version History

This file tracks the new AllPreflop_Flop postflop development line.

The repository was created from the earlier PokerVision_Solver_Preflop baseline. Legacy preflop history remains available in Git history, but the active version log below starts from the AllPreflop_Flop line.

---

## V0.3.0 - Postflop Source Contracts

**Status:** closed  
**Final technical checkpoint:** `8f238b9 - V0.3.4 add postflop module result contracts`  
**Close step:** `V0.3.5 - Contract Test Gate / Version Close`  
**Validation:** `51 passed`  
**Next block:** `V0.4.0 - Source Discovery + Postflop Normalizer`

### Goal

Create strict data contracts for the future postflop chain:

```text
source JSON -> source candidate -> raw source -> normalized frame -> module result -> warnings/errors -> future trace
```

This version does not search files, normalize real JSON, detect street, reconstruct preflop history, filter players, calculate equity, build ranges, make poker decisions, create runtime click plans, click, or modify the main PokerVision runtime.

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
pytest tests/test_postflop_contracts_v030.py -q
8 passed in 0.17s
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
pytest tests/test_postflop_contracts_v030.py tests/test_postflop_source_contracts_v030.py -q
21 passed in 0.15s
```

Notes:

- V0.3.2 preserves the V0.3.1 API surface.
- `PostflopSourceType.values()` remains stable.
- `ModuleWarning` / `ModuleError` keep structured `source_file`, `field_name`, and severity validation.

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
pytest tests/test_postflop_contracts_v030.py tests/test_postflop_source_contracts_v030.py tests/test_postflop_normalized_frame_contract_v030.py -q
37 passed in 0.24s
```

Notes:

- `NormalizedPostflopFrame` is not a perfect poker-state requirement.
- It is an honest data layer: extracted fields, raw fields, warnings, and status.
- Player-state is captured, not re-filtered.

### V0.3.4 - Module Result / Future Runtime Contracts

**Commit:** `8f238b9 - V0.3.4 add postflop module result contracts`

Added enum/status types:

- `StreetName`
- `ModuleResultStatus`
- `PreflopHistoryStatus`
- `PostflopDecisionAction`
- `RuntimeGuardStatus`
- `ProbeReportStatus`

Added result contracts:

- `StreetDetectionResult`
- `PreflopHistoryResult`
- `PostflopDecision`
- `PostflopRuntimePlan`
- `PostflopTrace`
- `PostflopProbeReport`
- `tests/test_postflop_module_result_contracts_v030.py`

Validation:

```text
pytest tests/test_postflop_contracts_v030.py tests/test_postflop_source_contracts_v030.py tests/test_postflop_normalized_frame_contract_v030.py tests/test_postflop_module_result_contracts_v030.py -q
51 passed in 0.38s
```

### V0.3.5 - Contract Test Gate / Version Close

Adds:

- `tools/run_v030_contract_gate.py`
- `outputs/postflop_contracts_v030/contract_gate_report.json`
- README / VERSION close state for V0.3.0

Purpose:

- run the full V0.3 contract test set;
- write a contract gate report;
- mark the project ready for V0.4.0 design;
- close V0.3.0 without adding new contract models.

Expected gate command:

```text
python tools/run_v030_contract_gate.py
```

Expected validation:

```text
51 passed
ready_for_v040 = true
```

---

## V0.2.0 - Source-Based Postflop Fixture Lab

**Status:** closed  
**Final technical checkpoint:** `01528aa - V0.2.5 add postflop fixture structure tests`  
**Documentation checkpoint:** `c4276ef - docs: close V0.2.0 fixture lab`  
**Validation:** `30 passed`

### Goal

Create a controlled source-based postflop fixture lab connected to the real PokerVision JSON/source structure.

This version does not create solver logic, source discovery, normalizer, contracts, player resolver, ranges, equity, poker decisions, runtime click plan, or click-chain changes.

### V0.2.1 - Fixture Strategy / Source Type Docs

**Commit:** `8cd8240 - V0.2.1 add postflop fixture lab docs`

Added:

- `docs/POSTFLOP_FIXTURE_STRATEGY.md`
- `docs/POSTFLOP_SOURCE_TYPES.md`
- `docs/POSTFLOP_FIXTURE_MANIFEST_RULES.md`

### V0.2.2 - Fixture Directory Skeleton

**Commit:** `25981ad - V0.2.2 add postflop fixture skeleton`

Added fixture skeleton under:

- `tests/fixtures/postflop/`

### V0.2.3 - First Source-Based Flop Fixture Case

**Commit:** `db9c2c4 - V0.2.3 add first postflop source fixture`

Added:

- `tests/fixtures/postflop/source_json/dark_json/flop_source_case_001.dark.json`
- `tests/fixtures/postflop/expected/flop_source_case_001.expected.json`

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
30 passed in 0.24s
```

---

## V0.1.0 - Current Baseline / Test / Source Audit

**Status:** closed  
**Final checkpoint:** `c2723c3 - V0.1.5 add final baseline report`  
**README checkpoint:** `3d19268 - docs: update README for V0.1.0 baseline audit`

### Goal

Create a factual audit layer for the current repository before starting postflop development.

### Subversions

- `6bb90f8 - V0.1.1 add project baseline audit`
- `c062077 - V0.1.2 add test suite health audit`
- `00bfea3 - V0.1.3 add json source map audit`
- `077eb88 - V0.1.4 add player state filtering audit`
- `c2723c3 - V0.1.5 add final baseline report`

---

## Initial imported baseline

**Commit:** `db16abd - initial snapshot: Real_Version_SolverPreflop as AllPreflop_Flop baseline`

This commit imported the previous preflop solver baseline into the new AllPreflop_Flop repository line.
