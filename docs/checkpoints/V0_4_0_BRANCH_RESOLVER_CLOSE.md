# V0.4.0 — Branch Resolver / Street Module Routing Close

**Status:** closed  
**Closing subversion:** V0.4.6  
**Commit message:** `V0.4.6 close branch resolver routing`  
**Final gate:** `125 passed`

---

## Purpose

V0.4.0 created the first routing layer inside the postflop solver engine.

Before V0.4.0, the project had:

- Clear_JSON-only architecture.
- ClearJsonInput.
- SolverInput.
- Field Mapping Contract.
- FieldUsageTrace.
- Clear_JSON fixture library.

After V0.4.0, the project can route a mapped SolverInput into the correct future solver branch:

```text
Clear_JSON -> ClearJsonInput -> SolverInput -> Branch Resolver -> SolverBranchResult
```

This is still not a poker decision layer.

---

## Subversion history

### V0.4.1 — Branch Contracts Baseline

**Commit:** `9fc9cee`

Created:

- `solver_postflop/branch_contracts.py`
- `tests/test_postflop_branch_contracts_v040.py`

Defined:

- `SolverBranch`
- `SolverBranchFamily`
- `SolverBranchResult`
- default next-module mapping
- branch family mapping

Branch types:

- `preflop_not_handled`
- `flop`
- `turn_not_implemented_yet`
- `river_not_implemented_yet`
- `unsupported`

---

### V0.4.2 — Branch Resolver Baseline

**Commit:** `54ac7c5`

Created:

- `solver_postflop/branch_resolver.py`
- `tests/test_postflop_branch_resolver_v040.py`

Added:

- `resolve_solver_branch(solver_input, solver_trace=None) -> SolverBranchResult`

Routing rules:

| board_cards count | branch |
|---:|---|
| 0 | `preflop_not_handled` |
| 3 | `flop` |
| 4 | `turn_not_implemented_yet` |
| 5 | `river_not_implemented_yet` |
| missing / 1 / 2 / 6+ | `unsupported` |

Unsupported reason:

```text
unsupported_board_card_count_for_branch_routing
```

This is a routing reason, not a validation error.

---

### V0.4.3 — Fixture-backed Branch Routing

**Commit:** `21b087f`

Created:

- `tests/test_postflop_branch_resolver_fixture_routing_v040.py`

Updated expected interpretation files with branch-routing metadata:

- `expected_branch`
- `expected_branch_family`
- `expected_branch_reason`
- `expected_branch_next_module`
- `expected_branch_contract_version`

Validated the V0.2 fixture library through:

```text
Clear_JSON fixture -> ClearJsonInput -> SolverInput -> Branch Resolver -> SolverBranchResult
```

Covered fixture routes:

- real flop -> `flop`
- synthetic flop -> `flop`
- synthetic turn -> `turn_not_implemented_yet`
- synthetic river -> `river_not_implemented_yet`

---

### V0.4.4 — Branch Resolver No-extra-checks Gate

**Commit:** `ab77eb1`

Created:

- `tests/test_postflop_branch_resolver_no_extra_checks_v040.py`

Protected Branch Resolver from accidental expansion into:

- card validation
- duplicate-card checks
- hero-board collision checks
- player filtering
- HERO reconstruction
- active-player reconstruction
- source discovery
- runtime/click-chain
- poker decision payloads
- runtime plans

Runtime checks confirmed:

- `resolve_solver_branch()` does not mutate Clear_JSON.
- `resolve_solver_branch()` does not mutate `players`.
- `resolve_solver_branch()` does not mutate `board_cards`.
- `resolve_solver_branch()` does not read files.
- decision/runtime flags remain disabled.

---

### V0.4.5 — Branch Resolver Documentation

**Commit:** `209beb3`

Created:

- `docs/POSTFLOP_BRANCH_RESOLVER.md`

Documented:

- Branch Resolver purpose.
- routing chain.
- branch types.
- routing rules.
- next-module policy.
- unsupported routing reason policy.
- no-validation policy.
- no-decision policy.
- no-runtime policy.
- preparation for V0.5.0 Flop Context Builder.

---

### V0.4.6 — Version Close / README / VERSION / Miro

Updated:

- `README.md`
- `VERSION.md`

Created:

- `docs/checkpoints/V0_4_0_BRANCH_RESOLVER_CLOSE.md`

---

## Final V0.4.0 architecture

```text
Clear_JSON
  -> ClearJsonInput
  -> SolverInput
  -> FieldMappingContract / FieldUsageTrace
  -> Branch Resolver
  -> SolverBranchResult
```

---

## BranchResult fields

`SolverBranchResult` contains:

- `case_id`
- `source_file`
- `branch`
- `branch_family`
- `next_module`
- `branch_reason`
- `is_decision_branch_enabled`
- `is_runtime_branch_enabled`
- `notes`

In V0.4.0:

```text
is_decision_branch_enabled = false
is_runtime_branch_enabled = false
```

---

## What V0.4.0 does not do

V0.4.0 does not:

- write flop decision engine
- write turn solver
- write river solver
- calculate equity
- build ranges
- classify board texture
- classify hand strength
- create runtime plan
- click
- validate PokerVision state
- rewrite Clear_JSON
- filter players
- create HERO
- create active player
- read Dark/Pending/Service/Runtime JSON

---

## Final test gate

Command:

```powershell
C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe -m pytest `
  tests/test_postflop_engine_contracts_v010.py `
  tests/test_postflop_clear_json_input_loader_v010.py `
  tests/test_postflop_solver_input_mapping_v010.py `
  tests/test_postflop_no_source_fallback_v010.py `
  tests/test_postflop_clear_json_fixture_skeleton_v020.py `
  tests/test_postflop_clear_json_minimum_cases_v020.py `
  tests/test_postflop_expected_interpretation_v020.py `
  tests/test_postflop_clear_json_fixture_manifest_v020.py `
  tests/test_postflop_field_mapping_contract_v030.py `
  tests/test_postflop_solver_input_field_usage_v030.py `
  tests/test_postflop_contract_backed_solver_input_mapping_v030.py `
  tests/test_postflop_no_validation_policy_v030.py `
  tests/test_postflop_branch_contracts_v040.py `
  tests/test_postflop_branch_resolver_v040.py `
  tests/test_postflop_branch_resolver_fixture_routing_v040.py `
  tests/test_postflop_branch_resolver_no_extra_checks_v040.py `
  -q
```

Result:

```text
125 passed
```

---

## Next version

### V0.5.0 — Flop Context Builder / Spot Family Layer

Next target chain:

```text
SolverInput + SolverBranchResult -> FlopContext
```

V0.5.0 will create the first specialized flop context layer, but it will still not:

- make poker decisions
- calculate equity
- build ranges
- classify board texture
- create runtime plans
- click
