# 2026-03-22 Widget Orb Small Stellated Dodecahedron + Gradient

## Summary
Updated the launcher orb shader to a small-stellated-dodecahedron-inspired faceted form and restored a flowing animated gradient similar to the prior swirl color motion.

## What Changed
- Updated `portal/templates/portal/index.html` shader:
  - Uses 12 spike directions (icosa-vertex basis) with pentagram-style local angular modulation for a stellated look.
  - Keeps facet seams and directional lighting for polyhedral depth.
  - Reintroduced dynamic gradient flow (`gradientFlow`, `gradientSpiral`, `gradientPulse`) and blended it into the stellated color field.
  - Retains shell-edge blending to smooth hard inner boundary transitions.

## Verification
- `python3 -m compileall portal` passed.
- Extracted widget script syntax check passed:
  - `node --check /tmp/widget-inline.js`

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-widget-orb-faceted-polyhedron-effect.md`
  - `wiki/2026-03-22-widget-orb-shadow-removal.md`
- Result:
  - Previous faceted-orb notes remain directionally accurate, but this entry supersedes shader details by adding stellation geometry and swirl-like gradient restoration.
  - Shadow-removal behavior remains current.
