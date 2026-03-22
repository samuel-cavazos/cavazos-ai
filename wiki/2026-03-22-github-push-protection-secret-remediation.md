# 2026-03-22 GitHub Push Protection Secret Remediation

## Summary
Push to `origin/main` was blocked by GitHub Push Protection (`GH013`) because `orb-chat-ui/.env` in commit history contained an OpenAI API key.

## What Happened
- Initial force push failed with:
  - `push declined due to repository rule violations`
  - Secret type: OpenAI API key
  - Reported location: `orb-chat-ui/.env` in commit `8720941...`

## Remediation
- Added secret ignores to `.gitignore`:
  - `orb-chat-ui/.env`
  - `.env`
- Removed tracked secret file from git index:
  - `git rm --cached orb-chat-ui/.env`
- Rewrote the single local commit to remove the secret from pushed history:
  - `git commit --amend --no-edit`
- Verified no tracked secret signatures remain:
  - `git grep -n "sk-proj\\|OPENAI_API_KEY"` returned no matches.
- Re-ran push:
  - `git push --force origin main` succeeded.

## Result
- Remote branch `origin/main` now points to sanitized commit `9a20f67`.
- Local branch tracking restored:
  - `main [origin/main]`

## Stale Documentation Check
- Reviewed:
  - `wiki/2026-03-22-sitewide-assistant-widget-global-include-chat-cutover.md`
  - `wiki/2026-03-21-resource-log-ingest-project-db-api-keys.md`
- Result:
  - Product/feature docs remain valid.
  - Added this operational wiki note to capture push-protection remediation and secret-handling expectations.
