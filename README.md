# PokerVision Solver AllPreflop Flop

Current line: **Clear_JSON-only postflop solver engine**

This repository was reset to the initial baseline and restarted with a clean postflop solver architecture.

The active development rule is:

```text
Clear_JSON -> ClearJsonInput -> SolverInput -> SolverTrace -> future solver modules
```

The postflop solver must not duplicate upstream PokerVision responsibilities. It starts from a ready Clear_JSON file.

---

## Current status

**Current closed version:** V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases  
**Latest closed subversion:** V0.2.6 — Version Close / README / VERSION / Miro Docs  
**Latest completed gate before close:** `62 passed` at V0.2.5/V0.2.6 gate  
**Next block:** V0.3.0 — SolverInput Mapping / Field Usage Contract

---

## Active architecture

V0.1.0 fixed the first engine layer:

```text
Clear_JSON -> ClearJsonInput -> SolverInput -> SolverTrace -> future branch resolver / solver modules
```

V0.2.0 added the permanent fixture layer:

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

The fixture library stores ready Clear_JSON cases and expected interpretation metadata. It does not store upstream temporary source artifacts as solver inputs.

---

## Current modules

- `solver_postflop/engine_contracts.py`
- `solver_postflop/clear_json_input.py`
- `solver_postflop/solver_input.py`

---

## Current fixture library

Fixture root:

```text
tests/fixtures/postflop_clear_json/
```

Current minimum cases:

| Case | Source kind | Street | Purpose |
|---|---|---|---|
| `real_flop_srp_btn_vs_bb_check_option` | real | flop | baseline real/project-format Clear_JSON case |
| `synthetic_flop_srp_oop_facing_cbet` | synthetic | flop | synthetic flop scenario derived from real structure |
| `synthetic_turn_after_flop_bet_call` | synthetic | turn | synthetic turn routing/context fixture |
| `synthetic_river_facing_large_bet` | synthetic | river | synthetic river routing/context fixture |

Each case has:

- a Clear_JSON fixture file
- a manifest entry
- an expected interpretation file

Expected interpretation files describe solver understanding only. They do **not** contain final poker decisions.

---

## Core policies

### Clear_JSON-only input

The postflop solver accepts only an explicitly passed Clear_JSON file or `ClearJsonInput` object.

### Read-only source handling

The original Clear_JSON content is preserved and referenced. It must not be mutated by the solver input layer.

### No fallback

The solver and fixture layer do not search temporary PokerVision artifacts or upstream project files.

### No validation in V0.1.x / V0.2.x

The early engine and fixture layers do not validate poker state, repair cards, reconstruct players, or infer missing HERO/active player data.

---

## Checkpoint history

| Version | Commit | Description |
|---|---:|---|
| Initial reset baseline | `db16abd` | initial snapshot after clean reset |
| V0.1.1 | `7fe5b4d` | add postflop engine contracts baseline |
| V0.1.2 | `1a4a2eb` | add Clear_JSON trusted input loader |
| V0.1.3 | `e80a582` | add SolverInput mapping baseline |
| V0.1.4 | `73163d9` | add postflop no-fallback architecture gate |
| V0.1.5 | `00b6b7d` | close solver engine blueprint documentation |
| V0.2.1 | `c2fa1a8` | add Clear_JSON fixture library docs |
| V0.2.2 | `d648478` | add Clear_JSON fixture skeleton |
| V0.2.3 | `fa9c509` | add minimum Clear_JSON fixture cases |
| V0.2.4 | `0050a9f` | add expected Clear_JSON interpretations |
| V0.2.5 | `901aee5` | add Clear_JSON fixture manifest gate |
| V0.2.6 | see latest commit | close Clear_JSON fixture library |

The previous old V0.x line is preserved in:

```text
backup/old-v0-line-before-clear-json-reset
```

---

## Full V0.1 + V0.2 gate

Run:

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
  -q
```

Expected at V0.2.6 close:

```text
62 passed
```

---

## Next planned block

**V0.3.0 — SolverInput Mapping / Field Usage Contract**

Planned purpose:

- turn the baseline V0.1.3 mapping into an official versioned contract
- define Clear_JSON field → SolverInput field → future module usage
- add FieldUsageTrace semantics for used / not_provided / ignored fields
- keep validation, decision logic, source discovery, runtime plans, and clicks out of V0.3.0

---

## Development method

For every version/subversion:

1. Discuss scope first.
2. Implement only after explicit approval.
3. Deliver a ZIP with ready project structure.
4. Integrate through one PowerShell command.
5. Run the required checks.
6. Commit and push a short Git checkpoint.
7. Update README / VERSION when a full version block is closed.
8. Document the version for Miro.
