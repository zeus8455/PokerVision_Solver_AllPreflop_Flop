# POSTFLOP CLEAR JSON FIELD MAPPING

## Version

**Version block:** V0.3.0 — SolverInput Mapping / Field Usage Contract  
**Subversion:** V0.3.5 — Field Mapping Documentation  
**Architecture:** Clear_JSON-only trusted input  
**Mapping version:** `v0.3.0`

---

## Purpose

This document defines the official field mapping policy for the postflop solver engine.

The mapping layer describes how data moves through the solver input pipeline:

**Clear_JSON field → SolverInput field → future solver module**

This layer is intentionally narrow. It does not validate poker state, repair data, reconstruct missing data, or infer hidden state. It only documents which fields are consumed, where they are placed, and which future solver modules are expected to use them.

---

## Current pipeline

The active V0.3 pipeline is:

**Clear_JSON → ClearJsonInput → SolverInput → FieldUsageTrace**

The concrete modules are:

**`solver_postflop/clear_json_input.py`**  
Loads one explicitly provided Clear_JSON file as trusted input.

**`solver_postflop/solver_input.py`**  
Builds `SolverInput` from `ClearJsonInput` using the official field mapping contract.

**`solver_postflop/field_mapping_contract.py`**  
Defines the official source field / target field / future module contract.

**`solver_postflop/field_usage_trace.py`**  
Reports which fields were used, which fields were not provided, which fields were ignored, and which future modules have relevant data.

---

## Non-validator policy

V0.3.0 is not a validator.

The mapping layer must not perform:

**duplicate card validation**  
**hero-board collision validation**  
**board count safety gate**  
**player filtering**  
**HERO reconstruction**  
**active player reconstruction**  
**preflop history reconstruction**  
**pot repair**  
**stack repair**  
**action repair**  
**source discovery fallback**  
**runtime plan creation**  
**click-chain logic**

Clear_JSON is treated as already prepared by the PokerVision pipeline.

If a field is not present, the correct behavior is:

**mark it as `not_provided`**

The correct behavior is not:

**guess it, reconstruct it, or block the mapping pipeline**

---

## Field groups

The official mapping contract is grouped into these categories:

**metadata**  
**cards**  
**players**  
**pot_stacks**  
**action_context**  
**preflop_context**

Each mapping entry defines:

**Clear_JSON source field or aliases**  
**SolverInput target field**  
**data kind**  
**requirement level**  
**future solver modules**  
**policy note**

---

# 1. Metadata mapping

| Clear_JSON field | SolverInput / trace target | Requirement | Future module usage | Policy note |
|---|---|---:|---|---|
| `case_id` | `ClearJsonInput.case_id`, trace context | optional | fixture reports, debug trace, future test reports | Used for case identity when present. |
| `table_id` | `SolverInput.table_id` | optional | trace, runtime linking later, report correlation | Missing value is `not_provided`. |
| `hand_id` | `SolverInput.hand_id` | optional | trace, hand reports, future runtime linking | Missing value is `not_provided`. |
| `timestamp` | future source timestamp context | optional | reports, future timeline correlation | Not a blocker if absent. |
| `created_at` | future source timestamp context | optional | reports, future timeline correlation | Alias-like timestamp source. |

## Metadata policy

The solver does not create table IDs, hand IDs, timestamps, or case IDs.

If a metadata field is missing, it is recorded in field usage trace as unavailable, but the mapping pipeline remains open.

---

# 2. Cards mapping

| Clear_JSON field | SolverInput target | Requirement | Future module usage | Policy note |
|---|---|---:|---|---|
| `hero_cards` | `SolverInput.hero_cards` | optional for mapping, required later for hand logic | street branch resolver, flop context, hand strength later, blocker/range logic later | Copied as provided. No card validation. |
| `board_cards` | `SolverInput.board_cards` | optional for mapping, required later for postflop branch routing | branch resolver, flop context, board texture later, draw module later, equity later | Copied as provided. No board validity check. |

## Cards policy

The mapping layer must not check:

**duplicate cards**  
**hero-board collision**  
**board card count validity**  
**card format validity**

Those responsibilities do not belong to V0.3.0.

At this layer, cards are moved as trusted data from Clear_JSON to SolverInput.

---

# 3. Players mapping

| Clear_JSON field | SolverInput target | Requirement | Future module usage | Policy note |
|---|---|---:|---|---|
| `players` | `SolverInput.players` | optional for mapping, required later for context | heads-up / multiway context, range assignment later, SPR/effective stack logic later | Copied as provided. No filtering. |
| `hero_id` | future hero identity usage | optional | flop context later, position context later | Not reconstructed if missing. |
| `hero` | future hero identity usage | optional | flop context later, position context later | Alias-like hero reference if Clear_JSON provides it. |
| `positions` | `SolverInput.positions` | optional | position logic, range assignment later, flop context later | Copied as provided. |

## Players policy

The solver mapping layer must not:

**filter players again**  
**remove folded players**  
**repair sitout state**  
**repair all-in state**  
**create HERO**  
**create active player**  
**invent missing positions**

The solver trusts PokerVision to provide the prepared player state.

If player-related fields are missing, the correct output is `not_provided`.

---

# 4. Pot / stacks mapping

| Clear_JSON field | SolverInput target | Requirement | Future module usage | Policy note |
|---|---|---:|---|---|
| `total_pot` | `SolverInput.pot` | optional | SPR later, bet sizing later, pressure modules later | Preferred pot source when present. |
| `pot` | `SolverInput.pot` | optional | SPR later, bet sizing later, pressure modules later | Alias/fallback source for pot. |
| `to_call` | `SolverInput.to_call` | optional | facing bet logic later, call/fold pressure later | Copied as provided. |
| `stacks` | `SolverInput.stacks` | optional | effective stack later, SPR later | Preferred stack source when present. |
| `chips` | `SolverInput.stacks` | optional | effective stack later, SPR later | Alias/fallback source for stacks. |
| `committed` | `SolverInput.committed_amounts` | optional | pot contribution context later, all-in pressure later | Preferred committed amount source. |
| `committed_amounts` | `SolverInput.committed_amounts` | optional | pot contribution context later, all-in pressure later | Alias/fallback source. |

## Pot / stacks policy

The mapping layer must not:

**repair pot**  
**recalculate total pot**  
**repair stacks**  
**infer committed amounts**  
**normalize all-in pressure**

It only maps fields that already exist in Clear_JSON.

---

# 5. Action context mapping

| Clear_JSON field | SolverInput target | Requirement | Future module usage | Policy note |
|---|---|---:|---|---|
| `allowed_actions` | `SolverInput.allowed_actions` | optional | decision availability later, runtime plan mapping later, click label selection later | Copied as provided. No action repair. |
| `action_context` | `SolverInput.action_context` | optional | branch-specific context later, flop context later | Copied as provided. |
| `current_actor` | future current actor usage | optional | future decision availability, future runtime linking | Not reconstructed if absent. |
| `active_player` | future current actor usage | optional | future decision availability, future runtime linking | Alias-like source. |

## Action context policy

The mapping layer must not:

**add check/call/fold manually**  
**repair allowed_actions**  
**infer missing action buttons**  
**create click labels**  
**create runtime plan**  
**create poker decision**

Action data is copied as trusted input. Missing action context becomes `not_provided`.

---

# 6. Preflop context mapping

| Clear_JSON field | SolverInput / future target | Requirement | Future module usage | Policy note |
|---|---|---:|---|---|
| `preflop_context` | future raw preflop context | optional | pot type interpretation later, range logic later | Not reconstructed if absent. |
| `pot_type` | future pot type usage | optional | SRP / 3bet / 4bet family logic later | Used only if already provided. |
| `preflop_aggressor` | future aggressor usage | optional | range assignment later, c-bet logic later | Not inferred if absent. |
| `hero_preflop_role` | future hero role usage | optional | positional role logic later | Not inferred if absent. |

## Preflop context policy

V0.3.0 does not reconstruct preflop history.

If Clear_JSON already provides preflop context, the solver can trace and expose it for future modules.

If it does not, the trace must mark it as:

**`not_provided`**

No Dark_JSON, Pending_JSON, service output, runtime output, or historical artifact may be queried to reconstruct it.

---

# FieldUsageTrace policy

`FieldUsageTrace` records how the mapping contract was applied.

It should contain:

**case_id**  
**source_file**  
**mapping_version**  
**fields_used**  
**fields_not_provided**  
**fields_ignored**  
**future_modules_enabled**  
**records**  
**notes**

## fields_used

A target field is recorded in `fields_used` when at least one source field from its contract entry exists in Clear_JSON.

Example:

If `total_pot` exists, then `pot` is used.

## fields_not_provided

A target field is recorded in `fields_not_provided` when none of its source fields exists in Clear_JSON.

Example:

If neither `preflop_context` nor related preflop fields exists, preflop context fields remain not provided.

## fields_ignored

A field is recorded in `fields_ignored` when it exists in Clear_JSON but is not described by the official field mapping contract.

Ignored does not mean invalid.

It means only:

**not consumed by the V0.3 mapping contract**

## future_modules_enabled

Future module labels are collected from used mapping entries.

This does not mean those future modules are implemented yet.

It means the mapped data is relevant to those modules later.

---

# Contract-backed mapping policy

After V0.3.3, `build_solver_input()` is contract-backed.

This means:

**mapping aliases come from `CLEAR_JSON_FIELD_MAPPINGS`**  
**used / not_provided fields align with contract entries**  
**`MAPPING_VERSION` follows `FIELD_MAPPING_VERSION`**  
**public API remains `build_solver_input(clear_input)`**  
**raw Clear_JSON reference remains attached to SolverInput**  
**Clear_JSON remains read-only**

---

# Fixture usage

V0.3.0 uses the fixture library created in V0.2.0:

**`tests/fixtures/postflop_clear_json/`**

The fixture library provides:

**real flop Clear_JSON**  
**synthetic flop Clear_JSON**  
**synthetic turn Clear_JSON**  
**synthetic river Clear_JSON**  
**expected interpretation JSON**  
**manifest.json**

V0.3.0 does not alter fixture semantics. It uses them to test mapping and trace behavior.

---

# What V0.3.0 does not do

V0.3.0 does not implement:

**street resolver**  
**branch resolver**  
**flop context builder**  
**turn logic**  
**river logic**  
**board texture classification**  
**hand strength evaluation**  
**draw detection**  
**range construction**  
**equity calculation**  
**decision engine**  
**runtime plan**  
**click-chain execution**

Those are future layers.

---

# Tests associated with V0.3.0

The V0.3.0 mapping contract is protected by:

**`tests/test_postflop_field_mapping_contract_v030.py`**  
Checks the official field mapping contract.

**`tests/test_postflop_solver_input_field_usage_v030.py`**  
Checks the FieldUsageTrace layer.

**`tests/test_postflop_contract_backed_solver_input_mapping_v030.py`**  
Checks that `build_solver_input()` is backed by the official contract.

**`tests/test_postflop_no_validation_policy_v030.py`**  
Checks that the mapping/trace layer does not become a validator.

---

# Final rule

V0.3.0 is a contract and trace layer.

It should answer:

**what Clear_JSON fields did the solver use?**  
**where did those fields go?**  
**what was not provided?**  
**what was ignored?**  
**which future modules will use these fields?**

It must not answer:

**is this poker state valid?**  
**what should HERO do?**  
**which button should be clicked?**
