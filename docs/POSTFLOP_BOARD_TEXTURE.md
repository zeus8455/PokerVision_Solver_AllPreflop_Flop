# POSTFLOP BOARD TEXTURE FEATURE BUILDER

## Version block

**Version:** V0.6.0 — Board Texture Feature Builder  
**Documentation checkpoint:** V0.6.6  
**Module scope:** `FlopContext -> BoardTextureFeatures`  
**Current status:** documentation-only checkpoint

---

## Purpose

The Board Texture Feature Builder is the first analytical feature layer in the postflop solver pipeline.

It receives an already-built `FlopContext` and creates a structured `BoardTextureFeatures` object that describes the flop board texture for future solver modules.

Pipeline position:

```text
Clear_JSON
  -> ClearJsonInput
  -> SolverInput
  -> Branch Resolver
  -> FlopContext
  -> BoardTextureFeatures
```

The module answers this question:

> What is the structure of the flop board?

It does **not** answer:

> What should HERO do?

---

## Architectural policy

V0.6.0 treats `Clear_JSON` and `FlopContext` as trusted upstream inputs.

The Board Texture Builder must stay a feature extractor. It must not become a validator, hand classifier, draw classifier, equity engine, range engine, decision engine, or runtime/click module.

### The module may use

- `FlopContext.case_id`
- `FlopContext.source_file`
- `FlopContext.board_cards`
- `FlopContext.raw_clear_json_ref` as read-only reference
- metadata needed for trace and future module handoff

### The module must preserve

- original `board_cards`
- original `hero_cards`
- original `players`
- original `raw_clear_json_ref`
- original `FlopContext`

---

## Output contract

Primary result:

```python
BoardTextureFeatures
```

Expected high-level fields:

- `case_id`
- `source_file`
- `board_cards`
- `suit_texture`
- `paired_texture`
- `rank_texture`
- `connection_texture`
- `volatility_class`
- `texture_tags`
- `features_used_by_future_modules`
- `notes`

The result must be serializable to JSON and safe to store in trace/report artifacts later.

---

## Suit texture

Suit texture describes suit distribution on the flop.

### `rainbow`

Three different suits.

Example:

```text
Ah 7d 2c
```

Future usage:

- lower immediate flush-draw pressure
- more static dry-board logic
- lower semi-bluff density from flush draws

### `two_tone`

Two cards share a suit and one card has another suit.

Example:

```text
Kh 9h 2c
```

Future usage:

- flush draw availability
- barrel planning
- range pressure
- protection needs

### `monotone`

All three cards share one suit.

Example:

```text
Qh Jh Th
```

Future usage:

- flush-completed board pressure
- range/nut advantage shifts
- blocker relevance
- cautious value/bluff split later

---

## Paired texture

Paired texture describes repeated board ranks.

### `unpaired`

All ranks are different.

Example:

```text
Ah 7d 2c
```

### `paired`

Exactly one pair on the board.

Example:

```text
Kh Kd 4c
```

Future usage:

- range advantage checks
- trips/full-house interaction later
- thinner value logic later

### `trips_board`

Three cards of the same rank on the board.

Example:

```text
7h 7d 7c
```

Future usage:

- board-lock situations
- kicker relevance
- special decision treatment later

---

## Rank texture

Rank texture describes the high-card and rank-composition profile of the flop.

### `ace_high`

Board contains an ace as the top rank.

Example:

```text
Ah 7d 2c
```

Future usage:

- preflop aggressor advantage
- c-bet frequency tendency later
- top-pair made-hand context in V0.7

### `king_high`

Board top rank is a king and no ace is present.

Example:

```text
Kh 9h 2c
```

Future usage:

- high-card pressure
- broadway range interaction
- future made-hand/draw evaluation

### `broadway_heavy`

Board has multiple broadway cards.

Example:

```text
Qh Jh Th
```

Future usage:

- straight density
- range interaction
- dynamic board handling

### `middle_connected`

Board is built around middle ranks with meaningful connectivity.

Example:

```text
9h 8d 6c
```

Future usage:

- straight-draw density
- caller range interaction
- higher dynamic potential

### `low_connected`

Low connected board.

Example:

```text
6h 5d 4c
```

Future usage:

- low-card range interaction
- straight-draw density
- protection/barrel planning later

### `low_static`

Low board with limited connectivity.

Example:

```text
8h 4d 2c
```

Future usage:

- static-board policy later
- lower immediate nut volatility

---

## Connection texture

Connection texture describes rank proximity and straight-draw density.

### `disconnected`

Large rank gaps and limited straight-draw structure.

Example:

```text
Ah 7d 2c
```

### `semi_connected`

Some proximity or partial interaction, but not dense.

Example:

```text
Kh 9h 7c
```

### `connected`

Ranks create clear straight-draw interaction.

Example:

```text
9h 8d 6c
```

### `highly_connected`

Very dense straight-draw structure.

Example:

```text
Jh Th 9c
```

Future usage:

- straight-draw density
- range interaction
- equity realization
- bet/check split later

---

## Volatility class

Volatility class summarizes how likely the board is to change strategic value across later streets.

### `static_board`

Low draw density and low volatility.

Example:

```text
Ah 7d 2c
```

Future usage:

- small-bet tendencies later
- lower protection urgency

### `semi_dynamic_board`

Some draw pressure or partial connectivity.

Example:

```text
Kh 9h 2c
```

Future usage:

- mixed bet/check policy later
- turn-card sensitivity

### `dynamic_board`

High draw density, strong connectivity, monotone structure, or wet texture.

Example:

```text
Qh Jh Th
```

Future usage:

- protection need
- larger sizing tendency later
- barrel planning

---

## Texture tags

`texture_tags` provide compact, stable labels for downstream modules.

Current tag examples:

- `ace_high_dry_rainbow`
- `king_high_two_tone`
- `monotone_broadway`
- `low_connected_dynamic`
- `paired_dry`
- `very_wet_connected`

Tags should be deterministic and useful for:

- future board texture reports
- V0.7 Hero Made Hand interaction
- V0.8 Hero Draw interaction
- future range/equity/decision modules

Tags must not contain final strategy or action recommendations.

---

## Fixture-backed coverage

V0.6.4 added synthetic texture fixtures for:

- `flop_texture_ace_high_dry_rainbow`
- `flop_texture_king_high_two_tone`
- `flop_texture_monotone_broadway`
- `flop_texture_low_connected`
- `flop_texture_middle_connected_two_tone`
- `flop_texture_paired_dry`
- `flop_texture_paired_dynamic`
- `flop_texture_very_wet_connected`

Each fixture passes this chain:

```text
Clear_JSON fixture
  -> load_clear_json_input()
  -> build_solver_input()
  -> resolve_solver_branch()
  -> build_flop_context()
  -> build_board_texture_features()
```

Expected JSON verifies:

- `expected_suit_texture`
- `expected_paired_texture`
- `expected_rank_texture`
- `expected_connection_texture`
- `expected_volatility_class`
- `expected_texture_tags`

---

## No-extra-logic policy

The Board Texture Builder must not:

- validate cards
- search for duplicate cards
- check hero-board collision
- filter players
- create HERO
- create active player
- determine HERO made hand
- determine HERO draws
- calculate equity
- build ranges
- create poker decisions
- create runtime plans
- click buttons
- read Dark/Pending/Service/Runtime JSON
- perform source discovery
- mutate `Clear_JSON`
- mutate `FlopContext`

These guarantees are enforced by:

```text
tests/test_postflop_board_texture_no_extra_logic_v060.py
```

---

## Relationship to future modules

### V0.7.0 — Hero Made Hand Classifier

Board Texture gives V0.7 contextual board structure.

V0.7 will classify HERO made-hand features such as:

- high card
- pair
- top pair
- middle pair
- bottom pair
- overpair
- two pair
- set / trips
- straight
- flush
- full house / quads

Board Texture does not perform this classification itself.

### V0.8.0 — Hero Draw Classifier

Board Texture gives V0.8 context for draw density and board volatility.

V0.8 will classify draw features such as:

- flush draw
- backdoor flush draw
- gutshot
- open-ended straight draw
- double gutshot
- overcards
- combo draw

Board Texture does not perform draw classification itself.

---

## Current V0.6.0 checkpoints

- **V0.6.1** — Board Texture contracts baseline
- **V0.6.2** — Board Texture builder baseline
- **V0.6.3** — Board Texture classification matrix
- **V0.6.4** — Fixture-backed Board Texture cases
- **V0.6.5** — Board Texture no-extra-logic gate
- **V0.6.6** — Board Texture documentation

---

## Final statement

After V0.6.0, the solver understands flop board structure, but still does not understand HERO hand strength, HERO draws, equity, ranges, or final decisions.

The active pipeline becomes:

```text
Clear_JSON
  -> SolverInput
  -> Branch Resolver
  -> FlopContext
  -> BoardTextureFeatures
```

The next block is:

```text
V0.7.0 — Hero Hand Classifier / Made Hand Features
```
