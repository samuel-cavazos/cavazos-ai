# 2026-03-22 Feature Stars Toggle via Info Icon

## Summary
Changed the landing/login highlight star points to be collapsed by default and expand/collapse when the Info icon is pressed.

## Changes
- Updated `portal/templates/portal/index.html`:
  - Feature list now supports collapse animation via:
    - `.feature-list.is-collapsed`
    - animated `max-height`, `opacity`, and margin transitions
  - Replaced Info icon anchor with toggle button:
    - `id="toggleFeatureListBtn"`
    - `aria-controls="featureList"`
    - `aria-expanded` updates on toggle
  - Set feature list initial collapsed state:
    - `class="feature-list is-collapsed"`
    - `aria-hidden="true"`
  - Added JS toggle handler in existing landing auth script.
  - Reset list to collapsed when returning to intro panel (`showInfoPanel()`).
- Updated `orb-chat-ui/index.html` for standalone parity:
  - same collapsed-by-default list and Info icon toggle behavior
  - added lightweight toggle script near existing footer/year script.

## Verification
- Ran `manage.py check` successfully (no issues).

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-info-button-image-icon.md`
  - `wiki/2026-03-22-login-stars-single-row.md`
- Result: no stale docs found; this entry adds interaction behavior on top of the existing icon and layout updates.
