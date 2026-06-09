# POSTFLOP_FIXTURE_MANIFEST_RULES.md

## Purpose

This document defines the rules for:

```text
tests/fixtures/postflop/manifest.json
```

The manifest is introduced in **V0.2.0 - Source-Based Postflop Fixture Lab**.
It is the index that connects fixture case metadata with source JSON and expected JSON files.

---

## Manifest role

The manifest must answer these questions for every case:

- what is the case id;
- what source JSON is used;
- what source type it has;
- whether the source is real or manual live-like;
- whether click-cycle is required;
- what expected JSON belongs to the source;
- whether a future normalized file is expected;
- what the case status is.

---

## Recommended manifest shape

The manifest should use this top-level shape:

```json
{
  "version": "0.2.0",
  "description": "Source-based postflop fixture manifest.",
  "allowed_source_types": [
    "dark_json",
    "pending_json",
    "service_json",
    "current_cycle_json",
    "runtime_json",
    "solver_payload_json",
    "final_clear_json",
    "manual_live_like_json",
    "unknown"
  ],
  "cases": []
}
```

---

## Required case fields

Each case must contain these fields:

```text
case_id
description
source_type
source_file
expected_file
normalized_file
street_candidate
pot_type_candidate
is_real_project_source
is_manual_live_like_source
source_of_truth_note
requires_click_cycle
status
notes
```

---

## case_id rule

`case_id` must be unique across the manifest.

Recommended format:

```text
flop_source_case_001
flop_source_case_002
turn_source_case_001
river_source_case_001
```

V0.2.0 starts with at least:

```text
flop_source_case_001
```

---

## source_type rule

`source_type` must be one of:

```text
dark_json
pending_json
service_json
current_cycle_json
runtime_json
solver_payload_json
final_clear_json
manual_live_like_json
unknown
```

Unknown source type must include explanatory notes.

---

## source_file rule

`source_file` must point to an existing JSON file.

It should usually live under:

```text
tests/fixtures/postflop/source_json/<source_type>/
```

or under a live-like tree:

```text
tests/fixtures/postflop/live_like_tree/
```

A fixture case without source JSON is invalid.

---

## expected_file rule

`expected_file` must point to an existing JSON file under:

```text
tests/fixtures/postflop/expected/
```

A fixture case without expected JSON is invalid.

The expected file must not contain poker decisions in V0.2.0.

---

## normalized_file rule

`normalized_file` may point to a future file under:

```text
tests/fixtures/postflop/normalized/
```

The file is allowed to be missing in V0.2.0 because the normalizer is not implemented yet.

This must remain valid until **V0.4.0 - Source Discovery + Postflop Normalizer**.

---

## Real/manual source flags

Every case must explicitly say whether it is a real project source or a manual live-like source.

Valid real source:

```json
{
  "is_real_project_source": true,
  "is_manual_live_like_source": false
}
```

Valid manual live-like source:

```json
{
  "is_real_project_source": false,
  "is_manual_live_like_source": true
}
```

Invalid ambiguous source:

```json
{
  "is_real_project_source": true,
  "is_manual_live_like_source": true
}
```

Invalid source with no origin:

```json
{
  "is_real_project_source": false,
  "is_manual_live_like_source": false
}
```

unless `status` is explicitly set to a review/quarantine state and notes explain why.

---

## requires_click_cycle rule

`requires_click_cycle` must be explicit.

For pre-click intermediate sources, it is usually:

```json
false
```

For final Clear_JSON or post-click final outputs, it may be:

```json
true
```

Core rule:

```text
Final Clear_JSON is not mandatory for V0.2.0.
```

---

## status rule

Allowed status values should include:

```text
active
review
legacy
quarantine
future
```

V0.2.0 fixture tests should require at least one active case after the first source case is added.

---

## expected JSON required fields

Expected JSON should describe source characteristics, not poker decisions.

Required expected fields:

```text
expected_source_type
expected_has_board_cards
expected_has_hero_cards
expected_has_players
expected_has_actions
expected_street_candidate
expected_required_fields_present
expected_can_be_used_for_future_normalizer
expected_requires_click_cycle
expected_notes
```

---

## What manifest tests must catch

Manifest tests must fail when:

- manifest.json is missing;
- duplicate case_id exists;
- required case field is missing;
- source_type is invalid;
- source_file does not exist;
- expected_file does not exist;
- manual source is marked as real source;
- both real/manual flags are true;
- Final Clear_JSON is treated as required;
- unknown source has no notes.

---

## What manifest tests must allow

Manifest tests must allow:

- missing normalized_file target before normalizer exists;
- non-final source types;
- pre-click JSON sources;
- manual_live_like_json when correctly flagged;
- unknown source when explicitly documented;
- absence of final_clear_json cases.

---

## Future migration

V0.3.0 contracts and V0.4.0 source discovery must reuse this manifest model instead of inventing a second metadata format.
