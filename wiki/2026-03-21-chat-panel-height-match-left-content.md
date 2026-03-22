# 2026-03-21 Chat Panel Height Match (Login Layout)

## Summary
Adjusted the landing/login two-column layout so the right chat/orb panel matches the left content column height on desktop.

## Changes
- `portal/templates/portal/index.html`
  - Ensured `.orb-panel` fills available column height with `height: 100%`.
  - Updated orb panel internal grid to `grid-template-rows: auto 1fr auto` so heading + orb canvas + assistant composer fill correctly.
  - Changed guest layout alignment from `align-items: start` to `align-items: stretch` in `.landing-guest .hero`.
- `orb-chat-ui/index.html`
  - Changed `.hero` alignment to `align-items: stretch`.
  - Added `height: 100%` to `.orb-panel` for parity with the Django template layout behavior.

## Verification
- Ran `manage.py check` successfully (no issues).

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-21-login-page-cavazos-texas-makeover.md`
  - `wiki/2026-03-21-live-intelligence-panel-removal.md`
- Result: no stale docs found. This entry extends the layout behavior from the makeover pass.
