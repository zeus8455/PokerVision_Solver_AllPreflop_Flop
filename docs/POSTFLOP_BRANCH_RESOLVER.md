# POSTFLOP BRANCH RESOLVER

## Version scope

Version: **V0.4.5 — Branch Resolver Documentation**

Parent block: **V0.4.0 — Solver Branch Resolver / Street Module Routing**

This document describes the first routing layer inside the Clear_JSON-only postflop solver engine.

The Branch Resolver is not a poker decision engine, not a validator, and not a runtime/click module. It only maps a prepared `SolverInput` to a branch result that tells the next solver module where the hand should go.

---

## Pipeline position

The active V0.4 pipeline is:

**Clear_JSON → ClearJsonInput → SolverInput → Branch Resolver → SolverBranchResult**

The resolver starts only after:

1. Clear_JSON was explicitly supplied to the solver.
2. `load_clear_json_input()` created `ClearJsonInput`.
3. `build_solver_input()` created a contract-backed `SolverInput`.
4. The Clear_JSON payload remains read-only.

The Branch Resolver does not open files, does not discover sources, and does not search neighboring JSON artifacts.

---

## Main responsibility

The Branch Resolver answers one question:

**Which future solver branch should handle this `SolverInput` next?**

It does not answer:

- whether the cards are valid;
- whether the board has duplicates;
- whether HERO collides with the board;
- whether the player list is correct;
- whether the poker action should be fold/call/check/bet/raise;
- whether a runtime click should happen.

---

## Files introduced by V0.4.0

Current V0.4 modules:

- `solver_postflop/branch_contracts.py`
- `solver_postflop/branch_resolver.py`

Current V0.4 tests:

- `tests/test_postflop_branch_contracts_v040.py`
- `tests/test_postflop_branch_resolver_v040.py`
- `tests/test_postflop_branch_resolver_fixture_routing_v040.py`
- `tests/test_postflop_branch_resolver_no_extra_checks_v040.py`

---

## Branch contract

`SolverBranchResult` is the public routing result.

It contains:

- `case_id`
- `source_file`
- `branch`
- `branch_family`
- `next_module`
- `branch_reason`
- `is_decision_branch_enabled`
- `is_runtime_branch_enabled`
- `notes`

For V0.4.0:

- `is_decision_branch_enabled` is always `false`.
- `is_runtime_branch_enabled` is always `false`.

This is intentional. V0.4.0 routes to future modules; it does not execute strategy or runtime actions.

---

## Branch types

The resolver uses the following branch values.

### `preflop_not_handled`

Used when the current `SolverInput` has no board cards.

Postflop solver does not process preflop. Preflop remains outside this module line.

Default next module:

**`preflop_solver_external_or_skip`**

---

### `flop`

Used when `SolverInput.board_cards` contains exactly 3 cards.

This is the first active postflop branch and leads toward V0.5.0 Flop Context Builder.

Default next module:

**`flop_context_builder`**

---

### `turn_not_implemented_yet`

Used when `SolverInput.board_cards` contains exactly 4 cards.

Turn is recognized as a separate branch, but V0.4.0 does not implement turn solver logic.

Default next module:

**`turn_solver_not_implemented_yet`**

---

### `river_not_implemented_yet`

Used when `SolverInput.board_cards` contains exactly 5 cards.

River is recognized as a separate branch, but V0.4.0 does not implement river solver logic.

Default next module:

**`river_solver_not_implemented_yet`**

---

### `unsupported`

Used when the current `SolverInput` cannot be routed to one of the implemented branch categories.

Examples:

- missing board card information;
- 1 board card;
- 2 board cards;
- 6+ board cards;
- unsupported future cases.

Default next module:

**`unsupported_branch_report`**

---

## Routing rules

V0.4.0 routes only by board-card count.

| `SolverInput.board_cards` state | Branch | Branch reason |
| --- | --- | --- |
| `0` cards | `preflop_not_handled` | `no_board_cards_preflop_or_not_postflop` |
| `3` cards | `flop` | `three_board_cards_flop_branch` |
| `4` cards | `turn_not_implemented_yet` | `four_board_cards_turn_branch_not_implemented_yet` |
| `5` cards | `river_not_implemented_yet` | `five_board_cards_river_branch_not_implemented_yet` |
| missing / `None` | `unsupported` | `board_cards_not_provided_for_branch_routing` |
| `1`, `2`, `6+` cards | `unsupported` | `unsupported_board_card_count_for_branch_routing` |

---

## Unsupported does not mean invalid

The reason:

**`unsupported_board_card_count_for_branch_routing`**

is a routing reason, not a validation error.

It does not mean:

- the cards are invalid;
- the source is dirty;
- PokerVision made a mistake;
- the solver should repair data.

It means only:

**the current V0.4 routing layer does not have a branch for this board-card count.**

---

## Next module policy

The resolver maps every branch to a default next module.

| Branch | Branch family | Next module |
| --- | --- | --- |
| `preflop_not_handled` | `non_postflop` | `preflop_solver_external_or_skip` |
| `flop` | `postflop_flop` | `flop_context_builder` |
| `turn_not_implemented_yet` | `postflop_turn` | `turn_solver_not_implemented_yet` |
| `river_not_implemented_yet` | `postflop_river` | `river_solver_not_implemented_yet` |
| `unsupported` | `unsupported` | `unsupported_branch_report` |

The `next_module` value is descriptive routing metadata. It does not call the module in V0.4.0.

---

## Fixture-backed routing

V0.4.3 connected the resolver to the V0.2 Clear_JSON fixture library.

Fixture path:

**`tests/fixtures/postflop_clear_json/`**

The fixture-backed chain is:

**manifest case → Clear_JSON fixture → ClearJsonInput → SolverInput → resolve_solver_branch() → SolverBranchResult → expected JSON**

Current expected JSON fields for branch routing:

- `expected_branch`
- `expected_branch_family`
- `expected_branch_reason`
- `expected_branch_next_module`
- `expected_branch_contract_version`

Current fixture coverage:

| Fixture family | Expected branch |
| --- | --- |
| real flop | `flop` |
| synthetic flop | `flop` |
| synthetic turn | `turn_not_implemented_yet` |
| synthetic river | `river_not_implemented_yet` |

---

## Read-only policy

The Branch Resolver must preserve the read-only architecture established in V0.1–V0.3.

It must not mutate:

- `SolverInput.raw_clear_json_ref`
- `SolverInput.board_cards`
- `SolverInput.hero_cards`
- `SolverInput.players`
- `SolverInput.allowed_actions`

The resolver result is a separate object.

---

## No-validation policy

The Branch Resolver must not validate poker state.

It must not perform:

- duplicate-card validation;
- hero-board collision validation;
- board validity checks;
- player filtering;
- HERO reconstruction;
- active player reconstruction;
- street repair;
- pot repair;
- action repair.

The resolver assumes `SolverInput` came from a trusted Clear_JSON prepared by PokerVision.

---

## No-source-discovery policy

The Branch Resolver must not use:

- Dark_JSON;
- Pending_JSON;
- Service JSON;
- Runtime JSON;
- source discovery;
- fallback source lookup;
- external project snapshot imports.

It receives `SolverInput` and returns `SolverBranchResult`.

---

## No-decision / no-runtime policy

The Branch Resolver must not create:

- final poker decisions;
- action decisions;
- runtime plans;
- click plans;
- click results;
- solver payloads for live execution.

V0.4.0 always keeps:

- `is_decision_branch_enabled = false`
- `is_runtime_branch_enabled = false`

Decision and runtime behavior belong to later versions.

---

## V0.4.0 checkpoint history

- **V0.4.1** — Branch contracts baseline.
- **V0.4.2** — Branch resolver baseline.
- **V0.4.3** — Fixture-backed branch routing.
- **V0.4.4** — Branch resolver no-extra-checks gate.
- **V0.4.5** — Branch resolver documentation.

---

## Current test gate

After V0.4.4, the full V0.1–V0.4 gate passed:

**125 passed**

V0.4.5 is documentation-only and should preserve the same gate.

---

## Next block prepared by V0.4.0

V0.4.0 prepares:

**V0.5.0 — Flop Context Builder / Spot Family Layer**

The intended next pipeline is:

**Clear_JSON → SolverInput → Branch Resolver → FlopContext**

Only `branch = flop` should be accepted by the first Flop Context Builder version.
