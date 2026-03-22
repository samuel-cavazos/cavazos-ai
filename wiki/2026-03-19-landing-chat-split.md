# 2026-03-19 Landing + Chat Page Split

## What changed

- Renamed the full chat experience from `orb-chat-ui/index.html` to `orb-chat-ui/chat.html`.
- Added a new branded landing page at `orb-chat-ui/index.html` for `cavazos.ai`.
- Embedded a compact orb preview on landing page via `chat.html?embed=orb`.
- Updated `orb-chat-ui/orb-chat-ui.js` with `embed=orb` mode so iframe previews hide chat composer/speech overlays.
- Updated `orb-chat-ui/Dockerfile` to copy both `index.html` and `chat.html`.

## Stale documentation check

- Updated `orb-chat-ui/README.md` to describe both routes and new file responsibilities.
- Updated previous wiki note (`2026-03-19-chat-input-modernization.md`) to reference `chat.html` instead of `index.html`.
