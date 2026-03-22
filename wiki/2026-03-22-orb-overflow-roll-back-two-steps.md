# 2026-03-22 Orb Overflow Rollback (Two Steps)

## Summary
Rolled back the last two orb overflow expansions to return the launcher orb to its prior size/footprint.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - Restored `.assistant-widget-orb-canvas` inset to `-18%`.
  - This effectively rolls back both prior incremental expansions (`-36%` and `-50%`).

## Verification
- `python3 -m compileall portal` passed.
- `node --check /tmp/widget-inline.js` passed.

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-orb-canvas-overflow-expansion.md`
  - `wiki/2026-03-22-orb-canvas-overflow-expansion-v2.md`
- Result:
  - Both entries are now historical and superseded by this rollback.
  - Current active overflow setting is `-18%`.
