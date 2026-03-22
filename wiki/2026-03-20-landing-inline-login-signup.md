# 2026-03-20 Landing Inline Login + Signup Panels

## What changed

- Updated Django landing auth UX on `/`:
  - `Login` now transitions the Live Intelligence panel into a login form in-place.
  - Added a top-left `← Back` control inside login form to return to the intro panel.
  - Added an in-place sign-up form with:
    - Username
    - Email
    - Password
    - Confirm password
  - Added transitions between login and sign-up panels without leaving landing page.
- Added backend endpoint `portal:ajax-signup` at `/auth/signup/` for the sign-up form.
- Enhanced login backend to authenticate by username or email.
- Added safe redirect validation for `next` so login/sign-up responses only redirect to local allowed paths.

## Validation

- Python syntax check passed for updated `portal/views.py` and `portal/urls.py`.
- Landing template JS flow updated for intro/login/signup state transitions and async submits.

## Stale documentation check

- Updated root `README.md` route list to include in-panel login/sign-up flow and new `/auth/signup/` endpoint.
- Existing orb isolation docs remain valid and do not conflict with this auth-panel change.
