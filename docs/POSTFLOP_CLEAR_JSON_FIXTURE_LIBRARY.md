# V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases

Status: **closed by V0.2.6**  
Line: **Clear_JSON-only postflop solver engine**  
Depends on: **V0.1.0 — Solver Engine Blueprint / Clear_JSON Input Contract**

---

## 1. Purpose

V0.2.0 creates a permanent Clear_JSON fixture library for the postflop solver engine.

The fixture library exists to give every future solver layer a stable test base:

```text
ready PokerVision Clear_JSON -> fixture case -> expected solver interpretation -> future solver module tests
```

V0.2.0 does not solve poker spots. It does not validate whether Clear_JSON is correct. It stores representative Clear_JSON files and expected interpretation metadata so later modules can be tested against repeatable cases.

---

## 2. Core policy

The fixture library follows the same rule as V0.1.0:

**Clear_JSON is the solver input format of truth.**

The postflop solver must not use upstream temporary artifacts as solver fixtures.

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

Active structure:

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

## 4. Current minimum case set

V0.2.0 closes with 4 starter cases:

| case_id | source_kind | street_group | role |
|---|---|---|---|
| `real_flop_srp_btn_vs_bb_check_option` | real | flop | real/project-format baseline case |
| `synthetic_flop_srp_oop_facing_cbet` | synthetic | flop | synthetic flop branch/context case |
| `synthetic_turn_after_flop_bet_call` | synthetic | turn | synthetic turn branch/context case |
| `synthetic_river_facing_large_bet` | synthetic | river | synthetic river branch/context case |

The turn and river cases are intentionally synthetic in V0.2.0. They exist to prepare future routing and context tests, not to claim live-source coverage.

---

## 5. Real Clear_JSON cases

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

## 6. Synthetic Clear_JSON cases

A synthetic Clear_JSON case is a test case created from a real Clear_JSON structure or from a template that follows the real structure.

Rules for synthetic cases:

- keep the structure close to real Clear_JSON
- change only the poker scenario fields needed for the target case
- mark the case as `source_kind = synthetic` in `manifest.json`
- link to `base_real_case_id` when derived from a real case
- do not pretend that synthetic cases came directly from live project output

---

## 7. Expected interpretation files

Each fixture case has an expected interpretation file in:

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

## 8. Relationship with V0.1.0 modules

Every fixture Clear_JSON is loadable through:

```python
load_clear_json_input(path)
```

The fixture tests also confirm that the fixture can enter the V0.1 pipeline:

```text
Clear_JSON fixture -> ClearJsonInput -> SolverInput -> SolverTrace
```

This confirms that the fixture library is compatible with the baseline engine contracts.

---

## 9. Test coverage at close

V0.2.0 closes with these fixture tests:

- `tests/test_postflop_clear_json_fixture_skeleton_v020.py`
- `tests/test_postflop_clear_json_minimum_cases_v020.py`
- `tests/test_postflop_expected_interpretation_v020.py`
- `tests/test_postflop_clear_json_fixture_manifest_v020.py`

Full V0.1 + V0.2 gate at close:

```text
62 passed
```

---

## 10. What V0.2.0 does not implement

V0.2.0 does not introduce:

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

## 11. Miro summary

**Card title:** V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases

**Purpose:** Create a permanent fixture base for postflop solver tests using ready Clear_JSON as the format of truth.

**Main rule:** The fixture library stores Clear_JSON cases only. It does not use upstream discovery/source artifacts as solver inputs.

**Implemented:** folder structure, manifest, real/synthetic cases, expected interpretation files, fixture integrity tests.

**Not implemented:** poker decisions, equity, ranges, branch resolver, safety validation, runtime plan, clicks.
