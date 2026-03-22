# 2026-03-20 Home Role Placeholders + Root Redirect

## What changed

- Updated post-login behavior so all successful logins now redirect to `/`.
  - Applies to AJAX username/password login/sign-up flow.
  - Applies to allauth/social login flow via account adapter.
- Updated Microsoft login launch URL from landing page to use `next=/`.
- Reused the existing landing "Live Intelligence" panel for authenticated users.
  - Superuser now sees placeholder heading: `Admin`.
  - Staff user now sees placeholder heading: `Staff`.
  - All other authenticated users now see placeholder heading: `Client`.

## Validation

- Verified via Django test client in running container:
  - superuser login returns `redirect_url: /` and `/` contains `Admin`.
  - staff login returns `redirect_url: /` and `/` contains `Staff`.
  - standard client login returns `redirect_url: /` and `/` contains `Client`.
- Verified Microsoft login endpoint still starts directly and returns `302` to Microsoft authorize URL.
- `docker compose exec -T cavazos-ai python manage.py check` passes.

## Stale documentation check

- Updated `README.md` route/redirect behavior notes to reflect root redirect and role-based placeholders on `/`.
- No additional stale docs found for this change.
