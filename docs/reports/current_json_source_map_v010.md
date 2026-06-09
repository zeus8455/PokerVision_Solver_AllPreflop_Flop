# V0.1.3 — JSON Source Map Audit

## Purpose

This report maps existing JSON artifacts and JSON-related code references before building the V0.2 source-based postflop fixture lab and V0.3 postflop source contracts.

## Summary

- Schema version: `v0.1.3-json-source-map`
- Total JSON files scanned: **187**
- Total code references: **1993**
- Available before click: **78**
- Available after click: **109**
- Requires click-cycle: **109**
- V0.2 fixture candidates: **183**
- V0.3 source candidates: **187**
- Manual live-like sources: **0**
- Final Clear JSON count: **10**

## Source Type Policy

Allowed source types:
- `dark_json`
- `pending_json`
- `service_json`
- `current_cycle_json`
- `runtime_json`
- `solver_payload_json`
- `final_clear_json`
- `manual_live_like_json`
- `unknown`

- Final Clear JSON is optional: **True**
- Manual live-like JSON must be explicit: **True**
- Source discovery must not depend only on Final Clear JSON: **True**

## Source Type Counts

| source_type | count |
|---|---:|
| `current_cycle_json` | 36 |
| `dark_json` | 1 |
| `final_clear_json` | 10 |
| `pending_json` | 28 |
| `runtime_json` | 2 |
| `solver_payload_json` | 101 |
| `unknown` | 9 |

## Candidate JSON Sources

| source_file | source_type | before_click | after_click | v020_candidate | street | notes |
|---|---|---:|---:|---:|---|---|
| `examples/clear_json/table_02_hand_29_preflop_01_preclick.json` | `unknown` | True | False | True | `flop` | source_type could not be inferred; requires manual review before V0.2 fixture use |
| `external/PokerVisionFinalVersionNoSolver_snapshot/Data_death_card/data_death_card.json` | `unknown` | True | False | False | `unknown` | source_type could not be inferred; requires manual review before V0.2 fixture use |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Decision_JSON/table_01/table_01_hand_05_preflop_01.action.json` | `current_cycle_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Decision_JSON/table_01/table_01_hand_45_preflop_01.action.json` | `current_cycle_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Decision_JSON/table_02/table_02_hand_59_preflop_01.action.json` | `current_cycle_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Decision_JSON/table_03/table_03_hand_03_preflop_01.action.json` | `current_cycle_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Decision_JSON/table_03/table_03_hand_18_preflop_01.action.json` | `current_cycle_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Decision_JSON/table_03/table_03_hand_50_preflop_01.action.json` | `current_cycle_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Decision_JSON/table_05/table_05_hand_04_preflop_01.action.json` | `current_cycle_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Decision_JSON/table_05/table_05_hand_17_preflop_01.action.json` | `current_cycle_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Decision_JSON/table_05/table_05_hand_22_preflop_01.action.json` | `current_cycle_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Runtime_Plan_JSON/table_01/table_01_hand_05_preflop_01.runtime_plan.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Runtime_Plan_JSON/table_01/table_01_hand_45_preflop_01.runtime_plan.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Runtime_Plan_JSON/table_02/table_02_hand_59_preflop_01.runtime_plan.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Runtime_Plan_JSON/table_03/table_03_hand_03_preflop_01.runtime_plan.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Runtime_Plan_JSON/table_03/table_03_hand_18_preflop_01.runtime_plan.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Runtime_Plan_JSON/table_03/table_03_hand_50_preflop_01.runtime_plan.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Runtime_Plan_JSON/table_05/table_05_hand_04_preflop_01.runtime_plan.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Runtime_Plan_JSON/table_05/table_05_hand_17_preflop_01.runtime_plan.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Action_Runtime_Plan_JSON/table_05/table_05_hand_22_preflop_01.runtime_plan.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON/table_01/table_01_hand_05_preflop_01.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON/table_01/table_01_hand_45_preflop_01.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON/table_02/table_02_hand_59_preflop_01.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON/table_03/table_03_hand_03_preflop_01.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON/table_03/table_03_hand_18_preflop_01.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON/table_03/table_03_hand_50_preflop_01.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON/table_05/table_05_hand_04_preflop_01.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON/table_05/table_05_hand_17_preflop_01.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON/table_05/table_05_hand_22_preflop_01.json` | `current_cycle_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_01/table_01_hand_05_flop.pending.json` | `pending_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_01/table_01_hand_05_flop_03.pending.json` | `pending_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_01/table_01_hand_05_preflop.pending.json` | `pending_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_01/table_01_hand_05_river.pending.json` | `pending_json` | True | False | True | `river` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_01/table_01_hand_05_turn.pending.json` | `pending_json` | True | False | True | `turn` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_01/table_01_hand_45_preflop.pending.json` | `pending_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_02/table_02_hand_59_preflop.pending.json` | `pending_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_03/table_03_hand_03_preflop.pending.json` | `pending_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_03/table_03_hand_18_flop.pending.json` | `pending_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_03/table_03_hand_18_flop_02.pending.json` | `pending_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_03/table_03_hand_18_preflop.pending.json` | `pending_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_03/table_03_hand_18_river.pending.json` | `pending_json` | True | False | True | `river` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_03/table_03_hand_18_river_03.pending.json` | `pending_json` | True | False | True | `river` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_03/table_03_hand_18_turn.pending.json` | `pending_json` | True | False | True | `turn` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_03/table_03_hand_50_preflop.pending.json` | `pending_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_05/table_05_hand_04_preflop.pending.json` | `pending_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_05/table_05_hand_17_preflop.pending.json` | `pending_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_05/table_05_hand_22_flop_02.pending.json` | `pending_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_05/table_05_hand_22_preflop.pending.json` | `pending_json` | True | False | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_05/table_05_hand_22_river.pending.json` | `pending_json` | True | False | True | `river` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Clear_JSON_Pending/table_05/table_05_hand_22_turn.pending.json` | `pending_json` | True | False | True | `turn` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_01/hand_02.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_01/hand_05_flop.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_01/hand_05_flop_03.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_01/hand_05_preflop.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_01/hand_05_river.dark.json` | `solver_payload_json` | False | True | True | `river` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_01/hand_05_turn.dark.json` | `solver_payload_json` | False | True | True | `turn` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_01/hand_41.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_01/hand_45_preflop.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_02/hand_31.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_02/hand_33.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_02/hand_35.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_02/hand_37.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_02/hand_39.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_02/hand_42.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_02/hand_46.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_02/hand_49.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_02/hand_51.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_02/hand_52.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_02/hand_53.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_02/hand_55.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_02/hand_57.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_02/hand_59_preflop.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_02/hand_62.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_03/hand_01.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_03/hand_03_preflop.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_03/hand_06.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_03/hand_08.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_03/hand_10.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_03/hand_12.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_03/hand_14.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_03/hand_16.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_03/hand_18_flop.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_03/hand_18_flop_02.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_03/hand_18_preflop.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_03/hand_18_river.dark.json` | `solver_payload_json` | False | True | True | `river` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_03/hand_18_river_03.dark.json` | `solver_payload_json` | False | True | True | `river` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_03/hand_18_turn.dark.json` | `solver_payload_json` | False | True | True | `turn` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_03/hand_43.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_03/hand_47.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_03/hand_50_preflop.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_04_preflop.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_07.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_09.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_11.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_13.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_15.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_17_preflop.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_17_preflop_02.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_19.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_20.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_21.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_22_flop.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_22_flop_02.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_22_preflop.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_22_river.dark.json` | `solver_payload_json` | False | True | True | `river` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_22_river_02.dark.json` | `solver_payload_json` | False | True | True | `river` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_22_turn.dark.json` | `solver_payload_json` | False | True | True | `turn` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_23.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_24.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_25.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_26.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_27.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_28.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_29.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_30.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_32.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_34.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_36.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_38.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| `external/PokerVisionFinalVersionNoSolver_snapshot/PokerVision V1_2/outputs/ui_display_cycle/current_cycle/Dark_JSON/table_05/hand_40.dark.json` | `solver_payload_json` | False | True | True | `flop` |  |
| ... | ... | ... | ... | ... | ... | 67 more JSON sources in JSON report |

## Key Audit Conclusion

V0.2 fixtures and V0.3 contracts must support intermediate source JSON. Final Clear_JSON must remain optional because postflop final output may be available only after click-cycle.
