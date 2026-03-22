# 2026-03-21 Superuser Shared Media Gallery

## Summary
- Added a dedicated superuser-only gallery page at `/superuser/gallery/` for shared media management.
- Added superuser-only upload and delete endpoints:
  - `/superuser/gallery/upload/` (POST)
  - `/superuser/gallery/delete/` (POST)
- Added public media URL serving at `/shared/<filename>` so uploaded files can be reused in emails and external sites.
- Linked the new gallery from superuser-facing UI:
  - authenticated home portal panel (`/`)
  - ops topbar (`/ops/`)

## Backend Changes
- Updated `cavazos_ai/settings.py`:
  - `SHARED_MEDIA_ROOT` with Docker-aware default (`/data/shared` when available, fallback to `<repo>/data/shared`)
  - `SHARED_MEDIA_MAX_UPLOAD_BYTES` defaulting to 25 MB
- Updated `portal/urls.py` with gallery + public shared media routes.
- Updated `portal/views.py` with:
  - gallery render/list view (`media_gallery`)
  - upload handler (`media_gallery_upload`)
  - delete handler (`media_gallery_delete`)
  - public file-serving view (`shared_media_file`)
  - filename normalization, blocked extension checks, unique filename conflict handling, and byte-size formatting helpers

## UI Changes
- Added `portal/templates/portal/media_gallery.html`:
  - dedicated upload panel
  - latest-upload URL copy field
  - card-based media grid with previews for image/video/audio
  - copy URL + open + delete actions per file
- Updated `portal/templates/portal/index.html` to include a superuser shortcut card linking to the gallery.
- Updated `portal/templates/portal/ops.html` to include a `Shared Gallery` topbar action.

## Security/Behavior Notes
- Upload blocks active-content extensions (`.html`, `.js`, `.svg`, scripts, executables, etc.) to reduce same-origin abuse risk.
- Public shared-media responses include:
  - `X-Content-Type-Options: nosniff`
  - long-lived cache header (`public, max-age=31536000, immutable`)
- Files with duplicate names are auto-renamed using numeric suffixes (for example: `logo-2.png`).

## Validation
- `python3 -m py_compile portal/views.py portal/urls.py cavazos_ai/settings.py` passed.
- `python manage.py check` could not run because Django is not installed in this environment.

## Stale Documentation Check
- Reviewed `README.md` route/access documentation and updated it to include shared media routes, access rules, and media storage configuration.
- Reviewed existing wiki entries related to portal navigation and superuser surfaces; no additional stale docs required changes for this feature.
