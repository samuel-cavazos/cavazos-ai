# 2026-03-22 Widget Orb Hover Effect Fidelity

## Summary
Adjusted the floating widget orb so hover/mouse movement visibly disturbs the orb (closer to the main chat orb behavior), with a transparent surrounding area and stronger visual spill.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - Fixed launcher orb sizing behavior by making `.assistant-widget-orb` block-sized.
  - Allowed visual spill outside the orb circle:
    - `.assistant-widget-orb` now uses `overflow: visible`
    - `.assistant-widget-orb-canvas` now renders larger (`inset: -24%`) for visible aura around the orb.
  - Added slight saturation boost to the orb canvas for clarity at small button size.
  - Tuned launcher orb simulation parameters for stronger response:
    - higher `mouseIntensity`, `clickIntensity`, `waterStrength`, and `impactForce`
    - adjusted simulation resolution for better small-size readability.
  - Enhanced shader output with an outer aura and alpha blend so the motion reads beyond the orb core.
  - Added `pointerenter` ripple injection and tighter pointer-move throttle for more immediate feedback.

## Verification
- `python3 -m compileall portal` passed.

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-assistant-widget-transparent-orb-launcher.md`
  - `wiki/2026-03-21-assistant-popup-widget-markdown-mermaid.md`
- Result:
  - No contradictions found.
  - Existing docs remain accurate; this entry records a fidelity tuning pass.
