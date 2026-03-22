# 2026-03-20 Persistent DB Volume Setup

## What changed

- Added SQLite DB path override in Django settings:
  - `DJANGO_DB_PATH` env var with fallback to local `BASE_DIR/db.sqlite3`.
- Updated compose service to persist DB on host:
  - `DJANGO_DB_PATH=/data/db.sqlite3`
  - volume mount `../data:/data`
- Kept existing startup flow (`migrate` + `runserver`) so migrations continue to apply automatically.
- Copied existing runtime DB into host-mounted path and verified key records (superuser + Microsoft SocialApp) in the persistent DB.

## Validation

- `settings.DATABASES['default']['NAME']` reports `/data/db.sqlite3` in running container.
- After container restart, records still exist:
  - `samuel` superuser remains present.
  - Microsoft SocialApp for `SITE_ID=1` remains present.
- `docker compose exec -T cavazos-ai python manage.py check` passes.

## Stale documentation check

- Updated `README.md` Docker section to document persistent SQLite storage mapping.
- Updated `orb-chat-ui/README.md` Docker behavior note with persistent DB mount details.
- No additional stale docs found.
