# V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases

Status: **planned block, V0.2.1 docs/schema step**
Line: **Clear_JSON-only postflop solver engine**
Depends on: **V0.1.0 — Solver Engine Blueprint / Clear_JSON Input Contract**

---

## 1. Purpose

V0.2.0 creates a permanent Clear_JSON fixture library for the postflop solver engine.

The fixture library exists to give every future solver layer a stable test base:

```text
ready PokerVision Clear_JSON
  -> fixture case
  -> expected solver interpretation
  -> future solver module tests
```

V0.2.0 does not solve poker spots. It does not validate whether Clear_JSON is correct. It stores representative Clear_JSON files and expected interpretation metadata so later modules can be tested against repeatable cases.

---

## 2. Core policy

The fixture library follows the same rule as V0.1.0:

**Clear_JSON is the solver input format of truth.**

The postflop solver must not use upstream temporary artifacts as solver fixtures. Fixture cases in V0.2.0 must be ready Clear_JSON files, not discovery-layer source files.

Allowed fixture input:

- real Clear_JSON
- synthetic Clear_JSON derived from the real Clear_JSON structure
- templates used to create future synthetic Clear_JSON cases

Not allowed as solver fixture input in V0.2.0:

- temporary upstream JSON files
- source discovery artifacts
- UI/runtime/click-cycle payloads
- raw detector outputs
- patched or repaired source trees

---

## 3. Fixture root

The permanent fixture root is:

```text
tests/fixtures/postflop_clear_json/
```

Required structure:

```text
tests/fixtures/postflop_clear_json/
  manifest.json
  real/
    flop/
    turn/
    river/
  synthetic/
    flop/
    turn/
    river/
  templates/
  expected/
```

This root name is intentional. It prevents the new fixture library from being confused with older source-first experiments.

---

## 4. Real Clear_JSON cases

A real Clear_JSON case is a file produced by the PokerVision chain and stored as close as possible to its original output format.

Rules for real cases:

- do not improve the poker data by hand
- do not normalize field names manually
- do not repair cards, players, pot, stacks, action context, or metadata
- do not add synthetic solver-only fields into the real Clear_JSON file
- if explanatory metadata is needed, store it in `manifest.json` or in the expected interpretation file

Purpose of real cases:

- keep the solver tested against the actual project format
- detect accidental breakage of `load_clear_json_input()`
- detect accidental breakage of `build_solver_input()`
- preserve a realistic source format for future module tests

---

## 5. Synthetic Clear_JSON cases

A synthetic Clear_JSON case is a test case created from a real Clear_JSON structure or from a template that follows the real structure.

Synthetic cases are used to cover solver branches that may not yet have enough real live examples.

Rules for synthetic cases:

- keep the structure close to real Clear_JSON
- change only the poker scenario fields needed for the target case
- mark the case as `source_kind = synthetic` in `manifest.json`
- link to `base_real_case_id` when derived from a real case
- do not pretend that synthetic cases came directly from live project output

Examples of future synthetic cases:

- flop single-raised pot, button versus big blind, check option
- flop single-raised pot, out of position facing continuation bet
- flop three-bet pot, in-position continuation bet
- flop multiway facing bet
- turn after flop bet-call
- river facing large bet

---

## 6. Expected interpretation files

Each fixture case must have an expected interpretation file in:

```text
tests/fixtures/postflop_clear_json/expected/
```

Expected interpretation files describe how the solver should understand the Clear_JSON case.

They do not contain final poker decisions.

Allowed expected interpretation fields include:

- `case_id`
- `expected_street_group`
- `expected_spot_family`
- `expected_hero_position`
- `expected_is_heads_up`
- `expected_is_multiway`
- `expected_pot_type`
- `expected_action_context`
- `expected_available_solver_branch`
- `expected_next_module`
- `expected_notes`

Forbidden in V0.2 expected files:

- final action such as fold/call/check/bet/raise
- bet sizing policy
- equity result
- range result
- click target
- runtime plan

---

## 7. Minimum V0.2.0 case set

V0.2.0 should prove the fixture library shape without building a huge scenario matrix.

Minimum required cases:

1. one real flop Clear_JSON
2. one synthetic flop Clear_JSON derived from the real flop case
3. one turn Clear_JSON, real if available, otherwise synthetic
4. one river Clear_JSON, real if available, otherwise synthetic

If turn or river cases are synthetic, the manifest must say so explicitly.

---

## 8. Relationship with V0.1.0 modules

Every fixture Clear_JSON must be loadable through:

```python
load_clear_json_input(path)
```

The fixture tests should also confirm that the fixture can enter the V0.1 pipeline:

```text
Clear_JSON fixture -> ClearJsonInput -> SolverInput -> SolverTrace
```

This confirms that the fixture library is compatible with the baseline engine contracts.

---

## 9. What V0.2.0 must not implement

V0.2.0 must not introduce:

- solver decision engine
- equity calculation
- range construction
- board texture classification
- hand strength evaluation
- street branch resolver
- runtime plan
- live click-chain
- source discovery
- Clear_JSON safety validation
- duplicate card checks
- hero-board collision checks
- player filtering
- HERO reconstruction

Those belong to later explicitly scoped versions.

---

## 10. V0.2.0 readiness criteria

V0.2.0 is ready when:

- `tests/fixtures/postflop_clear_json/` exists
- the real/synthetic/templates/expected structure exists
- `manifest.json` exists
- each case has a unique `case_id`
- each case references an existing Clear_JSON file
- each case references an existing expected interpretation file
- fixture Clear_JSON files can be loaded through `load_clear_json_input()`
- expected files do not require final poker decisions
- V0.1 tests still pass
- V0.2 fixture tests pass

---

## 11. Miro summary

**Card title:** V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases

**Purpose:** Create a permanent fixture base for postflop solver tests using ready Clear_JSON as the format of truth.

**Main rule:** The fixture library stores Clear_JSON cases only. It does not use upstream discovery/source artifacts as solver inputs.

**Implemented by the full version:** folder structure, manifest, real/synthetic cases, expected interpretation files, fixture integrity tests.

**Not implemented:** poker decisions, equity, ranges, branch resolver, safety validation, runtime plan, clicks.
