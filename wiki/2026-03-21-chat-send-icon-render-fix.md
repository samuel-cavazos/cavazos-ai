# 2026-03-21 Chat Send Icon Render Fix

## Request

Fix chat input send button rendering where the button appeared as a blue square with no visible send icon.

## What Changed

- Added inline SVG send icon markup to portal assistant send button in:
  - `portal/templates/portal/index.html`
- Added explicit icon sizing for `.assistant-send svg` in the same template.
- Added inline SVG send icon markup to orb chat send button in:
  - `orb-chat-ui/chat.html`

## Verification

Executed:

- `python3 -m compileall portal orb-chat-ui`
- `.venv/bin/python manage.py test`

Results:

- template/static compile checks completed without errors
- test suite passed (`15` tests)

## Stale Documentation Check

- Reviewed README/wiki scope for this change.
- No route/API/storage behavior changed; no documentation updates were required beyond this wiki record.
