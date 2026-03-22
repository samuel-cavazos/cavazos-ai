# 2026-03-19 Django Auth + allauth Setup

## What changed

- Added a Django project (`manage.py`, `cavazos_ai/`) and `portal` app.
- Added inline login UX on landing page:
  - `Login` button swaps Live Intelligence content into a login form.
  - Login form includes `Submit` and `Back` controls.
- Added auth endpoints:
  - `portal:ajax-login` (`/auth/login/`) for session login from inline form.
  - `portal:ajax-logout` (`/auth/logout/`) for future UI wiring.
- Added authenticated chat route (`/chat/`). Landing orb preview routing was later replaced by direct in-page rendering.
  - Superseded on 2026-03-22: `/chat/` now permanently redirects (`301`) to `/` after site-wide floating-widget rollout.
- Added `django-allauth` configuration and Microsoft provider wiring in settings for future social login setup.
- Added root `README.md` and `requirements.txt` for Django setup.

## Stale documentation check

- Updated `orb-chat-ui/README.md` to describe its current role as static asset bundle + legacy snapshot.
- Added root `README.md` with Django run instructions and allauth setup notes.
- Existing older wiki notes remain historical, with this page defining current auth architecture.
