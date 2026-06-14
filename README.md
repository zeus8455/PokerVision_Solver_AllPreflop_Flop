# PokerVision Solver AllPreflop Flop

Current development line: **Clear_JSON-only postflop solver engine**.

This repository is maintained as a staged solver-development project:

```text
Discuss scope -> approve subversion -> ZIP overlay -> pytest gate -> commit/push -> checkpoint docs -> Miro card
```

The active postflop solver line is intentionally isolated from real postflop decision/click execution until those layers are explicitly designed and approved.

---

## Current status

**Current closed version:** `V0.12.0 — Preflop Range Import / Range State Foundation`

**Closing subversion:** `V0.12.7 — Close V0.12.0 / README + VERSION Checkpoint`

**Closing checkpoint commit:** created by `V0.12.7 close range state foundation`

**Latest implementation checkpoint before close:** `7ff80ef — V0.12.6 add range architecture gate`

**Latest official postflop cumulative gate:**

```text
594 passed in 18.73s
```

**Next planned version:** `V0.13.0 — Blocker Filtering / Available Combo State`

---

## Official test policy for this development line

The official regression gate for the active Clear_JSON-only postflop line is the cumulative postflop gate:

```powershell
$postflopTests = Get-ChildItem tests -File -Filter "test_postflop_*.py" | Sort-Object Name | ForEach-Object { $_.FullName }
C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe -m pytest $postflopTests -q
```

The raw global `pytest -q` suite is **not** the official gate for this line because it still includes legacy preflop/V2/live/snapshot tests with external runtime/config dependencies.

Those tests are not allowed to block the V0.1+ Clear_JSON-only postflop solver line unless a future version explicitly re-integrates them.

---

## Active architecture after V0.12.0

```text
Existing PokerVision main live runtime
-> Pending postflop Clear_JSON capture hook
-> Live Clear_JSON schema adapter
-> Solver-readable .clear.json artifact
-> Offline postflop audit runner
-> ClearJsonInput
-> SolverInput
-> Branch Resolver
-> FlopContext
-> BoardTextureFeatures
-> MadeHandFeatures
-> DrawFeatures
-> EquityScenarioInput
-> EquityEngine
-> PokerKit backend
-> EquityResult
-> RangeImporter
-> RangeState
```

V0.12.0 adds the baseline range foundation:

```text
FlopContext -> RangeImporter -> RangeState
```

The range layer is **baseline import only**. It selects or imports a starting preflop/postflop baseline range for the current postflop spot family and stores the result as `RangeState`.

---

## Range source status after V0.12.0

### `ranges/hero_preflop_ranges.json`

Detected as an existing project range source:

```text
schema = preflop_ranges_v1
source_type_candidate = existing_project_ranges
contains_range_shorthand_strings = true
contains_combo_level_compact_strings = false
requires_expansion_before_v013 = true
```

This file can remain available as an existing shorthand range source, but it is not enough by itself for V0.13 blocker filtering until shorthand expansion exists.

### `ranges/postflop_default_ranges.json`

Created as a synthetic baseline postflop range pack for V0.12 importer tests:

```text
schema = pokervision_solver_postflop_default_ranges_v1
source_type = postflop_default_ranges
combo_level_compact_string_count = 551
requires_expansion_before_v013 = false
next_module = range_importer_v0124
```

This file provides combo-level compact strings suitable for the next blocker-filtering layer.

---

## Non-negotiable V0.12 policy

V0.12.0 is **RangeState foundation only**.

The range layer may:

- consume `FlopContext`;
- read `spot_family`, `pot_type`, and position context;
- select a baseline source from `ranges/postflop_default_ranges.json`;
- create `RangeState`;
- create HERO/opponent `PlayerRangeState` entries;
- preserve `RangeSourceInfo`;
- preserve combo-level `combo_groups`;
- return structured `unknown_range` without crashing.

The range layer must not create or perform:

- blocker filtering;
- combo removal by HERO cards or board cards;
- range narrowing from flop action;
- texture-based range weighting;
- equity recalculation;
- postflop decision logic;
- bet sizing policy;
- postflop Action_Decision_JSON;
- postflop Action_Runtime_Plan_JSON;
- Action_Button detector calls;
- physical mouse clicks;
- Clear_JSON validation;
- player filtering;
- HERO/opponent invention;
- live source discovery;
- Dark/Pending/Service/Runtime JSON fallback.

`RangeState` is an input for future solver modules. It is **not** a poker decision and does not authorize runtime actions.

---

## Closed version chain

### V0.1.0 — Solver Engine Blueprint / Clear_JSON Input Contract

**Closed by:** `V0.1.5`

**Checkpoint commit:** `00b6b7d`

Created the baseline trusted-input chain:

```text
Clear_JSON -> ClearJsonInput -> SolverInput -> SolverTrace
```

Core policy:

- Clear_JSON is trusted input.
- Solver does not search Dark/Pending/Service/Runtime JSON.
- Solver does not validate cards or player state.
- Solver does not mutate Clear_JSON.

Final gate:

```text
25 passed
```

---

### V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases

**Closed by:** `V0.2.6`

**Checkpoint commit:** `ee56990`

Created the permanent postflop Clear_JSON fixture library:

```text
tests/fixtures/postflop_clear_json/
```

Final gate:

```text
62 passed
```

---

### V0.3.0 — SolverInput Mapping / Field Usage Contract

**Closed by:** `V0.3.6`

**Checkpoint commit:** `4603c68`

Created the official mapping contract:

```text
Clear_JSON field -> SolverInput field -> future solver module
```

Key modules:

- `solver_postflop/field_mapping_contract.py`
- `solver_postflop/field_usage_trace.py`
- `docs/POSTFLOP_CLEAR_JSON_FIELD_MAPPING.md`

Final gate:

```text
94 passed
```

---

### V0.4.0 — Solver Branch Resolver / Street Module Routing

**Closed by:** `V0.4.6`

**Checkpoint commit:** `6da8320`

Created the routing chain:

```text
SolverInput -> Branch Resolver -> SolverBranchResult
```

Routing rules:

```text
0 board cards -> preflop_not_handled
3 board cards -> flop
4 board cards -> turn_not_implemented_yet
5 board cards -> river_not_implemented_yet
missing / 1 / 2 / 6+ -> unsupported
```

Final gate:

```text
125 passed
```

---

### V0.5.0 — Flop Context Builder / Spot Family Layer

**Closed by:** `V0.5.7`

**Checkpoint commit:** `1d7154e`

Created the flop context builder layer:

```text
SolverInput + SolverBranchResult -> FlopContext
```

Final gate:

```text
163 passed
```

---

### V0.6.0 — Board Texture Builder

**Closed by:** `V0.6.7`

**Checkpoint commit:** `341657d`

Created board texture feature extraction for flop boards:

```text
FlopContext -> BoardTextureFeatures
```

Final gate:

```text
205 passed
```

---

### V0.7.0 — Hero Made Hand Classifier

**Closed by:** `V0.7.7`

**Checkpoint commit:** `67e0183`

Created hero made-hand feature classification:

```text
FlopContext + BoardTextureFeatures -> MadeHandFeatures
```

Final gate:

```text
254 passed
```

---

### V0.8.0 — Hero Draw Classifier

**Closed by:** `V0.8.7`

**Checkpoint commit:** `0b787bd`

Created hero draw feature classification:

```text
FlopContext + BoardTextureFeatures + MadeHandFeatures -> DrawFeatures
```

Final gate:

```text
297 passed
```

---

### V0.9.0 — Main Live Clear_JSON Audit / Postflop Capture Evidence

### V0.9.8 — Close V0.9.0 / Live Audit Checkpoint

**Closed by:** `V0.9.8`

**Closing checkpoint:** `6ea2c62 — V0.9.8 close live audit checkpoint`

V0.9.0 integrated the current solver modules with the existing PokerVision live runtime for audit-only evidence:

```text
main live -> postflop Clear_JSON capture -> schema adapter -> audit runner -> V0.1–V0.8 feature chain
```

Final V0.9 live evidence:

```text
evidence_status = passed
total_files_seen = 5
total_clear_json_processed = 5
module_chain_status = flop_features_completed
board_texture = 1
flop_contexts = 1
made_hand = 1
draw_features = 1
runtime_click_chain_status = existing_project_chain_not_invoked_by_audit
errors = []
```

Final V0.9 test gate:

```text
405 passed at V0.9.7.4
```

---

### V0.10.0 — Equity Input Builder / PokerKit Scenario Preparation

**Status:** closed by V0.10.5

**Closing checkpoint:** `bc2408e — V0.10.5 close equity input builder`

V0.10.0 created the equity-input preparation layer:

```text
FlopContext + BoardTextureFeatures + MadeHandFeatures + DrawFeatures -> EquityScenarioInput
```

Subversions:

- `fce43d9` — `V0.10.1 add equity input contracts`
- `3a34f71` — `V0.10.2 add equity input builder`
- `6f47c05` — `V0.10.3 add equity input fixture coverage`
- `ee62827` — `V0.10.4 add equity input architecture gate`
- `bc2408e` — `V0.10.5 close equity input builder`

Final V0.10 targeted gate:

```text
46 passed in 0.44s
```

Final V0.10 postflop cumulative gate:

```text
457 passed in 5.23s
```

Final result:

```text
Clear_JSON -> SolverInput -> Branch Resolver -> FlopContext -> BoardTextureFeatures -> MadeHandFeatures -> DrawFeatures -> EquityScenarioInput
```

V0.10.0 did **not** create PokerKit simulation, equity calculation, ranges, blocker filtering, decision logic, runtime plans, Action_Button calls, clicks, or bet sizing.

---

### V0.11.0 — PokerKit-backed Equity Engine / Raw Equity Snapshot

**Status:** closed by V0.11.10

**Closing checkpoint:** `293f3a2 — V0.11.10 close PokerKit raw equity engine`

V0.11.0 created the first raw-equity calculation layer:

```text
EquityScenarioInput -> Equity Engine -> PokerKit backend -> EquityResult
```

Subversions:

- `9461337` — `V0.11.1 add equity result contracts`
- `9f8ce7b` — `V0.11.2 add PokerKit backend skeleton`
- `b1abe87` — `V0.11.3 add PokerKit capability probe`
- `4240fb5` — `V0.11.4 add equity engine wrapper`
- `a9cc10d` — `V0.11.5 add PokerKit card API probe`
- `6da958b` — `V0.11.6 add first numeric raw equity backend`
- `09b8056` — `V0.11.7 integrate numeric equity engine result`
- `2245820` — `V0.11.8 add equity scenario fixture coverage`
- `e85656b` — `V0.11.9 add equity architecture gate`
- `293f3a2` — `V0.11.10 close PokerKit raw equity engine`

PokerKit local environment:

```text
pokerkit = 0.7.4
```

Final V0.11 targeted gate:

```text
69 passed in 11.07s
```

Final V0.11 postflop cumulative gate:

```text
526 passed in 16.37s
```

Final result:

```text
Clear_JSON -> SolverInput -> Branch Resolver -> FlopContext -> BoardTextureFeatures -> MadeHandFeatures -> DrawFeatures -> EquityScenarioInput -> EquityResult
```

V0.11.0 supports numeric heads-up raw equity.

Multiway is intentionally structured/deferred. V0.11.0 did **not** create ranges, blocker filtering, range narrowing, decisions, runtime plans, Action_Button calls, clicks, or bet sizing.

---

### V0.12.0 — Preflop Range Import / Range State Foundation

**Status:** closed by V0.12.7

**Closing checkpoint:** `V0.12.7 — Close V0.12.0 / README + VERSION Checkpoint`

V0.12.0 created the baseline range-state layer:

```text
FlopContext -> RangeImporter -> RangeState
```

Subversions:

- `e2ae8b0` — `V0.12.1 add range contracts`
- `51b8b8c` — `V0.12.2 add range source inventory`
- `2dc9fb0` — `V0.12.3 add synthetic baseline range pack`
- `f5e1cae` — `V0.12.4 add range importer`
- `4857867` — `V0.12.5 add range state fixture coverage`
- `7ff80ef` — `V0.12.6 add range architecture gate`

Key files:

- `solver_postflop/range_contracts.py`
- `solver_postflop/range_importer.py`
- `ranges/hero_preflop_ranges.json`
- `ranges/postflop_default_ranges.json`
- `tools/run_postflop_range_source_inventory.py`
- `tests/test_postflop_range_contracts_v120.py`
- `tests/test_postflop_range_source_inventory_v120.py`
- `tests/test_postflop_synthetic_baseline_ranges_v120.py`
- `tests/test_postflop_range_importer_v120.py`
- `tests/test_postflop_range_state_from_flop_context_v120.py`
- `tests/test_postflop_range_no_extra_logic_v120.py`
- `tests/fixtures/postflop_range_state_v0125/expected/`
- `docs/POSTFLOP_RANGE_STATE.md`
- `outputs/postflop_range_inventory/latest_range_source_inventory_report.json`

Range source inventory confirmed:

```text
ranges/hero_preflop_ranges.json:
  schema = preflop_ranges_v1
  source_type_candidate = existing_project_ranges
  contains_range_shorthand_strings = true
  contains_combo_level_compact_strings = false
  requires_expansion_before_v013 = true

ranges/postflop_default_ranges.json:
  schema = pokervision_solver_postflop_default_ranges_v1
  source_type = postflop_default_ranges
  combo_level_compact_string_count = 551
  requires_expansion_before_v013 = false
```

Final V0.12 targeted gate:

```text
68 passed in 1.68s
```

Final V0.12 postflop cumulative gate:

```text
594 passed in 18.73s
```

Final result:

```text
Clear_JSON -> SolverInput -> Branch Resolver -> FlopContext -> BoardTextureFeatures -> MadeHandFeatures -> DrawFeatures -> EquityScenarioInput -> EquityResult -> RangeState
```

V0.12.0 did **not** create blocker filtering, combo removal by hero/board cards, range narrowing, equity recalculation, decisions, runtime plans, Action_Button calls, clicks, Clear_JSON validation, player filtering, or fallback to temporary JSON sources.

---

## Current test gate

Run the official postflop cumulative test suite:

```powershell
cd "C:\PokerVision_Solver_AllPreflop_Flop"
$postflopTests = Get-ChildItem tests -File -Filter "test_postflop_*.py" | Sort-Object Name | ForEach-Object { $_.FullName }
C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe -m pytest $postflopTests -q
```

Expected after V0.12.7 overlay:

```text
594 passed
```

---

## Next planned block

### V0.13.0 — Blocker Filtering / Available Combo State

Planned chain:

```text
RangeState + hero_cards + board_cards -> AvailableComboState
```

Scope must be discussed and approved before any V0.13.0 code is written.

Candidate direction:

- introduce combo-state contracts;
- treat HERO cards and board cards as blockers for poker calculation;
- remove blocked combos from `RangeState` into `AvailableComboState`;
- preserve `RangeState` as read-only;
- do not validate or repair Clear_JSON;
- keep range narrowing, equity recalculation, decision/runtime/click out of V0.13.0.
