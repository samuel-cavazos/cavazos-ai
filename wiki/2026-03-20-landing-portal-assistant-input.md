# 2026-03-20 Landing Portal Assistant Input

## What changed

- Added a Tailwind-styled portal assistant chat composer directly below the Beast orb on landing page (`/`).
- Loaded Tailwind utility runtime (`cdn.tailwindcss.com`) in landing template with `preflight` disabled to avoid overriding existing page base styles.
- Added portal assistant preview form elements:
  - input (`portalAssistantInput`)
  - send button (`portalAssistantSend`)
  - live-region reply target (`portalAssistantReply`)
- Added a minimal client-side submit handler that prevents full-page reload and keeps this composer in preview mode until backend wiring is added.

## Validation

- `curl http://localhost:5173/` returns `200`.
- Landing HTML contains:
  - Tailwind CDN script include
  - `portalAssistantForm`
  - `portalAssistantInput`
  - portal assistant preview text
- `docker compose exec -T cavazos-ai python manage.py check` passes.

## Stale documentation check

- Updated `README.md` landing-route bullets to document the portal assistant input under orb preview.
- Updated `orb-chat-ui/README.md` behavior notes to include the new landing composer.
- No additional stale docs found.
