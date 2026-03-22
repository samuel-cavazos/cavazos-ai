# 2026-03-22 Chat Window Maximize Full Viewport

## Summary
Adjusted the chat window maximize behavior so the green button now expands the desktop chat window to use the full available viewport (edge-to-edge) instead of an inset maximized frame.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - Changed maximize geometry from inset-clamped bounds to full viewport:
    - `left: 0`, `top: 0`, `width: viewport.width`, `height: viewport.height`
  - Added `.assistant-widget-panel.is-maximized` class to enforce full-viewport frame and zero corner radius.
  - Added runtime maximize class toggling (`setMaximizedMode`) during:
    - maximize/restore toggle
    - open transition when already maximized
    - viewport sync updates
    - close cleanup

## Verification
- `python3 -m compileall portal` passed.
- `node --check /tmp/widget-inline.js` passed.

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-orb-morph-macos-window-chat.md`
  - `wiki/2026-03-21-assistant-popup-widget-markdown-mermaid.md`
- Result:
  - No contradictions found.
  - New entry reflects an incremental refinement of maximize behavior within the new macOS-window chat model.
