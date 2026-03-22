# 2026-03-20 Landing Orb Isolation

## What changed

- Removed iframe-based orb embedding from landing pages.
- Added dedicated landing renderer `orb-chat-ui/landing-orb.js` that has no chat input or chat submit handlers.
- Updated both landing pages to render an in-page orb container (`#landingOrbContainer`) instead of embedding chat:
  - `portal/templates/portal/index.html`
  - `orb-chat-ui/index.html`
- Removed Django `orb-preview` route and view to avoid exposing chat-template rendering for landing preview.
- Updated static Docker config to include `landing-orb.js` in build context and image.

## Validation

- Python syntax check passed for updated Django modules.
- JavaScript syntax check passed for `landing-orb.js`.
- `docker compose build` in `orb-chat-ui/` completed successfully after including `landing-orb.js`.

## Stale documentation check

- Updated root `README.md` to remove old iframe preview route mention.
- Updated `orb-chat-ui/README.md` to document `landing-orb.js` and direct-render behavior.
- Updated previous Django setup wiki note to avoid stale `orb-preview` route language.
