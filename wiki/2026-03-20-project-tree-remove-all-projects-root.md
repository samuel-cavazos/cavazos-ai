# 2026-03-20 Project Tree Remove All Projects Root

## Request

Remove the `All Projects` top-level wrapper in project navigation tree.

## Changes

Updated `portal/templates/portal/index.html`:

- removed the root `<details>` node labeled `All Projects`.
- projects are now rendered directly as top-level tree folder nodes.
- each top-level project still contains nested resource rows and `Open` action.

## Verification

- `python manage.py check` passed.
- template load check for `portal/index.html` passed.

## Stale Documentation Check

- Reviewed README and existing wiki docs.
- No README updates required for this structure-only UI tweak.
