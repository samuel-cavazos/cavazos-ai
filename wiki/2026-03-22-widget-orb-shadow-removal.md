# 2026-03-22 Widget Orb Shadow Removal

## Summary
Removed the remaining perceived "shadow behind the orb" on the floating chat launcher.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - `.assistant-widget-orb` now uses `box-shadow: none;`
  - Launcher orb shader no longer renders an external aura layer; alpha now follows the orb body only (`finalAlpha = inCircle`).

## Verification
- Confirmed active CSS:
  - `.assistant-widget-orb { box-shadow: none; }`
- Confirmed shader output:
  - `vec3 finalColor = orbColor;`
  - `float finalAlpha = inCircle;`

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-widget-orb-hover-effect-fidelity.md`
  - `wiki/2026-03-22-orb-aura-edge-falloff-fit.md`
  - `wiki/2026-03-22-widget-orb-edge-clipping-reduction.md`
- Result:
  - Prior aura/glow tuning docs remain valid as historical context but are superseded for current launcher visuals.
  - Current behavior intentionally removes the behind-orb glow/shadow layer.
