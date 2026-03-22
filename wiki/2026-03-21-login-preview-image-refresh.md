# 2026-03-21 Login Preview Image Refresh

## Request

Replace the previously used login preview image with the newly recreated `./logo.png`.

## What Changed

- Synced recreated root image into static asset path used by the landing/login page:
  - source: `/home/data-team/cavazos-ai/logo.png`
  - destination: `/home/data-team/cavazos-ai/orb-chat-ui/logo.png`

## Verification

- Confirmed destination file metadata now matches recreated source image:
  - PNG `1024 x 1024`

## Stale Documentation Check

- Reviewed docs scope for this change.
- No route/API/behavior changes were introduced; no README updates required.
