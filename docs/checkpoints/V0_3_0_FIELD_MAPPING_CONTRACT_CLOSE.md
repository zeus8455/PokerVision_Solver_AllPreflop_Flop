# V0.3.0 — SolverInput Mapping / Field Usage Contract Close

**Status:** closed by V0.3.6  
**Close checkpoint:** V0.3.6 — Version Close / README / VERSION / Miro  
**Expected commit message:** `V0.3.6 close SolverInput mapping contract`  
**Final validation:** `94 passed`  
**Next block:** V0.4.0 — Solver Branch Resolver / Street Module Routing

---

## 1. Version goal

V0.3.0 created the official field usage layer for the Clear_JSON-only postflop solver engine.

The target pipeline after V0.3.0 is:

```text
Clear_JSON -> ClearJsonInput -> contract-backed SolverInput -> FieldUsageTrace
```

The purpose of this block was not to create poker logic. The purpose was to define exactly how the solver consumes fields from trusted Clear_JSON files:

```text
Clear_JSON field -> SolverInput field -> future solver module
```

---

## 2. What V0.3.0 created

### V0.3.1 — Field Mapping Contract Baseline

**Commit:** `66bd6a1 - V0.3.1 add postflop field mapping contract`

Created:

- `solver_postflop/field_mapping_contract.py`
- `tests/test_postflop_field_mapping_contract_v030.py`

The mapping contract introduced:

- `FIELD_MAPPING_VERSION = "v0.3.0"`
- `ClearJsonFieldRequirement`
- `FutureSolverModule`
- `FieldMappingEntry`
- `CLEAR_JSON_FIELD_MAPPINGS`

Covered groups:

- metadata
- cards
- players
- pot / stacks
- action context
- preflop context

Validation:

```text
70 passed
```

---

### V0.3.2 — Field Usage Trace Layer

**Commit:** `00de073 - V0.3.2 add postflop field usage trace`

Created:

- `solver_postflop/field_usage_trace.py`
- `tests/test_postflop_solver_input_field_usage_v030.py`

The trace layer introduced:

- `FieldUsageStatus`
- `FieldUsageRecord`
- `FieldUsageTrace`
- `build_field_usage_trace(clear_input, solver_input)`

The trace layer reports:

- fields used
- fields not provided
- fields ignored
- future modules enabled by available fields
- mapping records connected to `FieldMappingEntry`

Validation:

```text
78 passed
```

---

### V0.3.3 — Contract-backed SolverInput Mapping

**Commit:** `99674e1 - V0.3.3 bind SolverInput mapping to field contract`

Updated:

- `solver_postflop/solver_input.py`
- `tests/test_postflop_solver_input_mapping_v010.py`

Created:

- `tests/test_postflop_contract_backed_solver_input_mapping_v030.py`

Result:

- `build_solver_input()` now uses `CLEAR_JSON_FIELD_MAPPINGS`.
- `MAPPING_VERSION` is synchronized with `FIELD_MAPPING_VERSION`.
- alias fields are resolved through the mapping contract.
- `raw_clear_json_ref` remains a reference to the original Clear_JSON object.
- the public API remains stable.

Public API:

```python
build_solver_input(clear_input) -> tuple[SolverInput, SolverTrace]
```

Validation:

```text
87 passed
```

---

### V0.3.4 — No Validation Policy Gate V0.3

**Commit:** `cba0daa - V0.3.4 add postflop no-validation mapping gate`

Created:

- `tests/test_postflop_no_validation_policy_v030.py`

This architecture gate protects the mapping/trace layer from accidental scope creep.

It verifies that the mapping layer does not perform:

- duplicate card validation
- hero-board collision validation
- board count safety gate
- player filtering
- HERO reconstruction
- active player reconstruction
- street resolver logic
- source discovery fallback
- runtime/click-chain logic
- Clear_JSON mutation
- poker decision creation
- runtime plan creation

Validation:

```text
94 passed
```

---

### V0.3.5 — Field Mapping Documentation

**Commit:** `7a3dfce - V0.3.5 document Clear_JSON field mapping`

Created:

- `docs/POSTFLOP_CLEAR_JSON_FIELD_MAPPING.md`

The document explains:

- the non-validator policy;
- metadata mapping;
- card mapping;
- player mapping;
- pot / stack mapping;
- action context mapping;
- preflop context mapping;
- FieldUsageTrace semantics;
- what future modules are expected to use each field group.

Validation:

```text
94 passed
```

---

### V0.3.6 — Version Close / README / VERSION / Miro

Created:

- `docs/checkpoints/V0_3_0_FIELD_MAPPING_CONTRACT_CLOSE.md`

Updated:

- `README.md`
- `VERSION.md`

Purpose:

- close the full V0.3.0 block;
- document the final V0.3.0 state;
- mark the project ready for V0.4.0;
- preserve the final V0.1 + V0.2 + V0.3 gate.

Validation:

```text
94 passed
```

---

## 3. Final V0.3.0 architecture

The final V0.3.0 chain is:

```text
Clear_JSON
  -> ClearJsonInput
  -> SolverInput built through CLEAR_JSON_FIELD_MAPPINGS
  -> FieldUsageTrace
```

The mapping layer now has three separate responsibilities:

1. `field_mapping_contract.py` defines the official mapping table.
2. `solver_input.py` builds SolverInput using the official contract.
3. `field_usage_trace.py` reports used / not_provided / ignored fields.

---

## 4. Final gate command

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
  -q
```

Expected result:

```text
94 passed
```

---

## 5. What V0.3.0 explicitly does not do

V0.3.0 does not:

- write street resolver;
- write branch resolver;
- write flop / turn / river logic;
- write poker decision logic;
- calculate equity;
- build ranges;
- classify board texture;
- determine hand strength;
- validate cards;
- check duplicate cards;
- check hero-board collision;
- validate board count;
- filter players;
- reconstruct HERO;
- reconstruct active player;
- reconstruct preflop history;
- search Dark / Pending / Service / Runtime JSON;
- create runtime plan;
- click.

---

## 6. Ready for V0.4.0

The next block is:

```text
V0.4.0 — Solver Branch Resolver / Street Module Routing
```

The planned next chain is:

```text
SolverInput -> SolverBranchResult
```

V0.4.0 should use the V0.2 fixture library and V0.3 contract-backed SolverInput as input.

It should route to:

- `preflop_not_handled`
- `flop`
- `turn_not_implemented_yet`
- `river_not_implemented_yet`
- `unsupported`

It must still not validate poker state or create decisions.
