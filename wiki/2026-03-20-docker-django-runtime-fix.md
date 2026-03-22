# 2026-03-20 Docker Runtime Fix for Auth

## What changed

- Switched `orb-chat-ui/compose.yaml` to run the Django app (build context `..`) on `localhost:5173` instead of static Nginx-only files.
- Added root `Dockerfile` for Django runtime image.
- Added root `.dockerignore` for leaner Docker context.
- Added missing dependency `requests` to `requirements.txt` (required by allauth Microsoft provider).
- Updated allauth config in `cavazos_ai/settings.py` to current settings keys:
  - `ACCOUNT_LOGIN_METHODS`
  - `ACCOUNT_SIGNUP_FIELDS`

## Validation

- `docker compose up --build -d` from `orb-chat-ui/` completed successfully.
- Container now starts Django on `0.0.0.0:8000` and maps to host `5173`.
- Initial migrations run successfully inside container.

## Stale documentation check

- Updated root `README.md` Docker section to match new compose behavior.
- Updated `orb-chat-ui/README.md` Docker section to reflect Django-backed runtime.
- Existing static snapshot notes remain accurate as historical/asset references.
