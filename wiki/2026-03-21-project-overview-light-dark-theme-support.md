# 2026-03-21 Project Overview Light/Dark Theme Support

## Summary
- Updated `portal/templates/portal/project_overview.html` to support both light and dark themes.
- Added light-mode default tokens with dark-mode overrides for:
  - system preference (`@media (prefers-color-scheme: dark)`)
  - explicit dark forcing (`html.dark` / `data-theme="dark"`)
- Refactored project overview UI styles to use tokens instead of dark-only hardcoded values, including:
  - page background flares and panel surfaces
  - header buttons/nav links
  - message cards
  - project navigation cards and active state
  - resource cards and links
  - form labels/inputs/help text
  - add-resource modal backdrop/dialog/close button
  - orb frame + assistant wrapper
  - footer text

## Validation
- Manual CSS inspection confirms `project_overview.html` now reads visual colors from theme tokens.
- Runtime checks were not executed in this environment because Django dependencies are not installed.

## Stale Documentation Check
- Reviewed existing wiki/README entries for route and behavior conflicts.
- No stale docs found; this is a style-only update with no route or workflow changes.
