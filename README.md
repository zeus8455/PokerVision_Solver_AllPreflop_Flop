# PokerVision Solver AllPreflop Flop

Current development line: **Clear_JSON-only postflop solver engine**.

This repository is maintained as a staged solver-development project:

```text
Discuss scope -> approve subversion -> ZIP overlay -> pytest gate -> commit/push -> checkpoint docs -> Miro card
```

The active postflop solver line is intentionally isolated from real postflop decision/click execution until those layers are explicitly designed and approved.

---

## Current status

**Current closed version:** `V0.9.0 — Main Live Clear_JSON Audit / Postflop Capture Evidence`

**Closing subversion:** `V0.9.8 — Close V0.9.0 / Live Audit Checkpoint`

**Closing checkpoint commit:** created by `V0.9.8 close live audit checkpoint`

**Latest code gate before close:** `405 passed` at `V0.9.7.4`

**Latest live evidence:** passed after V0.9.7.4

```text
evidence_status = passed
total_files_seen = 5
total_clear_json_processed = 5
module_chain_status = flop_features_completed
artifacts_written.board_texture = 1
artifacts_written.flop_contexts = 1
artifacts_written.made_hand = 1
artifacts_written.draw_features = 1
runtime_click_chain_status = existing_project_chain_not_invoked_by_audit
errors = []
```

**Next planned version:** `V0.10.0 — to be discussed before implementation`

---

## Active architecture after V0.9.0

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
```

The V0.9 audit layer proves that the existing project can generate live postflop Clear_JSON artifacts that are readable by the current V0.1–V0.8 solver modules.

---

## Non-negotiable V0.9 policy

V0.9.0 is **audit-only** for the postflop solver line.

The postflop solver/audit layer must not create or perform:

- postflop poker decisions;
- postflop Action_Decision_JSON;
- postflop Action_Runtime_Plan_JSON;
- Action_Button detector calls;
- physical mouse clicks;
- equity calculations;
- range calculations;
- bet sizing policy.

The existing PokerVision live click-chain may still exist in the wrapped project, but the postflop solver line does not invoke it in V0.9.0.

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
- `V0.9.8` — `close live audit checkpoint`

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

## Current test gate

Run the full current test suite:

```powershell
C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe -m pytest tests -q
```

Expected after V0.9.8 overlay:

```text
411 passed
```

---

## Next planned block

### V0.10.0 — to be discussed before implementation

No V0.10.0 code should be written until its scope is explicitly discussed and approved.

Candidate discussion areas:

- whether to begin a postflop decision-input contract;
- whether to add turn/river feature placeholders or real modules;
- whether to formalize range/equity inputs;
- whether to keep V0.10 audit-only or start decision blueprint work.
