# 2026-03-22 Site-Wide Assistant Widget + Legacy /chat Cutover

## Summary
Promoted the floating orb/chat widget to a shared site-wide component across portal pages, moved widget implementation into a reusable global include, and hard-cut legacy `/chat/` to a permanent redirect.

## What Changed
- Added shared include:
  - `portal/templates/portal/includes/assistant_widget.html`
  - Contains widget CSS, markup, runtime dependencies (`marked`, `DOMPurify`, `mermaid`), and widget controller JS.
  - Added role/profile hook on widget root via `data-agent-profile` (`guest`, `client_staff`, `superuser`).
  - Exposed `window.PortalAssistantWidget.getAgentProfile()` and passed `agentProfile` to `setSubmitHandler` callback payload.
- Updated portal pages to render the widget globally via include:
  - `portal/templates/portal/index.html`
  - `portal/templates/portal/ops.html`
  - `portal/templates/portal/media_gallery.html`
  - `portal/templates/portal/project_overview.html`
  - `portal/templates/portal/resource_detail.html`
- Refactored `index.html`:
  - Removed embedded widget CSS/HTML/JS and now uses shared include.
  - Kept only landing-specific widget-mode layout rules (`.assistant-widget-mode .hero` and `.assistant-widget-mode .orb-panel`).
- Legacy `/chat/` cutover:
  - Replaced with permanent redirect to home in `portal/urls.py`:
    - `path("chat/", RedirectView.as_view(pattern_name="portal:home", permanent=True), name="chat")`
  - Removed `chat_view` usage from `portal/views.py`.
  - Updated superuser `ops` top action from `Open Chat` to `Home`.
  - Updated non-superuser redirects in `ops_overview` and `media_gallery` to `portal:home`.
- Added test coverage in `portal/tests.py`:
  - Legacy `/chat/` returns `301` to home.
  - Widget marker present on home, project/resource pages, and superuser ops/gallery pages.

## Verification
- `python3 -m compileall portal` passed.
- `.venv/bin/python manage.py test portal.tests` passed (`19` tests).
- Extracted include JS syntax check passed:
  - `node --check /tmp/assistant_widget_inline.js`

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-21-assistant-popup-widget-markdown-mermaid.md`
  - `wiki/2026-03-22-chat-widget-copy-and-demo-removal.md`
  - `wiki/2026-03-22-widget-topbar-trash-right-outline.md`
  - `wiki/2026-03-19-django-auth-allauth-setup.md`
  - `wiki/2026-03-19-microsoft-login-ops-overview.md`
- Result:
  - Prior entries that reference widget implementation only in `portal/templates/portal/index.html` are now partially stale for file location/scope.
  - Behavioral details remain valid; implementation location is now centralized in `portal/templates/portal/includes/assistant_widget.html`.
  - This entry supersedes those path/scope references.
  - Updated older auth/SSO docs to annotate `/chat/` route behavior as superseded by 2026-03-22 cutover.
