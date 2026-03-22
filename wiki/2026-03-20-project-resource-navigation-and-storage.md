# 2026-03-20 Project Resource Navigation And Storage

## Request

Implement project/resource portal foundations using `resources.md` as the resource payload reference:

- Users should see project navigation after login.
- Projects contain resources.
- Superusers can assign users to projects.
- Project directory + project-level SQLite should be created in persistent storage.
- Resource records should exist in global Django DB and project DB mirror.

## What Changed

### Data model and storage

- Added `Project`, `ProjectMembership`, and `Resource` models in `portal/models.py`.
- Added signal-based storage sync:
  - ensure per-project directory/db exists after project save.
  - upsert resource mirror row after resource save.
  - delete mirror row after resource delete.
- Added `portal/project_storage.py` helpers for project DB lifecycle and mirror row operations.
- Added `PROJECTS_ROOT` setting (defaults to `/data/projects`).

### Portal endpoints and access behavior

- Added routes and views:
  - project create
  - project overview
  - project member add
  - project resource create
  - project resource detail
  - project resource delete
- Enforced access:
  - superusers see all projects.
  - non-superusers only see projects they are members of.
  - management POST routes are superuser-only.

### UI templates

- Updated landing `portal/templates/portal/index.html` authenticated panel:
  - now shows project navigation instead of role placeholder-only content.
  - includes superuser project-create form.
- Added `portal/templates/portal/project_overview.html`:
  - resource listing, delete action, member management, create-resource form.
- Added `portal/templates/portal/resource_detail.html`:
  - global resource data + project mirror record display.

### Admin and migrations

- Added `portal/admin.py` registrations for new models.
- Generated migration `portal/migrations/0001_initial.py`.

## Verification

Executed in container image with repository bind-mounted:

- `python manage.py makemigrations portal`
- `python manage.py migrate --noinput`
- `python manage.py check`
- `python manage.py showmigrations portal`
- template load check for:
  - `portal/index.html`
  - `portal/project_overview.html`
  - `portal/resource_detail.html`

Results:

- Migration `portal.0001_initial` applied successfully.
- System check returned no issues.
- Templates loaded successfully.

## Stale Documentation Check

- `README.md` was stale (still described role placeholders on `/`).
- Updated `README.md` to describe project navigation flow, project/resource routes, and persistent project DB storage.
