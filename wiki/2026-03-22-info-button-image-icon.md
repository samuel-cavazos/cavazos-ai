# 2026-03-22 Info Button Replaced With Image Icon

## Summary
Replaced the landing-page `Info` text button with the provided `info-icon.png` image button.

## Changes
- Synced icon asset:
  - `info-icon.png` -> `orb-chat-ui/info-icon.png`
- Updated `portal/templates/portal/index.html`:
  - Replaced intro `Info` link text button with image link using `{% static 'info-icon.png' %}`.
  - Added `.info-image-link img` sizing rule so icon button uses compact icon dimensions instead of full-size login image dimensions.
- Updated `orb-chat-ui/index.html` for standalone parity:
  - Replaced `Info` text link with image icon link (`info-icon.png`).
  - Added matching `.info-image-link img` size rule.

## Verification
- Ran `manage.py check` successfully (no issues).
- Confirmed static icon file exists at `orb-chat-ui/info-icon.png`.

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-login-image-buttons-and-theme-support.md`
  - `wiki/2026-03-21-login-page-cavazos-texas-makeover.md`
- Result: no stale docs found; this update is additive (Info control icon swap).
