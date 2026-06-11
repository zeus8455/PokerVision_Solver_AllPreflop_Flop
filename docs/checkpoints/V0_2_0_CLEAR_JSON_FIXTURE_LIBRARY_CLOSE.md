# V0.2.0 Close Checkpoint — Clear_JSON Fixture Library

Status: **closed by V0.2.6**  
Line: **Clear_JSON-only postflop solver engine**  
Close subversion: **V0.2.6 — Version Close / README / VERSION / Miro Docs**

---

## 1. Version goal

V0.2.0 created the permanent fixture base for the postflop solver engine.

The version did not implement poker decisions. It created stable Clear_JSON test material and integrity tests so future versions can use shared cases instead of ad-hoc JSON files.

Main chain:

```text
ready Clear_JSON -> fixture case -> manifest entry -> expected interpretation -> future solver module tests
```

---

## 2. Closed subversions

### V0.2.1 — Fixture Library Docs / Manifest Schema

Commit: `c2fa1a8`

Created:

- `docs/POSTFLOP_CLEAR_JSON_FIXTURE_LIBRARY.md`
- `docs/POSTFLOP_CLEAR_JSON_FIXTURE_MANIFEST.md`

Result:

- Clear_JSON-only fixture policy documented
- real/synthetic policy documented
- manifest schema documented
- expected interpretation policy documented

---

### V0.2.2 — Fixture Directory Skeleton

Commit: `d648478`

Created:

- `tests/fixtures/postflop_clear_json/manifest.json`
- `real/flop`, `real/turn`, `real/river`
- `synthetic/flop`, `synthetic/turn`, `synthetic/river`
- `templates`
- `expected`
- `tests/test_postflop_clear_json_fixture_skeleton_v020.py`

Result:

- physical fixture library structure exists
- skeleton structure protected by tests

---

### V0.2.3 — Minimum Clear_JSON Cases

Commit: `fa9c509`

Created:

- `real_flop_srp_btn_vs_bb_check_option.clear.json`
- `synthetic_flop_srp_oop_facing_cbet.clear.json`
- `synthetic_turn_after_flop_bet_call.clear.json`
- `synthetic_river_facing_large_bet.clear.json`
- `tests/test_postflop_clear_json_minimum_cases_v020.py`

Result:

- fixture library has a minimum real/synthetic case set
- each case loads through `load_clear_json_input()`
- real/synthetic separation is explicit

---

### V0.2.4 — Expected Solver Interpretation Files

Commit: `0050a9f`

Created:

- one expected interpretation file per Clear_JSON case
- manifest links to expected files
- `tests/test_postflop_expected_interpretation_v020.py`

Result:

- every fixture has expected solver interpretation metadata
- expected files describe interpretation only
- no final poker action is present in expected files

---

### V0.2.5 — Fixture Manifest / Library Tests

Commit: `901aee5`

Created:

- `tests/test_postflop_clear_json_fixture_manifest_v020.py`

Result:

- strict manifest gate added
- case IDs, file paths, source kinds, expected links, purpose fields, module targets, and no-temp-source policy are checked

---

### V0.2.6 — Version Close / README / VERSION / Miro Docs

Commit: see repository latest commit after integration

Created / updated:

- `README.md`
- `VERSION.md`
- `docs/POSTFLOP_CLEAR_JSON_FIXTURE_LIBRARY.md`
- `docs/POSTFLOP_CLEAR_JSON_FIXTURE_MANIFEST.md`
- `docs/checkpoints/V0_2_0_CLEAR_JSON_FIXTURE_LIBRARY_CLOSE.md`

Result:

- V0.2.0 officially closed
- README/VERSION now point to V0.3.0 as next planned block
- Miro documentation checkpoint prepared

---

## 3. Fixture library final state

Root:

```text
tests/fixtures/postflop_clear_json/
```

Current case files:

```text
real/flop/real_flop_srp_btn_vs_bb_check_option.clear.json
synthetic/flop/synthetic_flop_srp_oop_facing_cbet.clear.json
synthetic/turn/synthetic_turn_after_flop_bet_call.clear.json
synthetic/river/synthetic_river_facing_large_bet.clear.json
```

Current expected files:

```text
expected/real_flop_srp_btn_vs_bb_check_option.expected.json
expected/synthetic_flop_srp_oop_facing_cbet.expected.json
expected/synthetic_turn_after_flop_bet_call.expected.json
expected/synthetic_river_facing_large_bet.expected.json
```

---

## 4. Final gate

Full V0.1 + V0.2 gate:

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

Expected result:

```text
62 passed
```

---

## 5. Scope intentionally not implemented

V0.2.0 does not implement:

- solver decision engine
- branch resolver
- street routing logic
- field mapping contract V0.3
- equity
- ranges
- board texture
- hand strength
- Clear_JSON safety validation
- duplicate card checks
- hero-board collision checks
- player filtering
- HERO reconstruction
- source discovery
- runtime plan
- click-chain

---

## 6. Next version

**V0.3.0 — SolverInput Mapping / Field Usage Contract**

Goal:

```text
Clear_JSON field -> SolverInput field -> future solver module usage
```

V0.3.0 should use the V0.2 fixture library as its stable test source.

---

## 7. Miro card

**Title:** V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases

**Status:** closed

**Purpose:** create a permanent, testable Clear_JSON fixture base for all future postflop solver modules.

**Implemented:** fixture docs, manifest schema, folder skeleton, 4 minimum Clear_JSON cases, 4 expected interpretation files, strict manifest/library tests, README/VERSION close.

**Final gate:** 62 passed.

**Next:** V0.3.0 — SolverInput Mapping / Field Usage Contract.
