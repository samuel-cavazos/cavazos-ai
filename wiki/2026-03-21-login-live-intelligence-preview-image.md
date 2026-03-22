# 2026-03-21 Login Live Intelligence Preview Image

## Request

Add the provided image above the `Live Intelligence` section on the unauthenticated login/landing panel.

## What Changed

- Copied provided image asset into static directory:
  - `orb-chat-ui/logo.png`
- Updated unauthenticated intro panel in `portal/templates/portal/index.html`:
  - inserted image block above `<span class="eyebrow">Live Intelligence</span>`
  - added `.intro-preview-image` styles for sizing, border, radius, and responsive fit

## Verification

Executed:

- `python3 -m compileall portal orb-chat-ui`
- `.venv/bin/python manage.py test`

Results:

- template/static compile checks succeeded
- test suite passed (`15` tests)

## Stale Documentation Check

- Reviewed README/wiki scope for this UI-only change.
- No route/API/storage behavior changed, so no additional documentation updates were required.
