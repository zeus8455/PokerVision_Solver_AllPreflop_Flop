# PokerVision Solver AllPreflop Flop

Current development line: **Clear_JSON-only postflop solver engine**.

This repository is maintained as a staged solver-development project. Each version/subversion is discussed first, implemented only after explicit approval, delivered as a ZIP overlay, checked with targeted pytest gates, committed, pushed, and documented for Miro.

---

## Current status

**Current closed version:** `V0.8.0 — Hero Draw Classifier / Draw Features`  
**Closing subversion:** `V0.8.7 — Version Close / README / VERSION / Miro`  
**Final V0.8 gate:** `297 passed`  
**Next planned version:** `V0.9.0 — Main Live Integration / Clear_JSON Capture / Full Module Audit`

The current closed postflop analysis chain is:

```text
Clear_JSON
  -> ClearJsonInput
  -> SolverInput
  -> Branch Resolver
  -> SolverBranchResult
  -> FlopContext
  -> BoardTextureFeatures
  -> MadeHandFeatures
  -> DrawFeatures
```

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

Final V0.1 gate:

```text
25 passed
```

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
Checkpoint commit: `341657d`

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

V0.6.0 added eight synthetic board-texture Clear_JSON fixtures and fixture-backed texture tests.

Final V0.6 gate:

```text
205 passed
```

---

### V0.7.0 — Hero Hand Classifier / Made Hand Features

Closed by: `V0.7.7`  
Checkpoint commit: `67e0183`

Created the HERO made-hand feature layer:

```text
FlopContext + BoardTextureFeatures -> MadeHandFeatures
```

Key files:

- `solver_postflop/hero_made_hand_contracts.py`
- `solver_postflop/hero_made_hand.py`
- `docs/POSTFLOP_HERO_MADE_HAND.md`
- `docs/checkpoints/V0_7_0_HERO_MADE_HAND_CLOSE.md`

MadeHandFeatures captures:

- HERO cards and board cards copied from `FlopContext`
- made-hand class: `high_card`, `one_pair`, `two_pair`, `three_of_a_kind`, `straight`, `flush`, `full_house`, `quads`
- pair class: `top_pair`, `middle_pair`, `bottom_pair`, `overpair`, `underpair`, `pocket_pair_below_board`, `no_pair_class`
- showdown value class
- strength tier: `air`, `weak_showdown`, `medium_showdown`, `strong_showdown`, `value_hand`, `very_strong_value`, `nut_or_near_nut`
- kicker relevance
- board interaction tags
- future-module usage metadata
- notes

V0.7.0 added thirteen synthetic made-hand Clear_JSON fixtures:

- `flop_made_hand_high_card`
- `flop_made_hand_top_pair_good_kicker`
- `flop_made_hand_middle_pair`
- `flop_made_hand_bottom_pair`
- `flop_made_hand_overpair`
- `flop_made_hand_underpair`
- `flop_made_hand_two_pair`
- `flop_made_hand_set`
- `flop_made_hand_trips`
- `flop_made_hand_straight`
- `flop_made_hand_flush`
- `flop_made_hand_full_house`
- `flop_made_hand_quads`

The fixture-backed pipeline is:

```text
Clear_JSON fixture
  -> ClearJsonInput
  -> SolverInput
  -> Branch Resolver
  -> FlopContext
  -> BoardTextureFeatures
  -> MadeHandFeatures
```

Final V0.7 gate:

```text
254 passed
```

---


### V0.8.0 — Hero Draw Classifier / Draw Features

Closed by: `V0.8.7`  
Checkpoint commit: created by commit `V0.8.7 close hero draw classifier`

Created the HERO draw feature layer:

```text
FlopContext + BoardTextureFeatures + MadeHandFeatures -> DrawFeatures
```

Key files:

- `solver_postflop/hero_draw_contracts.py`
- `solver_postflop/hero_draw.py`
- `docs/POSTFLOP_HERO_DRAW.md`
- `docs/checkpoints/V0_8_0_HERO_DRAW_CLOSE.md`

DrawFeatures captures:

- HERO cards and board cards copied from `FlopContext`
- flush draw class: `no_flush_draw`, `backdoor_flush_draw`, `weak_flush_draw`, `standard_flush_draw`, `nut_flush_draw_candidate`
- straight draw class: `no_straight_draw`, `gutshot`, `open_ended_straight_draw`, `double_gutshot`, `combo_straight_draw`
- overcard class: `no_overcards`, `one_overcard`, `two_overcards`
- combo draw class: `no_combo_draw`, `flush_plus_gutshot`, `flush_plus_oesd`, `pair_plus_flush_draw`, `pair_plus_straight_draw`, `pair_plus_combo_draw`, `overcards_plus_draw`
- draw strength tier: `no_draw`, `backdoor_only`, `weak_draw`, `medium_draw`, `strong_draw`, `premium_combo_draw`
- draw tags
- future-module usage metadata
- notes

V0.8.0 added thirteen synthetic draw Clear_JSON fixtures:

- `flop_draw_no_draw`
- `flop_draw_backdoor_flush`
- `flop_draw_standard_flush_draw`
- `flop_draw_nut_flush_draw`
- `flop_draw_gutshot`
- `flop_draw_oesd`
- `flop_draw_double_gutshot`
- `flop_draw_two_overcards`
- `flop_draw_fd_plus_gutshot`
- `flop_draw_fd_plus_oesd`
- `flop_draw_pair_plus_fd`
- `flop_draw_pair_plus_straight_draw`
- `flop_draw_premium_combo_draw`

The fixture-backed pipeline is:

```text
Clear_JSON fixture
  -> ClearJsonInput
  -> SolverInput
  -> Branch Resolver
  -> FlopContext
  -> BoardTextureFeatures
  -> MadeHandFeatures
  -> DrawFeatures
```

Final V0.8 gate:

```text
297 passed
```

---

## Active architecture policy

The current solver line remains strictly Clear_JSON-only.

The postflop solver modules do **not**:

- search or read Dark/Pending/Service/Runtime JSON as solver input
- validate cards
- detect duplicate cards
- check hero-board collisions
- repair board cards
- filter players again
- create HERO
- create active player
- reconstruct preflop history from temporary runtime sources
- compute equity
- build ranges
- create poker decisions
- create runtime plans
- call Action_Button detector
- click

Each layer must preserve upstream objects as read-only input and produce narrow feature contracts for later modules.

---

## Next planned version

### V0.9.0 — Main Live Integration / Clear_JSON Capture / Full Module Audit

Planned audit chain:

```text
live/main cycle
  -> Clear_JSON capture
  -> ClearJsonInput
  -> SolverInput
  -> Branch Resolver
  -> FlopContext
  -> BoardTextureFeatures
  -> MadeHandFeatures
  -> DrawFeatures
  -> module audit report
```

V0.9.0 will verify that the fixture-proven modules also work on real live Clear_JSON created by the project.

Important boundaries:

- existing project live click-chain may run as part of the real capture cycle
- postflop solver does not create poker decisions
- postflop solver does not create runtime plans
- postflop solver does not call Action_Button
- postflop solver does not click
- solver input remains Clear_JSON only

V0.9.0 is an integration/audit block, not an equity/range/decision block.
