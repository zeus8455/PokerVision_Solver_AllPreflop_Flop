# VERSION

Project: **PokerVision_Solver_AllPreflop_Flop**

Development line: **Clear_JSON-only postflop solver engine**

---

## Current status

**Current closed version:** `V0.11.0 — PokerKit-backed Equity Engine / Raw Equity Snapshot`

**Closing subversion:** `V0.11.10 — Close V0.11.0 / README + VERSION Checkpoint`

**Latest implementation checkpoint before close:** `e85656b — V0.11.9 add equity architecture gate`

**Latest official postflop cumulative gate:** `526 passed in 17.88s`

**PokerKit local version:** `0.7.4`

**Next planned version:** `V0.12.0 — Preflop Range Import / Range State Foundation`

---

## Baseline

### Initial repository baseline

- `db16abd` — `initial snapshot: Real_Version_SolverPreflop as AllPreflop_Flop baseline`

---

## V0.1.0 — Solver Engine Blueprint / Clear_JSON Input Contract

**Status:** closed

**Closing checkpoint:** `00b6b7d — V0.1.5 close solver engine blueprint`

### Subversions

- `7fe5b4d` — `V0.1.1 add postflop engine contracts baseline`
- `1a4a2eb` — `V0.1.2 add Clear_JSON trusted input loader`
- `e80a582` — `V0.1.3 add SolverInput mapping baseline`
- `73163d9` — `V0.1.4 add postflop no-fallback architecture gate`
- `00b6b7d` — `V0.1.5 close solver engine blueprint`

### Final gate

```text
25 passed
```

### Final result

```text
Clear_JSON -> ClearJsonInput -> SolverInput -> SolverTrace
```

---

## V0.2.0 — Clear_JSON Fixture Library / Real + Synthetic Solver Cases

**Status:** closed

**Closing checkpoint:** `ee56990 — V0.2.6 close Clear_JSON fixture library`

### Subversions

- `c2fa1a8` — `V0.2.1 add Clear_JSON fixture library docs`
- `d648478` — `V0.2.2 add Clear_JSON fixture skeleton`
- `fa9c509` — `V0.2.3 add minimum Clear_JSON fixture cases`
- `0050a9f` — `V0.2.4 add expected Clear_JSON interpretations`
- `901aee5` — `V0.2.5 add Clear_JSON fixture manifest gate`
- `ee56990` — `V0.2.6 close Clear_JSON fixture library`

### Final gate

```text
62 passed
```

---

## V0.3.0 — SolverInput Mapping / Field Usage Contract

**Status:** closed

**Closing checkpoint:** `4603c68 — V0.3.6 close SolverInput mapping contract`

### Subversions

- `66bd6a1` — `V0.3.1 add postflop field mapping contract`
- `00de073` — `V0.3.2 add postflop field usage trace`
- `99674e1` — `V0.3.3 bind SolverInput mapping to field contract`
- `cba0daa` — `V0.3.4 add postflop no-validation mapping gate`
- `7a3dfce` — `V0.3.5 document Clear_JSON field mapping`
- `4603c68` — `V0.3.6 close SolverInput mapping contract`

### Final gate

```text
94 passed
```

---

## V0.4.0 — Solver Branch Resolver / Street Module Routing

**Status:** closed

**Closing checkpoint:** `6da8320 — V0.4.6 close branch resolver routing`

### Subversions

- `9fc9cee` — `V0.4.1 add postflop branch contracts`
- `54ac7c5` — `V0.4.2 add postflop branch resolver baseline`
- `21b087f` — `V0.4.3 add fixture-backed branch routing`
- `ab77eb1` — `V0.4.4 add branch resolver no-extra-checks gate`
- `209beb3` — `V0.4.5 document postflop branch resolver`
- `6da8320` — `V0.4.6 close branch resolver routing`

### Final gate

```text
125 passed
```

---

## V0.5.0 — Flop Context Builder / Spot Family Layer

**Status:** closed

**Closing checkpoint:** `1d7154e — V0.5.7 close flop context builder`

### Subversions

- `a4a3567` — `V0.5.1 add flop context contracts`
- `5d10849` — `V0.5.2 add flop context builder baseline`
- `377832c` — `V0.5.3 add flop spot family classifier`
- `ed3504f` — `V0.5.4 add fixture-backed flop context`
- `0fed29c` — `V0.5.5 add flop context no-extra-logic gate`
- `aa33c9b` — `V0.5.6 document flop context builder`
- `1d7154e` — `V0.5.7 close flop context builder`

### Final gate

```text
163 passed
```

---

## V0.6.0 — Board Texture Builder

**Status:** closed

**Closing checkpoint:** `341657d — V0.6.7 close board texture builder`

### Subversions

- `d648100` — `V0.6.1 add board texture contracts`
- `19013a6` — `V0.6.2 add board texture builder baseline`
- `247738e` — `V0.6.3 add board texture classification matrix`
- `9b2729a` — `V0.6.4 add fixture-backed board texture cases`
- `89a3985` — `V0.6.5 add board texture no-extra-logic gate`
- `ed3ce55` — `V0.6.6 document board texture builder`
- `341657d` — `V0.6.7 close board texture builder`

### Final gate

```text
205 passed
```

---

## V0.7.0 — Hero Made Hand Classifier

**Status:** closed

**Closing checkpoint:** `67e0183 — V0.7.7 close hero made hand classifier`

### Subversions

- `2001c6e` — `V0.7.1 add hero made hand contracts`
- `2f7ecdc` — `V0.7.2 add hero made hand classifier baseline`
- `2142871` — `V0.7.3 add hero made hand pair strength matrix`
- `a650eb8` — `V0.7.4 add fixture-backed hero made hand cases`
- `daa1923` — `V0.7.5 add hero made hand no-extra-logic gate`
- `adb6b14` — `V0.7.6 document hero made hand classifier`
- `67e0183` — `V0.7.7 close hero made hand classifier`

### Final gate

```text
254 passed
```

---

## V0.8.0 — Hero Draw Classifier

**Status:** closed

**Closing checkpoint:** `0b787bd — V0.8.7 close hero draw classifier`

### Subversions

- `87ab817` — `V0.8.1 add hero draw contracts`
- `05b4f4d` — `V0.8.2 add hero draw classifier baseline`
- `2051e9a` — `V0.8.3 add hero draw combo strength matrix`
- `8dac329` — `V0.8.4 add fixture-backed hero draw cases`
- `762e729` — `V0.8.5 add hero draw no-extra-logic gate`
- `41c3261` — `V0.8.6 document hero draw classifier`
- `0b787bd` — `V0.8.7 close hero draw classifier`

### Final gate

```text
297 passed
```

---

## V0.9.0 — Main Live Clear_JSON Audit / Postflop Capture Evidence

**Status:** closed by V0.9.8

**Closing checkpoint:** `6ea2c62 — V0.9.8 close live audit checkpoint`

### Subversions

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

### Final live evidence

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

### Final code gate before close

```text
405 passed at V0.9.7.4
```

### Final result

```text
Clear_JSON -> SolverInput -> Branch Resolver -> FlopContext -> BoardTexture -> MadeHand -> DrawFeatures
```

V0.9.0 did **not** create postflop decisions, runtime plans, Action_Button calls, clicks, equity, ranges, or bet sizing.

---

## V0.10.0 — Equity Input Builder / PokerKit Scenario Preparation

**Status:** closed by V0.10.5

**Closing checkpoint:** `bc2408e — V0.10.5 close equity input builder`

### Subversions

- `fce43d9` — `V0.10.1 add equity input contracts`
- `3a34f71` — `V0.10.2 add equity input builder`
- `6f47c05` — `V0.10.3 add equity input fixture coverage`
- `ee62827` — `V0.10.4 add equity input architecture gate`
- `bc2408e` — `V0.10.5 close equity input builder`

### Final targeted gate

```text
46 passed in 0.44s
```

### Final postflop cumulative gate

```text
457 passed in 5.23s
```

### Final result

```text
Clear_JSON -> SolverInput -> Branch Resolver -> FlopContext -> BoardTextureFeatures -> MadeHandFeatures -> DrawFeatures -> EquityScenarioInput
```

V0.10.0 did **not** calculate equity, import PokerKit in the equity input layer, build ranges, create decisions, create runtime plans, or click.

---

## V0.11.0 — PokerKit-backed Equity Engine / Raw Equity Snapshot

**Status:** closed by V0.11.10

**Closing checkpoint:** `V0.11.10 — Close V0.11.0 / README + VERSION Checkpoint`

### Subversions

- `9461337` — `V0.11.1 add equity result contracts`
- `9f8ce7b` — `V0.11.2 add PokerKit backend skeleton`
- `b1abe87` — `V0.11.3 add PokerKit capability probe`
- `4240fb5` — `V0.11.4 add equity engine wrapper`
- `a9cc10d` — `V0.11.5 add PokerKit card API probe`
- `6da958b` — `V0.11.6 add first numeric raw equity backend`
- `09b8056` — `V0.11.7 integrate numeric equity engine result`
- `2245820` — `V0.11.8 add equity scenario fixture coverage`
- `e85656b` — `V0.11.9 add equity architecture gate`

### PokerKit local environment

```text
pokerkit = 0.7.4
```

### Capability probe

```text
status = available
available_symbols = NoLimitTexasHoldem, Automation, Mode, State, StandardHighHand, Card, Rank, Suit, Deck
```

### Card API probe

```text
A_spades -> As
K_hearts -> Kh
10_spades -> Ts
StandardHighHand.from_game(...) = ok
example = Straight (AsKhQdJcTs)
```

### Final targeted gate

```text
69 passed in 10.90s
```

### Final postflop cumulative gate

```text
526 passed in 17.88s
```

### Final result

```text
Clear_JSON -> SolverInput -> Branch Resolver -> FlopContext -> BoardTextureFeatures -> MadeHandFeatures -> DrawFeatures -> EquityScenarioInput -> EquityResult
```

V0.11.0 supports numeric heads-up raw equity through local PokerKit. Multiway is intentionally structured/deferred. V0.11.0 did **not** create ranges, blocker filtering, range narrowing, decisions, runtime plans, Action_Button calls, clicks, or bet sizing.

---

## Next planned version

### V0.12.0 — Preflop Range Import / Range State Foundation

Scope must be discussed and approved before any V0.12.0 code is written.
