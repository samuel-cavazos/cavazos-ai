# 2026-03-20 Project Tree Default Collapsed

## Request

Initialize the project navigation tree collapsed by default.

## Changes

Updated `portal/templates/portal/index.html`:

- removed default `open` state on top-level project `<details>` nodes.
- all project directories now render collapsed on initial page load.

## Verification

- `python manage.py check` passed.
- template load check for `portal/index.html` passed.

## Stale Documentation Check

- Reviewed README and wiki docs.
- No README updates needed for this default-state UI change.
