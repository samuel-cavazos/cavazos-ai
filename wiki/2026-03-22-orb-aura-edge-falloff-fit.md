# 2026-03-22 Orb Aura Edge Falloff Fit (No Canvas Expansion)

## Summary
Adjusted the orb launcher shader so aura/glow fades out near canvas boundaries instead of expanding canvas size. This keeps the orb footprint stable while reducing visual clipping.

## What Changed
- Updated `portal/templates/portal/index.html` launcher orb fragment shader:
  - Added edge-distance based fade factor using `vUv`:
    - computes nearest distance to canvas edge
    - applies `smoothstep` fade
    - multiplies aura by this edge fade
  - Slightly reduced aura alpha contribution (`0.52` -> `0.5`).
- Kept `.assistant-widget-orb-canvas` at `inset: -18%` (no further size expansion).

## Verification
- `python3 -m compileall portal` passed.
- `node --check /tmp/widget-inline.js` passed.

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-orb-overflow-roll-back-two-steps.md`
  - `wiki/2026-03-22-orb-canvas-overflow-expansion-v2.md`
- Result:
  - No contradictions found.
  - This entry documents the preferred current approach (shader fitting) over further canvas expansion.
