# 2026-03-22 Widget Orb Clipping Fix

## Summary
Fixed clipping of the floating widget orb aura/effects so the orb renders cleanly beyond the launcher bounds.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - Set `.assistant-widget-launcher` to `overflow: visible` so the enlarged orb canvas is not clipped by the button bounds.
  - Set `.assistant-widget` to `overflow: visible` to allow visual spill from the launcher within the widget container.

## Verification
- `python3 -m compileall portal` passed.

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-widget-orb-hover-effect-fidelity.md`
  - `wiki/2026-03-22-assistant-widget-transparent-orb-launcher.md`
- Result:
  - No contradictions found.
  - Existing widget docs remain valid; this entry captures the clipping-specific correction.
