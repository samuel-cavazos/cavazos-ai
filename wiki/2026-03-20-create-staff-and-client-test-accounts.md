# 2026-03-20 Create Staff And Client Test Accounts

## Request

Create test accounts:

- `staff`
- `client`

with password `happy777`.

## Changes

Executed Django shell against persistent DB (`/data/db.sqlite3`) and ensured both users exist:

- `staff`: `is_staff=True`, `is_superuser=False`
- `client`: `is_staff=False`, `is_superuser=False`
- password set to `happy777` for both

## Verification

Shell output confirmed:

- `staff: created, is_staff=True, is_superuser=False`
- `client: created, is_staff=False, is_superuser=False`

## Stale Documentation Check

- reviewed README/wiki scope.
- no README changes required for account provisioning only.
