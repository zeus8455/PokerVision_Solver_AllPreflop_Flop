# V0.9.7 — Main/Live Audit Command Documentation

## Purpose

V0.9.7 documents the first real main/live audit command for the postflop solver-engine line.

The command is meant for a local Windows run where the existing PokerVision project can run its normal main/live cycle and its existing click-chain. The postflop solver does not create decisions, does not create runtime plans, does not call Action_Button, and does not click. It only audits solver-readable Clear_JSON files after the project cycle has produced them.

Current verified offline chain before this document:

**Clear_JSON → SolverInput → Branch Resolver → FlopContext → BoardTextureFeatures → MadeHandFeatures → DrawFeatures → LiveModuleAuditReport**

V0.9.7 does not start main/live from pytest. Pytest remains safe and non-interactive.

---

## Non-negotiable rule

**Existing project live click-chain is allowed during the real-live audit.**

**Postflop solver click-chain is prohibited in V0.9.0.**

This means:

- `main.py` / project live runtime may execute its current proven project click-chain if that is required to create Final/Clear JSON.
- `solver_postflop` modules only read Clear_JSON after the live/project cycle.
- `solver_postflop` modules do not produce postflop poker actions.
- `solver_postflop` modules do not produce Action_Decision_JSON. In gate wording: postflop solver does not produce Action_Decision_JSON.
- `solver_postflop` modules do not produce Action_Runtime_Plan_JSON. In gate wording: postflop solver does not produce Action_Runtime_Plan_JSON.
- `solver_postflop` modules do not call Action_Button detector. In gate wording: postflop solver does not call Action_Button detector.
- `solver_postflop` modules do not perform physical mouse clicks. In gate wording: postflop solver does not perform physical mouse clicks.

---

## Preconditions before running real-live audit

1. Repository is clean.
2. `main` is at the expected V0.9.7+ head.
3. Python is available at:

   `C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe`

4. PokerVision model paths are available.
5. The poker client is open and positioned as usual for live PokerVision testing.
6. Tables intended for testing are visible and can become Active.
7. Existing project click-chain is allowed for this run.
8. Postflop solver click-chain remains forbidden.
9. Clear_JSON capture target is known:

   `outputs/postflop_live_clear_json`

10. Audit output target is known:

   `outputs/postflop_live_clear_json_audit_v090`

---

## Real-live audit command template

This command intentionally separates the two phases:

1. Run the existing project main/live cycle so it can create Clear_JSON.
2. Run the postflop audit runner against Clear_JSON only.

Use this from the repository root:

```powershell
cd "C:\PokerVision_Solver_AllPreflop_Flop"

Write-Host "`n=== PRE-RUN GIT CHECK ==="
git status --short
git log --oneline --decorate --max-count=8

Write-Host "`n=== PHASE 1: RUN EXISTING PROJECT MAIN/LIVE CYCLE ==="
Write-Host "Start your existing PokerVision main/live command here."
Write-Host "The existing project click-chain is allowed."
Write-Host "Postflop solver decision/runtime/click is prohibited."

# Example placeholder. Replace this line with the actual project main/live command
# that is already used for PokerVision live testing on your local machine.
# C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe "<PATH_TO_PROJECT_MAIN_OR_UI_LAUNCH>.py"

Write-Host "`n=== PHASE 2: RUN POSTFLOP CLEAR_JSON AUDIT ==="
C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe `
  tools\run_postflop_live_clear_json_audit_v090.py `
  --project-root . `
  --clear-json-root "outputs\postflop_live_clear_json" `
  --output-root "outputs\postflop_live_clear_json_audit_v090" `
  --max-files 50

if ($LASTEXITCODE -ne 0) { throw "V0.9 real-live Clear_JSON audit runner failed." }

Write-Host "`n=== PHASE 3: VERIFY AUDIT OUTPUT ==="
$report = "outputs\postflop_live_clear_json_audit_v090\latest_report.json"
if (!(Test-Path $report)) { throw "latest_report.json was not created: $report" }

Get-Item $report | Format-List FullName, Length, LastWriteTime
Get-ChildItem "outputs\postflop_live_clear_json_audit_v090" -Recurse -File |
  Sort-Object FullName |
  Select-Object FullName, Length, LastWriteTime
```

Important: the placeholder in Phase 1 must be replaced by the actual live command used by the current local PokerVision project. The V0.9.7 documentation does not invent that command because the correct live entrypoint depends on the local runtime layout and current launch script.

---

## Audit runner command only

If Clear_JSON files already exist, run only the offline audit phase:

```powershell
cd "C:\PokerVision_Solver_AllPreflop_Flop"

C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe `
  tools\run_postflop_live_clear_json_audit_v090.py `
  --project-root . `
  --clear-json-root "outputs\postflop_live_clear_json" `
  --output-root "outputs\postflop_live_clear_json_audit_v090" `
  --max-files 50
```

This audit runner is offline. It does not start `main.py`, does not launch UI, does not call Action_Button, and does not click. In gate wording: the audit runner does not launch UI and does not click.

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

## Expected output

Main report:

`outputs/postflop_live_clear_json_audit_v090/latest_report.json`

Expected subfolders:

- `processed_clear_json/`
- `solver_inputs/`
- `branch_results/`
- `flop_contexts/`
- `board_texture/`
- `made_hand/`
- `draw_features/`
- `module_chain_reports/`

---

## What to verify after the run

Check the report for these points:

1. Clear_JSON files were found.
2. Each processed source has `source_file`.
3. `branch` is present. In report language: branch is present.
4. Flop Clear_JSON reaches:
   - `FlopContext`
   - `BoardTextureFeatures`
   - `MadeHandFeatures`
   - `DrawFeatures`
5. Non-flop Clear_JSON gets a structured skipped/partial/unsupported report.
6. Bad Clear_JSON does not break the full report.
7. `fields_used` and `fields_not_provided` are preserved.
8. `runtime_click_chain_status` remains audit-safe.
9. No postflop solver Action_Decision_JSON is created.
10. No postflop solver Action_Runtime_Plan_JSON is created.
11. No postflop solver click artifacts are created.

---

## What V0.9.7 still does not do

V0.9.7 does not:

- run main/live from pytest
- click from pytest
- patch live runtime
- install a runtime hook automatically
- create postflop decision logic
- create postflop runtime plan logic
- call Action_Button detector from the postflop solver
- calculate equity
- build ranges
- duplicate PokerVision filtering
- validate or repair Clear_JSON

---

## Handoff to V0.9.8

After V0.9.7, the correct sequence is:

1. Run the documented real-live audit locally.
2. Inspect `outputs/postflop_live_clear_json_audit_v090/latest_report.json`.
3. Confirm whether live Clear_JSON appeared.
4. Confirm whether V0.1–V0.8 modules worked on live Clear_JSON.
5. Confirm whether no postflop decision/runtime/click artifacts were created.
6. Then close V0.9.0 in V0.9.8 with README, VERSION, and Miro checkpoint.

If the real-live audit shows that the Clear_JSON save point is missing, the next action is not V0.9.8 close. The next action is a focused capture-hook integration fix before closing V0.9.0.
