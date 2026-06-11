# VERSION

Project: **PokerVision_Solver_AllPreflop_Flop**  
Development line: **Clear_JSON-only postflop solver engine**

---

## Current status

**Current closed version:** `V0.6.0 — Board Texture Feature Builder`  
**Closing subversion:** `V0.6.7 — Version Close / README / VERSION / Miro`  
**Final gate:** `205 passed`  
**Next planned version:** `V0.7.0 — Hero Hand Classifier / Made Hand Features`

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

This is a **routing layer**, not a validator or decision engine.

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

Flop spot families:

```text
srp_heads_up
threebet_pot_heads_up
fourbet_low_spr
limp_or_passive_pot
multiway_pot
unknown_flop_spot
```

This layer groups ready solver input into a flop context. It does not validate cards, filter players, reconstruct preflop history, classify board texture, classify HERO made hand, compute equity, create decisions, create runtime plans, or click.

---

## V0.6.0 — Board Texture Feature Builder

**Status:** closed by V0.6.7  
**Closing checkpoint:** created by commit `V0.6.7 close board texture builder`

### Subversions

- `d648100` — `V0.6.1 add board texture contracts`
- `19013a6` — `V0.6.2 add board texture builder baseline`
- `247738e` — `V0.6.3 add board texture classification matrix`
- `9b2729a` — `V0.6.4 add fixture-backed board texture cases`
- `89a3985` — `V0.6.5 add board texture no-extra-logic gate`
- `ed3ce55` — `V0.6.6 document board texture builder`
- `V0.6.7` — `close board texture builder`

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
- Eight fixture-backed board texture synthetic Clear_JSON cases
- Board texture no-extra-logic architecture gate
- Board texture documentation

Board texture dimensions:

```text
suit_texture:       rainbow / two_tone / monotone
paired_texture:     unpaired / paired / trips_board
rank_texture:       ace_high / king_high / broadway_heavy / middle_connected / low_connected / low_static
connection_texture: disconnected / semi_connected / connected / highly_connected
volatility_class:   static_board / semi_dynamic_board / dynamic_board
```

Stable texture tags include:

```text
ace_high_dry_rainbow
king_high_two_tone
monotone_broadway
low_connected_dynamic
paired_dry
very_wet_connected
```

This layer describes board structure for future solver modules. It does not validate cards, filter players, classify HERO made hand, classify HERO draws, compute equity, build ranges, create decisions, create runtime plans, or click.

---

## Next planned version

### V0.7.0 — Hero Hand Classifier / Made Hand Features

Target:

```text
FlopContext + BoardTextureFeatures -> MadeHandFeatures
```

V0.7.0 will classify HERO made-hand features for future solver modules while keeping validation, equity, ranges, decision logic, runtime plans, and click-chain out of scope.
