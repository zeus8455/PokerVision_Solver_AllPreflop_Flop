# PokerVision_Solver_AllPreflop_Flop

Postflop solver development line for PokerVision on top of the existing AllPreflop / Preflop Solver baseline.

## Current status

**Current closed block:** V0.3.0 — SolverInput Mapping / Field Usage Contract  
**Current close checkpoint:** V0.3.6 — Version Close / README / VERSION / Miro  
**Expected close commit message:** `V0.3.6 close SolverInput mapping contract`  
**Latest verified gate:** `94 passed`  
**Next planned block:** V0.4.0 — Solver Branch Resolver / Street Module Routing

## Active architecture

The active postflop solver direction is Clear_JSON-only:

```text
Clear_JSON -> ClearJsonInput -> SolverInput -> FieldUsageTrace -> future solver modules
```

The solver does not search temporary PokerVision JSON sources. It accepts only explicitly provided Clear_JSON files that are already prepared by the PokerVision pipeline.

## Development rule

For every version/subversion:

1. discuss the scope first;
2. implement only after explicit approval;
3. deliver a ZIP with ready project structure;
4. integrate through one PowerShell command;
5. run the required checks;
6. commit and push a short Git checkpoint;
7. update README / VERSION when a full version block is closed;
8. document the version in Miro.

No runtime, click-chain, source-of-truth, player-state, validation, or solver decision logic is changed without a separate approved version.

---

# Closed version: V0.1.0 — Solver Engine Blueprint / Clear_JSON Input Contract

**Status:** closed  
**Close checkpoint:** `00b6b7d - V0.1.5 close solver engine blueprint`  
**Validation:** `25 passed`

## Goal

Create the postflop solver foundation:

```text
Clear_JSON -> ClearJsonInput -> SolverInput -> SolverTrace
```

V0.1.0 created the trusted input loader, baseline SolverInput mapping, and no-fallback architecture gate. It did not create poker decisions, source discovery, validation, runtime plans, or click-chain logic.

## Subversions

- `7fe5b4d - V0.1.1 add postflop engine contracts baseline`
- `1a4a2eb - V0.1.2 add Clear_JSON trusted input loader`
- `e80a582 - V0.1.3 add SolverInput mapping baseline`
- `73163d9 - V0.1.4 add postflop no-fallback architecture gate`
- `00b6b7d - V0.1.5 close solver engine blueprint`

---

# Closed version: V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases

**Status:** closed  
**Close checkpoint:** `ee56990 - V0.2.6 close Clear_JSON fixture library`  
**Validation:** `62 passed`

## Goal

Create a permanent Clear_JSON fixture library for future solver tests:

```text
real Clear_JSON -> templates -> synthetic Clear_JSON -> expected solver interpretation
```

Fixture root:

```text
tests/fixtures/postflop_clear_json/
```

V0.2.0 did not create solver decision logic, branch routing, source discovery, validation, runtime plans, or click-chain logic.

## Subversions

- `c2fa1a8 - V0.2.1 add Clear_JSON fixture library docs`
- `d648478 - V0.2.2 add Clear_JSON fixture skeleton`
- `fa9c509 - V0.2.3 add minimum Clear_JSON fixture cases`
- `0050a9f - V0.2.4 add expected Clear_JSON interpretations`
- `901aee5 - V0.2.5 add Clear_JSON fixture manifest gate`
- `ee56990 - V0.2.6 close Clear_JSON fixture library`

## Fixture library contents

- 1 real flop Clear_JSON case
- 1 synthetic flop Clear_JSON case
- 1 synthetic turn Clear_JSON case
- 1 synthetic river Clear_JSON case
- 4 expected interpretation files
- strict manifest/library tests

---

# Closed version: V0.3.0 — SolverInput Mapping / Field Usage Contract

**Status:** closed by V0.3.6  
**Close checkpoint:** V0.3.6 — Version Close / README / VERSION / Miro  
**Validation:** `94 passed`

## Goal

Create the official field mapping contract for the postflop solver:

```text
Clear_JSON field -> SolverInput field -> future solver module
```

V0.3.0 converts the earlier baseline mapping into a versioned contract-backed layer. It does not validate poker state, reconstruct missing data, detect street, build a branch resolver, produce poker decisions, create runtime plans, or click.

## Subversions

- `66bd6a1 - V0.3.1 add postflop field mapping contract`
- `00de073 - V0.3.2 add postflop field usage trace`
- `99674e1 - V0.3.3 bind SolverInput mapping to field contract`
- `cba0daa - V0.3.4 add postflop no-validation mapping gate`
- `7a3dfce - V0.3.5 document Clear_JSON field mapping`
- `V0.3.6 - close SolverInput mapping contract`

## Final V0.3.0 chain

```text
Clear_JSON
  -> ClearJsonInput
  -> contract-backed SolverInput
  -> FieldUsageTrace
```

## Created / updated modules

- `solver_postflop/field_mapping_contract.py`
- `solver_postflop/field_usage_trace.py`
- `solver_postflop/solver_input.py`
- `docs/POSTFLOP_CLEAR_JSON_FIELD_MAPPING.md`
- `tests/test_postflop_field_mapping_contract_v030.py`
- `tests/test_postflop_solver_input_field_usage_v030.py`
- `tests/test_postflop_contract_backed_solver_input_mapping_v030.py`
- `tests/test_postflop_no_validation_policy_v030.py`

## Final gate

```text
pytest \
  tests/test_postflop_engine_contracts_v010.py \
  tests/test_postflop_clear_json_input_loader_v010.py \
  tests/test_postflop_solver_input_mapping_v010.py \
  tests/test_postflop_no_source_fallback_v010.py \
  tests/test_postflop_clear_json_fixture_skeleton_v020.py \
  tests/test_postflop_clear_json_minimum_cases_v020.py \
  tests/test_postflop_expected_interpretation_v020.py \
  tests/test_postflop_clear_json_fixture_manifest_v020.py \
  tests/test_postflop_field_mapping_contract_v030.py \
  tests/test_postflop_solver_input_field_usage_v030.py \
  tests/test_postflop_contract_backed_solver_input_mapping_v030.py \
  tests/test_postflop_no_validation_policy_v030.py \
  -q

94 passed
```

---

# Next planned block: V0.4.0 — Solver Branch Resolver / Street Module Routing

V0.4.0 will create the first routing layer:

```text
SolverInput -> SolverBranchResult
```

Planned files:

- `solver_postflop/branch_contracts.py`
- `solver_postflop/branch_resolver.py`
- `docs/POSTFLOP_BRANCH_RESOLVER.md`
- `tests/test_postflop_branch_contracts_v040.py`
- `tests/test_postflop_branch_resolver_v040.py`
- `tests/test_postflop_branch_resolver_no_extra_checks_v040.py`

V0.4.0 must not validate cards, filter players, reconstruct HERO, search temporary JSON, create poker decisions, create runtime plans, or click.
