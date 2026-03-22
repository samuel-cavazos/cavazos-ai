# 2026-03-22 Widget Orb Faceted Polyhedron Effect

## Summary
Replaced the launcher orb swirl shader with a faceted polyhedron-style effect and softened the inner boundary transition into the orb shell.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - Launcher orb border softened:
    - `border: 1px solid rgba(183, 211, 236, 0.34);`
  - Replaced swirl fragment shader logic with faceted shading:
    - Uses rotating icosa-style normals (dual-inspired faceting for dodeca-like look).
    - Computes nearest/second-nearest face influence for visible facet seams.
    - Keeps animated color cycling via time + water ripple influence.
  - Added shell blend near the edge to smooth the previous hard inner boundary:
    - Edge region now transitions into a shell color mix instead of a sharp ring.

## Verification
- `python3 -m compileall portal` passed.
- Extracted widget script syntax check passed:
  - `node --check /tmp/widget-inline.js`

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-widget-orb-shadow-removal.md`
  - `wiki/2026-03-22-orb-aura-edge-falloff-fit.md`
  - `wiki/2026-03-22-orb-size-tuning-inset-minus-8.md`
- Result:
  - Shadow-removal and size-tuning docs remain accurate.
  - Aura/falloff notes are historical and superseded by the faceted shader behavior for the current launcher orb visuals.
