# 2026-03-22 Resource Log Ingest URL: Full HTTPS + Copy Box

## Summary
Updated the resource detail API-key section to show the full HTTPS log ingest endpoint in a horizontally-scrollable URL box with a one-click copy button.

## What Changed
- Updated `portal/views.py` in `_resource_detail_response`:
  - Added `resource_log_ingest_path` using `reverse("portal:resource-log-ingest", ...)`.
  - Added `resource_log_ingest_url` as full absolute URL using host + HTTPS:
    - `https://<host>/projects/<project-uuid>/resources/<resource-uuid>/logs/`
- Updated `portal/templates/portal/resource_detail.html`:
  - Replaced inline relative-path text (`/projects/.../logs/`) with:
    - scrollable URL container (`.copy-url-box`) showing `{{ resource_log_ingest_url }}`
    - `Copy URL` button (`#copyResourceLogIngestUrlBtn`)
  - Added small JS handler:
    - primary path: `navigator.clipboard.writeText(...)`
    - fallback path: select + `document.execCommand("copy")`
    - temporary `Copied` button feedback state.

## Verification
- `python3 -m compileall portal` passed.
- `.venv/bin/python manage.py test portal.tests` passed (`20` tests).
- Added/verified test in `portal/tests.py`:
  - `test_resource_detail_displays_full_https_log_ingest_url_for_superuser`
- Inline script syntax check passed:
  - `node --check /tmp/resource-detail-inline.js`

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-21-resource-log-ingest-project-db-api-keys.md`
  - `wiki/2026-03-22-sitewide-assistant-widget-global-include-chat-cutover.md`
- Result:
  - Resource log-ingest and API-key architecture docs remain correct.
  - Resource-detail UI copy now uses a full URL box + copy action instead of a relative-path code snippet; this entry supersedes older UI wording.
