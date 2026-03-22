# 2026-03-22 Chat Markdown Light-Mode Code Contrast Fix

## Summary
Fixed unreadable markdown code text in light mode by preserving dark code highlights while forcing light foreground text color for code elements.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - `.assistant-widget-markdown code` now sets `color: #e8f3ff;`
  - `.assistant-widget-markdown pre code` now sets `color: #e8f3ff;`

## Why
- In light-mode user bubbles, base text color is dark (`#8a4b0f`), which was inheriting into markdown code and becoming unreadable on dark code backgrounds.
- This keeps the dark highlight treatment while restoring readable contrast.

## Verification
- `python3 -m compileall portal` passed.
- Extracted widget script syntax check passed:
  - `node --check /tmp/widget-inline.js`

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-widget-topbar-thin-macos-trash-control.md`
  - `wiki/2026-03-22-widget-orb-gradient-shift-fix.md`
- Result:
  - No conflicts.
  - This is an additive styling fix specific to markdown code contrast in light mode.
