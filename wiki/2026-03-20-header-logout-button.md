# 2026-03-20 Header Logout Button

## What changed

- Added a top-right `Logout` button to landing page header for authenticated users.
- Updated landing header layout to support right-side authenticated actions.
- Kept mobile behavior sane by preventing header logout button from stretching full width.
- Updated logout endpoint behavior:
  - Standard form POST redirects to `/`.
  - AJAX/XHR logout requests continue returning JSON (`{ ok, redirect_url }`).

## Validation

- Authenticated home render includes header logout control.
- Posting `/auth/logout/` as standard form returns `302` to `/`.
- Posting `/auth/logout/` with `X-Requested-With: XMLHttpRequest` returns `200` JSON.
- `docker compose exec -T cavazos-ai python manage.py check` passes.

## Stale documentation check

- Updated `README.md` route list with `/auth/logout/` behavior.
- Existing auth flow docs remain accurate after this UI/logout behavior update.
