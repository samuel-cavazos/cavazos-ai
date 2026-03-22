# 2026-03-20 Auth Form Layout Refinement

## What changed

- Refined landing auth panel spacing in `portal/templates/portal/index.html` so login/sign-up forms fit more comfortably within the left panel.
- Increased shared panel min-height on desktop and tablet breakpoints to keep form content vertically balanced.
- Constrained auth panel content width and centered it (`max-width` + `margin-inline: auto`) so fields are easier to scan.
- Increased form rhythm with larger field/input spacing and slightly larger input padding.
- Kept mobile behavior practical by removing width constraints at small breakpoints and preserving top-aligned flow.

## Validation

- Django app check passed in the compose runtime via:
  `docker compose -f orb-chat-ui/compose.yaml exec -T cavazos-ai python manage.py check`.
- Verified the landing template still uses the same in-panel transition architecture (`.auth-panel-stack` / `.auth-panel-view`) with no route navigation required.

## Stale documentation check

- Reviewed `README.md` and `orb-chat-ui/README.md`; existing route/runtime/auth documentation remains accurate after this UI-spacing-only change.
- No README edits were required.
