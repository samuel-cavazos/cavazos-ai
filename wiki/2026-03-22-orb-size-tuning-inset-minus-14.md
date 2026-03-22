# 2026-03-22 Orb Size Tuning (`inset: -14%`)

## Summary
Reduced launcher orb visual size by tightening the orb canvas overflow inset.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - Changed `.assistant-widget-orb-canvas` inset from `-18%` to `-14%`.

## Verification
- `python3 -m compileall portal` passed.
- `node --check /tmp/widget-inline.js` passed.

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-orb-aura-edge-falloff-fit.md`
  - `wiki/2026-03-22-orb-overflow-roll-back-two-steps.md`
- Result:
  - No contradictions found.
  - This entry records a visual size refinement while keeping the shader edge-falloff approach.
