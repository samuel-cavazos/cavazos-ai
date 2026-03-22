# 2026-03-22 Chat Widget Copy + Demo Removal

## Summary
Cleaned up chat-widget copy and removed demo onboarding content from the chat window.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - Removed the chat demo chip UI block (`Markdown Demo`, `Mermaid Demo`).
  - Removed related demo-chip JS bindings (`demoButtons` query + click handlers).
  - Removed auto-injected welcome message content (deleted `ensureWelcomeMessage` function and calls).
  - Updated assistant message meta label from `Beast` to `Assistant`.
  - Updated chat input placeholder:
    - `Ask Beast anything about your infrastructure...` -> `Ask Beast...`
  - Updated heading copy:
    - `Hi, I'm Beast. How may I assist you?` -> `Hi. How may I assist you?`

## Verification
- `python3 -m compileall portal` passed.
- Extracted widget script syntax check passed:
  - `node --check /tmp/widget-inline.js`

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-widget-topbar-thin-macos-trash-control.md`
  - `wiki/2026-03-22-widget-topbar-trash-right-outline.md`
  - `wiki/2026-03-22-orb-morph-macos-window-chat.md`
- Result:
  - Window controls/layout docs remain accurate.
  - Prior chat copy references are superseded by this entry.
