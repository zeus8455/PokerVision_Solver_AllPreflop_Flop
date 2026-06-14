# POSTFLOP RANGE STATE

## Version scope

`V0.12.0 — Preflop Range Import / Range State Foundation` creates the first baseline range layer for the postflop solver.

The scope is intentionally limited:

```text
FlopContext + spot context -> RangeImporter -> RangeState
```

The range layer does **not** perform blocker filtering, range narrowing, equity recalculation, decision selection, runtime planning, or UI clicking.

## Current chain

After V0.12, the active postflop chain is:

```text
Clear_JSON
  -> SolverInput
  -> Branch Resolver
  -> FlopContext
  -> BoardTextureFeatures
  -> MadeHandFeatures
  -> DrawFeatures
  -> EquityScenarioInput
  -> EquityResult
  -> RangeState
```

`RangeState` is the foundation that future modules will use to reason about possible HERO and opponent holdings.

## Why RangeState exists

Raw heads-up equity from V0.11 is useful, but it is not sufficient for a serious postflop solver. A decision engine needs a structured baseline for:

- HERO baseline range;
- opponent baseline range;
- spot family: SRP, 3bet pot, 4bet low SPR, limp/passive, multiway, unknown;
- positions and pot type;
- combo buckets that future blocker filtering can process.

V0.12 only imports or selects the starting baseline range. It does not refine that range using flop action.

## Range contracts

`solver_postflop/range_contracts.py` defines:

- `RangeState`
- `PlayerRangeState`
- `RangeSourceInfo`
- `RangeBucket`
- `RangeSourceType`
- `RangeConfidenceClass`
- `RangeImportStatus`
- `RangeWeightingMode`

The critical field for future V0.13 work is:

```text
PlayerRangeState.combo_groups
```

This field stores compact combo strings grouped by bucket, for example:

```json
{
  "suited_broadways": ["AsKs", "AhKh"],
  "premium_pairs": ["AsAh", "QcQd"]
}
```

V0.12 stores these combos as baseline data only. It does not remove blocked combos.

## Range sources

### existing_project_ranges

`ranges/hero_preflop_ranges.json` exists and is detected by the inventory tool as an existing project range source.

Current inventory status:

- schema: `preflop_ranges_v1`
- source type candidate: `existing_project_ranges`
- contains range shorthand strings: true
- contains combo-level compact strings: false
- requires expansion before V0.13: true

This file is useful as a source of preflop strategy structure, but it is not directly ready for blocker filtering until shorthand expansion exists.

### postflop_default_ranges

`ranges/postflop_default_ranges.json` is the V0.12 synthetic baseline range pack.

Current status:

- schema: `pokervision_solver_postflop_default_ranges_v1`
- source type: `postflop_default_ranges`
- contains combo-level compact strings: true
- supports V0.12 importer tests
- ready as baseline input for future V0.13 blocker filtering

The default pack contains baseline cases for:

- `flop_range_srp_heads_up_btn_vs_bb`
- `flop_range_srp_oop_bb_vs_btn`
- `flop_range_3bet_pot_ip`
- `flop_range_3bet_pot_oop`
- `flop_range_4bet_low_spr`
- `flop_range_limp_passive`
- `flop_range_multiway`
- `flop_range_unknown_context`

### synthetic_test_ranges

Synthetic test ranges are allowed only for fixture coverage and regression control. They must stay clearly marked as synthetic and must not be treated as live proof.

### unknown_range

`unknown_range` is a structured non-fatal state.

It means the solver could not select a baseline range source for the context. The pipeline must not crash. Future decision modules should treat this as low-confidence input or use a conservative fallback/no-aggressive-strategy path.

## Range Importer

`solver_postflop/range_importer.py` performs one conversion:

```text
FlopContext -> RangeState
```

It reads already-built context fields:

- `spot_family`
- `pot_context.pot_type`
- `position_context.hero_position`
- `player_context.players`, when provided

Then it selects a baseline case from `ranges/postflop_default_ranges.json` and returns a `RangeState`.

The importer is read-only with respect to `FlopContext`.

## What V0.12 does not do

V0.12 must not do any of the following:

- blocker filtering;
- combo removal by HERO cards;
- combo removal by board cards;
- range narrowing by flop action;
- range weighting by board texture;
- equity recalculation;
- exploit strategy;
- decision engine;
- runtime plan;
- click mapping;
- physical click;
- Clear_JSON validation;
- player filtering;
- missing player creation;
- fallback discovery through Dark/Pending/Service/Runtime JSON.

## Why blocker filtering is deferred

Blocker filtering belongs to V0.13.

V0.12 only guarantees that combo-level baseline data exists in `RangeState`. V0.13 will consume:

```text
RangeState + hero_cards + board_cards -> AvailableComboState
```

This keeps the architecture clean:

- V0.12 = baseline import;
- V0.13 = card blocker filtering;
- later versions = action model, strategy input, decision logic, runtime/click.

## Fixture coverage

V0.12 fixture coverage confirms:

- SRP BTN vs BB;
- SRP BB vs BTN;
- 3bet IP;
- 3bet OOP;
- 4bet low SPR;
- limp/passive;
- multiway;
- unknown context.

The expected outputs under `tests/fixtures/postflop_range_state_v0125/expected/` are trace-append-ready JSON representations of `RangeState`.

## Architecture invariant

RangeState is a baseline data object. It is not a poker decision.

Any module that imports baseline ranges and also tries to decide, click, validate cards, repair players, or read temporary PokerVision JSON sources violates the V0.12 boundary.
