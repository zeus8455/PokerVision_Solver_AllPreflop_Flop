# POSTFLOP_BLOCKER_FILTERING — V0.13.0

## Purpose

V0.13.0 adds the first combo-level availability layer for the postflop solver:

`RangeState + hero_cards + board_cards -> AvailableComboState`

The layer answers which combos from an already-imported baseline range remain available after known HERO and board cards are used as poker blockers.

## Current chain

After V0.13, the active chain is:

`Clear_JSON -> SolverInput -> Branch Resolver -> FlopContext -> BoardTextureFeatures -> MadeHandFeatures -> DrawFeatures -> EquityScenarioInput -> EquityResult -> RangeState -> AvailableComboState`

## Inputs

The module consumes:

- `RangeState` from the V0.12 range importer.
- `hero_cards` from already-built solver context.
- `board_cards` from already-built solver context.

The module does not discover or read Dark/Pending/Service/Runtime JSON.

## Output: AvailableComboState

`AvailableComboState` stores:

- `case_id`
- `source_file`
- `spot_family`
- `hero_cards_used_as_blockers`
- `board_cards_used_as_blockers`
- `player_combo_states`
- total combo counts before filtering
- total available combo counts
- total blocked combo counts
- per-reason blocked counts
- `range_source_info`
- `next_module = flop_action_model_later`

## PlayerComboState

Each player keeps a separate `PlayerComboState`:

- `player_id`
- `position`
- `range_name`
- `combo_count_before`
- `combo_count_available`
- `combo_count_blocked`
- `blocked_by_hero_count`
- `blocked_by_board_count`
- `available_combo_groups`
- `blocked_combo_groups`
- `combo_group_availability`
- `blocker_results`

Multiway players are processed separately. The module never merges opponent ranges into one synthetic range.

## BlockedComboReason

The blocker layer distinguishes:

- `blocked_by_hero_card`
- `blocked_by_board_card`
- `blocked_by_hero_and_board`
- `not_blocked`

Malformed combo strings are excluded from the available state in a structured way. They do not crash the pipeline.

## Important boundary

This layer is poker blocker logic, not source validation.

It does not:

- validate Clear_JSON;
- check card collisions as an integrity audit;
- check HERO-board collision;
- filter players;
- rebuild RangeState;
- create new ranges;
- narrow ranges by flop action;
- recalculate equity;
- make a poker decision;
- create a runtime plan;
- click UI buttons;
- use Dark/Pending/Service/Runtime JSON as solver input.

## Relationship to V0.12

V0.12 creates `RangeState` from `FlopContext` and baseline range sources.

V0.13 consumes that `RangeState` and applies known-card blockers only. It keeps the original `RangeState` read-only.

## Relationship to V0.14 and V0.14.5

V0.14.0 will add:

`FlopActionModel -> ActionButtonSnapshot -> ActionOptionResolver`

V0.14.5 will later add action-based range weighting:

`AvailableComboState + FlopActionModel + action history -> NarrowedRangeState`

V0.13 does not do action-based narrowing.
