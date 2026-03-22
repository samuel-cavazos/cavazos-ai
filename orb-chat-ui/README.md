# Orb UI Asset Bundle

This directory now acts as the static asset bundle for the Django app in the repository root.

Active Django templates live in `portal/templates/portal/`, while this directory provides:

- `orb-chat-ui.css`
- `orb-chat-ui.js`
- `landing-orb.js`

## Files

- `index.html`: legacy static landing snapshot
- `chat.html`: legacy static chat snapshot
- `orb-chat-ui.css`: orb/speech visual style + composer state polish
- `orb-chat-ui.js`: shared orb renderer and minimal chat controller
- `landing-orb.js`: isolated orb renderer for landing pages (no chat markup)

## Behavior

- Django landing template runs `landing-orb.js` directly inside landing page markup.
- Django chat template uses the same orb renderer and modernized composer UI.
- Django landing orb preview now includes a Tailwind-styled portal assistant composer (preview-mode submit handler).
- Django superuser overview (`/ops/`) is rendered via Django template (not static snapshot assets).
- Auth is handled in Django (`portal` app + allauth), not in static HTML files.

## Hook your own chat behavior

`orb-chat-ui.js` exposes `window.OrbChatUI`.

```js
window.OrbChatUI.setSubmitHandler(async ({ prompt, setBusy, setReply, clearInput, focusInput }) => {
  setBusy(true);
  try {
    const reply = await myChatRequest(prompt);
    setReply(reply);
    clearInput();
    focusInput();
  } catch (error) {
    setReply(error?.message || "Request failed.", true);
  } finally {
    setBusy(false);
  }
});
```

You can also listen to `window` event `orb-chat-ui:submit` if you prefer event-driven wiring.

## Docker Run

`compose.yaml` in this folder now runs the root Django app (build context `..`) so auth flows are available at `localhost:5173`.
It also mounts `../data` into the container so SQLite persists at `/data/db.sqlite3` across rebuilds.

```bash
docker compose up --build
```

Open `http://localhost:5173`.

For live file sync/restart during development:

```bash
docker compose watch
```

To stop:

```bash
docker compose down
```

## Legacy Static Snapshot

`index.html` and `chat.html` in this folder are retained as static snapshots, but auth behavior should be tested through Django.
