# V0.8.0 — Hero Draw Classifier / Draw Features

## Status

**Current checkpoint:** V0.8.6 — Hero Draw Documentation  
**Module layer:** postflop feature extraction  
**Primary output:** `DrawFeatures`  
**Previous layer:** `MadeHandFeatures`  
**Next planned layer:** V0.9.0 — Main Live Integration / Clear_JSON Capture / Full Module Audit

---

## 1. Purpose / Scope

`Hero Draw Classifier` is the postflop solver layer that describes HERO's improvement potential on the flop.

It receives already-prepared solver context and produces structured draw metadata for future modules.

Current feature chain:

```text
Clear_JSON
  -> SolverInput
  -> Branch Resolver
  -> FlopContext
  -> BoardTextureFeatures
  -> MadeHandFeatures
  -> DrawFeatures
```

The module answers:

- does HERO have a flush draw?
- does HERO have a backdoor flush draw?
- does HERO have a gutshot?
- does HERO have an open-ended straight draw?
- does HERO have a double gutshot?
- does HERO have overcards?
- is the draw a combo draw?
- how strong is the draw potential?

This layer does **not** make poker decisions.

It does **not** calculate equity.

It does **not** build opponent ranges.

It does **not** create runtime plans or click instructions.

---

## 2. Input Contract

The classifier consumes three already-built objects:

```text
FlopContext
BoardTextureFeatures
MadeHandFeatures
```

### 2.1 FlopContext

`FlopContext` provides the hand-level postflop state:

- `case_id`
- `source_file`
- `hero_cards`
- `board_cards`
- `players`
- `pot`
- `to_call`
- `allowed_actions`
- `spot_family`
- `raw_clear_json_ref`

The draw module treats this data as trusted solver input.

It does not repair, validate, normalize, or re-filter it.

### 2.2 BoardTextureFeatures

`BoardTextureFeatures` provides board context produced by V0.6.0:

- suit texture
- paired texture
- rank texture
- connection texture
- volatility class
- texture tags

The draw module may use this as context for tagging and future trace clarity, but it does not rebuild board texture.

### 2.3 MadeHandFeatures

`MadeHandFeatures` provides ready hand information produced by V0.7.0:

- made hand class
- pair class
- showdown value class
- strength tier
- board interaction tags
- kicker relevance

The draw module may use this to identify pair-plus-draw combo categories, but it does not reclassify made hands.

---

## 3. Output Contract

The output is `DrawFeatures` from `solver_postflop/hero_draw_contracts.py`.

The expected fields include:

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

The output is feature metadata only.

It is not an action payload.

It is not a runtime payload.

It is not an equity result.

---

## 4. FlushDrawClass Policy

The flush draw classifier describes HERO's suit-based improvement potential.

Supported classes:

```text
no_flush_draw
backdoor_flush_draw
weak_flush_draw
standard_flush_draw
nut_flush_draw_candidate
```

### 4.1 no_flush_draw

Used when HERO has no meaningful flush improvement path on the flop.

This class does not mean the hand is weak overall. It only means there is no flush draw component.

### 4.2 backdoor_flush_draw

Used when HERO has a backdoor flush path that requires turn and river cards to complete.

This is weaker than a direct flush draw and normally maps to low future equity contribution.

### 4.3 weak_flush_draw

Reserved for non-premium direct flush draw structures when the implementation needs to distinguish weaker flush draws from standard/nut candidates.

The current layer stores the category for future use; it still does not make decisions.

### 4.4 standard_flush_draw

Used when HERO has a direct flush draw but not a nut-flush candidate.

This is relevant for future semi-bluff, call equity, and turn barrel planning.

### 4.5 nut_flush_draw_candidate

Used when HERO has a direct flush draw with a high/nut-relevant suit card.

The word `candidate` is intentional: this module does not perform exhaustive nut validation or range analysis.

---

## 5. StraightDrawClass Policy

The straight draw classifier describes HERO's rank-based improvement potential.

Supported classes:

```text
no_straight_draw
gutshot
open_ended_straight_draw
double_gutshot
combo_straight_draw
```

### 5.1 no_straight_draw

Used when HERO has no meaningful straight improvement path.

### 5.2 gutshot

Used when HERO has an inside straight draw.

This is usually weaker than an open-ended draw and often maps to `weak_draw` or `medium_draw` depending on other features.

### 5.3 open_ended_straight_draw

Used when HERO has an open-ended straight draw.

This has stronger improvement potential than a single gutshot.

### 5.4 double_gutshot

Used when HERO has two inside straight completion paths.

This is treated as a stronger straight draw structure than a single gutshot.

### 5.5 combo_straight_draw

Reserved for richer straight-draw structures where a hand has multiple straight improvement components.

It is used as feature metadata for future equity and strategy modules.

---

## 6. OvercardClass Policy

The overcard classifier describes whether HERO has cards above the board's highest relevant rank.

Supported classes:

```text
no_overcards
one_overcard
two_overcards
```

### 6.1 no_overcards

Used when HERO has no overcard backup.

### 6.2 one_overcard

Used when one HERO card is above the board's relevant top rank.

This can matter for float logic, delayed c-bet logic, or thin call logic in future modules.

### 6.3 two_overcards

Used when both HERO cards are overcards.

This may increase future turn/river improvement potential, especially when combined with straight or flush draws.

---

## 7. ComboDrawClass Policy

Combo draw classification combines draw components and made-hand context.

Supported classes:

```text
no_combo_draw
flush_plus_gutshot
flush_plus_oesd
pair_plus_flush_draw
pair_plus_straight_draw
pair_plus_combo_draw
overcards_plus_draw
```

### 7.1 no_combo_draw

Used when HERO has no combined draw structure.

A hand may still have a single draw, such as only a gutshot or only a flush draw.

### 7.2 flush_plus_gutshot

Used when HERO has both a flush draw and a gutshot.

This is stronger than either component alone.

### 7.3 flush_plus_oesd

Used when HERO has both a flush draw and an open-ended straight draw.

This is a premium combo candidate for future semi-bluff and aggressive line selection.

### 7.4 pair_plus_flush_draw

Used when HERO already has a made pair and also has a flush draw.

This matters because the hand has both showdown value and improvement potential.

### 7.5 pair_plus_straight_draw

Used when HERO already has a made pair and also has a straight draw.

### 7.6 pair_plus_combo_draw

Used when HERO has a made pair plus multiple draw components.

This is not a decision by itself; it is a high-signal feature for future strategy.

### 7.7 overcards_plus_draw

Used when HERO has overcards plus a draw.

This often functions as equity backup in future call/float/semi-bluff logic.

---

## 8. DrawStrengthTier Policy

`DrawStrengthTier` summarizes draw potential for future modules.

Supported tiers:

```text
no_draw
backdoor_only
weak_draw
medium_draw
strong_draw
premium_combo_draw
```

### 8.1 no_draw

Used when HERO has no meaningful draw component.

### 8.2 backdoor_only

Used when the only improvement path is backdoor potential.

### 8.3 weak_draw

Used for lower-value single draw structures.

### 8.4 medium_draw

Used for normal direct draw structures such as standard flush draws or simple straight draws.

### 8.5 strong_draw

Used for high-quality draws, nut draw candidates, or stronger multi-component draw structures.

### 8.6 premium_combo_draw

Used for the strongest draw structures, especially direct flush draw plus strong straight draw or similar high-density improvement hands.

This tier is still not a decision.

---

## 9. Draw Tags

`draw_tags` are compact metadata labels for future modules.

Examples:

```text
backdoor_fd
standard_fd
nut_fd_candidate
gutshot
oesd
double_gutshot
fd_plus_gutshot
fd_plus_oesd
pair_plus_fd
pair_plus_straight_draw
two_overcards_plus_draw
premium_combo_draw_candidate
```

Tags are used by future layers to avoid re-deriving known structure.

They should remain descriptive and stable.

They should not encode final actions.

---

## 10. Fixture Coverage

V0.8.4 added fixture-backed coverage for draw features.

Synthetic Clear_JSON draw cases include:

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

The fixture pipeline is:

```text
Clear_JSON fixture
  -> load_clear_json_input()
  -> build_solver_input()
  -> resolve_solver_branch()
  -> build_flop_context()
  -> build_board_texture_features()
  -> build_made_hand_features()
  -> build_draw_features()
```

Expected JSON fields include:

- `expected_flush_draw_class`
- `expected_straight_draw_class`
- `expected_overcard_class`
- `expected_combo_draw_class`
- `expected_draw_strength_tier`
- `expected_draw_tags`
- `expected_draw_version`

---

## 11. No-extra-logic Policy

V0.8.5 introduced the architecture gate for Hero Draw.

The module must not do any of the following:

- validate cards
- search duplicate cards
- check hero-board collision
- discover external source JSON
- fallback to Dark JSON
- fallback to Pending JSON
- fallback to Service JSON
- fallback to Runtime JSON
- read files
- write files
- filter players
- create HERO
- create active player
- run equity
- call PokerKit
- build ranges
- produce poker decisions
- create runtime plans
- call button detectors
- click anything

The module must preserve read-only behavior for:

- `raw_clear_json_ref`
- `FlopContext`
- `BoardTextureFeatures`
- `MadeHandFeatures`
- `hero_cards`
- `board_cards`
- `players`
- `allowed_actions`

---

## 12. Relationship to MadeHandFeatures

`DrawFeatures` uses `MadeHandFeatures` as context, especially for pair-plus-draw categories.

However, Hero Draw must not reclassify made hands.

Made hand classification belongs to V0.7.0.

Draw classification belongs to V0.8.0.

The modules are intentionally separated:

```text
V0.7.0: what does HERO already have?
V0.8.0: what can HERO improve to?
```

---

## 13. Handoff to V0.9.0

After V0.8.0 closes, the feature chain is complete enough for live audit:

```text
Clear_JSON
  -> SolverInput
  -> Branch Resolver
  -> FlopContext
  -> BoardTextureFeatures
  -> MadeHandFeatures
  -> DrawFeatures
```

V0.9.0 should verify that this chain works on live Clear_JSON produced by the real project.

V0.9.0 may allow the existing project click-chain to run, because the real project may need completed live cycles to save final Clear_JSON.

However, the postflop solver must still not create decisions, runtime plans, or clicks.

The V0.9.0 audit should prove:

- live Clear_JSON is created
- postflop Clear_JSON is saved in the correct Clear folder
- solver modules V0.1–V0.8 can process live Clear_JSON
- module reports are produced
- postflop solver does not interfere with runtime/click-chain

---

## 14. Stable Boundary

Hero Draw Classifier is a feature extraction layer only.

It is allowed to answer:

```text
What draw potential does HERO have?
```

It is not allowed to answer:

```text
Should HERO bet/call/fold/raise?
```

That boundary must remain strict until dedicated equity, range, and decision modules are introduced.

