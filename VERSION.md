# VERSION

Active line: **PokerVision_Solver_AllPreflop_Flop — Clear_JSON-only Postflop Solver Engine**

Repository reset point:

- `db16abd` — initial snapshot: Real_Version_SolverPreflop as AllPreflop_Flop baseline

Old pre-reset V0.x history is preserved in:

- `backup/old-v0-line-before-clear-json-reset`

---

## Current version

# V0.1.0 — Solver Engine Blueprint / Clear_JSON Input Contract

Status: **closed by V0.1.5**

Purpose:

Create the first clean postflop solver engine layer based only on ready Clear_JSON input.

Fixed pipeline:

```text
Clear_JSON -> ClearJsonInput -> SolverInput -> SolverTrace
```

Main rule:

The solver reads trusted Clear_JSON and does not duplicate upstream PokerVision responsibilities.

---

## V0.1.1 — Postflop Package Baseline

Commit: `7fe5b4d`  
Status: closed

Implemented:

- `solver_postflop/__init__.py`
- `solver_postflop/engine_contracts.py`
- `ClearJsonInput`
- `SolverInput`
- `SolverTrace`
- `tests/test_postflop_engine_contracts_v010.py`

Result:

- postflop package exists as an isolated engine layer
- base contracts are importable and constructible
- no preflop/runtime/click dependency in the package contract baseline

---

## V0.1.2 — Clear_JSON Trusted Input Loader

Commit: `1a4a2eb`  
Status: closed

Implemented:

- `solver_postflop/clear_json_input.py`
- `load_clear_json_input(path)`
- `tests/test_postflop_clear_json_input_loader_v010.py`

Result:

- explicit Clear_JSON path is read
- `raw_data`, `source_file`, `loaded_at` are stored
- `case_id`, `hand_id`, `table_id` are extracted when present
- missing metadata does not fail the loader
- no automatic fallback source is used

---

## V0.1.3 — SolverInput Mapping Baseline

Commit: `e80a582`  
Status: closed

Implemented:

- `solver_postflop/solver_input.py`
- `build_solver_input(clear_input)`
- `tests/test_postflop_solver_input_mapping_v010.py`

Result:

- `SolverInput` is built from `ClearJsonInput`
- `SolverTrace` records used and missing fields
- `raw_clear_json_ref` is preserved
- missing optional fields are traced, not treated as errors
- no poker validation or source fallback is introduced

---

## V0.1.4 — No Fallback / No Validation Architecture Gate

Commit: `73163d9`  
Status: closed

Implemented:

- `tests/test_postflop_no_source_fallback_v010.py`

Result:

- no temporary-source fallback is allowed
- loader opens only the explicitly passed Clear_JSON file
- `build_solver_input` does not read project files
- public API stays focused on V0.1 engine input contracts
- Clear_JSON remains read-only at the mapping layer

---

## V0.1.5 — Version Close / Docs / README / VERSION

Commit: pending  
Status: closes V0.1.0

Implemented:

- `docs/POSTFLOP_SOLVER_ENGINE_BLUEPRINT.md`
- updated `README.md`
- updated `VERSION.md`

Result:

- V0.1.0 architecture documented
- README points to the new clean solver line
- VERSION tracks the new V0.1.0 subversion history
- Miro documentation block prepared

Required gate:

```powershell
C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe -m pytest `
  tests/test_postflop_engine_contracts_v010.py `
  tests/test_postflop_clear_json_input_loader_v010.py `
  tests/test_postflop_solver_input_mapping_v010.py `
  tests/test_postflop_no_source_fallback_v010.py `
  -q
```

Expected:

```text
25 passed
```

---

## V0.1.0 closed scope

Implemented:

- postflop package baseline
- engine contracts
- trusted Clear_JSON loader
- SolverInput mapper
- SolverTrace usage tracking
- no-fallback architecture gate
- documentation checkpoint

Not implemented by design:

- flop decision logic
- turn/river logic
- equity calculation
- ranges
- board texture classification
- hand strength evaluation
- source discovery
- normalizer
- runtime plan
- click-chain
- Clear_JSON safety validation
- duplicate card checks
- player filtering
- HERO reconstruction

---

## Next version

# V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases

Planned scope:

- create fixture root: `tests/fixtures/postflop_clear_json/`
- add `real/`, `synthetic/`, `templates/`, `expected/`
- add `manifest.json`
- add minimum real/synthetic flop/turn/river cases
- add expected solver interpretation files
- keep decision logic out of V0.2.0
