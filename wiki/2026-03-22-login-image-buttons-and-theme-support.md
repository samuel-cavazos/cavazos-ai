# 2026-03-22 Login Image Buttons + Light/Dark Theme Support

## Summary
- Swapped landing/login CTA buttons to use user-provided image assets:
  - `login.png`
  - `logout.png`
- Restored full light/dark support for the redesigned login page by making guest styling theme-variable driven (light base with dark overrides).

## Changes
- Synced root assets into static directory served by Django:
  - `login.png` -> `orb-chat-ui/login.png`
  - `logout.png` -> `orb-chat-ui/logout.png`
- Updated `portal/templates/portal/index.html`:
  - Replaced intro login text button with image button using `{% static 'login.png' %}`.
  - Replaced header logout text button with image button using `{% static 'logout.png' %}`.
  - Added reusable image-button styles (`.image-action-btn` / `.image-action-link`).
  - Converted `landing-guest` theme to:
    - light-mode defaults
    - dark-mode overrides via:
      - `@media (prefers-color-scheme: dark)` (unless forced light)
      - explicit `:root[data-theme="dark"]` / `html.dark`
  - Updated guest accent colors and panel/card tones to use theme variables instead of hardcoded dark-only values.
- Updated `orb-chat-ui/index.html`:
  - Replaced login text link with image button (`login.png`) for standalone parity.
  - Added matching image-link styling.

## Verification
- Ran `manage.py check` successfully (no issues).

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-21-login-page-cavazos-texas-makeover.md`
  - `wiki/2026-03-21-landing-login-light-dark-theme-support.md`
  - `wiki/2026-03-21-assistant-popup-widget-markdown-mermaid.md`
- Result:
  - prior makeover docs remain valid historical context.
  - this entry records the new image-button controls and current guest light/dark behavior baseline.
