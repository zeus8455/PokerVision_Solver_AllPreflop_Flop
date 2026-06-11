# PokerVision_Solver_AllPreflop_Flop — Version History

This file tracks the reset Clear_JSON-only postflop development line.

Repository baseline:

```text
db16abd - initial snapshot: Real_Version_SolverPreflop as AllPreflop_Flop baseline
```

Legacy preflop/runtime history remains in the imported repository baseline. The active postflop solver line starts from the reset Clear_JSON-only blocks below.

---

## V0.3.0 — SolverInput Mapping / Field Usage Contract

**Status:** closed by V0.3.6  
**Close checkpoint:** V0.3.6 — Version Close / README / VERSION / Miro  
**Validation:** `94 passed`  
**Next block:** `V0.4.0 — Solver Branch Resolver / Street Module Routing`

### Goal

Create the official, versioned contract for mapping trusted Clear_JSON fields into SolverInput fields and FieldUsageTrace records:

```text
Clear_JSON field -> SolverInput field -> future solver module
```

V0.3.0 is not a validator and not a safety gate. It does not validate cards, detect duplicate cards, check hero-board collision, validate board count, filter players, reconstruct HERO, reconstruct active player, repair pot/stack/action state, search temporary JSON sources, create poker decisions, create runtime plans, or click.

### V0.3.1 — Field Mapping Contract Baseline

**Commit:** `66bd6a1 - V0.3.1 add postflop field mapping contract`

Added:

- `solver_postflop/field_mapping_contract.py`
- `tests/test_postflop_field_mapping_contract_v030.py`

Contract exports:

- `FIELD_MAPPING_VERSION = "v0.3.0"`
- `ClearJsonFieldRequirement`
- `FutureSolverModule`
- `FieldMappingEntry`
- `CLEAR_JSON_FIELD_MAPPINGS`

Validation:

```text
70 passed
```

### V0.3.2 — Field Usage Trace Layer

**Commit:** `00de073 - V0.3.2 add postflop field usage trace`

Added:

- `solver_postflop/field_usage_trace.py`
- `tests/test_postflop_solver_input_field_usage_v030.py`

Trace exports:

- `FieldUsageStatus`
- `FieldUsageRecord`
- `FieldUsageTrace`
- `build_field_usage_trace`

Validation:

```text
78 passed
```

### V0.3.3 — Contract-backed SolverInput Mapping

**Commit:** `99674e1 - V0.3.3 bind SolverInput mapping to field contract`

Updated:

- `solver_postflop/solver_input.py`
- `tests/test_postflop_solver_input_mapping_v010.py`

Added:

- `tests/test_postflop_contract_backed_solver_input_mapping_v030.py`

Result:

- `build_solver_input()` now uses `CLEAR_JSON_FIELD_MAPPINGS`.
- `MAPPING_VERSION` is synchronized with `FIELD_MAPPING_VERSION`.
- alias fields such as `total_pot/pot`, `stacks/chips`, and `committed/committed_amounts` are resolved through the mapping contract.
- public API remains stable: `build_solver_input(clear_input) -> tuple[SolverInput, SolverTrace]`.

Validation:

```text
87 passed
```

### V0.3.4 — No Validation Policy Gate V0.3

**Commit:** `cba0daa - V0.3.4 add postflop no-validation mapping gate`

Added:

- `tests/test_postflop_no_validation_policy_v030.py`

Purpose:

- protect the mapping/trace layer from accidentally becoming card validation, player filtering, source discovery, street routing, poker decision, runtime plan, or click-chain logic.

Validation:

```text
94 passed
```

### V0.3.5 — Field Mapping Documentation

**Commit:** `7a3dfce - V0.3.5 document Clear_JSON field mapping`

Added:

- `docs/POSTFLOP_CLEAR_JSON_FIELD_MAPPING.md`

Purpose:

- document metadata, cards, players, pot/stacks, action context, and preflop context mapping groups;
- document FieldUsageTrace semantics;
- document non-validator policy.

Validation:

```text
94 passed
```

### V0.3.6 — Version Close / README / VERSION / Miro

**Commit message:** `V0.3.6 close SolverInput mapping contract`

Added:

- `docs/checkpoints/V0_3_0_FIELD_MAPPING_CONTRACT_CLOSE.md`

Updated:

- `README.md`
- `VERSION.md`

Purpose:

- close the full V0.3.0 block;
- mark the project ready for V0.4.0 design;
- preserve the final V0.3.0 gate result.

Validation:

```text
94 passed
```

---

## V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases

**Status:** closed  
**Close checkpoint:** `ee56990 - V0.2.6 close Clear_JSON fixture library`  
**Validation:** `62 passed`

### Goal

Create a permanent Clear_JSON fixture library for future postflop solver modules.

Fixture root:

```text
tests/fixtures/postflop_clear_json/
```

### Subversions

- `c2fa1a8 - V0.2.1 add Clear_JSON fixture library docs`
- `d648478 - V0.2.2 add Clear_JSON fixture skeleton`
- `fa9c509 - V0.2.3 add minimum Clear_JSON fixture cases`
- `0050a9f - V0.2.4 add expected Clear_JSON interpretations`
- `901aee5 - V0.2.5 add Clear_JSON fixture manifest gate`
- `ee56990 - V0.2.6 close Clear_JSON fixture library`

---

## V0.1.0 — Solver Engine Blueprint / Clear_JSON Input Contract

**Status:** closed  
**Close checkpoint:** `00b6b7d - V0.1.5 close solver engine blueprint`  
**Validation:** `25 passed`

### Goal

Create the trusted Clear_JSON-only solver foundation:

```text
Clear_JSON -> ClearJsonInput -> SolverInput -> SolverTrace
```

### Subversions

- `7fe5b4d - V0.1.1 add postflop engine contracts baseline`
- `1a4a2eb - V0.1.2 add Clear_JSON trusted input loader`
- `e80a582 - V0.1.3 add SolverInput mapping baseline`
- `73163d9 - V0.1.4 add postflop no-fallback architecture gate`
- `00b6b7d - V0.1.5 close solver engine blueprint`

---

## Next planned block

## V0.4.0 — Solver Branch Resolver / Street Module Routing

Planned chain:

```text
Clear_JSON -> ClearJsonInput -> SolverInput -> FieldUsageTrace -> Branch Resolver -> SolverBranchResult
```

V0.4.0 will not create poker decisions, runtime plans, or click-chain behavior.
