# 2026-03-20 Auth Panel Transition Smoothing

## What changed

- Updated landing auth panel rendering in `portal/templates/portal/index.html` to avoid layout jump:
  - Added an overlay stack container (`.auth-panel-stack`) for intro/login/sign-up views.
  - Added view state classes (`.auth-panel-view`, `.is-active`) with opacity/translate transitions.
  - Panels now keep a stable shared footprint, so clicking `Login` does not collapse/expand the panel height.
- Added click `preventDefault()` handlers for all panel navigation buttons (`Login`, `Back`, `Sign Up`, `Back to Login`, `Sign in`) to avoid unintended navigation behavior.
- Replaced `hidden` attribute toggling with class-based state switching and `aria-hidden` updates for smoother transitions.

## Validation

- Checked updated template structure and state-transition script.
- Verified no iframe/auth-route fallback is used for these transitions.

## Stale documentation check

- Existing auth docs in `README.md` and `wiki/2026-03-20-landing-inline-login-signup.md` remain accurate.
- No additional README edits were required for this UI-only transition refinement.
