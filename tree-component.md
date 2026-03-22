# Wiki Navigation Tree Component (Exact Recreation Spec)

This is the implementation-grade handoff for recreating the wiki navigation exactly as it exists today, both functionally and visually.

## 0) Source Of Truth (Do Not Guess)

Use these files as canonical behavior:

- Backend payload builder: `dashboard/views.py`
  - `_build_wiki_page_listing_context`
  - `_extract_wiki_h1_headings_from_markdown`
  - `_filter_wiki_navigation_headings`
- Wiki template + renderer: `dashboard/templates/pages/wiki.html`
- Shared sidebar/tree styling: `dashboard/static/css/app.css`
- Visual parity references (same nav style language):
  - `dashboard/templates/pages/resources.html`
  - `dashboard/templates/pages/team.html`
- Tests that encode nav metadata expectations: `dashboard/tests/test_wiki_navigation.py`

The root and `docs/` copies of this document must stay identical.

## 1) Component Boundaries

The wiki tree is built in 3 layers:

1. Server builds `wiki_pages` metadata dictionaries.
2. Template serializes each page into a hidden `<a data-wiki-row ...>` payload row.
3. Client JS reads rows, normalizes DTOs, and rebuilds a `<details>/<summary>` tree into `[data-wiki-tree]`.

The visible tree is JS-rendered; the hidden rows are the serialization contract.

## 2) Required DOM Contract

Required elements for full feature parity:

- `[data-wiki-tree]` mount point for generated tree
- `[data-wiki-row]` hidden source rows (one per page)
- `[data-wiki-search]` search input (optional but supported)
- `[data-wiki-visible-count]` visible page count (optional)
- `[data-wiki-no-results]` empty state block (optional)
- `[data-wiki-view-label]` banner label for active/open branch (optional)
- `[data-wiki-layout]` root shell for collapse class toggling
- `[data-wiki-sidebar-toggle]` collapse button in sidebar
- `[data-wiki-sidebar-open]` reopen button in banner

If the sidebar controls are missing, the tree still renders; collapse behavior is disabled.

## 3) Hidden Row Data Contract (`[data-wiki-row]`)

Each row is an anchor with class `wiki-sidebar-page-link` and optional `is-active` class.
`is-active` marks the selected page and drives auto-open behavior in the generated tree.

Example row:

```html
<a
  class="wiki-sidebar-page-link is-active"
  href="/wiki/?scope=resource&resource_uuid=...&page=docs/overview&page_id=123"
  data-wiki-row
  data-page-scope="resource"
  data-page-title="Overview"
  data-page-path="docs/overview"
  data-page-is-draft="0"
  data-page-nav-scope="team"
  data-page-teams="platform|sre"
  data-page-team-names="Platform|SRE"
  data-page-team-name=""
  data-page-nav-team-names="Platform|SRE"
  data-page-nav-wiki-label="Payments API"
  data-page-nav-h1-headings="[{&quot;title&quot;:&quot;Runbook&quot;,&quot;anchor&quot;:&quot;runbook&quot;,&quot;level&quot;:1}]"
  data-page-resource-name="Payments API"
  data-page-resource-uuid="b7a...">
</a>
```

### Attribute behavior

- `href`: required; fallback `#` if missing
- `data-page-scope`: `workspace|team|resource`; defaults to `workspace`
- `data-page-title`: page title; fallback to `data-page-path`, then `Untitled page`
- `data-page-path`: slash path; split into folder segments
- `data-page-is-draft`: `1|0`
- `data-page-nav-scope`: `account|team|global`; parser fallback `account`
- `data-page-team-names`: pipe-separated team names for workspace page grouping
- `data-page-team-name`: primary team name (team-scope pages)
- `data-page-nav-team-names`: pipe-separated team names for resource/team grouping
- `data-page-nav-wiki-label`: label for resource bucket; fallback order:
  1. `data-page-nav-wiki-label`
  2. `data-page-resource-name`
  3. `data-page-resource-uuid`
  4. `Wiki`
- `data-page-nav-h1-headings`: JSON array of heading objects
- `data-page-resource-name`: optional resource display name
- `data-page-resource-uuid`: optional resource UUID
- `data-page-teams`: currently emitted but not consumed by wiki JS (keep for compatibility)

Heading JSON item shape:

```json
{"title":"Runbook","anchor":"runbook","level":1}
```

`level` is normalized to `1` or `2` only.

## 4) Backend Metadata Rules (Exact)

`_build_wiki_page_listing_context` creates `wiki_pages` rows consumed by the template.

### 4.1 Scope-to-nav mapping

- Workspace pages:
  - draft => `nav_scope = account`
  - non-draft with team access => `nav_scope = team`
  - non-draft with no teams => `nav_scope = global`
  - `nav_wiki_label = Workspace Wiki`
- Team pages:
  - `nav_scope = team`
  - `nav_team_names` gets resolved team name
  - `nav_wiki_label = Team Wiki`
- Resource pages:
  - `nav_scope` pulled from resource access scope (`account|team|global`)
  - `nav_team_names` from resource team-sharing map
  - `nav_wiki_label` = resource name fallback to resource UUID fallback `Resource Wiki`

### 4.2 Heading extraction/filtering

If cached headings are unavailable/stale, markdown is parsed.

Extraction rules (`_extract_wiki_h1_headings_from_markdown`):

- Parses ATX H1/H2 only (`#` or `##`)
- Ignores fenced code blocks (``` and ~~~ toggles)
- Strips trailing `#` markers in heading text
- Anchor normalization:
  - lowercase
  - remove non `[a-z0-9\s-]`
  - collapse whitespace/hyphen runs to single `-`
  - fallback `section`
- Duplicate slug suffixing: `heading`, `heading-1`, `heading-2`, ...
- Hard cap max headings: 24 by default (bounded up to 80)

Filtering rules (`_filter_wiki_navigation_headings`):

- Keep only valid entries with title+anchor
- Normalize level into `1` or `2`
- Drop H1 whose normalized title equals page title
  - prevents duplicate page title in page-heading children

## 5) Frontend Normalization Rules

From `wiki.html` inline script:

- Source rows are normalized into `sourcePages[]` then sorted by:
  1. `path` ascending
  2. `title` ascending
- `parseList` splits on `|`, trims, drops empty values
- `parseHeadingList`:
  - parses JSON array only
  - accepts objects with `title`, `anchor`, `level`
  - coerces `level` to `1|2`
  - de-duplicates by case-insensitive key: `level:title#anchor`
  - invalid JSON => empty heading list

Each normalized page DTO includes:

- `href`, `title`, `path`, `segments[]`, `scope`, `isDraft`
- `navScope`, `teamNames[]`, `teamName`, `navTeamNames[]`
- `navWikiLabel`, `navH1Headings[]`
- `resourceName`, `resourceUuid`, `isActive`

## 6) Tree Grouping And Render Algorithm

Render root is always one top-level `All` folder node.

### 6.1 Search filter

Search term is case-insensitive substring across this haystack:

- title
- path
- `teamNames`
- `teamName`
- `navTeamNames`
- `navWikiLabel`
- heading titles
- `resourceName`
- `resourceUuid`

No match behavior:

- `[data-wiki-visible-count]` => `0`
- `[data-wiki-no-results]` shown
- `[data-wiki-view-label]` => `No pages`
- tree body not rendered

### 6.2 Grouping precedence

For each filtered item:

- `scope === resource`
  - with `navTeamNames`: Team -> Resource Label bucket
  - without `navTeamNames`: top-level Resource Label bucket
- `scope === team`
  - Team -> `Team Wiki` bucket (teamName + navTeamNames, deduped)
  - no team labels => workspace bucket
- `scope === workspace`
  - with `teamNames`: Team -> `Workspace Wiki` bucket
  - without teams: workspace bucket

### 6.3 Order and open-state rules

Ordering:

- Team buckets: alphabetical
- Resource buckets inside team: alphabetical
- Top-level resource buckets: alphabetical
- Workspace bucket rendered last (label `Workspace Wiki`)
- Recursive path folders: alphabetical by segment
- Leaf pages in a folder: alphabetical by title

Open behavior:

- Root `All` node is always open.
- Active page branch auto-opens up the chain.
- On initial non-search render, first top-level group auto-opens if nothing active opened yet.
- Page node (`wiki-tree-node--page`) opens when:
  - active page, or
  - search term present and page has headings

Heading children:

- Max 24 heading links rendered per page (`slice(0, 24)`)
- H1 class: `wiki-tree-page--heading-h1`
- H2 class: `wiki-tree-page--heading-h2`

## 7) Sidebar Collapse Behavior

Wiki sidebar collapse state:

- Storage key: `alshival.wiki.sidebar-collapsed`
- Class toggle target: `[data-wiki-layout]` adds/removes `is-sidebar-collapsed`
- Desktop only persistence
- Mobile (`max-width: 980px`): forced expanded; stored collapse ignored

Button choreography:

- Collapse button `[data-wiki-sidebar-toggle]` updates:
  - `aria-expanded`
  - `aria-label`
  - `title`
  - arrow glyph (`‹` / `›`)
- Reopen button `[data-wiki-sidebar-open]` toggles `.is-visible`

## 8) Visual Spec (Aesthetic Fidelity)

These values are the key style signatures from `app.css`.

### 8.1 Shell and sidebar

- `.resources-layout`: base 2-col grid `minmax(220px, 280px) minmax(0, 1fr)`
- `.wiki-layout` overrides to wide nav: `minmax(420px, 520px) minmax(0, 1fr)`
- `.wiki-layout.is-sidebar-collapsed`: single column + `.wiki-sidebar { display: none; }`
- `.team-folder-panel`: `padding: 0.9rem; position: sticky; top: 1rem`
- `.wiki-sidebar`:
  - `border-radius: 22px`
  - layered gradient background over `var(--panel)`

### 8.2 Tree primitives

- `.folder-icon`: pill token style used for `DIR`, `PG`, `H1`, `H2`
  - width `2.2rem`, tiny uppercase text, pill border
- `.wiki-tree-node`:
  - border `1px solid var(--border)`
  - radius `12px`
  - dark translucent background (light mode override)
- `.wiki-tree-node__summary`:
  - flex row, gap `0.45rem`, padding `0.4rem 0.5rem`
  - default details marker hidden
- `.wiki-tree-node__label`:
  - 600 weight, `0.82rem`, ellipsis truncation
- `.wiki-tree-node__count`:
  - `0.72rem`, `var(--muted)`
- `.wiki-tree-node__children`:
  - grid gap `0.22rem`, padded container
- `.wiki-tree-node--folder > .wiki-tree-node__children`:
  - left dashed guideline + nested indent

### 8.3 Page + heading rows

- `.wiki-tree-page` shared for page links and heading links
  - border radius `10px`, subtle paddings, transparent border by default
- Hover/focus: blue-tinted border/background
- Active: stronger blue border/background (`.wiki-tree-page.is-active`)
- `.wiki-tree-node--page > .wiki-tree-node__summary .wiki-tree-page` has tighter padding
- `.wiki-tree-page--heading-h2` adds left indent (`margin-left: 1rem`)

### 8.4 Responsive behavior

At `max-width: 980px`:

- `.resources-layout` collapses to single column
- `team-folder-panel` becomes non-sticky (`position: static`)
- JS forces sidebar expanded (no collapsed mode on mobile)

## 9) Shared Style Parity With Dev Projects

The Resources page uses the same nav visual language and collapse choreography:

- Same sidebar classes: `.wiki-sidebar`, `.wiki-sidebar-head`, `.wiki-sidebar-pages`
- Same tree classes: `.wiki-tree-node*`, `.wiki-tree-page*`, `.folder-icon`
- Same collapse UX pattern, but different storage key:
  - resources key: `alshival.resources.sidebar-collapsed`

If recreation must match both wiki and dev-projects aesthetics, copy the shared CSS blocks exactly rather than reinterpreting.

## 10) Non-Obvious Invariants

- Keep native `<details>/<summary>` structure; JS and keyboard behavior depend on it.
- Keep class names unchanged unless JS/template selectors are updated together.
- Keep hidden-row serialization approach; renderer expects DOM payload, not API fetch.
- Keep search as substring across all metadata fields (including heading titles).
- Keep active row marker (`is-active`) on hidden source row.
- Do not remove `data-page-teams` even though it is currently unused.

## 11) Validation Checklist (Before Hand-off)

1. Active wiki page auto-expands its full branch path and highlights selected page.
2. Search filters by title/path/team/resource/heading text and updates visible count.
3. Zero-result search shows no-results state and sets view label to `No pages`.
4. Resource pages shared to multiple teams appear under each team bucket.
5. Team pages group under `Team Wiki`; workspace under `Workspace Wiki`.
6. H1 equal to page title is not shown in heading links.
7. H2 headings render indented (`wiki-tree-page--heading-h2`).
8. Desktop collapse state persists across reloads.
9. Mobile width (`<= 980px`) always shows expanded sidebar behavior.
10. Visual treatment matches existing resources/wiki sidebars (spacing, radii, gradients, token pills).

## 12) Regression Guardrails

Current automated coverage (`dashboard/tests/test_wiki_navigation.py`) asserts:

- shared-resource pages expose correct `nav_wiki_label` and `nav_repo_label`
- heading extraction includes H2 and skips duplicate title H1

If behavior changes, update tests and this document in the same PR.
