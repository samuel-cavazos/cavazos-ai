# 2026-03-21 Landing Login Light/Dark Theme Support

## Summary
- Updated landing/login styling in `portal/templates/portal/index.html` to support both light and dark appearance modes.
- Added light-mode design tokens as defaults and dark-mode token overrides for:
  - system preference (`@media (prefers-color-scheme: dark)`)
  - explicit theme forcing via `html.dark` or `data-theme="dark"`
- Refactored login-panel-adjacent styles (`.intro`, `.orb-panel`, `.btn-secondary`, `.panel-back`, `.login-label`, `.login-input`, `.auth-divider`, `.login-hint`, `.auth-switch`, `.auth-link`) to use theme variables instead of dark-only hardcoded colors.

## Validation
- `python3 manage.py check` failed locally because Django is not installed in this environment (`ModuleNotFoundError: No module named 'django'`).

## Stale Documentation Check
- Reviewed `README.md` and prior landing/login wiki pages for conflicts.
- No stale documentation found; existing auth/login flow docs remain accurate, and this change only adds visual theme support.

## Follow-up Fix
- Updated dark-theme selector precedence in `portal/templates/portal/index.html` so forced light mode is respected even if `html.dark` is present.
- Changed selector from `html.dark` to `html.dark:not([data-theme="light"])`.

## Follow-up Stale Documentation Check
- Existing note remains accurate; no further README/wiki updates required for this selector-precedence fix.
