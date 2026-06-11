# V0.5.0 — Postflop Flop Context Builder

## Status

This document belongs to the V0.5.0 development block:

**V0.5.0 — Flop Context Builder / Spot Family Layer**

The Flop Context layer sits after the Branch Resolver and before analytical flop modules such as Board Texture, Hero Made Hand, Draw Features, Ranges, Equity, and the future Decision Engine.

Pipeline position:

```text
Clear_JSON → ClearJsonInput → SolverInput → Branch Resolver → FlopContext → future flop modules
```

V0.5.0 is not a decision layer. It does not answer whether HERO should check, bet, call, raise, or fold. It only groups already prepared Clear_JSON / SolverInput fields into a stable context object for later modules.

---

## Core policy

The Flop Context Builder treats Clear_JSON as a trusted input that has already been prepared by the upstream PokerVision chain.

The builder must remain:

- Clear_JSON-only.
- Read-only toward Clear_JSON.
- Non-validating.
- Non-filtering.
- Non-decision-making.
- Independent from runtime and click-chain logic.

It must not reconstruct missing poker state from temporary JSON sources.

---

## Input contract

The builder consumes:

```text
SolverInput + SolverBranchResult
```

The branch result must point to the flop branch:

```text
branch = flop
```

If the branch is not `flop`, the builder must not silently build a context. A predictable error is expected because FlopContext is valid only after the Branch Resolver has routed the hand into the flop branch.

---

## Output contract

The builder returns:

```text
FlopContext
```

The FlopContext contains:

- Metadata context.
- Board / card context.
- Pot context.
- Player context.
- Action context.
- Position context.
- Spot family.
- Next module pointer.
- Fields used.
- Fields not provided.
- Notes.
- Raw Clear_JSON reference.

The default next module after FlopContext is:

```text
flop_board_texture_builder
```

---

## Metadata context

Metadata fields come from SolverInput and the Branch Result.

| Source | FlopContext field | Policy |
|---|---|---|
| `SolverInput.case_id` / raw Clear_JSON `case_id` | `case_id` | Used for test/report linkage. |
| `SolverInput.source_file` / trace source | `source_file` | Used for fixture/runtime trace. |
| `SolverInput.table_id` | `table_id` | Copied as provided. |
| `SolverInput.hand_id` | `hand_id` | Copied as provided. |
| `SolverBranchResult.branch` | `branch` | Must be `flop`. |
| `SolverInput.raw_clear_json_ref` | `raw_clear_json_ref` | Preserved as read-only reference. |

No metadata field should trigger validation or repair logic.

---

## Board and card context

The builder copies card fields from SolverInput:

| Source | FlopContext field | Policy |
|---|---|---|
| `SolverInput.hero_cards` | `hero_cards` | Copied without validation. |
| `SolverInput.board_cards` | `board_cards` | Copied without validation. |

The builder must not:

- Validate card syntax.
- Check duplicate cards.
- Check hero-board collision.
- Repair card count.
- Infer missing cards.
- Normalize cards beyond copying the provided SolverInput value.

Board analysis belongs to later modules, starting with:

```text
V0.6.0 — Board Texture Feature Builder
```

---

## Pot context

The builder creates a `FlopPotContext` from already available fields.

Expected fields:

| Source | FlopPotContext field | Policy |
|---|---|---|
| `SolverInput.pot` | `pot` | Copied as provided. |
| `SolverInput.to_call` | `to_call` | Copied as provided. |
| stack/effective stack data if already available | `effective_stack` | Used only if available. |
| pot and effective stack if already available | `spr` | May be derived only from already available numbers; no reconstruction. |
| `pot_type` from raw Clear_JSON / SolverInput context | `pot_type` | Used only if already present. |

If optional fields are missing, they must be recorded in:

```text
context_fields_not_provided
```

The builder must not recover pot type, stack, SPR, or preflop pot structure from Dark_JSON, Pending_JSON, Service JSON, Runtime JSON, screen state, or click artifacts.

---

## Player context

The builder creates a `FlopPlayerContext` from SolverInput.

Expected fields:

| Source | FlopPlayerContext field | Policy |
|---|---|---|
| `SolverInput.players` | `players` | Copied without re-filtering. |
| HERO metadata if already available | `hero_id` | Used only if present. |
| player list / context | `opponents` | May be copied/derived from already provided players only. |
| player count / context | `is_heads_up` | Based on already provided context; no repair. |
| player count / context | `is_multiway` | Based on already provided context; no repair. |

The builder must not:

- Re-filter players.
- Remove folded players.
- Change sitout state.
- Change all-in state.
- Create HERO.
- Create active player.
- Reconstruct missing player state.

Player filtering belongs upstream in PokerVision before Clear_JSON is produced.

---

## Position context

The builder creates a `FlopPositionContext` from already available metadata.

Typical fields:

- HERO position.
- Position type if already available.
- In-position / out-of-position if already available.
- Button / blinds if already available.

If the data is not present in SolverInput / Clear_JSON, it must be recorded as not provided. The builder must not infer position from external source files.

---

## Action context

The builder creates a `FlopActionContext` from already available action data.

Expected fields:

| Source | FlopActionContext field | Policy |
|---|---|---|
| `SolverInput.allowed_actions` | `allowed_actions` | Copied as provided. |
| `SolverInput.action_context` | `action_context` | Copied as provided. |
| `current_actor` / `active_player` if already present | `current_actor` | Used only if available. |
| allowed action information if provided | `can_check`, `can_call`, `can_bet`, `can_raise` | May be represented from existing data only. |
| action context if provided | `facing_bet`, `facing_raise` | Used only if already present. |

The builder must not:

- Add missing actions manually.
- Repair allowed actions.
- Convert actions into click labels.
- Decide between check/call/bet/raise/fold.
- Build runtime action payloads.

Action availability is used later by the decision engine and runtime mapping, not by V0.5.0.

---

## Spot family policy

The Flop Context layer assigns a broad working spot family for future flop modules.

Supported spot families:

| Spot family | Meaning |
|---|---|
| `srp_heads_up` | Single-raised pot heads-up. |
| `threebet_pot_heads_up` | Three-bet pot heads-up. |
| `fourbet_low_spr` | Four-bet or low-SPR pot. |
| `limp_or_passive_pot` | Limped or passive pot structure. |
| `multiway_pot` | Multiway flop context. |
| `unknown_flop_spot` | Insufficient context for a supported family. |

Classification must use only fields already present in SolverInput / Clear_JSON, such as:

- `pot_type`.
- `preflop_context` if already provided.
- `action_context` if already provided.
- player count / explicit multiway hints if already provided.

The classifier must not reconstruct preflop history from temporary JSON sources.

---

## Fields used and not provided

Every FlopContext should record:

```text
context_fields_used
context_fields_not_provided
```

`context_fields_used` should include fields consumed from SolverInput / Clear_JSON, such as:

- `hero_cards`
- `board_cards`
- `players`
- `pot`
- `to_call`
- `allowed_actions`
- `action_context`
- `positions`
- `pot_type`

`context_fields_not_provided` should include optional fields that were expected by future modules but absent from the trusted input, such as:

- `preflop_context`
- `preflop_aggressor`
- `hero_preflop_role`
- `effective_stack`
- `spr`
- `current_actor`

Missing optional fields are not errors at this layer.

---

## Fixture-backed coverage

The V0.5.0 line uses the V0.2.0 Clear_JSON fixture library.

Current fixture-backed FlopContext tests cover:

- Real flop Clear_JSON.
- Synthetic flop Clear_JSON.

The tested chain is:

```text
Clear_JSON fixture
→ load_clear_json_input()
→ build_solver_input()
→ resolve_solver_branch()
→ build_flop_context()
```

Expected files include V0.5 fields such as:

- `expected_flop_spot_family`
- `expected_flop_action_context`
- `expected_flop_position_context`
- `expected_flop_next_module`
- `expected_flop_fields_used`
- `expected_flop_fields_not_provided`

---

## Explicit non-goals for V0.5.0

The Flop Context Builder must not do the following:

- Validate cards.
- Check duplicate cards.
- Check hero-board collision.
- Filter players.
- Reconstruct HERO.
- Reconstruct active player.
- Repair folded / sitout / all-in state.
- Reconstruct preflop history from Dark_JSON.
- Search temporary JSON sources.
- Classify board texture.
- Classify HERO made hand.
- Classify HERO draws.
- Calculate equity.
- Build ranges.
- Make poker decisions.
- Create runtime plans.
- Execute clicks.

These boundaries are protected by V0.5 no-extra-logic tests.

---

## Handoff to V0.6.0

V0.5.0 prepares the input layer for:

```text
V0.6.0 — Board Texture Feature Builder
```

The next module will consume FlopContext and build:

```text
FlopContext → BoardTextureFeatures
```

V0.6.0 will analyze board structure, but it will still not validate cards, filter players, calculate equity, build ranges, decide actions, or interact with runtime/click-chain.

---

## Summary

After V0.5.0, the solver understands not just that the hand is on the flop, but also the basic flop context:

- Spot family.
- Pot context.
- Player context.
- Position context.
- Action context.
- Used fields.
- Missing optional fields.
- Next module.

The active chain becomes:

```text
Clear_JSON → SolverInput → Branch Resolver → FlopContext
```
