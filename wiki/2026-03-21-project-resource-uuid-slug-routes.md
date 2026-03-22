# 2026-03-21 Project/Resource UUID + Slug Routes

## Request

Rework routing so project/resource pages use stable UUID-backed paths, then add editable slug-based URLs:

- project detail at UUID path
- resource detail at UUID path
- project slug editable in project settings modal for `/projects/<slug>/`
- resource slug support as well

## What Changed

### Data model

- Added immutable `uuid` fields to:
  - `Project`
  - `Resource`
- Added `Resource.slug` with per-project uniqueness constraint.
- Extended model behavior:
  - `Resource.save()` now slugifies provided slug or auto-generates a unique slug from resource name.
  - `Project.save()` now handles slug changes by moving/ensuring project storage directory and re-syncing resource mirror rows.

### Migration

- Added `portal/migrations/0003_project_and_resource_uuid_slug_routes.py`.
- Migration strategy:
  - add nullable UUID fields first
  - add `Resource.slug`
  - backfill UUIDs and unique per-project resource slugs via data migration
  - enforce UUID uniqueness/non-null and add per-project resource slug unique constraint

### Routes and views

- Replaced integer-param management routes with UUID params for project/resource management endpoints.
- Added canonical slug routes:
  - `/projects/<project-slug>/`
  - `/projects/<project-slug>/resources/<resource-slug>/`
- Added UUID project route redirect to canonical slug route.
- Added superuser settings POST endpoints:
  - project slug update
  - resource slug update

### UI templates

- Home/project navigation links now use slug routes.
- Project overview links/resources now resolve using slugs for detail pages.
- Added **Project Settings** modal in project overview for superuser slug updates.
- Added optional `Resource Slug` input in add-resource modal.
- Added resource slug update form on resource detail page for superusers.

### Tests

- Added `portal/tests.py` covering:
  - slug and UUID route behavior
  - UUID management POST endpoints
  - superuser authorization behavior
  - slug update flows
  - old integer URL non-support

## Verification

Executed:

- `python3 -m compileall portal cavazos_ai manage.py`
- `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- `.venv/bin/python manage.py makemigrations --check`
- `DJANGO_DB_PATH=/tmp/cavazos-test.sqlite3 .venv/bin/python manage.py migrate --noinput`
- `PROJECTS_ROOT=/tmp/cavazos-projects DJANGO_DB_PATH=/tmp/cavazos-test.sqlite3 .venv/bin/python manage.py test`

Results:

- compile succeeded
- migrations check passed with no pending model changes
- test suite passed (`10` tests)

## Stale Documentation Check

- Checked docs for old integer project/resource route references.
- Updated `README.md` route and UX sections to reflect new UUID + slug behavior.
- No additional active docs with stale integer route references were found.
