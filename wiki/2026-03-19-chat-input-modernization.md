# 2026-03-19 Chat Input Modernization

## What changed

- Updated chat composer markup (now in `orb-chat-ui/chat.html`) to a modern utility-class layout using Tailwind CDN.
- Refined composer CSS in `orb-chat-ui/orb-chat-ui.css` to remove old conflicting shape styles and keep accessibility/state polish.
- Fixed `setBusy` in `orb-chat-ui/orb-chat-ui.js` so busy mode now disables/enables input and send button correctly.

## Stale documentation check

- Reviewed `orb-chat-ui/README.md` and updated file/behavior descriptions to reflect Tailwind-based composer styling.
- No additional project docs were found that referenced old composer styles.
