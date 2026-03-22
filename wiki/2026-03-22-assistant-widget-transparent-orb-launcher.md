# 2026-03-22 Assistant Widget Transparent Orb Launcher

## Summary
Reworked the floating "Beast" chat trigger on the landing/login page so the launcher uses the interactive water-orb renderer with transparent surroundings, making the orb appear to float over the page canvas.

## What Changed
- Updated `portal/templates/portal/index.html`:
  - Replaced the prior CSS-only orb launcher markup with a dedicated canvas host:
    - `#assistantWidgetOrbCanvas`
  - Restyled `.assistant-widget-launcher` to be an orb-first floating button.
  - Removed the synthetic pseudo-element orb animation styles and replaced them with canvas host styles.
  - Removed dark fill behind the launcher shell so only the rendered orb appears (transparent around the orb).
  - Added an inline launcher renderer (`initializeLauncherOrb`) that:
    - imports Three.js dynamically
    - runs a compact water ripple simulation
    - renders the orb with alpha outside the sphere (`gl_FragColor` uses `inCircle` as alpha)
    - responds to pointer hover/move and click/touch for ripple effects
    - disposes event listeners/renderer on unload
  - Preserved existing popup widget behavior (`open`, `close`, message rendering, Markdown/Mermaid support).

## Verification
- `python3 -m compileall portal` passed.
- Could not run `manage.py check` in this environment because Django dependencies are not installed (`ModuleNotFoundError: No module named 'django'`).

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-21-assistant-popup-widget-markdown-mermaid.md`
  - `README.md`
  - `orb-chat-ui/README.md`
- Result:
  - No documentation conflicts found.
  - Existing widget docs remain valid; this update is a visual/interaction enhancement of the launcher trigger.
