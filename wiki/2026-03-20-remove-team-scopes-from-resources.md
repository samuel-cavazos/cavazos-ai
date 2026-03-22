# 2026-03-20 Remove Team Scopes From Resources

## Request

Remove team-scope support from resources and database.

## Changes

### Data model / database

Updated `portal/models.py`:

- removed `Resource.resource_team_names` field.
- removed `team` from `Resource.ACCESS_SCOPE_CHOICES`.
- removed `team` from `Resource.ssh_credential_scope` choices (via shared scope choices).

Generated and applied migration:

- `portal/migrations/0002_remove_resource_resource_team_names_and_more.py`
  - drops `resource_team_names` column.
  - migrates any existing `access_scope='team'` to `account`.
  - migrates any existing `ssh_credential_scope='team'` to `account`.
  - updates field choices to `account|global`.

### Request payload normalization

Updated `portal/views.py` `_normalize_resource_payload`:

- removed parsing of `resource_scope` and `resource_team_names`.
- resource `access_scope` now defaults to `account` in this implementation.
- `ssh_scope` is sanitized to allowed values (`account|global` or blank).

### UI

Updated `portal/templates/portal/project_overview.html`:

- removed `Resource Team Names` from Add Resource modal.
- removed `Team` option from `SSH Credential Scope`.

Updated `portal/templates/portal/resource_detail.html`:

- removed `Team Names` display row.

### Project DB mirror metadata

Updated `portal/project_storage.py`:

- removed `resource_team_names` from mirrored `metadata_json` payload.

## Verification

- `python manage.py migrate --noinput` applied migration `portal.0002...`.
- `python manage.py check` passed.
- `python manage.py makemigrations --check --dry-run` reported no pending changes.
- template load checks passed for:
  - `portal/project_overview.html`
  - `portal/resource_detail.html`
- smoke test resource creation confirmed no `resource_team_names` attribute and no mirrored `resource_team_names` metadata key.

## Stale Documentation Check

- `README.md` was updated to remove `resource_team_names` mention and reflect `access_scope` as `account|global`.
- historical wiki entries remain as change history; current behavior is documented here.
