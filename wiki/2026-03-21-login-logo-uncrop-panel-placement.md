# 2026-03-21 Login Logo Uncrop + Panel Placement

## Request

Logo was cropped on the login intro panel. Remove framed/container-style treatment and place logo directly on panel without cropping.

## What Changed

- Updated `portal/templates/portal/index.html` `.intro-preview-image` styles:
  - removed framed container visuals (`border`, background, shadow)
  - removed cropping behavior (`max-height` + `object-fit: cover`)
  - switched to intrinsic rendering (`height: auto`, `object-fit: contain`)
  - constrained width for panel fit: `width: min(100%, 13.5rem)`

## Verification

Executed:

- `python3 -m compileall portal`
- `.venv/bin/python manage.py test`

Results:

- template compile checks succeeded
- test suite passed (`15` tests)

## Stale Documentation Check

- Reviewed docs scope for this UI-only adjustment.
- No route/API/storage behavior changed; no README update required.
