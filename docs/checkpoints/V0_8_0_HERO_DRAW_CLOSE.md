# V0.8.0 Close — Hero Draw Classifier / Draw Features

## Status

**Version:** V0.8.0 — Hero Draw Classifier / Draw Features  
**Closing subversion:** V0.8.7 — Version Close / README / VERSION / Miro  
**Status:** closed  
**Final gate:** 297 passed  
**Next version:** V0.9.0 — Main Live Integration / Clear_JSON Capture / Full Module Audit

---

## Purpose

V0.8.0 created the HERO draw feature layer for the Clear_JSON-only postflop solver engine.

The closed chain is now:

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

The module answers one question only:

```text
What draw and improvement potential does HERO currently have on the flop?
```

It does **not** answer:

```text
What should HERO do?
```

It does **not** calculate equity, build ranges, create runtime plans, or click.

---

## Subversion history

### V0.8.1 — Hero Draw Contracts Baseline

Commit:

```text
87ab817 — V0.8.1 add hero draw contracts
```

Added:

- `solver_postflop/hero_draw_contracts.py`
- `tests/test_postflop_hero_draw_contracts_v080.py`

Updated:

- `solver_postflop/__init__.py`

Created contracts:

- `DrawFeatures`
- `DrawClass`
- `FlushDrawClass`
- `StraightDrawClass`
- `OvercardClass`
- `DrawStrengthTier`
- `ComboDrawClass`

Created stable contract metadata:

- `DRAW_CONTRACT_VERSION`
- `DRAW_CLASSES`
- `FLUSH_DRAW_CLASSES`
- `STRAIGHT_DRAW_CLASSES`
- `OVERCARD_CLASSES`
- `COMBO_DRAW_CLASSES`
- `DRAW_STRENGTH_TIERS`
- `DRAW_FUTURE_MODULES`

Gate:

```text
265 passed
```

---

### V0.8.2 — Hero Draw Classifier Baseline

Commit:

```text
05b4f4d — V0.8.2 add hero draw classifier baseline
```

Added:

- `solver_postflop/hero_draw.py`
- `tests/test_postflop_hero_draw_baseline_v080.py`

Updated:

- `solver_postflop/__init__.py`

Created public builder:

```text
build_draw_features(flop_context, board_texture_features, made_hand_features) -> DrawFeatures
```

The baseline classifier recognized:

- no draw
- backdoor flush draw
- standard flush draw
- nut flush draw candidate
- gutshot
- open-ended straight draw
- one overcard
- two overcards

Gate:

```text
276 passed
```

---

### V0.8.3 — Combo Draw / Draw Strength Matrix

Commit:

```text
2051e9a — V0.8.3 add hero draw combo strength matrix
```

Updated:

- `solver_postflop/hero_draw.py`
- `tests/test_postflop_hero_draw_baseline_v080.py`

Added:

- `tests/test_postflop_hero_draw_classifier_v080.py`

Expanded classifier output:

- `double_gutshot`
- `flush_plus_gutshot`
- `flush_plus_oesd`
- `pair_plus_flush_draw`
- `pair_plus_straight_draw`
- `pair_plus_combo_draw`
- `overcards_plus_draw`
- `premium_combo_draw`
- draw strength tier
- draw tags and aliases

Combo draw classes:

```text
no_combo_draw
flush_plus_gutshot
flush_plus_oesd
pair_plus_flush_draw
pair_plus_straight_draw
pair_plus_combo_draw
overcards_plus_draw
```

Draw strength tiers:

```text
no_draw
backdoor_only
weak_draw
medium_draw
strong_draw
premium_combo_draw
```

Gate:

```text
285 passed
```

---

### V0.8.4 — Fixture-backed Draw Cases

Commit:

```text
8dac329 — V0.8.4 add fixture-backed hero draw cases
```

Added thirteen synthetic Clear_JSON draw fixtures in:

```text
tests/fixtures/postflop_clear_json/synthetic/flop/
```

Fixture cases:

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

Added expected JSON files in:

```text
tests/fixtures/postflop_clear_json/expected/
```

Expected result fields:

- `expected_flush_draw_class`
- `expected_straight_draw_class`
- `expected_overcard_class`
- `expected_combo_draw_class`
- `expected_draw_strength_tier`
- `expected_draw_tags`
- `expected_draw_version = v0.8.4`

Updated:

- `tests/fixtures/postflop_clear_json/manifest.json`

Added:

- `tests/test_postflop_hero_draw_fixture_cases_v080.py`

Fixture-backed chain:

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

Gate:

```text
291 passed
```

---

### V0.8.5 — Hero Draw No-extra-logic Gate

Commit:

```text
762e729 — V0.8.5 add hero draw no-extra-logic gate
```

Added:

- `tests/test_postflop_hero_draw_no_extra_logic_v080.py`

The gate protects the module from expanding into the wrong layer.

It checks that `hero_draw.py` does not contain or perform:

- card validation
- duplicate card checks
- hero-board collision checks
- source discovery
- fallback to Dark/Pending/Service/Runtime JSON
- player filtering
- HERO creation
- active player creation
- equity logic
- PokerKit execution
- range logic
- decision logic
- runtime plan logic
- Action_Button logic
- click logic
- file/json IO

Read-only checks protect:

- Clear_JSON raw ref
- FlopContext
- BoardTextureFeatures
- MadeHandFeatures
- hero cards
- board cards
- players
- allowed actions

Gate:

```text
297 passed
```

---

### V0.8.6 — Hero Draw Documentation

Commit:

```text
41c3261 — V0.8.6 document hero draw classifier
```

Added:

- `docs/POSTFLOP_HERO_DRAW.md`

The documentation fixed:

- purpose/scope
- input contract
- output contract
- flush draw policy
- straight draw policy
- overcard policy
- combo draw policy
- draw strength tier policy
- draw tags
- fixture coverage
- no-extra-logic policy
- handoff to V0.9.0 live audit

Gate:

```text
297 passed
```

---

### V0.8.7 — Version Close / README / VERSION / Miro

Commit:

```text
V0.8.7 — close hero draw classifier
```

Updated:

- `README.md`
- `VERSION.md`

Added:

- `docs/checkpoints/V0_8_0_HERO_DRAW_CLOSE.md`

No code, tests, fixtures, contracts, classifier logic, runtime, or click-chain files were changed in this closing subversion.

Final gate:

```text
297 passed
```

---

## Final module output

`DrawFeatures` is now the stable V0.8 output object.

It contains:

- `case_id`
- `source_file`
- `hero_cards`
- `board_cards`
- `flush_draw_class`
- `straight_draw_class`
- `overcard_class`
- `combo_draw_class`
- `draw_strength_tier`
- `draw_tags`
- `features_used_by_future_modules`
- `notes`
- `raw_clear_json_ref`

---

## Final feature classes

### FlushDrawClass

```text
no_flush_draw
backdoor_flush_draw
weak_flush_draw
standard_flush_draw
nut_flush_draw_candidate
```

### StraightDrawClass

```text
no_straight_draw
gutshot
open_ended_straight_draw
double_gutshot
combo_straight_draw
```

### OvercardClass

```text
no_overcards
one_overcard
two_overcards
```

### ComboDrawClass

```text
no_combo_draw
flush_plus_gutshot
flush_plus_oesd
pair_plus_flush_draw
pair_plus_straight_draw
pair_plus_combo_draw
overcards_plus_draw
```

### DrawStrengthTier

```text
no_draw
backdoor_only
weak_draw
medium_draw
strong_draw
premium_combo_draw
```

---

## Final fixture coverage

V0.8.4 added thirteen draw fixtures:

```text
flop_draw_no_draw
flop_draw_backdoor_flush
flop_draw_standard_flush_draw
flop_draw_nut_flush_draw
flop_draw_gutshot
flop_draw_oesd
flop_draw_double_gutshot
flop_draw_two_overcards
flop_draw_fd_plus_gutshot
flop_draw_fd_plus_oesd
flop_draw_pair_plus_fd
flop_draw_pair_plus_straight_draw
flop_draw_premium_combo_draw
```

Each fixture is paired with expected JSON and manifest metadata.

The fixture gate verifies the full chain:

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

---

## Architecture boundaries preserved

V0.8.0 did **not** add:

- card validation
- duplicate-card detection
- hero-board collision checks
- source discovery
- temporary JSON fallback
- player filtering
- HERO creation
- active player creation
- equity calculation
- PokerKit execution
- range building
- poker decision logic
- runtime plan creation
- Action_Button calls
- click execution

The module remains a pure feature extraction layer.

---

## Final chain after V0.8.0

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

At this point the postflop solver understands:

- trusted Clear_JSON input
- solver input mapping
- branch routing
- flop context
- board texture
- HERO made hand
- HERO draw potential

It still does not make poker decisions.

---

## Handoff to V0.9.0

The next block is:

```text
V0.9.0 — Main Live Integration / Clear_JSON Capture / Full Module Audit
```

V0.9.0 should verify that the complete V0.1–V0.8 chain works on live Clear_JSON generated by the real project.

Planned V0.9 chain:

```text
main/live run
  -> live Clear_JSON capture
  -> ClearJsonInput
  -> SolverInput
  -> Branch Resolver
  -> FlopContext
  -> BoardTextureFeatures
  -> MadeHandFeatures
  -> DrawFeatures
  -> audit report
```

Important V0.9 boundary:

- existing project live click-chain may run to create correct Clear_JSON
- postflop solver must not create decisions
- postflop solver must not create runtime plans
- postflop solver must not call Action_Button
- postflop solver must not click

---

## Final close statement

V0.8.0 is closed with the final gate:

```text
297 passed
```

The project is ready for V0.9.0 live Clear_JSON integration/audit.
