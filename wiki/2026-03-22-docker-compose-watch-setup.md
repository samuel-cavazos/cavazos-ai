# 2026-03-22 Docker Compose Watch Setup

## Summary
Configured Docker Compose file-watch so `docker compose watch` is enabled for local development.

## Changes
- Updated `orb-chat-ui/compose.yaml`:
  - Added `develop.watch` rules for service `cavazos-ai`.
  - `sync+restart` on source changes for:
    - `../cavazos_ai` -> `/app/cavazos_ai`
    - `../portal` -> `/app/portal`
    - `../orb-chat-ui` -> `/app/orb-chat-ui`
    - `../manage.py` -> `/app/manage.py`
  - `rebuild` on image/dependency changes for:
    - `../requirements.txt`
    - `../Dockerfile`
- Updated docs:
  - `orb-chat-ui/README.md` with `docker compose watch` usage.
  - `README.md` with `docker compose watch` usage note.

## Verification
- Ran:
  - `docker compose -f orb-chat-ui/compose.yaml config`
- Result: compose config is valid and includes resolved `develop.watch` entries.

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-20-docker-django-runtime-fix.md`
  - `wiki/2026-03-20-persistent-db-volume.md`
- Result: no stale documentation found; prior runtime/volume notes remain accurate.
