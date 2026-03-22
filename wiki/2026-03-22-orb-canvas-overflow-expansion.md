# 2026-03-22 Orb Canvas Overflow Expansion (4-Side Clip Fix)

## Summary
Fixed visible clipping of the orb aura on all sides by enlarging the orb canvas render bounds around the launcher.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - Increased `.assistant-widget-orb-canvas` overflow inset from `-18%` to `-36%`.
  - This gives the orb shader more room to render outer glow/smoke without hitting the canvas boundary.

## Verification
- `python3 -m compileall portal` passed.
- `node --check /tmp/widget-inline.js` passed.

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-widget-orb-edge-clipping-reduction.md`
  - `wiki/2026-03-22-chat-window-maximize-full-viewport.md`
- Result:
  - No contradictions found.
  - This entry refines orb renderer overflow behavior after the newer window-morph implementation.
