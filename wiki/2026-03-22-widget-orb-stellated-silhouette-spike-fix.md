# 2026-03-22 Widget Orb Stellated Silhouette Spike Fix

## Summary
Adjusted the launcher orb shader so the small-stellated-dodecahedron look has an actual spiky silhouette instead of reading as a sphere with projected facets.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - Replaced circular alpha mask with directional spike-boundary masking:
    - Computes spike influence from rotated 12-direction basis.
    - Builds `boundaryRadius` from `baseRadius + spikeRadius * silhouetteSpike`.
    - Uses that boundary for alpha, producing visible silhouette spikes.
  - Updated faceting calculations to use rotated spike directions directly (no sphere-like projection feel).
  - Increased stellation influence and tuned seam/spec/rim weights for clearer spike form.
  - Smoothed shell-edge blending near the boundary to reduce hard inner ring artifacts.
  - Removed launcher orb circular border:
    - `.assistant-widget-orb { border: 0; }`

## Verification
- `python3 -m compileall portal` passed.
- Extracted widget script syntax check passed:
  - `node --check /tmp/widget-inline.js`

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-widget-orb-faceted-polyhedron-effect.md`
  - `wiki/2026-03-22-widget-orb-small-stellated-dodecahedron-with-gradient.md`
- Result:
  - Prior notes remain useful historical context.
  - Current shader behavior is now silhouette-driven (spiky outline) and supersedes previous “projected sphere” appearance details.
