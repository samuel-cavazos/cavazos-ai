# 2026-03-21 Live Intelligence Panel Removal

## Summary
Removed the container/card styling behind the landing-page **Live Intelligence** content so it renders directly on the page canvas.

## Changes
- Updated panel styling split so only orb preview keeps card treatment:
  - `portal/templates/portal/index.html`
  - `orb-chat-ui/index.html`
- Moved border/background/blur/radius styles from shared selector to `.orb-panel` only.
- Explicitly set `.intro` to canvas-style rendering:
  - `border: 0`
  - `background: transparent`
  - `backdrop-filter: none`
  - `border-radius: 0`
- Kept grid layout and padding unchanged to preserve spacing and responsive behavior.

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-21-landing-login-light-dark-theme-support.md`
  - `wiki/2026-03-19-landing-chat-split.md`
- Result: no stale operational docs found. Existing entries remain valid as historical change records; this note documents the current panel-style update.
