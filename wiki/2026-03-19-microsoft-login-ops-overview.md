# 2026-03-19 Microsoft Login + Superuser Ops Overview

## What changed

- Added Microsoft SSO entry in landing login form (`OR` divider + `Admin Sign in with Microsoft` button).
- Added role-aware redirect behavior:
  - Superusers land on `/ops/` after login.
  - Non-superusers continue through safe `next` fallback behavior to `/chat/`.
    - Superseded on 2026-03-22: legacy `/chat/` now permanently redirects (`301`) to `/`.
- Added custom allauth adapters:
  - `PortalAccountAdapter` for role-aware post-login redirect.
  - `PortalSocialAccountAdapter` to gate Microsoft login by allowlist + superuser requirement.
- Added new superuser-only overview page at `/ops/` with design-first placeholder portfolio cards.
- Added `DJANGO_SITE_ID` and `MICROSOFT_ALLOWED_EMAILS` config support in settings.
- Updated local docker compose environment to set `DJANGO_SITE_ID=1`.
- Registered Microsoft SocialApp + Site mappings in runtime DB for local/prod hostnames.

## Validation

- `docker compose exec -T cavazos-ai python manage.py check` passes.
- `python -m py_compile` passes for updated Python modules.
- Login API check returns `/ops/` redirect for `samuel` superuser.
- Anonymous landing response includes both `auth-divider` and `Admin Sign in with Microsoft` button.

## Stale documentation check

- Updated `README.md` routes and Microsoft setup notes for `/ops/`, callbacks, allowlist, and redirect behavior.
- Updated `orb-chat-ui/README.md` behavior note to include Django-rendered `/ops/` overview.
- No remaining stale docs found for this change set.
