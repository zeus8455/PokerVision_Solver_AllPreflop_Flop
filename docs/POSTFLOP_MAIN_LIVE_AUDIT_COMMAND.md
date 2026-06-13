# V0.9.7.4 — Main/Live Audit Command / Hygiene Command

## Purpose

This document fixes the V0.9 live-audit command so the run is reproducible and not polluted by stale files from previous attempts.

The V0.9 live audit proves only this technical chain:

**main.py live → postflop Clear_JSON capture → schema adapter → audit runner → Clear_JSON → SolverInput → Branch Resolver → FlopContext → BoardTextureFeatures → MadeHandFeatures → DrawFeatures**

It does not prove postflop poker decisions, bet sizing, equity, ranges, Action_Button execution, or postflop clicks. Pytest remains safe and non-interactive.

---

## Non-negotiable rule

**Existing project live click-chain is allowed during the live audit.**

**Postflop solver click-chain is prohibited in V0.9.0.**

The postflop solver/audit layer must not create:

- postflop decisions
- postflop Action_Decision_JSON
- postflop Action_Runtime_Plan_JSON
- Action_Button detector calls
- physical mouse clicks
- equity calculations
- range calculations

---

## Why cleanup is mandatory

The capture folder can contain `.clear.json` files created by older capture versions. Those stale files may not contain the V0.9.7.3 solver-compatible aliases:

- `board_cards`
- `hero_cards`
- `hero_id`
- `total_pot`
- `table_id`
- `hand_id`

If stale files remain, the report can mix old broken files with new valid files and produce misleading `preflop_not_handled` results.

Before every V0.9 live audit, clean both roots:

- `outputs\postflop_live_clear_json_audit_v090`
- `external\PokerVisionFinalVersionNoSolver_snapshot\PokerVision V1_2\outputs\postflop_live_clear_json`

---

## Real-live audit command

Run this from the repository root:

```powershell
cd "C:\PokerVision_Solver_AllPreflop_Flop"

Write-Host "`n=== PRE-RUN GIT CHECK ==="
git status --short
git log --oneline --decorate --max-count=8

Write-Host "`n=== CLEAN STALE AUDIT/CAPTURE OUTPUTS ==="
Remove-Item "outputs\postflop_live_clear_json_audit_v090" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "external\PokerVisionFinalVersionNoSolver_snapshot\PokerVision V1_2\outputs\postflop_live_clear_json" -Recurse -Force -ErrorAction SilentlyContinue

$env:POKERVISION_CONTROLLED_LIVE_READY_PROFILE = "V8_1_CONTROLLED_ACTION_BUTTON"
$env:POKERVISION_CONTROLLED_LIVE_CLICK = "V3_1_ONE_CLICK"
$env:POKERVISION_CONTROLLED_LIVE_TEST_SCOPE = "V8_7_FULL_LIVE_CHAIN_NO_LIMIT"
$env:POKERVISION_CONTROLLED_LIVE_CLICK_TABLE_IDS = "table_01,table_02,table_03,table_04,table_05,table_06"

Remove-Item Env:\POKERVISION_CONTROLLED_LIVE_CLICK_MAX_CLICKS_PER_RUN -ErrorAction SilentlyContinue

$python = "C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe"

Write-Host "`n=== PHASE 1: RUN EXISTING PROJECT MAIN/LIVE CYCLE ==="
Write-Host "The existing project click-chain is allowed."
Write-Host "Postflop solver decision/runtime/click is prohibited."
& $python tools\run_live_main_with_postflop_capture_v0972.py

$clearJsonRoot = "external\PokerVisionFinalVersionNoSolver_snapshot\PokerVision V1_2\outputs\postflop_live_clear_json"

Write-Host "`n=== CLEAR FILES ==="
Get-ChildItem $clearJsonRoot -Recurse -File -Filter "*.clear.json" |
    Sort-Object LastWriteTime -Descending |
    Select-Object FullName, Length, LastWriteTime |
    Format-List

Write-Host "`n=== PHASE 2: RUN POSTFLOP CLEAR_JSON AUDIT ==="
& $python `
  tools\run_postflop_live_clear_json_audit_v090.py `
  --project-root . `
  --clear-json-root $clearJsonRoot `
  --output-root "outputs\postflop_live_clear_json_audit_v090" `
  --max-files 50

if ($LASTEXITCODE -ne 0) {
    throw "Postflop Clear_JSON audit runner failed."
}

$report = "outputs\postflop_live_clear_json_audit_v090\latest_report.json"
$toolResult = "outputs\postflop_live_clear_json_audit_v090\tool_result.json"

Write-Host "`n=== PHASE 3: VERIFY AUDIT OUTPUT ==="
Write-Host "`n=== VERIFY REPORT FILES ==="
if (!(Test-Path $report)) { throw "latest_report.json was not created: $report" }
if (!(Test-Path $toolResult)) { throw "tool_result.json was not created: $toolResult" }
Get-Item $report, $toolResult | Format-List FullName, Length, LastWriteTime

Write-Host "`n=== VERIFY V0.9 LIVE EVIDENCE ==="
$tool = Get-Content $toolResult -Raw | ConvertFrom-Json

if ($tool.total_files_seen -le 0) { throw "Evidence failed: total_files_seen must be > 0" }
if ($tool.total_clear_json_processed -le 0) { throw "Evidence failed: total_clear_json_processed must be > 0" }
if ($tool.module_chain_status -ne "flop_features_completed") { throw "Evidence failed: module_chain_status must be flop_features_completed" }
if ($tool.artifacts_written.board_texture -le 0) { throw "Evidence failed: board_texture must be > 0" }
if ($tool.artifacts_written.made_hand -le 0) { throw "Evidence failed: made_hand must be > 0" }
if ($tool.artifacts_written.draw_features -le 0) { throw "Evidence failed: draw_features must be > 0" }
if ($tool.runtime_click_chain_status -ne "existing_project_chain_not_invoked_by_audit") { throw "Evidence failed: runtime_click_chain_status mismatch" }
if ($tool.errors.Count -ne 0) { throw "Evidence failed: tool_result.errors is not empty" }
if ($tool.evidence_status -ne "passed") { throw "Evidence failed: evidence_status must be passed" }

Write-Host "V0.9 live evidence PASSED."

Write-Host "`n=== GIT STATUS AFTER LIVE AUDIT ==="
git status --short
```

---


## Clear_JSON-only input policy

The postflop audit runner accepts only solver-readable Clear_JSON candidates.

Accepted target pattern:

- `*.clear.json`
- files classified by V0.9.2 discovery as `clear_json`

Rejected as solver input:

- Dark_JSON
- Pending_JSON
- Service_JSON
- Runtime_JSON
- Action_Decision_JSON
- Action_Runtime_Plan_JSON
- Button detector JSON
- temporary project/runtime artifacts

The runner must not use Dark/Pending/Service/Runtime JSON as fallback solver input.

---

## What to verify after the run

Check the report for these points:

1. Clear_JSON files were found.
2. Each processed source has `source_file`.
3. `branch` is present. In report language: branch is present.
4. Flop Clear_JSON reaches DrawFeatures through FlopContext, BoardTextureFeatures, and MadeHandFeatures.
5. Non-flop Clear_JSON gets a structured skipped/partial/unsupported report.
6. Bad Clear_JSON does not break the full report.
7. `fields_used` and `fields_not_provided` are preserved.
8. `runtime_click_chain_status` remains audit-safe.
9. The postflop solver does not produce Action_Decision_JSON.
10. The postflop solver does not produce Action_Runtime_Plan_JSON.
11. The postflop solver does not call Action_Button detector.
12. The postflop solver does not perform physical mouse clicks and does not click.
13. The audit runner does not launch UI and does not click.

---

## Audit runner command only

If fresh `.clear.json` files already exist, run only the offline audit phase:

```powershell
cd "C:\PokerVision_Solver_AllPreflop_Flop"

C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe `
  tools\run_postflop_live_clear_json_audit_v090.py `
  --project-root . `
  --clear-json-root "external\PokerVisionFinalVersionNoSolver_snapshot\PokerVision V1_2\outputs\postflop_live_clear_json" `
  --output-root "outputs\postflop_live_clear_json_audit_v090" `
  --max-files 50
```

This audit runner is offline. It does not start main.py, does not launch UI, does not call Action_Button, and does not click.

---
## Expected evidence

A successful V0.9 live-audit report must prove:

- `total_files_seen > 0`
- `total_clear_json_processed > 0`
- `module_chain_status = flop_features_completed`
- `artifacts_written.board_texture > 0`
- `artifacts_written.made_hand > 0`
- `artifacts_written.draw_features > 0`
- `runtime_click_chain_status = existing_project_chain_not_invoked_by_audit`
- `errors = []`
- `evidence_status = passed`

Turn and river may be present, but they are expected to route to structured placeholders until turn/river modules exist.

---

## Expected output

Main report:

`outputs/postflop_live_clear_json_audit_v090/latest_report.json`

Windows path:

`outputs\postflop_live_clear_json_audit_v090\latest_report.json`

Tool summary and evidence status:

`outputs\postflop_live_clear_json_audit_v090\tool_result.json`

Expected artifact subfolders:

- `processed_clear_json/`
- `solver_inputs/`
- `branch_results/`
- `flop_contexts/`
- `board_texture/`
- `made_hand/`
- `draw_features/`
- `module_chain_reports/`

---

## Handoff to V0.9.8

After this command produces `evidence_status = passed`, V0.9.0 can be closed in V0.9.8 with README, VERSION, and checkpoint/Miro documentation.

Correct handoff to V0.9.8:

1. Run the documented real-live audit locally.
2. Inspect `outputs/postflop_live_clear_json_audit_v090/latest_report.json`.
3. Confirm whether live Clear_JSON appeared.
4. Confirm whether V0.1–V0.8 modules worked on live Clear_JSON.
5. Confirm whether no postflop decision/runtime/click artifacts were created.
6. Then close V0.9.0 in V0.9.8.

If live Clear_JSON or evidence is missing, the next action is a focused capture-hook integration fix before closing V0.9.0.
