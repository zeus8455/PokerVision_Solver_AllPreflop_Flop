# V0.4 Temporary Fix — Postflop Clear_JSON Capture Stub

## Purpose

This commit preserves the current temporary test fix that allows collecting postflop Clear_JSON files for lop, 	urn, and iver while the real postflop solver/runtime/click-chain is not implemented yet.

## Why this exists

The legacy live runtime only publishes final Clear_JSON after a completed click/dry-run transaction. That works for preflop, but postflop is currently unsupported by the solver/runtime branch. As a result, valid postflop frames were not reaching final Clear_JSON capture.

## Temporary behavior

- Preflop click-chain remains unchanged.
- Postflop lop/turn/river capture is allowed for source-data collection.
- Postflop uses a safe no-click stub.
- The stub must never be treated as a real postflop decision engine.
- The stub must not become the final V0.4+ architecture.

## Required later cleanup

Later versions must remove or rework this logic and replace it with the proper chain:

source discovery -> source adapter -> normalized postflop frame -> street detector -> preflop context import -> postflop solver -> guarded runtime plan -> click-chain -> final Clear_JSON.

## Important warning

This is a temporary capture bridge only. Before real postflop action execution, restore strict Active/runtime/click discipline and remove any broad capture bypasses.
