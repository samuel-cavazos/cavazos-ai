# 2026-03-21 Landing Tagline H2 Typography

## Summary
Adjusted the landing/login intro tagline to use h2-sized typography instead of the larger h1 treatment.

## Changes
- Added a dedicated `.intro-headline` style in:
  - `portal/templates/portal/index.html`
  - `orb-chat-ui/index.html`
- Updated intro tagline markup in both files from:
  - `<h1>Wrangle bugs in your code before they run wild.</h1>`
  - to `<h2 class="intro-headline">Wrangle bugs in your code before they run wild.</h2>`
- Kept full-width rendering (`max-width: none`) so the previous width behavior remains unchanged.

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-21-landing-headline-copy-update.md`
  - `wiki/2026-03-21-landing-tagline-full-width.md`
- Result: no stale docs found. Prior entries remain accurate for copy and width; this entry records the typography adjustment.
