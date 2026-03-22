# 2026-03-21 Superuser Home Shared Media Link De-emphasis

## Summary
- Reduced visual prominence of the shared media entry point on authenticated home (`/`) for superusers.
- Removed the large shortcut container that sat above the project navigation tree.
- Replaced it with a compact inline `Shared media gallery` utility link adjacent to the `Admin` role chip.

## Files Updated
- `portal/templates/portal/index.html`
  - removed `.admin-shortcuts` and related note styles/markup
  - added `.admin-utility-link` style
  - moved gallery entry point into the dashboard header line

## Validation
- Template structure reviewed after edit; no route or backend behavior changed.
- Runtime Django checks were not executed in this environment because dependencies are unavailable.

## Stale Documentation Check
- Reviewed `README.md` and existing wiki route notes:
  - no route/access behavior changed
  - no additional README/wiki updates required beyond this UI change log entry
