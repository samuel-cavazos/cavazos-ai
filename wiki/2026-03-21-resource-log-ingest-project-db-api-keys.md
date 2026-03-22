# 2026-03-21 Resource Log Ingest + Project-DB API Keys

## Request

Add resource log ingest endpoint support for cloud-style forwarding with allowed levels:

- `debug`
- `info`
- `warning`
- `error`
- `alert`

Then enforce resource-level API key authentication for `/logs/` and ensure API keys are stored in the **project SQLite DB** (not global Django DB).

## What Changed

### Project DB schema (`project.sqlite3`)

Extended `ensure_project_storage()` to create and maintain:

- `resource_api_keys`
- `resource_logs`

in addition to existing `resources` mirror table.

Added helpers in `portal/project_storage.py` for:

- create/list/revoke resource API keys
- authenticate resource API keys (with `last_used_at` update)
- store ingested resource logs

### Log ingest endpoint

Added route:

- `POST /projects/<project-uuid>/resources/<resource-uuid>/logs/`

Behavior:

- requires resource API key via `X-Resource-API-Key` or `Authorization: Bearer ...`
- accepts single log object or batch `{"logs": [...]}` payload
- validates levels: `debug`, `info`, `warning`, `error`, `alert` (case-insensitive input)
- writes logs to project DB `resource_logs`

### Resource detail API key management

Added superuser-only resource API key controls in resource detail UI:

- create key
- list keys (name, prefix, status, created/last-used)
- revoke key

The newly created key value is shown once via session-backed flash payload.

### Routing and views

Added UUID-based endpoints:

- create API key
- revoke API key
- ingest logs

Updated view context for resource detail to surface API keys from project DB.

### Tests

Expanded `portal/tests.py` coverage:

- superuser API key creation
- non-superuser API key create forbidden
- `/logs/` rejects missing key
- `/logs/` accepts valid key + `Alert` level
- `/logs/` rejects invalid level

## Verification

Executed:

- `.venv/bin/python manage.py makemigrations --check`
- `.venv/bin/python manage.py test`
- `.venv/bin/python manage.py check`

Results:

- no pending Django model migrations
- tests passed (`15` tests)
- Django system check clean

## Stale Documentation Check

- Reviewed route/storage documentation for this feature area.
- Updated `README.md` to document:
  - resource API key management routes
  - `/logs/` ingest route and auth headers
  - log payload contract and levels
  - project DB storage of `resource_api_keys` and `resource_logs`
- No additional active docs with conflicting log-ingest/API-key behavior were found.
