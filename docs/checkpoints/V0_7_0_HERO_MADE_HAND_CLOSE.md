# V0.7.0 Close — Hero Hand Classifier / Made Hand Features

## Status

**Version:** V0.7.0 — Hero Hand Classifier / Made Hand Features  
**Closing subversion:** V0.7.7 — Version Close / README / VERSION / Miro  
**Status:** closed  
**Final gate:** 254 passed  
**Next version:** V0.8.0 — Hero Draw Classifier / Draw Features

---

## Purpose

V0.7.0 created the HERO made-hand feature layer for the Clear_JSON-only postflop solver engine.

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
```

The module answers one question only:

```text
What made hand does HERO currently have on the flop?
```

It does **not** answer:

```text
What should HERO do?
```

---

## Subversion history

### V0.7.1 — Hero Made Hand Contracts Baseline

Commit:

```text
2001c6e — V0.7.1 add hero made hand contracts
```

Added:

- `solver_postflop/hero_made_hand_contracts.py`
- `tests/test_postflop_hero_made_hand_contracts_v070.py`

Updated:

- `solver_postflop/__init__.py`

Created contracts:

- `MadeHandFeatures`
- `MadeHandClass`
- `PairClass`
- `ShowdownValueClass`
- `MadeHandStrengthTier`

Created stable contract metadata:

- `MADE_HAND_CONTRACT_VERSION`
- `MADE_HAND_CLASSES`
- `PAIR_CLASSES`
- `SHOWDOWN_VALUE_CLASSES`
- `MADE_HAND_STRENGTH_TIERS`
- `MADE_HAND_FUTURE_MODULES`

Gate:

```text
214 passed
```

---

### V0.7.2 — Hero Made Hand Classifier Baseline

Commit:

```text
2f7ecdc — V0.7.2 add hero made hand classifier baseline
```

Added:

- `solver_postflop/hero_made_hand.py`
- `tests/test_postflop_hero_made_hand_baseline_v070.py`

Updated:

- `solver_postflop/__init__.py`

Created public builder:

```text
build_made_hand_features(flop_context, board_texture_features) -> MadeHandFeatures
```

The baseline classifier recognized:

- `high_card`
- `one_pair`
- `two_pair`
- `three_of_a_kind`
- `straight`
- `flush`
- `full_house`
- `quads`

Gate:

```text
226 passed
```

---

### V0.7.3 — Pair Class / Strength Tier Matrix

Commit:

```text
2142871 — V0.7.3 add hero made hand pair strength matrix
```

Updated:

- `solver_postflop/hero_made_hand.py`
- `tests/test_postflop_hero_made_hand_baseline_v070.py`

Added:

- `tests/test_postflop_hero_made_hand_classifier_v070.py`

Expanded classifier output:

- `pair_class`
- `strength_tier`
- `showdown_value_class`
- `kicker_relevance`
- `board_interaction_tags`

Pair classifications:

```text
top_pair
middle_pair
bottom_pair
overpair
underpair
pocket_pair_below_board
no_pair_class
```

Strength tiers:

```text
air
weak_showdown
medium_showdown
strong_showdown
value_hand
very_strong_value
nut_or_near_nut
```

Gate:

```text
242 passed
```

---

### V0.7.4 — Fixture-backed Made Hand Cases

Commit:

```text
a650eb8 — V0.7.4 add fixture-backed hero made hand cases
```

Added thirteen synthetic Clear_JSON made-hand fixtures in:

```text
tests/fixtures/postflop_clear_json/synthetic/flop/
```

Fixture cases:

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

Added expected JSON files in:

```text
tests/fixtures/postflop_clear_json/expected/
```

Expected fields:

- `expected_made_hand_class`
- `expected_pair_class`
- `expected_strength_tier`
- `expected_kicker_relevance`
- `expected_board_interaction_tags`
- `expected_made_hand_version = v0.7.4`

Updated:

- `tests/fixtures/postflop_clear_json/manifest.json`

Added:

- `tests/test_postflop_hero_made_hand_fixture_cases_v070.py`

Fixture-backed pipeline:

```text
Clear_JSON fixture
  -> ClearJsonInput
  -> SolverInput
  -> Branch Resolver
  -> FlopContext
  -> BoardTextureFeatures
  -> MadeHandFeatures
```

Gate:

```text
248 passed
```

---

### V0.7.5 — Hero Made Hand No-extra-logic Gate

Commit:

```text
daa1923 — V0.7.5 add hero made hand no-extra-logic gate
```

Added:

- `tests/test_postflop_hero_made_hand_no_extra_logic_v070.py`

The gate protects Hero Made Hand from expanding into unrelated modules:

- no card validation
- no duplicate-card checking
- no hero-board collision checking
- no source discovery
- no fallback to Dark/Pending/Service/Runtime JSON
- no player filtering
- no HERO creation
- no active-player creation
- no draw classifier
- no equity logic
- no range logic
- no decision logic
- no runtime-plan logic
- no click-chain logic
- no file / JSON IO inside `hero_made_hand.py`

Read-only protected inputs:

- Clear_JSON raw ref
- FlopContext
- BoardTextureFeatures
- hero_cards
- board_cards
- players
- allowed_actions

Gate:

```text
254 passed
```

---

### V0.7.6 — Hero Made Hand Documentation

Commit:

```text
adb6b14 — V0.7.6 document hero made hand classifier
```

Added:

- `docs/POSTFLOP_HERO_MADE_HAND.md`

Documented:

- role of `MadeHandFeatures`
- chain `Clear_JSON -> SolverInput -> Branch Resolver -> FlopContext -> BoardTextureFeatures -> MadeHandFeatures`
- input contract
- output contract
- `MadeHandClass` policy
- `PairClass` policy
- `ShowdownValueClass` / `MadeHandStrengthTier` policy
- kicker relevance policy
- board interaction tags
- V0.7.4 fixture coverage
- V0.7.5 no-extra-logic policy
- handoff to V0.8.0 Hero Draw Classifier

Gate:

```text
254 passed
```

---

### V0.7.7 — Version Close / README / VERSION / Miro

Commit:

```text
V0.7.7 close hero made hand classifier
```

Updates:

- `README.md`
- `VERSION.md`
- `docs/checkpoints/V0_7_0_HERO_MADE_HAND_CLOSE.md`

Expected final gate:

```text
254 passed
```

---

## Final V0.7.0 result

V0.7.0 closes the HERO made-hand feature layer:

```text
FlopContext + BoardTextureFeatures -> MadeHandFeatures
```

The solver now understands:

- board texture from V0.6.0
- HERO made-hand class
- pair class
- showdown value class
- strength tier
- kicker relevance
- board interaction tags

This is still feature extraction only.

The module does not make a poker decision and does not interact with runtime/click logic.

---

## MadeHandFeatures output

`MadeHandFeatures` contains:

- `case_id`
- `source_file`
- `hero_cards`
- `board_cards`
- `made_hand_class`
- `pair_class`
- `showdown_value_class`
- `strength_tier`
- `kicker_relevance`
- `board_interaction_tags`
- `features_used_by_future_modules`
- `notes`

---

## Made hand classes

```text
high_card
one_pair
two_pair
three_of_a_kind
straight
flush
full_house
quads
```

### Scope note

The classifier uses trusted Clear_JSON cards as already prepared input. It does not validate or repair cards.

---

## Pair classes

```text
top_pair
middle_pair
bottom_pair
overpair
underpair
pocket_pair_below_board
no_pair_class
```

### Pair-class purpose

Pair-class metadata is intended for future modules such as:

- value betting
- bluff catching
- pot control
- protection betting
- thin value selection
- defensive call/fold thresholds

V0.7.0 does not implement those modules.

---

## Strength tiers

```text
air
weak_showdown
medium_showdown
strong_showdown
value_hand
very_strong_value
nut_or_near_nut
```

### Strength-tier purpose

Strength tier is a coarse made-hand feature for future decision logic.

It is not a final action recommendation.

---

## Board interaction tags

Examples of tags used by the classifier include:

- `top_pair_good_kicker_candidate`
- `overpair_candidate`
- `set_candidate`
- `trips_candidate`
- `board_paired_hand`
- `strong_made_hand`
- `nut_or_near_nut_candidate`

These tags are intentionally descriptive and are meant to support later modules:

- Draw classifier
- Equity input builder
- Range interaction modules
- Decision engine

---

## Architecture boundaries

V0.7.0 does **not**:

- validate cards
- search duplicate cards
- check hero-board collision
- read temporary JSON as solver input
- fallback to Dark/Pending/Service/Runtime JSON
- filter players again
- create HERO
- create active player
- calculate draws
- calculate equity
- build ranges
- make poker decisions
- create runtime plans
- call Action_Button detector
- click

---

## Read-only discipline

V0.7.0 treats all upstream data as read-only:

- Clear_JSON raw ref
- SolverInput
- FlopContext
- BoardTextureFeatures
- hero_cards
- board_cards
- players
- allowed_actions

`MadeHandFeatures` is a derived feature object only.

---

## Handoff to V0.8.0

Next version:

```text
V0.8.0 — Hero Draw Classifier / Draw Features
```

V0.8.0 will extend the chain:

```text
Clear_JSON
  -> ClearJsonInput
  -> SolverInput
  -> Branch Resolver
  -> FlopContext
  -> BoardTextureFeatures
  -> MadeHandFeatures
  -> DrawFeatures
```

V0.8.0 should classify draw potential only:

- flush draw
- backdoor flush draw
- straight draw
- gutshot
- open-ended straight draw
- double gutshot
- overcards
- combo draw
- draw strength tier

It must preserve the same no-decision, no-runtime, no-click discipline.
