# 2026-03-21 Login Page Cavazos + Texas Makeover

## Summary
Reworked the unauthenticated login/landing experience with a cleaner, modern layout and a Cavazos/Texas visual direction focused on content placement and readability.

## What Changed
- Added new typography pair for guest experience:
  - `Fraunces` (headline serif)
  - `Manrope` (body UI)
- Added guest-only page mode via body class:
  - `landing-guest` (unauthenticated)
  - `landing-authed` (authenticated)
- Implemented guest-only palette and layout overrides in `portal/templates/portal/index.html`:
  - warm Texas-inspired accent tones mixed with the existing deep-blue platform aesthetic
  - tighter hero spacing and reduced empty vertical space in intro stack
  - stronger visual hierarchy for headline, lede, CTA buttons, and highlights
  - feature highlights converted to compact card-style items for cleaner scanning
  - login/sign-up panels styled as restrained cards for clarity and focus
- Updated intro content copy hierarchy in unauthenticated state:
  - added kicker: `Texas-built infrastructure command center`
  - refined supporting paragraph and highlight lines for clearer value communication
- Mirrored equivalent visual/content updates in `orb-chat-ui/index.html` for standalone parity.

## Files Updated
- `portal/templates/portal/index.html`
- `orb-chat-ui/index.html`

## Verification
- Ran `manage.py check` successfully (no issues).

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-21-landing-login-light-dark-theme-support.md`
  - `wiki/2026-03-21-live-intelligence-panel-removal.md`
  - `wiki/2026-03-21-landing-tagline-h2-typography.md`
- Result: no stale operational docs found. Prior pages remain valid historical records; this entry documents the new guest makeover baseline.
