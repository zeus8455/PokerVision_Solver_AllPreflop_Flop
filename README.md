# PokerVision Solver AllPreflop Flop

Current development line: **Clear_JSON-only postflop solver engine**.

This repository is now maintained as a staged solver-development project. Each version/subversion is discussed first, implemented only after explicit approval, delivered as a ZIP overlay, checked with targeted pytest gates, committed, pushed, and documented for Miro.

---

## Current status

**Current closed version:** `V0.4.0 — Solver Branch Resolver / Street Module Routing`  
**Closing subversion:** `V0.4.6 — Version Close / README / VERSION / Miro`  
**Final V0.4 gate:** `125 passed`  
**Next planned version:** `V0.5.0 — Flop Context Builder / Spot Family Layer`

---

## Closed version chain

### V0.1.0 — Solver Engine Blueprint / Clear_JSON Input Contract

Closed by: `V0.1.5`  
Checkpoint commit: `00b6b7d`

Created the initial Clear_JSON-only engine layer:

```text
Clear_JSON -> ClearJsonInput -> SolverInput -> SolverTrace
```

Key files:

- `solver_postflop/engine_contracts.py`
- `solver_postflop/clear_json_input.py`
- `solver_postflop/solver_input.py`
- `docs/POSTFLOP_SOLVER_ENGINE_BLUEPRINT.md`

Core policy:

- Clear_JSON is trusted input.
- Solver does not search Dark/Pending/Service/Runtime JSON.
- Solver does not validate cards or player state.
- Solver does not mutate Clear_JSON.

---

### V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases

Closed by: `V0.2.6`  
Checkpoint commit: `ee56990`

Created the permanent Clear_JSON fixture library:

```text
tests/fixtures/postflop_clear_json/
```

Fixture structure:

- `real/flop/`
- `real/turn/`
- `real/river/`
- `synthetic/flop/`
- `synthetic/turn/`
- `synthetic/river/`
- `templates/`
- `expected/`
- `manifest.json`

Final V0.2 gate:

```text
62 passed
```

---

### V0.3.0 — SolverInput Mapping / Field Usage Contract

Closed by: `V0.3.6`  
Checkpoint commit: `4603c68`

Created the official mapping contract:

```text
Clear_JSON field -> SolverInput field -> future solver module
```

Key files:

- `solver_postflop/field_mapping_contract.py`
- `solver_postflop/field_usage_trace.py`
- `docs/POSTFLOP_CLEAR_JSON_FIELD_MAPPING.md`

V0.3 also moved `build_solver_input()` to contract-backed mapping while preserving the public API.

Final V0.3 gate:

```text
94 passed
```

---

### V0.4.0 — Solver Branch Resolver / Street Module Routing

Closed by: `V0.4.6`

Created the first routing layer:

```text
SolverInput -> SolverBranchResult
```

Key files:

- `solver_postflop/branch_contracts.py`
- `solver_postflop/branch_resolver.py`
- `docs/POSTFLOP_BRANCH_RESOLVER.md`
- `docs/checkpoints/V0_4_0_BRANCH_RESOLVER_CLOSE.md`

Branch types:

- `preflop_not_handled`
- `flop`
- `turn_not_implemented_yet`
- `river_not_implemented_yet`
- `unsupported`

Routing rules:

```text
0 board cards        -> preflop_not_handled
3 board cards        -> flop
4 board cards        -> turn_not_implemented_yet
5 board cards        -> river_not_implemented_yet
missing / 1 / 2 / 6+ -> unsupported
```

Final V0.4 gate:

```text
125 passed
```

---

## Current active architecture

```text
Clear_JSON
  -> ClearJsonInput
  -> SolverInput
  -> FieldMappingContract / FieldUsageTrace
  -> Branch Resolver
  -> SolverBranchResult
```

The project currently routes postflop input into future solver modules, but it does **not** make poker decisions.

---

## Current test gate

Run the current full V0.1 + V0.2 + V0.3 + V0.4 gate:

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

Expected result:

```text
125 passed
```

---

## Next planned block

### V0.5.0 — Flop Context Builder / Spot Family Layer

Target chain:

```text
Clear_JSON -> SolverInput -> Branch Resolver -> FlopContext
```

V0.5.0 will create the first specialized flop context layer, but it will still not make poker decisions, compute equity, classify board texture, or interact with runtime/click-chain.
