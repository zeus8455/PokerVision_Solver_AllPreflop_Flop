# VERSION

Project: **PokerVision_Solver_AllPreflop_Flop**  
Development line: **Clear_JSON-only postflop solver engine**

---

## Current status

**Current closed version:** `V0.7.0 — Hero Hand Classifier / Made Hand Features`  
**Closing subversion:** `V0.7.7 — Version Close / README / VERSION / Miro`  
**Final gate:** `254 passed`  
**Next planned version:** `V0.8.0 — Hero Draw Classifier / Draw Features`

Current closed chain:

```text
Clear_JSON
  -> ClearJsonInput
  -> SolverInput
  -> Branch Resolver
  -> FlopContext
  -> BoardTextureFeatures
  -> MadeHandFeatures
```

---

## Baseline

### Initial repository baseline

- `db16abd` — `initial snapshot: Real_Version_SolverPreflop as AllPreflop_Flop baseline`

---

## V0.1.0 — Solver Engine Blueprint / Clear_JSON Input Contract

**Status:** closed  
**Closing checkpoint:** `00b6b7d — V0.1.5 close solver engine blueprint`

### Subversions

- `7fe5b4d` — `V0.1.1 add postflop engine contracts baseline`
- `1a4a2eb` — `V0.1.2 add Clear_JSON trusted input loader`
- `e80a582` — `V0.1.3 add SolverInput mapping baseline`
- `73163d9` — `V0.1.4 add postflop no-fallback architecture gate`
- `00b6b7d` — `V0.1.5 close solver engine blueprint`

### Final gate

```text
25 passed
```

### Final result

Created the baseline chain:

```text
Clear_JSON -> ClearJsonInput -> SolverInput -> SolverTrace
```

---

## V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases

**Status:** closed  
**Closing checkpoint:** `ee56990 — V0.2.6 close Clear_JSON fixture library`

### Subversions

- `c2fa1a8` — `V0.2.1 add Clear_JSON fixture library docs`
- `d648478` — `V0.2.2 add Clear_JSON fixture skeleton`
- `fa9c509` — `V0.2.3 add minimum Clear_JSON fixture cases`
- `0050a9f` — `V0.2.4 add expected Clear_JSON interpretations`
- `901aee5` — `V0.2.5 add Clear_JSON fixture manifest gate`
- `ee56990` — `V0.2.6 close Clear_JSON fixture library`

### Final gate

```text
62 passed
```

---

## V0.3.0 — SolverInput Mapping / Field Usage Contract

**Status:** closed  
**Closing checkpoint:** `4603c68 — V0.3.6 close SolverInput mapping contract`

### Subversions

- `66bd6a1` — `V0.3.1 add postflop field mapping contract`
- `00de073` — `V0.3.2 add postflop field usage trace`
- `99674e1` — `V0.3.3 bind SolverInput mapping to field contract`
- `cba0daa` — `V0.3.4 add postflop no-validation mapping gate`
- `7a3dfce` — `V0.3.5 document Clear_JSON field mapping`
- `4603c68` — `V0.3.6 close SolverInput mapping contract`

### Final gate

```text
94 passed
```

---

## V0.4.0 — Solver Branch Resolver / Street Module Routing

**Status:** closed  
**Closing checkpoint:** `6da8320 — V0.4.6 close branch resolver routing`

### Subversions

- `9fc9cee` — `V0.4.1 add postflop branch contracts`
- `54ac7c5` — `V0.4.2 add postflop branch resolver baseline`
- `21b087f` — `V0.4.3 add fixture-backed branch routing`
- `ab77eb1` — `V0.4.4 add branch resolver no-extra-checks gate`
- `209beb3` — `V0.4.5 document postflop branch resolver`
- `6da8320` — `V0.4.6 close branch resolver routing`

### Final gate

```text
125 passed
```

### Final result

Created the routing chain:

```text
SolverInput -> Branch Resolver -> SolverBranchResult
```

V0.4.0 maps board-card count to branch result:

```text
0 board cards        -> preflop_not_handled
3 board cards        -> flop
4 board cards        -> turn_not_implemented_yet
5 board cards        -> river_not_implemented_yet
missing / 1 / 2 / 6+ -> unsupported
```

This is a routing layer, not a validator or decision engine.

---

## V0.5.0 — Flop Context Builder / Spot Family Layer

**Status:** closed  
**Closing checkpoint:** `1d7154e — V0.5.7 close flop context builder`

### Subversions

- `a4a3567` — `V0.5.1 add flop context contracts`
- `5d10849` — `V0.5.2 add flop context builder baseline`
- `377832c` — `V0.5.3 add flop spot family classifier`
- `ed3504f` — `V0.5.4 add fixture-backed flop context`
- `0fed29c` — `V0.5.5 add flop context no-extra-logic gate`
- `aa33c9b` — `V0.5.6 document flop context builder`
- `1d7154e` — `V0.5.7 close flop context builder`

### Final gate

```text
163 passed
```

### Final result

Created the flop-context chain:

```text
SolverInput + SolverBranchResult -> FlopContext
```

V0.5.0 added:

- Flop context contracts
- Flop context builder baseline
- Spot family classifier
- Fixture-backed FlopContext test coverage
- No-extra-logic architecture gate
- FlopContext documentation

---

## V0.6.0 — Board Texture Feature Builder

**Status:** closed  
**Closing checkpoint:** `341657d — V0.6.7 close board texture builder`

### Subversions

- `d648100` — `V0.6.1 add board texture contracts`
- `19013a6` — `V0.6.2 add board texture builder baseline`
- `247738e` — `V0.6.3 add board texture classification matrix`
- `9b2729a` — `V0.6.4 add fixture-backed board texture cases`
- `89a3985` — `V0.6.5 add board texture no-extra-logic gate`
- `ed3ce55` — `V0.6.6 document board texture builder`
- `341657d` — `V0.6.7 close board texture builder`

### Final gate

```text
205 passed
```

### Final result

Created the board-texture feature chain:

```text
FlopContext -> BoardTextureFeatures
```

V0.6.0 added:

- Board texture contracts
- Board texture builder baseline
- Board texture classification matrix
- Fixture-backed board texture cases
- No-extra-logic architecture gate
- Board texture documentation
- V0.6 close checkpoint

---

## V0.7.0 — Hero Hand Classifier / Made Hand Features

**Status:** closed by V0.7.7  
**Closing checkpoint:** created by commit `V0.7.7 close hero made hand classifier`

### Subversions

- `2001c6e` — `V0.7.1 add hero made hand contracts`
- `2f7ecdc` — `V0.7.2 add hero made hand classifier baseline`
- `2142871` — `V0.7.3 add hero made hand pair strength matrix`
- `a650eb8` — `V0.7.4 add fixture-backed hero made hand cases`
- `daa1923` — `V0.7.5 add hero made hand no-extra-logic gate`
- `adb6b14` — `V0.7.6 document hero made hand classifier`
- `V0.7.7` — `close hero made hand classifier`

### Final gate

```text
254 passed
```

### Final result

Created the HERO made-hand feature chain:

```text
FlopContext + BoardTextureFeatures -> MadeHandFeatures
```

V0.7.0 added:

- Hero made-hand contracts
- Hero made-hand classifier baseline
- Pair class / strength tier matrix
- Fixture-backed made-hand coverage
- No-extra-logic architecture gate
- Hero made-hand documentation
- V0.7 close checkpoint

### Main output contract

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

### Made hand classes

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

### Pair classes

```text
top_pair
middle_pair
bottom_pair
overpair
underpair
pocket_pair_below_board
no_pair_class
```

### Strength tiers

```text
air
weak_showdown
medium_showdown
strong_showdown
value_hand
very_strong_value
nut_or_near_nut
```

### Architecture boundaries

V0.7.0 does not validate cards, find duplicate cards, check hero-board collisions, filter players, create HERO, calculate draws, calculate equity, build ranges, make decisions, create runtime plans, or click.

---

## Next version

## V0.8.0 — Hero Draw Classifier / Draw Features

**Status:** planned

Planned chain:

```text
FlopContext + BoardTextureFeatures + MadeHandFeatures -> DrawFeatures
```

V0.8.0 will classify HERO draw potential only:

- flush draw
- backdoor flush draw
- straight draw
- gutshot
- open-ended straight draw
- double gutshot
- overcards
- combo draw
- draw strength tier

V0.8.0 will not calculate equity, build ranges, make decisions, create runtime plans, call Action_Button, or click.
