# PokerVision Solver AllPreflop Flop

Current development line: **Clear_JSON-only postflop solver engine**.

This repository is maintained as a staged solver-development project:

```text
Discuss scope -> approve subversion -> ZIP overlay -> pytest gate -> commit/push -> checkpoint docs -> Miro card
```

The active postflop solver line is intentionally isolated from real postflop decision/click execution until those layers are explicitly designed and approved.

---

## Current status

**Current closed version:** `V0.11.0 — PokerKit-backed Equity Engine / Raw Equity Snapshot`

**Closing subversion:** `V0.11.10 — Close V0.11.0 / README + VERSION Checkpoint`

**Closing checkpoint commit:** created by `V0.11.10 close PokerKit raw equity engine`

**Latest implementation checkpoint before close:** `e85656b — V0.11.9 add equity architecture gate`

**Latest official postflop cumulative gate:**

```text
526 passed in 17.88s
```

**Next planned version:** `V0.12.0 — Preflop Range Import / Range State Foundation`

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

## Active architecture after V0.11.0

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
```

V0.11.0 adds the first raw-equity calculation layer:

```text
EquityScenarioInput -> Equity Engine -> PokerKit backend -> EquityResult
```

V0.11.0 supports **numeric heads-up raw equity** through local PokerKit `0.7.4`.

Multiway equity is intentionally left as a **structured deferred result**. Unknown or unsupported contexts are also structured results, not pipeline crashes.

---

## Non-negotiable V0.11 policy

V0.11.0 is **raw equity snapshot only**.

The equity layer may:

- consume `EquityScenarioInput`;
- call the isolated PokerKit backend adapter;
- calculate numeric heads-up raw equity;
- return `EquityResult`;
- preserve backend metadata, sample counts, confidence, notes, and structured unavailable/error states.

The equity layer must not create or perform:

- opponent range construction;
- range narrowing from action history;
- blocker filtering as a range module;
- postflop decision logic;
- bet sizing policy;
- postflop Action_Decision_JSON;
- postflop Action_Runtime_Plan_JSON;
- Action_Button detector calls;
- physical mouse clicks;
- Clear_JSON validation;
- duplicate-card validation as source validation;
- player filtering;
- HERO/opponent invention;
- live source discovery;
- Dark/Pending/current_cycle fallback.

`hero_equity` is a numeric input for future solver modules. It is **not** a poker decision.

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

**Closed by:** `V0.9.8`

**Closing checkpoint:** `V0.9.8 — Close V0.9.0 / Live Audit Checkpoint`

V0.9.0 integrated the current solver modules with the existing PokerVision live runtime for audit-only evidence:

```text
main live -> postflop Clear_JSON capture -> schema adapter -> audit runner -> V0.1–V0.8 feature chain
```

Subversions:

- `bf062c5` — `V0.9.1 add live audit report contracts`
- `6928575` — `V0.9.2 add Clear_JSON discovery gate`
- `0fabc40` — `V0.9.3 add Clear_JSON module pipeline runner`
- `54e4f55` — `V0.9.4 add Clear_JSON capture hook audit`
- `813dd5f` — `V0.9.5 add Clear_JSON audit tool runner`
- `3b17f9f` — `V0.9.6 add no postflop click architecture gate`
- `eb7fed5` — `V0.9.7 document main live Clear_JSON audit command`
- `cca11f0` — `V0.9.7.1 integrate runtime Clear_JSON capture hook`
- `52738bc` — `V0.9.7.2 add pending postflop Clear_JSON capture`
- `14289f5` — `V0.9.7.3 adapt live Clear_JSON schema for postflop audit`
- `5e315c8` — `V0.9.7.4 add live audit hygiene gate`
- `6ea2c62` — `V0.9.8 close live audit checkpoint`

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

Key files:

- `solver_postflop/equity_input_contracts.py`
- `solver_postflop/equity_input.py`
- `tests/test_postflop_equity_input_contracts_v100.py`
- `tests/test_postflop_equity_input_builder_v100.py`
- `tests/test_postflop_equity_input_from_fixtures_v100.py`
- `tests/test_postflop_equity_input_no_extra_logic_v100.py`
- `tests/fixtures/postflop_equity_input_v0103/`
- `docs/POSTFLOP_EQUITY_INPUT.md`

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

**Closing checkpoint:** `V0.11.10 — Close V0.11.0 / README + VERSION Checkpoint`

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

Key files:

- `solver_postflop/equity_contracts.py`
- `solver_postflop/equity_backend_pokerkit.py`
- `solver_postflop/equity_engine.py`
- `tools/run_pokerkit_capability_probe.py`
- `tools/run_pokerkit_card_api_probe.py`
- `tests/test_postflop_equity_contracts_v110.py`
- `tests/test_postflop_equity_backend_pokerkit_v110.py`
- `tests/test_postflop_pokerkit_capability_probe_v110.py`
- `tests/test_postflop_pokerkit_card_api_probe_v110.py`
- `tests/test_postflop_equity_backend_numeric_v110.py`
- `tests/test_postflop_equity_engine_v110.py`
- `tests/test_postflop_equity_engine_numeric_integration_v110.py`
- `tests/test_postflop_equity_from_scenarios_v110.py`
- `tests/test_postflop_equity_no_extra_logic_v110.py`
- `docs/POSTFLOP_EQUITY_ENGINE.md`
- `outputs/postflop_pokerkit_capability/latest_pokerkit_capability_report.json`
- `outputs/postflop_pokerkit_card_api/latest_pokerkit_card_api_report.json`

PokerKit local environment:

```text
pokerkit = 0.7.4
```

Capability probe confirmed:

```text
status = available
available_symbols = NoLimitTexasHoldem, Automation, Mode, State, StandardHighHand, Card, Rank, Suit, Deck
```

Card API probe confirmed:

```text
A_spades -> As
K_hearts -> Kh
10_spades -> Ts
StandardHighHand.from_game(...) = ok
example = Straight (AsKhQdJcTs)
```

Final V0.11 targeted gate:

```text
69 passed in 10.90s
```

Final V0.11 postflop cumulative gate:

```text
526 passed in 17.88s
```

Final result:

```text
Clear_JSON -> SolverInput -> Branch Resolver -> FlopContext -> BoardTextureFeatures -> MadeHandFeatures -> DrawFeatures -> EquityScenarioInput -> EquityResult
```

V0.11.0 supports numeric heads-up raw equity. Multiway is intentionally structured/deferred. V0.11.0 did **not** create ranges, blocker filtering, range narrowing, decisions, runtime plans, Action_Button calls, clicks, or bet sizing.

---

## Current test gate

Run the official postflop cumulative test suite:

```powershell
cd "C:\PokerVision_Solver_AllPreflop_Flop"
$postflopTests = Get-ChildItem tests -File -Filter "test_postflop_*.py" | Sort-Object Name | ForEach-Object { $_.FullName }
C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe -m pytest $postflopTests -q
```

Expected after V0.11.10 overlay:

```text
526 passed
```

---

## Next planned block

### V0.12.0 — Preflop Range Import / Range State Foundation

Scope must be discussed and approved before any V0.12.0 code is written.

Candidate direction:

- introduce range result contracts;
- import/select baseline range source by spot family;
- create `RangeState` without blocker filtering;
- keep equity-range integration for later versions;
- keep decision/runtime/click out of V0.12.0.
