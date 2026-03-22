# 2026-03-20 Remove Scope From Add Resource Modal

## Request

Remove the `Scope` field from the `Add Resource` modal form.

## Change

Updated `portal/templates/portal/project_overview.html`:

- removed the `Scope` select field (`resource_scope`) from the modal form.
- remaining fields unchanged.

Backend remains compatible since `resource_scope` is optional and defaults to `account` when not provided.

## Verification

- `python manage.py check` passed.
- template load check for `portal/project_overview.html` passed.

## Stale Documentation Check

- reviewed README/wiki docs.
- no README update required for this form-field removal.
