# 2026-03-20 Remove Microsoft Login Hint

## What changed

- Removed the helper sentence under the landing page login form:
  - "Microsoft social login can be enabled later through django-allauth SocialApp setup."
- File updated: `portal/templates/portal/index.html`.

## Validation

- Confirmed the line was removed from the login panel markup.

## Stale documentation check

- Reviewed `README.md` and existing auth wiki notes.
- No stale docs found; social-login capability is still documented at setup/runtime level, while this UI text removal only affects landing copy.
