# 2026-03-20 Project Navigation Tree Component Style

## Request

Switch project navigation listing to the tree navigation style defined in `tree-component.md`, with:

- projects as top-level nodes,
- resources nested under each project as a deeper level.

## Changes

### Backend

Updated `portal/views.py`:

- `_projects_for_user` now prefetches `resources` ordered by name to support nested tree rendering without N+1 queries.

### Home template

Updated `portal/templates/portal/index.html` authenticated project panel:

- replaced flat project list with `<details>/<summary>` tree structure.
- added root `All Projects` node.
- each project is a folder node with resource count.
- each project node contains resource links as child rows.
- project overview link (`Open`) remains available in each project summary row.

### Styling

Added tree-style classes inspired by `tree-component.md`:

- `wiki-tree-node*`
- `wiki-tree-page*`
- `folder-icon`
- nested child guideline + token/pill styling

## Verification

- `python manage.py check` passed.
- template load check for `portal/index.html` passed.

## Stale Documentation Check

- Reviewed current `README.md` and wiki entries.
- No README changes needed; existing architecture and route documentation remain accurate.
