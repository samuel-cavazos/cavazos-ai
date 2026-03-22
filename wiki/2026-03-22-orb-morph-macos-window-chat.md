# 2026-03-22 Orb Morph to Draggable macOS-style Chat Window

## Summary
Implemented a creative chat interaction overhaul on the landing/login page: the orb now morphs into a macOS-style chat window on desktop, supports dragging and bounded resizing, provides red close + green maximize controls, and morphs back to the orb on close. Mobile now uses a fullscreen chat panel with close control and simplified transition behavior.

## What Changed
- Updated `portal/templates/portal/index.html`.
- Reworked assistant widget shell:
  - Added macOS-style titlebar controls (red close, green maximize).
  - Added desktop resize handles (N/E/S/W + corners).
  - Added drag handle behavior from titlebar.
- Reworked open/close behavior:
  - Orb click now morph-opens into window.
  - Close control morph-contracts the window back to orb.
  - Session state persists for window frame + chat content while page remains loaded.
- Added desktop window manager logic:
  - viewport clamping
  - bounded resizing
  - maximize/restore
  - responsive reflow on viewport resize and breakpoint changes
- Added mobile mode behavior:
  - fullscreen chat panel
  - body scroll lock while mobile chat is open
  - maximize control hidden in mobile mode
- Preserved existing chat functionality:
  - Markdown rendering
  - Mermaid rendering
  - preview/demo prompt behavior
  - `window.PortalAssistantWidget` integration API

## Verification
- `python3 -m compileall portal` passed.
- Extracted widget inline script and checked syntax with Node:
  - `node --check /tmp/widget-inline.js` passed.

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-21-assistant-popup-widget-markdown-mermaid.md`
  - `wiki/2026-03-22-assistant-widget-transparent-orb-launcher.md`
  - `wiki/2026-03-22-widget-orb-hover-effect-fidelity.md`
  - `wiki/2026-03-22-widget-orb-clipping-fix.md`
  - `wiki/2026-03-22-widget-orb-edge-clipping-reduction.md`
  - `README.md`
  - `orb-chat-ui/README.md`
- Result:
  - Older dated wiki entries remain valid historical checkpoints.
  - New behavior supersedes prior popup-only UX; this entry is the current source of truth for login-page assistant interaction.
  - No additional README updates required for this UI-only change.
