# V0.2.0 — Source-Based Postflop Fixture Lab Plan


## Goal

Create a source-based postflop fixture lab connected to real PokerVision JSON source types.
This version must not implement solver logic, normalizer, source discovery, player resolver, equity, ranges, poker decisions, runtime click plans, clicking, or runtime changes.

## Required files / folders

- `docs/POSTFLOP_FIXTURE_STRATEGY.md`
- `docs/POSTFLOP_SOURCE_TYPES.md`
- `docs/POSTFLOP_FIXTURE_MANIFEST_RULES.md`
- `tests/fixtures/postflop/manifest.json`
- `tests/fixtures/postflop/source_json/`
- `tests/fixtures/postflop/live_like_tree/`
- `tests/fixtures/postflop/normalized/`
- `tests/fixtures/postflop/expected/`
- `tests/test_postflop_fixture_manifest_v020.py`
- `tests/test_postflop_fixture_structure_v020.py`
- `tests/test_postflop_source_fixture_types_v020.py`

## Allowed source_type values

- `dark_json`
- `pending_json`
- `service_json`
- `current_cycle_json`
- `runtime_json`
- `solver_payload_json`
- `final_clear_json`
- `manual_live_like_json`
- `unknown`

## Mandatory rules

- **Final Clear_JSON is not required:** `False`.
- **manual_live_like_json rule:** Must be marked as manual and never presented as real-source.
- Each fixture case must have `case_id`, `source_type`, `source_file`, `expected_file`, `status`, and source truth metadata.
- `manual_live_like_json` must use `is_manual_live_like_source = true`.
- Real project source JSON must use `is_real_project_source = true` only when it actually comes from project outputs.

## Must not do in V0.2

- postflop solver
- normalizer
- source discovery
- player resolver
- equity
- ranges
- poker decisions
- runtime click plan
- clicking
- runtime changes
