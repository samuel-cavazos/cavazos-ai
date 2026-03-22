# 2026-03-22 Orb Size Tuning (`inset: -8%`)

## Summary
Reduced launcher orb overflow inset from `-14%` to `-8%` to make the orb visibly smaller.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - `.assistant-widget-orb-canvas` now uses `inset: -8%;`

## Verification
- Confirmed the active style in template:
  - `.assistant-widget-orb-canvas { inset: -8%; }`

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-orb-size-tuning-inset-minus-14.md`
  - `wiki/2026-03-22-orb-size-reconfirm-minus-14.md`
- Result:
  - Prior `-14%` notes are now historical and superseded by this entry.
  - No conflicting implementation remains in code.
