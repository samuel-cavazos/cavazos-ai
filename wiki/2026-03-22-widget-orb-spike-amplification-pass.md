# 2026-03-22 Widget Orb Spike Amplification Pass

## Summary
Increased the stellated orb spike sharpness and length so the geometry reads more aggressively "spiky" instead of rounded.

## What Changed
- Updated shader parameters in `portal/templates/portal/index.html`:
  - Silhouette spike narrowing/extension:
    - `pow(align, 22.0)` -> `pow(align, 32.0)`
    - `baseRadius` reduced (`0.62` -> `0.58`)
    - `spikeRadius` increased (`0.26` -> `0.36`)
    - Added `tipBoost = pow(silhouetteSpike, 1.8)` before boundary radius composition.
  - Stellation shape sharpening:
    - Increased star-arm exponent and stellation weighting.
    - Increased spike-direction normal influence (`0.84` -> `0.92`).
  - Reduced shell softening influence near edges so tips remain crisp.

## Verification
- `python3 -m compileall portal` passed.
- Extracted widget script syntax check passed:
  - `node --check /tmp/widget-inline.js`

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-widget-orb-stellated-silhouette-spike-fix.md`
  - `wiki/2026-03-22-widget-orb-gradient-shift-fix.md`
- Result:
  - Prior entries remain valid history.
  - This pass supersedes spike-intensity details with a more extreme silhouette/tip profile.
