# 2026-03-21 Landing Assistant Composer Light/Dark Theme Support

## Summary
- Updated the landing orb-side assistant composer in `portal/templates/portal/index.html` to support both light and dark themes.
- Replaced hardcoded dark Tailwind utility styling on composer elements with theme-token-based CSS classes:
  - `assistant-form`
  - `assistant-icon`
  - `assistant-input`
  - `assistant-send`
  - `assistant-caption`
- Added light and dark design tokens for assistant composer surfaces, text, placeholders, focus states, and button gradients.

## Validation
- Manual code inspection confirms the assistant form no longer uses dark-only Tailwind classes.
- Runtime checks were not executed in this environment because Django dependencies are not installed.

## Stale Documentation Check
- Reviewed `wiki/2026-03-20-landing-portal-assistant-input.md`.
- Its note that the composer was "Tailwind-styled" is now historical for this component; this entry supersedes that implementation detail.
- No README route/behavior docs required updates.
