# 2026-03-21 Login Logo Refresh + Horizontal Centering

## Request

Use updated `./logo.png` on the login intro panel and center the logo horizontally on the panel.

## What Changed

- Refreshed static logo asset by syncing:
  - source: `/home/data-team/cavazos-ai/logo.png`
  - destination: `/home/data-team/cavazos-ai/orb-chat-ui/logo.png`
- Updated landing intro image CSS in `portal/templates/portal/index.html`:
  - changed `.intro-preview-image` margin from left-aligned to centered:
    - `margin: 0 auto 0.35rem;`

## Verification

Executed:

- `python3 -m compileall portal`
- `.venv/bin/python manage.py test`

Results:

- template compile checks succeeded
- test suite passed (`15` tests)

## Stale Documentation Check

- Reviewed docs scope for this UI-only update.
- No route/API/storage behavior changed, so no README update was required.
