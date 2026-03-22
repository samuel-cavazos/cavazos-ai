# Resource Data Collection Reference

This document describes what the application collects when creating/updating resources.

## Source Of Truth

- `dashboard/templates/pages/resources.html` (Add/Edit forms + client-side visibility rules)
- `dashboard/views.py`
  - `_normalize_resource_target`
  - `_resource_metadata_from_request`
  - `_resolve_resource_scope_payload`
  - `_resolve_ssh_payload`
  - `add_resource_item` / `edit_resource_item`
- `dashboard/resources_store.py`
  - `add_resource` / `update_resource`
  - `_display_target`

## Supported Resource Types

The UI supports these `resource_type` values:

- `api`
- `vm`
- `database`
- `queue`
- `service`
- `other`

## Common Data Collected For All Types

These fields are collected for every resource type:

- `name` (required)
- `resource_type` (required)
- `notes` (optional)
- `github_repositories` (optional, multi-select + manual text)
- `resource_scope` (`account|team|global`; `global` only for superusers)
- `resource_team_names` (only if scope is `team`)

Also accepted on POST (not exposed as standard visible fields in the modal):

- `meta_*` keys are copied into `resource_metadata`.

## Type-Specific Data Collected

| Resource type | Type-specific inputs shown | What must resolve to create/update | Stored canonical target |
| --- | --- | --- | --- |
| `api` | `healthcheck_url` | `healthcheck_url` (or `target` fallback) | `target = healthcheck_url` |
| `vm` | `address`, optional SSH block | `address` (or `target` fallback) | `target = address` |
| `database` | `address`, `port`, `db_type` | `address` (or parsed from `target`) | `target = address[:port]` |
| `queue` | `target` | `target` | `target` |
| `service` | `target` | `target` | `target` |
| `other` | `target` | `target` | `target` |

### Normalization Rules

On submit, backend normalization (`_normalize_resource_target`) runs:

- `api`
  - if `healthcheck_url` is empty and `target` is present, `healthcheck_url = target`
  - then `target = healthcheck_url`
- `vm`
  - if `address` is empty and `target` is present, `address = target`
  - then `target = address`
- `database`
  - if `address` is empty and `target` contains `:`, split into `address` + `port`
  - otherwise use `target` as `address`
  - then `target = address:port` (or just `address` if no port)

Create/update proceeds only when all are non-empty after normalization:

- `name`
- `resource_type`
- `target`

## VM SSH Data Collection

SSH fields are VM-specific in UI. For non-VM resources, backend clears SSH payload before save.

VM SSH fields:

- `ssh_mode` (`inline` or `saved`)
- `ssh_username`
- `ssh_port` (defaults to `22` when username is set and port is empty)
- `ssh_credential_id` (saved key mode)
- `ssh_scope` (`account|team|global`; `global` only for superusers)
- `ssh_team_names` (when `ssh_scope=team`)
- `ssh_key_name`
- `ssh_key_text` or `ssh_key_file`
- `clear_ssh_key` (edit form)

Important rules:

- Saved key mode requires `ssh_username`; otherwise key selection is cleared.
- Inline key text/file without `ssh_username` is ignored.
- Inline team-scope key without selected teams is discarded.
- When a key is saved/selected, key material is not stored in plaintext in form payload; credentials are stored in SSH credential stores and resource stores credential reference (`ssh_credential_id`, `ssh_credential_scope`).

## GitHub Repository Metadata Collection

Repositories are collected from:

- `github_repositories` (multi-select)
- `github_repositories_manual` (text; comma/newline tolerant)

Normalization behavior:

- normalized to `owner/repo`
- deduplicated case-insensitively
- max 50 entries
- saved under `resource_metadata.github_repositories`

## Access Scope Collection

- If `resource_scope = team`, at least one valid `resource_team_names` entry is required.
- If no valid team is selected, scope falls back to `account`.
- Non-team scopes clear `resource_team_names`.

## Storage Fields Written

Resource records persist these primary fields:

- `name`, `resource_type`, `target`
- `address`, `port`, `db_type`, `healthcheck_url`
- `notes`
- `access_scope` + team access mapping
- `ssh_key_name`, `ssh_username`, `ssh_port`, `ssh_credential_id`, `ssh_credential_scope`
- `resource_metadata` (including `github_repositories`)
