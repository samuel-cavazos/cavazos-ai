# 2026-03-22 Widget Topbar Trash Right + Outline Style

## Summary
Adjusted the chat topbar clear control to use a red outline trash icon (no filled bubble) and moved it to the right side of the topbar.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - `.assistant-widget-window-dot.is-trash` is now transparent with no border/background bubble.
  - Trash SVG is scaled to control size (`0.86rem`) and uses red outline stroke (`#ff5b57`).
  - Added `.assistant-widget-window-tools` container on the right side of the header.
  - Moved `#assistantWidgetClear` out of left macOS dot group to the right-side tools area.

## Verification
- `python3 -m compileall portal` passed.
- Extracted widget script syntax check passed:
  - `node --check /tmp/widget-inline.js`

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-widget-topbar-thin-macos-trash-control.md`
  - `wiki/2026-03-22-chat-markdown-light-mode-code-contrast-fix.md`
- Result:
  - Thin macOS topbar changes remain valid.
  - Header control layout/details are superseded by this entry for trash icon placement/style.
