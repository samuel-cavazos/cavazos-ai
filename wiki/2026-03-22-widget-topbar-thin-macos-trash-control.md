# 2026-03-22 Widget Topbar Thin macOS + Trash Control

## Summary
Refined the chat window topbar to a thinner macOS-style control strip, removed visible title/status text, and replaced the `Clear` text button with a red trash icon control matching the close/maximize button size.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - Topbar density reduced:
    - `.assistant-widget-head` padding changed to `0.34rem 0.62rem`
    - tighter gaps and lighter gradient treatment.
  - Removed visible topbar copy:
    - removed `Beast Assistant` title from the header.
    - removed visible `Preview mode...` text from the header.
  - Replaced text clear action:
    - removed `.assistant-widget-head-btn` clear button.
    - added `#assistantWidgetClear` as `.assistant-widget-window-dot.is-trash` with inline trash SVG, same 0.86rem control size as close/maximize.
  - Added hidden live status region for JS status updates:
    - `#assistantWidgetStatus` now uses `.assistant-widget-status-live` (screen-reader-only style) outside the topbar.

## Verification
- `python3 -m compileall portal` passed.
- Extracted widget script syntax check passed:
  - `node --check /tmp/widget-inline.js`

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-orb-morph-macos-window-chat.md`
  - `wiki/2026-03-22-chat-window-maximize-full-viewport.md`
- Result:
  - Core macOS window behavior remains accurate.
  - Header/control details are superseded by this entry (thin topbar, no visible header text, trash icon clear control).
