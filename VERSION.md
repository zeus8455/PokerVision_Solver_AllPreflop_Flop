# VERSION

Active line: **PokerVision_Solver_AllPreflop_Flop — Clear_JSON-only Postflop Solver Engine**

Repository reset point:

- `db16abd` — initial snapshot: Real_Version_SolverPreflop as AllPreflop_Flop baseline

Old pre-reset V0.x history is preserved in:

- `backup/old-v0-line-before-clear-json-reset`

---

## Current closed version

# V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases

Status: **closed by V0.2.6**

Purpose: Create the permanent Clear_JSON fixture library for future postflop solver tests.

Fixed fixture pipeline:

```text
ready Clear_JSON -> fixture case -> manifest entry -> expected interpretation -> future solver module tests
```

Main rule: The fixture library stores ready Clear_JSON cases only. It does not use upstream temporary source artifacts as solver inputs.

---

# V0.1.0 — Solver Engine Blueprint / Clear_JSON Input Contract

Status: **closed by V0.1.5**  
Close commit: `00b6b7d`

Purpose: Create the first clean postflop solver engine layer based only on ready Clear_JSON input.

Fixed pipeline:

```text
Clear_JSON -> ClearJsonInput -> SolverInput -> SolverTrace
```

## V0.1 subversions

### V0.1.1 — Postflop Package Baseline

Commit: `7fe5b4d`  
Status: closed

Implemented:

- `solver_postflop/__init__.py`
- `solver_postflop/engine_contracts.py`
- `ClearJsonInput`
- `SolverInput`
- `SolverTrace`
- `tests/test_postflop_engine_contracts_v010.py`

### V0.1.2 — Clear_JSON Trusted Input Loader

Commit: `1a4a2eb`  
Status: closed

Implemented:

- `solver_postflop/clear_json_input.py`
- `load_clear_json_input(path)`
- `tests/test_postflop_clear_json_input_loader_v010.py`

### V0.1.3 — SolverInput Mapping Baseline

Commit: `e80a582`  
Status: closed

Implemented:

- `solver_postflop/solver_input.py`
- `build_solver_input(clear_input)`
- `tests/test_postflop_solver_input_mapping_v010.py`

### V0.1.4 — No Fallback / No Validation Architecture Gate

Commit: `73163d9`  
Status: closed

Implemented:

- `tests/test_postflop_no_source_fallback_v010.py`

### V0.1.5 — Version Close / Docs / README / VERSION

Commit: `00b6b7d`  
Status: closed V0.1.0

Implemented:

- `docs/POSTFLOP_SOLVER_ENGINE_BLUEPRINT.md`
- updated `README.md`
- updated `VERSION.md`

Required gate at close:

```text
25 passed
```

---

# V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases

Status: **closed by V0.2.6**

Implemented scope:

- permanent fixture root: `tests/fixtures/postflop_clear_json/`
- `real/`, `synthetic/`, `templates/`, `expected/` structure
- `manifest.json`
- minimum real/synthetic flop/turn/river cases
- expected solver interpretation files
- strict manifest/library gate
- full V0.1 + V0.2 test gate

Not implemented by design:

- solver decision engine
- branch resolver
- equity calculation
- range construction
- board texture classification
- hand strength evaluation
- Clear_JSON safety validation
- duplicate card checks
- player filtering
- HERO reconstruction
- source discovery
- runtime plan
- click-chain

## V0.2 subversions

### V0.2.1 — Fixture Library Docs / Manifest Schema

Commit: `c2fa1a8`  
Status: closed

Implemented:

- `docs/POSTFLOP_CLEAR_JSON_FIXTURE_LIBRARY.md`
- `docs/POSTFLOP_CLEAR_JSON_FIXTURE_MANIFEST.md`
- fixture root policy
- manifest field contract
- expected interpretation policy

Required gate:

```text
25 passed
```

### V0.2.2 — Fixture Directory Skeleton

Commit: `d648478`  
Status: closed

Implemented:

- `tests/fixtures/postflop_clear_json/manifest.json`
- `real/flop`, `real/turn`, `real/river`
- `synthetic/flop`, `synthetic/turn`, `synthetic/river`
- `templates`
- `expected`
- `tests/test_postflop_clear_json_fixture_skeleton_v020.py`

Required gate:

```text
33 passed
```

### V0.2.3 — Minimum Clear_JSON Cases

Commit: `fa9c509`  
Status: closed

Implemented:

- `real_flop_srp_btn_vs_bb_check_option.clear.json`
- `synthetic_flop_srp_oop_facing_cbet.clear.json`
- `synthetic_turn_after_flop_bet_call.clear.json`
- `synthetic_river_facing_large_bet.clear.json`
- updated `manifest.json`
- `tests/test_postflop_clear_json_minimum_cases_v020.py`

Required gate:

```text
45 passed
```

### V0.2.4 — Expected Solver Interpretation Files

Commit: `0050a9f`  
Status: closed

Implemented:

- one expected interpretation file per Clear_JSON fixture
- manifest expected_file links
- `tests/test_postflop_expected_interpretation_v020.py`

Required gate:

```text
53 passed
```

### V0.2.5 — Fixture Manifest / Library Tests

Commit: `901aee5`  
Status: closed

Implemented:

- `tests/test_postflop_clear_json_fixture_manifest_v020.py`
- strict manifest integrity checks
- real/synthetic policy checks
- no source/temp-path policy checks
- no final-decision expected-file checks

Required gate:

```text
62 passed
```

### V0.2.6 — Version Close / README / VERSION / Miro Docs

Commit: see latest repository commit after integration  
Status: closed V0.2.0

Implemented:

- updated `README.md`
- updated `VERSION.md`
- updated fixture docs to closed status
- added `docs/checkpoints/V0_2_0_CLEAR_JSON_FIXTURE_LIBRARY_CLOSE.md`

Required gate:

```text
62 passed
```

---

## Next planned version

# V0.3.0 — SolverInput Mapping / Field Usage Contract

Status: planned

Purpose:

- create official field mapping contract
- document Clear_JSON field → SolverInput field → future module usage
- add field usage trace discipline
- use V0.2 fixture library as the test source
- keep validation, solver decision, source discovery, runtime plan, and clicks out of V0.3.0
