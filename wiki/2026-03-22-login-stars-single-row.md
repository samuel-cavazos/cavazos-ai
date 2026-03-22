# 2026-03-22 Login Star Highlights Single-Row Layout

## Summary
Adjusted the landing/login layout so the three starred highlight cards can fit on a single row on wider desktop viewports.

## Changes
- Updated `portal/templates/portal/index.html`:
  - Widened guest page container: `.landing-guest .page` to `min(1280px, 96vw)`.
  - Widened intro info content region: `.landing-guest .intro-info-view` max-width to `58rem`.
  - Changed highlight card grid to three columns on wide viewports:
    - `.landing-guest .feature-list { grid-template-columns: repeat(3, minmax(0, 1fr)); }`
  - Added responsive breakpoints:
    - `<= 1280px`: 2 columns
    - `<= 860px`: 1 column
- Mirrored corresponding width/grid breakpoint behavior in `orb-chat-ui/index.html` for standalone parity.

## Verification
- Ran `manage.py check` successfully (no issues).

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-21-login-page-cavazos-texas-makeover.md`
  - `wiki/2026-03-21-assistant-popup-widget-markdown-mermaid.md`
- Result: no stale operational docs found; this entry extends the existing makeover with responsive width/grid tuning.
