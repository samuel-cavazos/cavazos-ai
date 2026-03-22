# 2026-03-22 Widget Orb Gradient Shift Fix

## Summary
Fixed weak/near-static color shifting on the stellated orb by increasing palette contrast and strengthening time-driven gradient blending.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - Increased base palette saturation:
    - `color1`: `[0.98, 0.56, 0.16]`
    - `color2`: `[0.18, 0.7, 1.0]`
    - `color3`: `[0.53, 0.32, 0.98]`
  - Added explicit time-varying hue wave to gradient composition:
    - `hueWave = 0.5 + 0.5 * cos(...)`
    - Mixed into `gradientColor` for stronger visible color drift.
  - Increased gradient influence on the stellated surface:
    - `mix(..., gradientColor, 0.68 + 0.2 * dominance)`
  - Added subtle animated hue wave on shell color so perimeter also shifts.

## Verification
- `python3 -m compileall portal` passed.
- Extracted widget script syntax check passed:
  - `node --check /tmp/widget-inline.js`

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-widget-orb-small-stellated-dodecahedron-with-gradient.md`
  - `wiki/2026-03-22-widget-orb-stellated-silhouette-spike-fix.md`
- Result:
  - Geometry/spike notes remain current.
  - This entry supersedes older shader color-motion details by making gradient transitions explicitly stronger and more visible.
