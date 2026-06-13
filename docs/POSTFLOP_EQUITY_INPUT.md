# POSTFLOP EQUITY INPUT — V0.10.0

## Purpose

`EquityScenarioInput` is the postflop solver handoff object prepared for the later equity layer.

V0.10.0 converts the already-built flop-chain objects into a single future equity scenario:

`FlopContext + BoardTextureFeatures + MadeHandFeatures + DrawFeatures -> EquityScenarioInput`

This layer is a metadata adapter only. It does not calculate equity, does not run simulations, and does not import PokerKit.

## Source objects

The builder consumes only objects that already exist in the Clear_JSON-only postflop chain:

- `FlopContext`
- `BoardTextureFeatures`
- `MadeHandFeatures`
- `DrawFeatures`

The builder treats these objects as read-only inputs. It copies and reshapes data; it does not repair, validate, or rediscover state.

## Output object

`EquityScenarioInput` contains:

- `case_id`
- `source_file`
- `hero`
- `board`
- `opponents`
- `spot_family`
- `pot`
- `to_call`
- `effective_stack`
- `spr`
- `position_context`
- `action_context`
- `board_texture_features`
- `made_hand_features`
- `draw_features`
- `equity_run_mode`
- `next_module = equity_engine`
- `fields_used`
- `fields_not_provided`
- `notes`

## HERO input

`EquityHeroInput` carries only metadata from the upstream context:

- HERO cards
- HERO position
- stack metadata if already provided
- effective stack if already provided
- notes

The builder does not create HERO, does not infer missing cards, and does not validate card uniqueness.

## Board input

`EquityBoardInput` carries:

- board cards
- street, currently `flop`
- board texture tags
- paired status
- suit structure
- straight/connection structure
- notes

The builder does not check duplicate cards, hero-board collision, or board-card validity. Those concerns are outside V0.10.0.

## Opponent input

`EquityOpponentModelInput` carries opponent metadata only if the upstream `FlopPlayerContext` already provides it.

Allowed behavior:

- copy known opponents from existing player context;
- derive `opponents_count` from known opponents;
- use existing `is_heads_up` / `is_multiway` flags;
- mark unknown contexts explicitly.

Forbidden behavior:

- creating missing opponents;
- filtering players;
- repairing positions;
- inventing player roles;
- importing ranges.

## Equity run modes

`EquityRunMode` defines the future computation path, not a computation result.

Current modes:

- `heads_up_exact_or_sampled`
- `multiway_sampled`
- `range_based_later`
- `unknown_context_mode`

`unknown_context_mode is not an error`. It means the future equity engine receives a structured scenario whose context is incomplete. The pipeline should remain stable and transparent.

## Fields trace

The builder must preserve traceability:

- `fields_used` records fields that were actually consumed;
- `fields_not_provided` records missing fields that were not invented;
- `notes` records important non-fatal state, such as unknown context handling.

This is required so later modules can distinguish known state from missing state.

## Explicit non-goals in V0.10.0

V0.10.0 does not:

- calculate equity;
- run PokerKit;
- run Monte Carlo or sampling;
- build opponent ranges;
- narrow ranges by action history;
- perform blocker filtering;
- validate Clear_JSON;
- validate cards;
- check duplicate cards;
- filter players;
- create HERO or opponents;
- make poker decisions;
- build runtime plans;
- click buttons;
- discover fallback JSON sources such as Dark/Pending/Service/Runtime JSON.

## PokerKit boundary

PokerKit belongs to V0.11.0 or later.

V0.10.0 does not import PokerKit. The first acceptable integration point is a separate backend adapter in the equity engine layer, not the input builder layer.

## Pipeline after V0.10.0

After V0.10.0 the intended chain is:

`Clear_JSON -> SolverInput -> Branch Resolver -> FlopContext -> BoardTextureFeatures -> MadeHandFeatures -> DrawFeatures -> EquityScenarioInput`

The next module is fixed as:

`next_module = equity_engine`

The next planned version is V0.11.0 — PokerKit-backed Equity Engine / Raw Equity Snapshot.
