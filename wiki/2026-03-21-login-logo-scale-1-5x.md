# 2026-03-21 Login Logo Scale 1.5x

## Request

Increase the login intro logo size by a factor of `1.5`.

## What Changed

- Updated login intro image width cap in `portal/templates/portal/index.html`:
  - from: `width: min(100%, 13.5rem);`
  - to: `width: min(100%, 20.25rem);`

This is an exact `1.5x` scale increase (`13.5 * 1.5 = 20.25`).

## Verification

- CSS value updated and saved in template.

## Stale Documentation Check

- Reviewed docs scope for this UI-only style adjustment.
- No route/API/storage behavior changed; no README updates were required.
