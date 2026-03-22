# 2026-03-21 Landing Tagline Full Width

## Request

Make the landing tagline/headline span full width instead of appearing compacted to the left.

## What Changed

- Removed the width cap on landing headline styles by changing:
  - `max-width: 17ch;` -> `max-width: none;`
- Applied in both render paths:
  - `portal/templates/portal/index.html`
  - `orb-chat-ui/index.html`

## Verification

Executed:

- `python3 -m compileall portal orb-chat-ui`
- `.venv/bin/python manage.py test`

Results:

- compile checks succeeded
- test suite passed (`15` tests)

## Stale Documentation Check

- Reviewed docs scope for this style-only update.
- No route/API/storage behavior changed; no README updates required.
