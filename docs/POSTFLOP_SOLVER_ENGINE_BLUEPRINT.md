# V0.1.0 — Solver Engine Blueprint / Clear_JSON Input Contract

Status: **closed by V0.1.5**  
Line: **new Clear_JSON-only postflop solver engine**  
Current baseline before V0.1.5 commit: **73163d9 — V0.1.4 add postflop no-fallback architecture gate**

---

## 1. Purpose

V0.1.0 establishes the first clean architecture layer for the new postflop solver engine after the repository reset.

The solver engine starts from a trusted PokerVision output file:

**Clear_JSON → ClearJsonInput → SolverInput → SolverTrace**

This version does not solve poker spots. It defines the input contract and proves that the postflop solver accepts only an explicitly provided Clear_JSON object/file.

---

## 2. Architecture fixed in V0.1.0

### 2.1 Clear_JSON-only input policy

The postflop solver reads a ready Clear_JSON file that has already passed through the main PokerVision chain.

The solver does **not** discover or repair upstream project artifacts. The only accepted source at this layer is an explicitly passed Clear_JSON path or a `ClearJsonInput` object.

### 2.2 Read-only policy

The solver must keep the original Clear_JSON content available through `raw_data` / `raw_clear_json_ref` and must not mutate the original dictionary.

### 2.3 No fallback policy

The solver must not search for alternative temporary or upstream JSON files.

Forbidden in V0.1.x:

- Dark/Pending/Service/Runtime source fallback
- automatic source discovery
- external snapshot scanning
- live/runtime/click-chain access
- preflop solver imports

### 2.4 No validation policy

V0.1.x is not a safety-validation layer. It does not verify whether poker data is correct. That responsibility stays upstream in PokerVision and in future dedicated modules if explicitly planned.

Forbidden in V0.1.x:

- duplicate card validation
- hero-board collision validation
- board count safety gate
- player filtering
- HERO reconstruction
- active player reconstruction
- pot/stack/action repair

---

## 3. Modules created in V0.1.0

### 3.1 `solver_postflop/engine_contracts.py`

Defines the core engine data contracts:

- `ClearJsonInput`
- `SolverInput`
- `SolverTrace`

These structures are pure contracts. They do not execute poker logic.

### 3.2 `solver_postflop/clear_json_input.py`

Defines:

- `load_clear_json_input(path)`

The loader reads only the explicit path passed to it and creates `ClearJsonInput`.

It stores:

- `source_file`
- `raw_data`
- `loaded_at`
- `case_id`, when present
- `hand_id`, when present
- `table_id`, when present

### 3.3 `solver_postflop/solver_input.py`

Defines:

- `build_solver_input(clear_input)`

The mapper builds:

- `SolverInput`
- `SolverTrace`

It records:

- `fields_used`
- `fields_not_provided`
- `mapping_version`
- `module_chain_next_step`

---

## 4. Field mapping baseline

V0.1.3 introduced the first minimal Clear_JSON to SolverInput mapping.

| Clear_JSON field | SolverInput field | Notes |
|---|---|---|
| `table_id` | `table_id` | table metadata |
| `hand_id` | `hand_id` | hand metadata |
| `hero_cards` | `hero_cards` | copied as provided |
| `board_cards` | `board_cards` | copied as provided |
| `players` | `players` | copied as provided |
| `total_pot` / `pot` | `pot` | `total_pot` has priority |
| `to_call` | `to_call` | copied as provided |
| `stacks` / `chips` | `stacks` | first available field |
| `committed_amounts` / `committed` | `committed_amounts` | first available field |
| `positions` | `positions` | copied as provided |
| `button` | `button` | copied as provided |
| `blinds` | `blinds` | copied as provided |
| `allowed_actions` | `allowed_actions` | copied as provided |
| `action_context` | `action_context` | copied as provided |

Missing optional fields are recorded in `SolverTrace.fields_not_provided`; they do not fail the V0.1.x pipeline.

---

## 5. Tests created in V0.1.0

### 5.1 `tests/test_postflop_engine_contracts_v010.py`

Confirms:

- package import works
- core contracts can be created
- `input_kind` defaults to `clear_json`
- package is isolated from preflop/runtime/live/click code

### 5.2 `tests/test_postflop_clear_json_input_loader_v010.py`

Confirms:

- explicit Clear_JSON file is loaded
- `ClearJsonInput` is created
- `raw_data` is preserved
- metadata is extracted when available
- metadata absence does not fail the loader
- source fallback is not used

### 5.3 `tests/test_postflop_solver_input_mapping_v010.py`

Confirms:

- `SolverInput` is built from `ClearJsonInput`
- core fields are mapped
- missing optional fields are traced
- `raw_clear_json_ref` is preserved
- Clear_JSON is not mutated

### 5.4 `tests/test_postflop_no_source_fallback_v010.py`

Confirms:

- no forbidden source fallback behavior exists
- loader opens only the explicit Clear_JSON path
- `build_solver_input` does not read files
- public API exposes only the intended V0.1 engine surface

---

## 6. V0.1.0 checkpoints

| Subversion | Commit | Scope | Result |
|---|---:|---|---|
| V0.1.1 | `7fe5b4d` | Postflop engine contracts baseline | closed |
| V0.1.2 | `1a4a2eb` | Clear_JSON trusted input loader | closed |
| V0.1.3 | `e80a582` | SolverInput mapping baseline | closed |
| V0.1.4 | `73163d9` | No-fallback architecture gate | closed |
| V0.1.5 | pending | Docs / README / VERSION close | closes V0.1.0 |

---

## 7. Required V0.1.0 gate

Run:

```powershell
C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe -m pytest `
  tests/test_postflop_engine_contracts_v010.py `
  tests/test_postflop_clear_json_input_loader_v010.py `
  tests/test_postflop_solver_input_mapping_v010.py `
  tests/test_postflop_no_source_fallback_v010.py `
  -q
```

Expected result at V0.1.5 close:

**25 passed**

---

## 8. Miro documentation block

**Card title:** V0.1.0 — Solver Engine Blueprint / Clear_JSON Input Contract

**Purpose:** Build the first clean postflop solver input layer after reset.

**Pipeline:** Clear_JSON → ClearJsonInput → SolverInput → SolverTrace

**Main rule:** Solver accepts only explicitly provided Clear_JSON. No temporary source discovery and no PokerVision chain duplication.

**Implemented:**

- engine contracts
- trusted Clear_JSON loader
- SolverInput mapper
- usage trace
- no-fallback architecture gate
- version close documentation

**Not implemented by design:**

- poker decisions
- street branch resolver
- equity/ranges
- board texture
- hand strength
- safety validation
- runtime plan
- live clicks
- source discovery
- normalizer

**Test gate:** 25 V0.1.x tests.

**Next card:** V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases

---

## 9. Next version

**V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases**

The next block should create a permanent fixture library based on real and synthetic Clear_JSON cases. It should not introduce poker decision logic yet.
