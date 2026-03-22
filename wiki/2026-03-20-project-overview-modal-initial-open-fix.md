# 2026-03-20 Project Overview Modal Initial Open Fix

## Issue

Project overview `Add Resource` modal rendered open on load and could not reliably close.

## Fix

Updated `portal/templates/portal/project_overview.html` modal behavior:

- switched from `hidden` attribute toggling to explicit class-based visibility:
  - base `.modal-backdrop` => `display: none`
  - `.modal-backdrop.is-open` => `display: grid`
- JS now controls visibility via `classList.add/remove('is-open')`.
- added explicit initialization call `closeResourceModal()` on load to force closed state.
- Escape handling now checks `is-open` class state.
- modal also updates `aria-hidden` on open/close.

## Verification

- `python manage.py check` passed.
- template load check for `portal/project_overview.html` passed.

## Stale Documentation Check

- reviewed README/wiki docs.
- no README updates needed for this modal state bugfix.
