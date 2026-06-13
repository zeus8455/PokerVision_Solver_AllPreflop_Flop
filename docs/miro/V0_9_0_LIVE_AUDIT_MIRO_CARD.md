# Miro Card — V0.9.0 Main Live Clear_JSON Audit / Postflop Capture Evidence

## **Version**

**V0.9.0 — Main Live Clear_JSON Audit / Postflop Capture Evidence**

**Closed by:** **V0.9.8 — Close V0.9.0 / Live Audit Checkpoint**

---

## **Main goal**

Prove that the existing PokerVision live runtime can produce **postflop Clear_JSON** artifacts that the new **Clear_JSON-only postflop solver modules** can read and process.

Target chain:

**main.py live → postflop Clear_JSON capture → schema adapter → audit runner → SolverInput → Branch Resolver → FlopContext → BoardTexture → MadeHand → DrawFeatures**

---

## **What was completed**

**V0.9.1** — Live audit report contracts.  
**V0.9.2** — Clear_JSON discovery gate.  
**V0.9.3** — Clear_JSON module pipeline runner.  
**V0.9.4** — Clear_JSON capture hook audit.  
**V0.9.5** — Clear_JSON audit tool runner.  
**V0.9.6** — No-postflop-click architecture gate.  
**V0.9.7** — Main live Clear_JSON audit command docs.  
**V0.9.7.1** — Runtime Clear_JSON capture hook integration.  
**V0.9.7.2** — Pending postflop Clear_JSON capture.  
**V0.9.7.3** — Live Clear_JSON schema adapter / flatten fields.  
**V0.9.7.4** — Live audit hygiene / runner import / stale capture guard.  
**V0.9.8** — README / VERSION / checkpoint / Miro close.

---

## **Final evidence**

Latest formal live evidence after V0.9.7.4:

**evidence_status:** `passed`  
**total_files_seen:** `5`  
**total_clear_json_processed:** `5`  
**module_chain_status:** `flop_features_completed`  
**board_texture:** `1`  
**flop_contexts:** `1`  
**made_hand:** `1`  
**draw_features:** `1`  
**runtime_click_chain_status:** `existing_project_chain_not_invoked_by_audit`  
**errors:** `[]`

---

## **Why V0.9.0 matters**

Before V0.9.0, the postflop solver modules existed mostly as fixture-backed offline layers.

After V0.9.0, the system has proof that live PokerVision runtime output can be captured and transformed into solver-readable Clear_JSON.

This makes the postflop solver line ready for the next planning block.

---

## **Important boundary**

V0.9.0 is **not** a postflop decision version.

It does **not** produce:

**postflop decisions**, **Action_Decision_JSON**, **Action_Runtime_Plan_JSON**, **Action_Button calls**, **clicks**, **equity**, **ranges**, or **bet sizing**.

The postflop solver remains **audit-only** at this checkpoint.

---

## **Known limitations**

**Turn/river** are captured but route to placeholders: `turn_not_implemented_yet`, `river_not_implemented_yet`.

**Spot family** can remain `unknown_flop_spot` because full live preflop/action context import is not implemented yet.

**Live evidence requires visible poker tables.** If no postflop spots appear, evidence correctly fails with `total_files_seen = 0`.

---

## **Next discussion**

**V0.10.0** should be discussed before coding.

Candidate directions:

**postflop decision input contract**, **turn/river module plan**, **preflop/action context import**, **range/equity boundary**, or **decision-blueprint audit-only layer**.
