# POSTFLOP HERO MADE HAND CLASSIFIER

## Version block

**Version:** V0.7.0 — Hero Hand Classifier / Made Hand Features  
**Documentation checkpoint:** V0.7.6  
**Module scope:** `FlopContext + BoardTextureFeatures -> MadeHandFeatures`  
**Current status:** documentation-only checkpoint

---

## Purpose

The Hero Made Hand Classifier is the second analytical feature layer in the postflop solver pipeline.

It receives an already-built `FlopContext` and the already-built `BoardTextureFeatures`, then creates a structured `MadeHandFeatures` object that describes HERO's current made hand on the flop.

Pipeline position:

```text
Clear_JSON
  -> ClearJsonInput
  -> SolverInput
  -> Branch Resolver
  -> FlopContext
  -> BoardTextureFeatures
  -> MadeHandFeatures
```

The module answers these questions:

> What made hand does HERO currently have?

> How strong is that made hand as a future strategy feature?

> How does the made hand interact with the board texture?

It does **not** answer:

> What should HERO do?

It also does **not** compute draws, equity, ranges, bet sizing, runtime plans, button sequences, or clicks.

---

## Architectural policy

V0.7.0 treats `Clear_JSON`, `SolverInput`, `FlopContext`, and `BoardTextureFeatures` as trusted upstream inputs.

The Hero Made Hand Classifier must stay a made-hand feature extractor. It must not become a validator, draw classifier, equity engine, range engine, decision engine, runtime planner, or click module.

### The module may use

- `FlopContext.case_id`
- `FlopContext.source_file`
- `FlopContext.hero_cards`
- `FlopContext.board_cards`
- `FlopContext.raw_clear_json_ref` as read-only reference
- `BoardTextureFeatures` as already-built board context
- rank and suit parsing needed to classify visible HERO/board made-hand strength

### The module must preserve

- original `hero_cards`
- original `board_cards`
- original `players`
- original `allowed_actions`
- original `raw_clear_json_ref`
- original `FlopContext`
- original `BoardTextureFeatures`

The module must not repair, validate, normalize, or re-source these values.

---

## Input contract

Primary inputs:

```python
FlopContext
BoardTextureFeatures
```

The public builder function is:

```python
build_made_hand_features(flop_context, board_texture_features) -> MadeHandFeatures
```

The input is expected to come from the existing trusted chain:

```text
Clear_JSON -> ClearJsonInput -> SolverInput -> Branch Resolver -> FlopContext -> BoardTextureFeatures
```

The Hero Made Hand Classifier does not search for files, does not inspect temporary runtime folders, and does not fallback to Dark/Pending/Service/Runtime JSON.

---

## Output contract

Primary result:

```python
MadeHandFeatures
```

Expected high-level fields:

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

The result must be serializable to JSON and safe to store in trace/report artifacts later.

The result is feature metadata only. It must not contain draw classes, equity values, range assignments, decisions, runtime plans, button sequences, or click results.

---

## MadeHandClass policy

`MadeHandClass` is the primary ready-hand label.

### `high_card`

HERO has no completed pair-or-better made hand with the visible board.

Future usage:

- air / low-showdown handling
- bluff and give-up candidate separation later
- draw module handoff in V0.8.0

### `one_pair`

HERO has exactly one pair using HERO cards and the board.

Future usage:

- pair-class matrix
- bluff-catch classification
- pot-control logic later
- protection/value thresholds later

### `two_pair`

HERO has two pair using HERO cards and the board.

Future usage:

- value-hand candidate
- vulnerable value logic on dynamic boards later
- board-pair interaction awareness later

### `three_of_a_kind`

HERO has trips or set-level three of a kind.

The detailed hand shape is expressed through `board_interaction_tags`, especially:

- `set_candidate`
- `trips_candidate`
- `three_of_a_kind_candidate`

Future usage:

- strong value categorization
- board-paired sensitivity
- later range interaction and bet sizing policy

### `straight`

HERO has a completed straight.

Future usage:

- very strong value bucket
- nut / near-nut candidate analysis later
- blocker and board-runout sensitivity later

### `flush`

HERO has a completed flush.

Future usage:

- very strong value bucket
- monotone / two-tone board context
- nut-candidate and blocker policy later

### `full_house`

HERO has a completed full house.

Future usage:

- nut-or-near-nut bucket
- board-paired special handling later
- stack-off / value extraction policy later

### `quads`

HERO has four of a kind.

Future usage:

- nut-or-near-nut bucket
- board-lock and maximum-value policy later

---

## PairClass policy

`PairClass` refines `one_pair` hands into future strategy-relevant groups.

### `top_pair`

HERO pairs the highest board rank.

Example pattern:

```text
Hero: Ah Qh
Board: As 7d 2c
```

Future usage:

- strong showdown bucket
- value/protection candidate later
- kicker relevance matters

### `second_pair` / `middle_pair`

HERO pairs a middle board rank.

Example pattern:

```text
Hero: 8h Qh
Board: As 8d 2c
```

Future usage:

- medium showdown bucket
- pot control and bluff-catch logic later
- board texture sensitivity later

### `bottom_pair`

HERO pairs the lowest board rank.

Example pattern:

```text
Hero: 2h Qh
Board: As 8d 2c
```

Future usage:

- weak showdown bucket
- protection / bluff-catch separation later
- vulnerable pair handling

### `overpair`

HERO has a pocket pair above the highest board card.

Example pattern:

```text
Hero: Kh Kd
Board: Qs 7d 2c
```

Future usage:

- strong showdown bucket
- value/protection candidate later
- stack-depth and texture-dependent policy later

### `underpair`

HERO has a pocket pair below the lowest board card.

Example pattern:

```text
Hero: 3h 3d
Board: As 8d 5c
```

Future usage:

- weak showdown bucket
- bluff-catch / give-up candidate later
- range/equity context later

### `pocket_pair_below_board`

HERO has a pocket pair that is not an overpair and is classified as a below-board pocket-pair hand shape.

Future usage:

- weak or medium showdown separation later
- board texture and action pressure sensitivity later

### `no_pair_class`

Used when pair-specific classification does not apply.

Examples:

- high card
- two pair
- straight
- flush
- full house
- quads
- unsupported/unknown pair shape

---

## ShowdownValueClass policy

`ShowdownValueClass` is a coarse future-strategy bucket.

Current V0.7.0 buckets:

- `air`
- `weak_showdown`
- `medium_showdown`
- `strong_showdown`
- `value_hand`
- `unknown`

This field is intentionally coarse. It is not a final poker decision.

Future usage:

- separating air / bluff candidates from showdown hands
- thin value and bluff-catch selection later
- equity/range handoff later

---

## MadeHandStrengthTier policy

`MadeHandStrengthTier` is the main strength abstraction used by later modules.

Current V0.7.0 tiers:

- `air`
- `weak_showdown`
- `medium_showdown`
- `strong_showdown`
- `value_hand`
- `very_strong_value`
- `nut_or_near_nut`
- `unknown`

### Tier mapping intent

`high_card` usually maps to:

```text
air
```

Weak one-pair classes usually map to:

```text
weak_showdown
```

Middle/second pair usually maps to:

```text
medium_showdown
```

Top pair and overpair usually map to:

```text
strong_showdown
```

Two pair and three of a kind usually map to:

```text
value_hand
```

Straight and flush usually map to:

```text
very_strong_value
```

Full house and quads usually map to:

```text
nut_or_near_nut
```

These labels are feature tiers. They are not betting instructions.

---

## Kicker relevance policy

`kicker_relevance` marks whether kicker quality may matter for future strategy.

Current values used by the classifier:

- `not_relevant`
- `low`
- `medium`
- `high`
- `not_evaluated`

Typical examples:

- high card: `low`
- top pair with broadway kicker: `high`
- top pair with weaker kicker: `medium` or `low`
- overpair / underpair / pocket-pair-only class: `not_relevant`
- trips/straight/flush/full house/quads: `not_relevant`

The module does not turn kicker relevance into a poker action.

---

## Board interaction tags

`board_interaction_tags` are lightweight metadata tags for downstream strategy modules.

Examples:

- `high_card`
- `one_pair`
- `top_pair`
- `top_pair_good_kicker_candidate`
- `top_pair_candidate`
- `overpair_candidate`
- `set_candidate`
- `trips_candidate`
- `three_of_a_kind_candidate`
- `strong_made_hand`
- `nut_or_near_nut_candidate`
- `board_unpaired`
- `board_paired`
- `board_trips_board`
- `board_rainbow`
- `board_two_tone`
- `board_monotone`

These tags are deliberately non-executable. They are not actions and not runtime instructions.

Future usage:

- value threshold selection
- bluff-catch candidate filtering
- protection logic
- equity/range interaction
- turn/river barrel planning

---

## Fixture coverage

V0.7.4 added fixture-backed made-hand coverage.

Synthetic Clear_JSON flop cases include:

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

Each expected JSON file stores:

- `expected_made_hand_class`
- `expected_pair_class`
- `expected_strength_tier`
- `expected_kicker_relevance`
- `expected_board_interaction_tags`
- `expected_made_hand_version`

The fixture pipeline validates this chain:

```text
Clear_JSON fixture
  -> ClearJsonInput
  -> SolverInput
  -> Branch Resolver
  -> FlopContext
  -> BoardTextureFeatures
  -> MadeHandFeatures
```

---

## No-extra-logic policy

V0.7.5 added an architecture gate for the Hero Made Hand Classifier.

The module must not contain:

- card validation logic
- duplicate-card checks
- hero-board collision checks
- dirty-source checks
- source discovery
- fallback to Dark/Pending/Service/Runtime JSON
- file or JSON IO
- player filtering
- HERO creation
- active-player creation
- draw classifier logic
- equity logic
- range logic
- decision logic
- runtime-plan logic
- Action_Button logic
- mouse/click logic

The module must also preserve read-only inputs:

- `Clear_JSON raw ref`
- `FlopContext`
- `BoardTextureFeatures`
- `hero_cards`
- `board_cards`
- `players`
- `allowed_actions`

---

## Notes on trusted input

This module assumes that upstream project layers already produced a trusted `Clear_JSON` representation.

Therefore, V0.7.0 intentionally does not ask:

- Are the cards valid?
- Are there duplicate cards?
- Does HERO collide with board cards?
- Should players be filtered again?
- Is HERO correctly created?
- Which temporary source JSON should be used?

Those questions belong outside this layer.

V0.7.0 asks only:

> Given this trusted `FlopContext` and `BoardTextureFeatures`, what made-hand features describe HERO's visible flop hand?

---

## Handoff to V0.8.0

V0.8.0 should build the next feature layer:

```text
FlopContext + BoardTextureFeatures + MadeHandFeatures -> DrawFeatures
```

V0.8.0 should classify:

- no draw
- backdoor flush draw
- standard flush draw
- nut flush draw candidate
- gutshot
- open-ended straight draw
- double gutshot
- overcards
- combo draw
- pair plus draw
- premium combo draw

V0.8.0 must preserve the same discipline:

- no equity
- no ranges
- no decision
- no runtime plan
- no clicks
- no dirty-source validation
- no duplicate PokerVision filtering

---

## Stable chain after V0.7.0

After V0.7.0 is fully closed, the postflop solver feature chain should be:

```text
Clear_JSON
  -> ClearJsonInput
  -> SolverInput
  -> Branch Resolver
  -> FlopContext
  -> BoardTextureFeatures
  -> MadeHandFeatures
```

This prepares the solver for V0.8.0:

```text
MadeHandFeatures -> DrawFeatures
```
