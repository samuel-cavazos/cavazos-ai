# 2026-03-22 Widget Orb Edge Clipping Reduction

## Summary
Reduced visible clipping on the floating orb widget by moving the launcher inward from viewport edges and removing the dark shadow layer behind the orb.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - Moved `.assistant-widget` further in from bottom-right on desktop.
  - Increased mobile inset for `.assistant-widget` from `0.65rem` to `1.2rem`.
  - Removed the external drop shadow behind `.assistant-widget-orb` (kept subtle inset ring only).
  - Reduced renderer spill size by changing `.assistant-widget-orb-canvas` inset from `-24%` to `-18%`.
  - Tightened shader aura radius/alpha to reduce edge overhang:
    - `circleRadius + 0.38` -> `circleRadius + 0.24`
    - aura alpha factor `0.62` -> `0.52`

## Verification
- `python3 -m compileall portal` passed.

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-widget-orb-clipping-fix.md`
  - `wiki/2026-03-22-widget-orb-hover-effect-fidelity.md`
- Result:
  - No contradictions found.
  - Existing docs remain valid; this entry records a follow-up tuning pass to reduce edge clipping artifacts.
