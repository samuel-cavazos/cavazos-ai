# 2026-03-21 Superuser Portal Tree + Create Input Theme Support

## Summary
- Updated authenticated portal styling on `/` in `portal/templates/portal/index.html` so superuser admin controls support both light and dark modes.
- Added theme tokens for admin/navigation components:
  - role chip
  - project tree container and item styles
  - tree action button styles
  - tree branch guide line
  - muted/resource meta text
  - project empty-state text
- Updated "Create project" input (`.inline-input`) to use shared theme-aware field/focus tokens instead of dark-only colors.

## Components Updated
- `.role-chip`
- `.folder-icon`
- `.wiki-tree-node*`
- `.wiki-tree-page*`
- `.project-empty`
- `.inline-input`

## Validation
- Manual CSS review confirms all targeted superuser components now read from theme variables.
- Runtime checks were not executed in this environment because Django dependencies are not installed.

## Stale Documentation Check
- Reviewed existing wiki auth/landing notes; no route/behavior docs changed.
- No stale README/wiki docs found for this style-only update.
