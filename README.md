# PokerVision Solver AllPreflop Flop

Current line: **new Clear_JSON-only postflop solver engine**

This repository was reset to the initial baseline and restarted with a clean postflop solver architecture.

The active development rule is:

**Clear_JSON → ClearJsonInput → SolverInput → SolverTrace → future solver modules**

The solver must not duplicate PokerVision upstream responsibilities. It starts from a ready Clear_JSON file.

---

## Current status

**Current closed version:** V0.1.0 — Solver Engine Blueprint / Clear_JSON Input Contract  
**Latest closed subversion:** V0.1.5 — Version Close / Docs / README / VERSION  
**Latest closed commit:** `00b6b7d` — V0.1.5 close solver engine blueprint  
**Active next block:** V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases

---

## Active architecture

V0.1.0 fixes the first engine layer:

```text
Clear_JSON
  -> ClearJsonInput
  -> SolverInput
  -> SolverTrace
  -> future branch resolver / solver modules
```

### Current modules

- `solver_postflop/engine_contracts.py`
- `solver_postflop/clear_json_input.py`
- `solver_postflop/solver_input.py`

### Current tests

- `tests/test_postflop_engine_contracts_v010.py`
- `tests/test_postflop_clear_json_input_loader_v010.py`
- `tests/test_postflop_solver_input_mapping_v010.py`
- `tests/test_postflop_no_source_fallback_v010.py`

---

## Core policies

### Clear_JSON-only input

The postflop solver accepts only an explicitly passed Clear_JSON file or `ClearJsonInput` object.

### Read-only source handling

The original Clear_JSON content is preserved and referenced. It must not be mutated by the solver input layer.

### No fallback

The solver does not search temporary PokerVision artifacts or upstream project files.

### No validation in V0.1.x / V0.2.x fixture setup

The early engine and fixture layers do not validate poker state, repair cards, reconstruct players, or infer missing HERO/active player data.

---

## V0.1.0 checkpoint history

| Version | Commit | Description |
|---|---:|---|
| Initial reset baseline | `db16abd` | initial snapshot after clean reset |
| V0.1.1 | `7fe5b4d` | add postflop engine contracts baseline |
| V0.1.2 | `1a4a2eb` | add Clear_JSON trusted input loader |
| V0.1.3 | `e80a582` | add SolverInput mapping baseline |
| V0.1.4 | `73163d9` | add postflop no-fallback architecture gate |
| V0.1.5 | `00b6b7d` | close solver engine blueprint documentation |

The previous old V0.x line is preserved in:

`backup/old-v0-line-before-clear-json-reset`

---

## V0.1 test gate

Run:

```powershell
C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe -m pytest `
  tests/test_postflop_engine_contracts_v010.py `
  tests/test_postflop_clear_json_input_loader_v010.py `
  tests/test_postflop_solver_input_mapping_v010.py `
  tests/test_postflop_no_source_fallback_v010.py `
  -q
```

Expected at V0.1.5 close:

```text
25 passed
```

---

## V0.2.0 planned block

**V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases**

Planned purpose:

- create permanent Clear_JSON fixture structure
- add real/synthetic fixture separation
- add manifest and expected interpretation files
- keep solver decision logic out of V0.2.0

Planned fixture root:

```text
tests/fixtures/postflop_clear_json/
```

V0.2.1 starts this block by documenting the fixture library policy and manifest schema.

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
