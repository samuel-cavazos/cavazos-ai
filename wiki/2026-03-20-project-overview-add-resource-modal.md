# 2026-03-20 Project Overview Add Resource Modal

## Request

Move the inline `Create Resource` form into an in-page modal and add `Add Resource` near top-right beside a settings cog.

## Changes

Updated `portal/templates/portal/project_overview.html`.

### Header actions

For superusers:

- added settings cog button (links to Django admin project change page).
- added `Add Resource` button next to settings cog in top-right actions.

### Resource creation UX

- removed inline `Create Resource` panel from page flow.
- added modal overlay + dialog containing full resource form.
- kept existing type-aware resource fields inside modal.
- modal controls:
  - open via `Add Resource`
  - close via X, Cancel, outside click, or Escape key.

### JS behavior

- preserved resource-type field toggling/required logic.
- added modal open/close handlers and body scroll lock while modal is open.

## Verification

- `python manage.py check` passed.
- template load check for `portal/project_overview.html` passed.

## Stale Documentation Check

- reviewed README and prior wiki docs.
- no README update required; this is a UI interaction refinement without route/data model changes.
