# POSTFLOP_FIXTURE_STRATEGY.md

## Purpose

This document defines the fixture strategy for the postflop development line of:

**PokerVision_Solver_AllPreflop_Flop**

The fixture lab is introduced in **V0.2.0 - Source-Based Postflop Fixture Lab**.
It exists to give future postflop modules a stable, testable source base before any solver, normalizer, player resolver, equity, range, or click-chain logic is added.

The fixture lab must reflect the real PokerVision data flow, not an idealized clean JSON format.

---

## Context from V0.1.0

V0.1.0 audited the current project and established several baseline facts:

- the repository is now **PokerVision_Solver_AllPreflop_Flop**;
- the current codebase still contains the existing **Preflop Solver baseline**;
- the project contains legacy, audit-only, live-only, and core baseline tests;
- the project contains multiple JSON source families, not only Final Clear_JSON;
- many JSON sources exist before click-cycle;
- player-state and filtering logic already exists and must not be duplicated by future postflop modules;
- postflop Final Clear_JSON may be absent without click-cycle.

Therefore, future postflop development must not assume that the only valid input is a perfect final Clear_JSON.

---

## Main strategy

The postflop fixture lab stores source-based cases.

Each case must describe:

```text
case_id
-> source JSON
-> source_type
-> expected JSON
-> optional future normalized JSON
-> test result
```

The purpose is not to solve poker spots.
The purpose is to preserve source data and define what future modules should be able to extract from it.

---

## What V0.2.0 creates

V0.2.0 creates the fixture lab structure:

```text
tests/fixtures/postflop/
  manifest.json
  source_json/
    dark_json/
    pending_json/
    service_json/
    current_cycle_json/
    runtime_json/
    solver_payload_json/
    final_clear_json/
    manual_live_like_json/
  live_like_tree/
  normalized/
  expected/
```

V0.2.0 also defines tests that protect this structure from accidental drift.

---

## Source-first rule

The fixture lab is source-first.

A fixture case is valid when it has:

- a manifest entry;
- a valid `source_type`;
- an existing `source_file`;
- an existing `expected_file`;
- explicit real/manual source flags;
- a clear note about whether click-cycle is required.

A fixture case is not required to have a final normalized output in V0.2.0, because the normalizer will be created later.

---

## Final Clear_JSON is optional

Final Clear_JSON is supported as a source type, but it is not required.

This is a core rule of the postflop line:

```text
Final Clear_JSON is one possible source, not the only source of truth.
```

Reason:

- postflop Final Clear_JSON may only appear after click-cycle;
- source discovery must be able to operate before click-cycle;
- live-cycle may expose useful intermediate JSON before finalization;
- future postflop tests must be able to use dark/pending/current/runtime/solver-payload sources.

---

## Manual live-like sources

Manual live-like JSON is allowed, but it must never be presented as a real project source.

If a source JSON is manually created or edited to imitate live-cycle output, then:

```json
{
  "is_manual_live_like_source": true,
  "is_real_project_source": false
}
```

The source must also include a clear `source_of_truth_note` in the manifest.

---

## Expected JSON rule

Expected JSON in V0.2.0 does not contain poker decisions.

It only describes source characteristics and future-normalizer expectations:

- expected source type;
- whether board cards are present;
- whether hero cards are present;
- whether players are present;
- whether actions are present;
- street candidate;
- required fields expected to be present;
- whether future normalizer can use the source;
- whether click-cycle is required;
- notes.

---

## What V0.2.0 must not do

V0.2.0 must not implement:

- source discovery;
- normalizer;
- source contracts;
- street detector;
- preflop history recovery;
- player resolver;
- player filtering;
- equity calculation;
- range building;
- poker decisions;
- runtime click plans;
- click execution;
- PokerVision runtime changes.

Those modules belong to later versions.

---

## Relationship to later versions

### V0.3.0 - Postflop Source Contracts

V0.3.0 will define strict data contracts:

```text
SourceCandidate -> RawSource -> NormalizedPostflopFrame -> warnings/errors -> future trace
```

### V0.4.0 - Source Discovery + Postflop Normalizer

V0.4.0 will read fixture sources and produce normalized frames.

V0.2.0 must prepare the source lab so these later modules have stable input data.

---

## Acceptance rule

V0.2.0 is successful when pytest confirms:

```text
manifest is valid
-> source files exist
-> expected files exist
-> source_type is valid
-> Final Clear_JSON is optional
-> manual sources are not mixed with real sources
-> fixture directory structure is stable
```
