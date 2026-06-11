# PokerVision Solver AllPreflop Flop

Current development line: **Clear_JSON-only postflop solver engine**.

This repository is maintained as a staged solver-development project. Each version/subversion is discussed first, implemented only after explicit approval, delivered as a ZIP overlay, checked with targeted pytest gates, committed, pushed, and documented for Miro.

---

## Current status

**Current closed version:** `V0.6.0 — Board Texture Feature Builder`  
**Closing subversion:** `V0.6.7 — Version Close / README / VERSION / Miro`  
**Final V0.6 gate:** `205 passed`  
**Next planned version:** `V0.7.0 — Hero Hand Classifier / Made Hand Features`

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
Checkpoint commit: `6da8320`

Created the first routing layer:

```text
SolverInput -> Branch Resolver -> SolverBranchResult
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

### V0.5.0 — Flop Context Builder / Spot Family Layer

Closed by: `V0.5.7`  
Checkpoint commit: `1d7154e`

Created the first specialized flop context layer:

```text
SolverInput + SolverBranchResult -> FlopContext
```

Key files:

- `solver_postflop/flop_context_contracts.py`
- `solver_postflop/flop_context.py`
- `docs/POSTFLOP_FLOP_CONTEXT.md`
- `docs/checkpoints/V0_5_0_FLOP_CONTEXT_CLOSE.md`

FlopContext captures:

- metadata context: case/source/table/hand/branch
- cards context: `hero_cards`, `board_cards`
- pot context: `pot`, `to_call`, optional effective-stack / SPR data if provided
- player context: players, heads-up / multiway metadata without refiltering
- action context: allowed actions and ready action context without repair
- spot family: SRP, 3bet, 4bet/low-SPR, limp/passive, multiway, unknown

Spot families:

- `srp_heads_up`
- `threebet_pot_heads_up`
- `fourbet_low_spr`
- `limp_or_passive_pot`
- `multiway_pot`
- `unknown_flop_spot`

Final V0.5 gate:

```text
163 passed
```

---

### V0.6.0 — Board Texture Feature Builder

Closed by: `V0.6.7`  
Checkpoint commit: created by commit `V0.6.7 close board texture builder`

Created the first analytical board-texture feature layer:

```text
FlopContext -> BoardTextureFeatures
```

Key files:

- `solver_postflop/board_texture_contracts.py`
- `solver_postflop/board_texture.py`
- `docs/POSTFLOP_BOARD_TEXTURE.md`
- `docs/checkpoints/V0_6_0_BOARD_TEXTURE_CLOSE.md`

BoardTextureFeatures captures:

- suit texture: `rainbow`, `two_tone`, `monotone`
- paired texture: `unpaired`, `paired`, `trips_board`
- rank texture: `ace_high`, `king_high`, `broadway_heavy`, `middle_connected`, `low_connected`, `low_static`
- connection texture: `disconnected`, `semi_connected`, `connected`, `highly_connected`
- volatility class: `static_board`, `semi_dynamic_board`, `dynamic_board`
- texture tags: stable labels such as `ace_high_dry_rainbow`, `king_high_two_tone`, `monotone_broadway`, `low_connected_dynamic`, `paired_dry`, `very_wet_connected`

V0.6.0 added eight synthetic board-texture Clear_JSON fixtures and fixture-backed texture tests:

- `flop_texture_ace_high_dry_rainbow`
- `flop_texture_king_high_two_tone`
- `flop_texture_monotone_broadway`
- `flop_texture_low_connected`
- `flop_texture_middle_connected_two_tone`
- `flop_texture_paired_dry`
- `flop_texture_paired_dynamic`
- `flop_texture_very_wet_connected`

Final V0.6 gate:

```text
205 passed
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
  -> FlopContext
  -> BoardTextureFeatures
```

The project now routes ready Clear_JSON into a flop context layer and extracts board texture features. It still does **not** make poker decisions.

---

## Current test gate

Run the current full V0.1 + V0.2 + V0.3 + V0.4 + V0.5 + V0.6 gate:

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
  tests/test_postflop_flop_context_contracts_v050.py `
  tests/test_postflop_flop_context_builder_v050.py `
  tests/test_postflop_flop_spot_family_v050.py `
  tests/test_postflop_flop_context_fixture_routing_v050.py `
  tests/test_postflop_flop_context_no_extra_logic_v050.py `
  tests/test_postflop_board_texture_contracts_v060.py `
  tests/test_postflop_board_texture_builder_v060.py `
  tests/test_postflop_board_texture_from_flop_context_v060.py `
  tests/test_postflop_board_texture_classification_matrix_v060.py `
  tests/test_postflop_board_texture_fixture_cases_v060.py `
  tests/test_postflop_board_texture_no_extra_logic_v060.py `
  -q
```

Expected result:

```text
205 passed
```

---

## Next planned block

### V0.7.0 — Hero Hand Classifier / Made Hand Features

Target chain:

```text
Clear_JSON -> SolverInput -> Branch Resolver -> FlopContext -> BoardTextureFeatures -> MadeHandFeatures
```

V0.7.0 will classify HERO made-hand features for future solver modules. It will still not make poker decisions, compute equity, build ranges, create runtime plans, or interact with click-chain.
