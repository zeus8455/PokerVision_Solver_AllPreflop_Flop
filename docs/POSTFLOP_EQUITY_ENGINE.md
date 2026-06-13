# V0.11.0 — PokerKit-backed Equity Engine / Raw Equity Snapshot

## Purpose

V0.11.0 adds the first numeric postflop equity layer to the Clear_JSON-only solver line.

The input to this layer is not raw PokerVision JSON. The input is the already prepared `EquityScenarioInput` produced by V0.10.0.

Current chain:

**Clear_JSON → SolverInput → Branch Resolver → FlopContext → BoardTextureFeatures → MadeHandFeatures → DrawFeatures → EquityScenarioInput → EquityResult**

## Scope

The V0.11 equity layer produces a **raw equity snapshot**.

It answers only this type of question:

> Given HERO cards, board cards, and the current raw scenario context, what is HERO's raw equity under the currently supported backend mode?

It does **not** answer:

- whether HERO should bet, check, call, raise, or fold;
- how much to bet;
- what button should be clicked;
- how opponent ranges should be narrowed;
- how action history changes strategy.

## Main modules

### `solver_postflop/equity_contracts.py`

Defines result contracts:

- `EquityResult`
- `EquityPlayerResult`
- `EquityBackendResult`
- `EquityComputationMode`
- `EquityConfidenceClass`
- `EquityBackendStatus`

This module must remain backend-independent. Importing it must not require PokerKit.

### `solver_postflop/equity_backend_pokerkit.py`

Contains the PokerKit-backed computation layer.

Allowed responsibilities:

- dynamically detect PokerKit availability;
- map PokerVision card strings to PokerKit card strings;
- use PokerKit card parsing and `StandardHighHand` evaluation;
- compute supported raw equity snapshots;
- return structured `EquityBackendResult` objects;
- return structured unavailable/error/deferred results without crashing the pipeline.

### `solver_postflop/equity_engine.py`

Upper wrapper:

- accepts `EquityScenarioInput`;
- selects the equity computation mode;
- calls the backend adapter;
- converts backend output into `EquityResult`;
- preserves metadata, sample count, confidence, and notes.

The engine must not import PokerKit directly. PokerKit usage is backend-scoped.

## Current supported calculation

V0.11 currently supports first numeric **heads-up raw equity**.

Supported data shape:

- HERO has two known hole cards;
- board has 3, 4, or 5 known cards;
- opponent count is one;
- backend is available.

The backend excludes known cards from the remaining deck, completes unknown opponent hole cards and missing board runout, evaluates hands with PokerKit, and returns:

- `hero_equity`
- `hero_win_rate`
- `hero_tie_rate`
- `sample_count_used`
- backend metadata

The relationship is:

`hero_equity ≈ hero_win_rate + hero_tie_rate / 2`

## Multiway status

Multiway full equity is intentionally not completed in V0.11.

Multiway scenarios return a structured deferred result instead of failing the solver pipeline.

This is intentional because later versions need stronger range and sampling policy before multiway results should be used for strategy.

## Unknown context status

Unknown or unsupported context is not a crash condition.

Examples:

- missing HERO cards;
- unsupported board size;
- unknown opponent count;
- backend unavailable;
- backend exception.

The engine should return structured unavailable/error/unknown results with notes. This keeps the solver trace inspectable.

## PokerKit usage

PokerKit is installed locally in the Python 3.12 environment and is not called through an external API.

Validated local version during V0.11 development:

- `pokerkit 0.7.4`

Validated symbols:

- `Card`
- `Rank`
- `Suit`
- `Deck`
- `StandardHighHand`
- `NoLimitTexasHoldem`
- `Automation`
- `Mode`
- `State`

Validated PokerVision-to-PokerKit examples:

- `A_spades → As`
- `K_hearts → Kh`
- `10_spades → Ts`

Validated hand-evaluation example:

- `StandardHighHand.from_game(...)` can produce `Straight (AsKhQdJcTs)`.

## What V0.11 must not do

The equity engine must not perform any of the following:

- range engine work;
- range narrowing;
- blocker filtering as a range module;
- action-history range adjustment;
- poker decision selection;
- runtime plan creation;
- click execution;
- Clear_JSON validation;
- duplicate-card validation as a source-cleaning layer;
- HERO invention;
- opponent invention;
- player filtering;
- live source discovery;
- fallback to Dark_JSON, Pending_JSON, current_cycle, or runtime JSON.

Those responsibilities belong to other explicitly versioned layers.

## Relationship to V0.12.0

V0.12.0 will introduce **RangeState / Preflop Range Import**.

That means V0.11 equity is intentionally **raw equity**, not range-aware strategic equity.

The decision engine must not treat V0.11 raw equity alone as a complete poker strategy.
