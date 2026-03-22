# 2026-03-20 Superuser Only Project Controls Hardening

## Request

Ensure project detail controls are visible only to superusers:

- settings cog
- Add Resource
- Member Access section

## Changes

### View context

Updated `portal/views.py` in `project_overview`:

- added explicit `can_manage_project = request.user.is_superuser` to template context.

### Template guards

Updated `portal/templates/portal/project_overview.html`:

- switched relevant control blocks from `user.is_superuser` checks to `can_manage_project`:
  - header settings cog
  - header `Add Resource` button
  - resource delete action buttons
  - `Manage Access` panel
  - `Add Resource` modal wrapper

This keeps UI visibility and capability aligned with superuser access.

## Verification

- `python manage.py check` passed.
- template load check for `portal/project_overview.html` passed.

## Stale Documentation Check

- reviewed README/wiki docs.
- no README updates required; no route or data contract changes.
