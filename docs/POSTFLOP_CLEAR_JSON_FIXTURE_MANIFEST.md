# V0.2.0 — Clear_JSON Fixture Manifest Contract

Status: **planned block, V0.2.1 docs/schema step**
Manifest path:

```text
tests/fixtures/postflop_clear_json/manifest.json
```

---

## 1. Purpose

The manifest is the central registry for every postflop Clear_JSON fixture case.

It must answer:

- what the case is
- where the Clear_JSON file is stored
- where the expected interpretation file is stored
- whether the case is real or synthetic
- what future solver modules the case is intended to support

The manifest is not a poker decision file and not a validation report.

---

## 2. Top-level manifest shape

The recommended manifest shape is:

```json
{
  "schema_version": "v0.2.0",
  "fixture_root": "tests/fixtures/postflop_clear_json",
  "cases": []
}
```

The `cases` array contains one object per fixture.

---

## 3. Required case fields

Each case entry must contain:

```json
{
  "case_id": "flop_real_case_001",
  "case_name": "Real flop Clear_JSON baseline case",
  "street_group": "flop",
  "spot_family": "srp_heads_up",
  "source_kind": "real",
  "clear_json_file": "real/flop/flop_real_case_001.clear.json",
  "expected_file": "expected/flop_real_case_001.expected.json",
  "base_real_case_id": null,
  "purpose": "test_solver_input_mapping",
  "solver_modules_targeted": ["solver_input_mapping", "future_branch_resolver"],
  "status": "active",
  "notes": []
}
```

---

## 4. Field definitions

### `case_id`

Stable unique identifier for the fixture case.

Rules:

- must be unique across the manifest
- should be lowercase snake_case
- should include street and source kind when useful

Example:

```text
flop_real_case_001
flop_synthetic_srp_btn_vs_bb_check_option_001
```

### `case_name`

Human-readable case title.

### `street_group`

Expected street group for fixture organization.

Allowed values in V0.2.0:

- `flop`
- `turn`
- `river`
- `unknown`

This is fixture metadata, not card validation.

### `spot_family`

High-level poker scenario family.

Examples:

- `srp_heads_up`
- `srp_multiway`
- `three_bet_pot`
- `four_bet_pot`
- `limp_pot`
- `facing_bet`
- `facing_raise`
- `check_option`
- `all_in_pressure`
- `unknown`

### `source_kind`

Defines whether the Clear_JSON is real or synthetic.

Allowed values:

- `real`
- `synthetic`

Rules:

- real files should remain as close as possible to actual PokerVision output
- synthetic files must never be marked as real

### `clear_json_file`

Relative path from fixture root to the Clear_JSON file.

Example:

```text
real/flop/flop_real_case_001.clear.json
```

### `expected_file`

Relative path from fixture root to the expected interpretation file.

Example:

```text
expected/flop_real_case_001.expected.json
```

### `base_real_case_id`

Reference to the real case used as the base for a synthetic case.

Rules:

- must be `null` for real cases
- should reference an existing real `case_id` when a synthetic case is derived from a real case
- may be `null` for template-derived synthetic cases if no real base exists yet, but notes must explain that choice

### `purpose`

Short reason the fixture exists.

Examples:

- `test_solver_input_mapping`
- `test_flop_branch_resolution`
- `test_srp_context`
- `test_multiway_context`
- `test_facing_bet_action_context`
- `test_future_decision_matrix`

### `solver_modules_targeted`

List of current or future modules this fixture is intended to support.

Examples:

- `clear_json_input_loader`
- `solver_input_mapping`
- `field_mapping_contract`
- `branch_resolver`
- `flop_context_builder`
- `future_decision_engine`

### `status`

Fixture lifecycle status.

Allowed values in V0.2.0:

- `active`
- `draft`
- `deprecated`

### `notes`

List of short notes about the case.

Use notes to explain synthetic derivation, incomplete real coverage, or future module relevance.

---

## 5. Expected interpretation file contract

Each expected file should use this minimum shape:

```json
{
  "case_id": "flop_real_case_001",
  "expected_street_group": "flop",
  "expected_spot_family": "srp_heads_up",
  "expected_hero_position": "BTN",
  "expected_is_heads_up": true,
  "expected_is_multiway": false,
  "expected_pot_type": "srp",
  "expected_action_context": "check_option",
  "expected_available_solver_branch": "flop_srp_branch",
  "expected_next_module": "flop_context_builder",
  "expected_notes": []
}
```

---

## 6. Expected file policy

Expected interpretation files should describe solver understanding only.

Allowed:

- street group
- spot family
- hero position
- heads-up/multiway context
- pot type
- action context
- available future branch
- next module
- notes

Not allowed in V0.2.0:

- final poker action
- bet size
- range output
- equity output
- hand strength output
- runtime plan
- click instruction

---

## 7. Manifest integrity rules

V0.2.0 tests should enforce:

- manifest exists
- `schema_version` exists
- `cases` is a list
- every `case_id` is unique
- every required field is present
- every `clear_json_file` exists
- every `expected_file` exists
- every `source_kind` is either `real` or `synthetic`
- every synthetic case has either a valid `base_real_case_id` or an explanatory note
- every case has a non-empty `purpose`
- every case has at least one `solver_modules_targeted` value
- expected file `case_id` matches manifest `case_id`
- expected files do not contain final decision fields

---

## 8. V0.2.0 manifest is not validation

The manifest may describe expected fixture interpretation, but it must not reject a Clear_JSON because of poker-state correctness.

The manifest layer must not perform:

- duplicate card validation
- hero-board collision checks
- board count safety gates
- player filtering
- HERO reconstruction
- active player reconstruction
- pot/action repair

Those checks remain outside V0.2.0.

---

## 9. Miro summary

**Card title:** V0.2.0 — Clear_JSON Fixture Manifest Contract

**Purpose:** Define the registry format for every real and synthetic postflop Clear_JSON fixture.

**Core fields:** case_id, case_name, street_group, spot_family, source_kind, clear_json_file, expected_file, base_real_case_id, purpose, solver_modules_targeted, status, notes.

**Expected files:** describe solver interpretation only, not final poker decisions.

**Test value:** protects fixture structure, prevents real/synthetic mixing, and ensures future solver tests use shared cases instead of random JSON files.
