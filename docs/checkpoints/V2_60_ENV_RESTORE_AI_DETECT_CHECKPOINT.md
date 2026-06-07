# V2.60.0 Environment Restore Checkpoint — AI_detect Path Recovery

## Date
2026-06-05

## Current restored code state
- Branch: restore-v2-60-clean
- Commit: d3268ee V2.60.0 add fixture review inspection
- Git working tree before checkpoint: clean
- Runtime snapshot restored from Git to exact V2.60.0 tracked state
- Deleted tests/tools from later cleanup versions are present again in V2.60.0:
  - tests files: 197
  - tools files: 110

## Root cause found
The V2.60.0 code was not broken.

The failure was caused by missing local environment path:

C:\PokerVision\AI_detect

In V2.60.0 config.py, model paths are hardcoded as absolute paths:

- C:\PokerVision\AI_detect\Trigger_UI_Detector\weights
- C:\PokerVision\AI_detect\Table_Seat_BoardPot_Detector\weights
- C:\PokerVision\AI_detect\Player_State_Detector\weights
- C:\PokerVision\AI_detect\Digit_Detector\weights
- C:\PokerVision\AI_detect\Card_Detector\weights
- C:\PokerVision\AI_detect\Action_Button_Detector\weights

The real model files were present here:

C:\PokerVision_Solver_Preflop\external\PokerVisionFinalVersionNoSolver_snapshot\AI_detect

Because the old absolute path was missing, YOLO detectors could not load the expected weights properly, live Trigger_UI / analysis chain produced no useful JSON, and the UI showed "Новых JSON: 0".

## Recovery performed
Created a Windows junction:

C:\PokerVision\AI_detect
->
C:\PokerVision_Solver_Preflop\external\PokerVisionFinalVersionNoSolver_snapshot\AI_detect

After this, all required best.pt files resolved correctly:

- Trigger_UI_Detector\weights\best.pt
- Table_Seat_BoardPot_Detector\weights\best.pt
- Player_State_Detector\weights\best.pt
- Digit_Detector\weights\best.pt
- Card_Detector\weights\best.pt
- Action_Button_Detector\weights\best.pt

## Verification
Startup audit after recovery:
- V12_LIVE_DATA_CAPTURE_NO_CLICK_MODE can be true/false depending on env
- AI detector paths still print as C:\PokerVision\AI_detect\...
- Those paths now physically resolve through the junction

Live no-click after recovery:
- Dark_JSON created
- Clear_JSON_Pending created
- Clear_JSON created
- Action_Runtime_Plan_JSON created
- JSON_Complete created

Real-live click after recovery:
- Real click mode was enabled:
  - ACTION_REAL_CLICK enabled=True, dry_run=False
  - SERVICE_REAL_CLICK enabled=True, dry_run=False
  - V10_REAL_CLICK_READINESS status=ready_for_controlled_real_click
- Live table_02 preflop spot completed real click:
  - HERO SB A5o vs UTG open 2bb
  - Solver_Preflop raw_action = fold
  - reason = range:vs_open.UTG|SB:default_or_override:fold
  - Action_Button clicked FOLD
  - Final Clear_JSON saved

Synthetic matrix verification:
- tools/run_v2_42_full_preflop_spot_matrix_e2e.py
- cases_total=53
- cases_ok=53
- cases_failed=0
- runtime_chain_ok=True
- semantic_exact_ok=True
- V2.42_FULL_PREFLOP_SPOT_MATRIX_E2E_OK=True

## Current conclusion
V2.60.0 runtime and solver chain are functional again.

The original breakage was environmental, not a code regression:
missing C:\PokerVision\AI_detect absolute model path.

## Known technical follow-up
There is still a lineage cleanup issue to inspect later:
some live Dark_JSON blocks show different decision_id values between solver/click and runtime_plan.

Action matched correctly in the real fold spot, but decision_id lineage should be normalized later to avoid future no-repeat / duplicate guard confusion.
