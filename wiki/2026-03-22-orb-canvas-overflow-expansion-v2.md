# 2026-03-22 Orb Canvas Overflow Expansion v2

## Summary
Expanded orb canvas overflow further to reduce residual aura clipping around the launcher.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - Increased `.assistant-widget-orb-canvas` inset from `-36%` to `-50%`.

## Verification
- `python3 -m compileall portal` passed.
- `node --check /tmp/widget-inline.js` passed.

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-orb-canvas-overflow-expansion.md`
  - `wiki/2026-03-22-widget-orb-edge-clipping-reduction.md`
- Result:
  - No contradictions found.
  - This is an incremental tuning update to the same overflow behavior.
