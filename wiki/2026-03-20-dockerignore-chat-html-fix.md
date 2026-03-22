# 2026-03-20 Dockerignore Chat HTML Fix

## What changed

- Updated `orb-chat-ui/.dockerignore` to include `chat.html` in the Docker build context.
- This resolves Docker build failures from `COPY chat.html ./chat.html` in `orb-chat-ui/Dockerfile`.

## Validation

- Ran `docker compose build` inside `orb-chat-ui/`.
- Build completed successfully and produced image `orb-chat-ui-orb-chat-ui:latest`.

## Stale documentation check

- Reviewed `orb-chat-ui/README.md`; no route/build instructions were stale for this fix.
- No additional doc edits were required beyond this wiki entry.
