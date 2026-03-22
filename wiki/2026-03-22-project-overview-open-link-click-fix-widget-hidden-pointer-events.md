# 2026-03-22 Project Overview Open-Link Click Fix (Widget Hidden State)

## Summary
Fixed an interaction bug where project navigation links/buttons (including "Open") could not be clicked because the closed assistant widget panel still intercepted pointer events.

## Root Cause
The shared widget panel had `display: grid` and `pointer-events: auto` styling, while also relying on the `hidden` attribute for closed state. In CSS, author rules overrode the default hidden behavior, leaving an invisible panel over page content.

## What Changed
- Updated `portal/templates/portal/includes/assistant_widget.html`:
  - Removed blanket pointer-events enablement for the panel in closed state.
  - Set launcher-only pointer events by default.
  - Set panel to `pointer-events: none` by default.
  - Enabled panel pointer events only when widget is open (`.assistant-widget[data-open="true"]`).
  - Added explicit hidden-state guard:
    - `.assistant-widget-panel[hidden] { display: none !important; pointer-events: none !important; }`

## Verification
- `python3 -m compileall portal` passed.
- `.venv/bin/python manage.py test portal.tests` passed (`19` tests).

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-sitewide-assistant-widget-global-include-chat-cutover.md`
  - `wiki/2026-03-22-chat-widget-copy-and-demo-removal.md`
- Result:
  - Site-wide widget rollout docs remain accurate.
  - Added this entry to document the post-rollout pointer-events regression fix.
