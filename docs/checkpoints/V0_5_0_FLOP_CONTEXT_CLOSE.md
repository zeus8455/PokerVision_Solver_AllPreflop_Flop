# V0.5.0 Close — Flop Context Builder / Spot Family Layer

Status: **closed by V0.5.7**  
Final gate: **163 passed**  
Closing commit: created after integrating this checkpoint with message `V0.5.7 close flop context builder`

---

## Purpose

V0.5.0 created the first specialized flop context layer for the Clear_JSON-only postflop solver engine.

The target chain after this version is:

```text
Clear_JSON
  -> ClearJsonInput
  -> SolverInput
  -> Branch Resolver
  -> SolverBranchResult
  -> FlopContext
```

The layer answers a context question:

```text
What type of flop situation is HERO in?
```

It does **not** answer a decision question:

```text
Should HERO fold / call / check / bet / raise?
```

---

## Version scope

V0.5.0 created:

- flop context contracts
- flop context builder baseline
- spot family classification
- fixture-backed flop context test coverage
- no-extra-logic architecture gate
- official FlopContext documentation
- README / VERSION close checkpoint

V0.5.0 deliberately did not create:

- BoardTextureFeatures
- Hero Made Hand classifier
- draw classifier
- equity calculation
- range construction
- poker decision engine
- runtime plan
- click-chain integration
- card validation
- player filtering
- preflop history reconstruction from temporary JSON

---

## Subversion history

| Subversion | Commit | Purpose |
|---|---:|---|
| V0.5.1 | `a4a3567` | Add flop context contracts |
| V0.5.2 | `5d10849` | Add FlopContext builder baseline |
| V0.5.3 | `377832c` | Add flop spot family classifier |
| V0.5.4 | `ed3504f` | Add fixture-backed FlopContext coverage |
| V0.5.5 | `0fed29c` | Add no-extra-logic architecture gate |
| V0.5.6 | `aa33c9b` | Document FlopContext builder |
| V0.5.7 | after integration | Close V0.5.0 in README / VERSION / Miro checkpoint |

---

## Implemented files

### Contracts

```text
solver_postflop/flop_context_contracts.py
```

Defines:

- `FlopContext`
- `FlopSpotFamily`
- `FlopActionContext`
- `FlopPositionContext`
- `FlopPotContext`
- `FlopPlayerContext`
- `DEFAULT_FLOP_NEXT_MODULE`
- `FLOP_SPOT_FAMILIES`

### Builder

```text
solver_postflop/flop_context.py
```

Defines:

- `build_flop_context(solver_input, branch_result)`
- `classify_flop_spot_family(solver_input)`

The builder requires:

```text
branch_result.branch == flop
```

Then it groups already-mapped data from `SolverInput` into a FlopContext.

### Documentation

```text
docs/POSTFLOP_FLOP_CONTEXT.md
```

Documents:

- FlopContext purpose
- context blocks
- field usage policy
- spot family policy
- not_provided policy
- no-validation policy
- handoff to V0.6.0

---

## FlopContext structure

FlopContext stores:

- `case_id`
- `source_file`
- `table_id`
- `hand_id`
- `branch`
- `hero_cards`
- `board_cards`
- `spot_family`
- `pot_context`
- `player_context`
- `position_context`
- `action_context`
- `next_module`
- `context_fields_used`
- `context_fields_not_provided`
- `raw_clear_json_ref`
- `notes`

---

## Context blocks

### Metadata context

Uses:

- `case_id`
- `source_file`
- `table_id`
- `hand_id`
- `branch`

Purpose:

- traceability
- fixture linking
- future report linking

### Cards context

Uses:

- `hero_cards`
- `board_cards`

Policy:

- copied as metadata
- no duplicate-card validation
- no hero-board collision validation
- no board repair

### Pot context

Uses available data:

- `pot`
- `to_call`
- optional `effective_stack`
- optional `spr`
- optional `pot_type`

Policy:

- no pot reconstruction from temporary JSON
- no repair of pot / stack / committed amounts
- missing optional fields are tracked as `not_provided`

### Player context

Uses:

- `players`
- derived heads-up / multiway metadata where available from ready input

Policy:

- no repeated player filtering
- no HERO creation
- no active-player creation
- no folded/sitout/all-in repair

### Action context

Uses:

- `allowed_actions`
- `action_context`

Policy:

- no check/call/fold insertion
- no click-label construction
- no action repair

---

## Spot family classifier

V0.5.3 added minimal spot-family classification.

Supported families:

```text
srp_heads_up
threebet_pot_heads_up
fourbet_low_spr
limp_or_passive_pot
multiway_pot
unknown_flop_spot
```

Classification is based only on available `SolverInput` / Clear_JSON data.

It must not reconstruct preflop history from Dark/Pending/Service/Runtime JSON.

---

## Fixture-backed coverage

V0.5.4 connected V0.2 fixture library to FlopContext.

Fixture chain tested:

```text
Clear_JSON fixture
  -> load_clear_json_input()
  -> build_solver_input()
  -> resolve_solver_branch()
  -> build_flop_context()
```

Covered current flop cases:

- `real_flop_srp_btn_vs_bb_check_option`
- `synthetic_flop_srp_oop_facing_cbet`

Expected JSON was extended with FlopContext-specific expected fields:

- `expected_flop_spot_family`
- `expected_flop_action_context`
- `expected_flop_position_context`
- `expected_flop_next_module`
- `expected_flop_fields_used`
- `expected_flop_fields_not_provided`

---

## Architecture gate

V0.5.5 added:

```text
tests/test_postflop_flop_context_no_extra_logic_v050.py
```

This gate protects FlopContext from turning into another module type.

It checks that FlopContext does not:

- validate board cards
- search duplicate cards
- check hero-board collision
- filter players
- create HERO
- create active player
- reconstruct preflop history from temporary JSON
- search fallback JSON
- create poker decisions
- create runtime plans
- contain click-chain logic
- mutate Clear_JSON / SolverInput data / BranchResult
- read files through `open()`

---

## Final test gate

Final V0.1 + V0.2 + V0.3 + V0.4 + V0.5 gate:

```powershell
C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe -m pytest `
  tests/test_postflop_engine_contracts_v010.py `
  tests/test_postflop_clear_json_input_loader_v010.py `
  tests/test_postflop_solver_input_mapping_v010.py `
  tests/test_postflop_no_source_fallback_v010.py `
  tests/test_postflop_clear_json_fixture_skeleton_v020.py `
  tests/test_postflop_clear_json_minimum_cases_v020.py `
  tests/test_postflop_expected_interpretation_v020.py `
  tests/test_postflop_clear_json_fixture_manifest_v020.py `
  tests/test_postflop_field_mapping_contract_v030.py `
  tests/test_postflop_solver_input_field_usage_v030.py `
  tests/test_postflop_contract_backed_solver_input_mapping_v030.py `
  tests/test_postflop_no_validation_policy_v030.py `
  tests/test_postflop_branch_contracts_v040.py `
  tests/test_postflop_branch_resolver_v040.py `
  tests/test_postflop_branch_resolver_fixture_routing_v040.py `
  tests/test_postflop_branch_resolver_no_extra_checks_v040.py `
  tests/test_postflop_flop_context_contracts_v050.py `
  tests/test_postflop_flop_context_builder_v050.py `
  tests/test_postflop_flop_spot_family_v050.py `
  tests/test_postflop_flop_context_fixture_routing_v050.py `
  tests/test_postflop_flop_context_no_extra_logic_v050.py `
  -q
```

Expected / recorded result:

```text
163 passed
```

---

## Miro summary

V0.5.0 closes the first flop-specific context layer.

Before V0.5.0, the solver knew only how to load Clear_JSON, map it into SolverInput, and route it to a street branch.

After V0.5.0, the solver can take a flop branch and build a structured FlopContext containing pot/player/action/position/card metadata and a first spot-family classification.

This is still not a poker decision engine. It is a preparation layer for future feature modules.

---

## Next block

```text
V0.6.0 — Board Texture Feature Builder
```

Planned next chain:

```text
Clear_JSON
  -> SolverInput
  -> Branch Resolver
  -> FlopContext
  -> BoardTextureFeatures
```

V0.6.0 will classify board texture, but it must remain separate from validation, hand strength, equity, ranges, decision logic, runtime plans, and click-chain.
