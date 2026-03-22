# 2026-03-20 Microsoft SocialApp Render Guard

## What changed

- Fixed landing-page 500 on `/` caused by `{% provider_login_url %}` when Microsoft `SocialApp` is missing for active `SITE_ID`.
- Replaced direct template-time provider tag usage with view-provided context fields:
  - `microsoft_login_available`
  - `microsoft_login_url`
- Updated login panel rendering behavior:
  - If available: show active Microsoft login link.
  - If unavailable: show disabled Microsoft button + clear setup hint instead of crashing.
- Updated compose run command to `runserver --noreload` to reduce restart instability from exit code `137` in this environment.
- Re-seeded runtime DB with:
  - superuser `samuel`
  - Microsoft `SocialApp` attached to local/prod Sites

## Validation

- `curl http://localhost:5173/` returns `200`.
- Landing HTML includes Microsoft login anchor (`/accounts/microsoft/login/?process=login&next=/ops/`) when SocialApp is present.
- `docker compose exec -T cavazos-ai python manage.py check` passes.

## Stale documentation check

- Updated `README.md` Microsoft notes to document graceful behavior when SocialApp is missing.
- Existing route/auth docs remain accurate; no additional stale docs found.
