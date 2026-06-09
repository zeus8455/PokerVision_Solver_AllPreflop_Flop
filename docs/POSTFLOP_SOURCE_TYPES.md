# POSTFLOP_SOURCE_TYPES.md

## Purpose

This document defines the allowed postflop fixture source types for:

**PokerVision_Solver_AllPreflop_Flop**

These source types are introduced for **V0.2.0 - Source-Based Postflop Fixture Lab** and must be reused by future postflop contracts and source discovery modules.

---

## Allowed source types

The allowed source types are:

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

No other source type should be added without an explicit versioned change.

---

## dark_json

**Meaning:** raw or near-raw PokerVision analysis output before it becomes a final clear state.

**Typical use:** early postflop source case when Final Clear_JSON is not available.

**Click-cycle requirement:** usually false.

**Postflop value:** high, because it may contain board/player/table state before final click-cycle.

---

## pending_json

**Meaning:** Clear_JSON_Pending or pending intermediate state before finalization.

**Typical use:** source candidate before click result.

**Click-cycle requirement:** usually false.

**Postflop value:** high, but source may be partially cleaned and should be checked carefully.

---

## service_json

**Meaning:** JSON related to Trigger_UI, service state, table status, active state, or UI service diagnostics.

**Typical use:** determine whether the table state was active/valid or skipped.

**Click-cycle requirement:** usually false.

**Postflop value:** medium. It may not contain full poker data, but it may explain why a spot is valid or invalid.

---

## current_cycle_json

**Meaning:** JSON from current UI/live-cycle folders.

**Typical use:** source candidate for live-like state before final output.

**Click-cycle requirement:** usually false.

**Postflop value:** high, because it may reflect the actual runtime state during an Active cycle.

---

## runtime_json

**Meaning:** runtime diagnostic or runtime state JSON.

**Typical use:** understand how a candidate moved through runtime, bridge, or click-planning layers.

**Click-cycle requirement:** can be true or false depending on file role.

**Postflop value:** medium. It may contain useful action context but is not guaranteed to contain full table state.

---

## solver_payload_json

**Meaning:** payload sent into or produced near solver bridge/runtime planning.

**Typical use:** inspect what data was passed into solver-related modules.

**Click-cycle requirement:** usually before final click, but depends on pipeline stage.

**Postflop value:** medium to high. Useful if it contains board, hero, player, pot, or allowed action context.

---

## final_clear_json

**Meaning:** final Clear_JSON or JSON_Complete after finalization/click-result stage.

**Typical use:** clean post-click reference source.

**Click-cycle requirement:** often true.

**Postflop value:** high, but it must not be treated as mandatory.

Core rule:

```text
final_clear_json is allowed, but it is not required for V0.2.0.
```

---

## manual_live_like_json

**Meaning:** manually created or edited JSON that imitates real PokerVision live-cycle output.

**Typical use:** fixture coverage when real source is missing but future module behavior needs a stable input.

**Click-cycle requirement:** depends on the case.

**Postflop value:** useful for tests, but it is not a real project source.

Required manifest flags:

```json
{
  "is_manual_live_like_source": true,
  "is_real_project_source": false
}
```

Manual live-like sources must always include notes explaining their origin.

---

## unknown

**Meaning:** JSON file exists, but its source family is not confidently identified.

**Typical use:** preserve potentially useful data without pretending it is a known source type.

**Click-cycle requirement:** unknown unless specified by case notes.

**Postflop value:** review-only until classified later.

Required manifest behavior:

- must include notes;
- must not be treated as source of truth;
- must not block fixture lab if handled explicitly.

---

## Source type rules

Each manifest case must have exactly one `source_type`.

The source type must be one of the allowed values.

A source type must not be inferred silently when creating fixture cases manually. If uncertain, use:

```text
unknown
```

and add a clear note.

---

## Real vs manual rule

A source can be either real project source or manual live-like source.

Valid examples:

```json
{
  "is_real_project_source": true,
  "is_manual_live_like_source": false
}
```

```json
{
  "is_real_project_source": false,
  "is_manual_live_like_source": true
}
```

Invalid example:

```json
{
  "is_real_project_source": true,
  "is_manual_live_like_source": true
}
```

This is ambiguous and must fail manifest validation.

---

## Future reuse

The same source type list must be reused by:

- V0.2 fixture manifest tests;
- V0.3 postflop contracts;
- V0.4 source discovery;
- V0.4 source adapter;
- V0.4 frame normalizer.
