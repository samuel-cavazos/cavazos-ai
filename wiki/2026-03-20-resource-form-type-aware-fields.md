# 2026-03-20 Resource Form Type Aware Fields

## Request

Make the project resource creation form show only fields relevant to the selected `resource_type`.

Examples requested:

- SSH fields only for Virtual Machines.
- DB fields only for Databases.
- API form should not ask for VM/DB-only fields.

## Changes

Updated `portal/templates/portal/project_overview.html`:

- Added resource-type grouped field sections with `data-resource-types`.
- Added conditional required rules with `data-required-for`.
- Added client-side controller bound to `#resourceTypeSelect` to:
  - show/hide relevant field groups,
  - disable hidden group controls so they are not submitted,
  - apply `required` only for active type-relevant fields.

### Active field behavior

- `api`:
  - shows `healthcheck_url` (required)
- `vm`:
  - shows `address` (required)
  - shows SSH sections
- `database`:
  - shows `address` (required)
  - shows `port`, `db_type`
- `queue`, `service`, `other`:
  - shows `target` (required)
- Common sections remain visible for all types:
  - scope/team fields
  - github repositories
  - notes

## Verification

- `python manage.py check` -> no issues.
- Template load check for `portal/project_overview.html` -> success.

## Stale Documentation Check

- Reviewed README and existing wiki entries.
- No stale README updates required for this UI-only behavior; existing architecture docs remain accurate.
