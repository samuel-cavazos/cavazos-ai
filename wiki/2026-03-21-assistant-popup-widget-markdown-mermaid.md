# 2026-03-21 Assistant Popup Widget (Orb Launcher + Markdown/Mermaid)

## Summary
Moved the landing-page assistant from the right-side panel into a floating popup widget, launched by an orb button in the bottom-right corner.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - Enabled widget mode via `assistant-widget-mode` body class.
  - Hid old right-side orb/chat panel in widget mode and switched hero layout to single-column.
  - Added floating orb launcher (`#assistantWidgetLauncher`) in the bottom-right.
  - Added popup chat panel (`#assistantWidgetPanel`) with:
    - message history list
    - clear/close controls
    - textarea composer + send button
    - demo chips for Markdown and Mermaid samples
  - Added Markdown + Mermaid runtime dependencies:
    - `marked`
    - `DOMPurify`
    - `mermaid`
  - Added widget controller script with:
    - Markdown rendering + sanitization
    - Mermaid block rendering from fenced code blocks
    - preview response fallback mode
    - external integration API: `window.PortalAssistantWidget.setSubmitHandler(fn)`

## Verification
- `manage.py check` passed.
- `manage.py test` passed (`15` tests).

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-21-chat-panel-height-match-left-content.md`
  - `wiki/2026-03-21-login-page-cavazos-texas-makeover.md`
  - `wiki/2026-03-21-landing-assistant-composer-light-dark-theme-support.md`
- Result:
  - Prior right-panel height tuning is now historical context because assistant UI moved to a popup widget.
  - No route/API docs became stale from this UI change.
