# cavazos.ai Portal (Django + allauth)

This repository hosts the `cavazos.ai` landing + portal experience with Django session auth, `django-allauth` (Microsoft-ready), and a project/resource model for monitored infrastructure.

## Current UX flow

- `/` is the landing page.
- Unauthenticated users get inline `Login` and `Sign Up` panels.
- After successful auth, users return to `/` and see **Project Navigation**.
- Superusers get a dedicated **Shared Media Gallery** entry point on `/`.
- Selecting a project opens `/projects/<project-slug>/` with resource list + project controls.
- Selecting a resource opens `/projects/<project-slug>/resources/<resource-slug>/`.

## Roles shown on home

On authenticated home (`/`), the panel shows role label based on Django flags:

- superuser -> `Admin`
- staff -> `Staff`
- all other authenticated users -> `Client`

## Project + Resource model

### Global DB (Django)

`portal` app includes:

- `Project`
- `ProjectMembership` (user <-> project)
- `Resource` (global record)

Resource fields align with `resources.md`, including:

- core: `name`, `resource_type`, `target`, `notes`
- type-specific: `address`, `port`, `db_type`, `healthcheck_url`
- scope: `access_scope` (`account` or `global`)
- metadata: `github_repositories`, `resource_metadata`
- ssh: `ssh_mode`, `ssh_*`

### Project-level persistent storage

Each project has a directory and SQLite mirror DB:

- root: `PROJECTS_ROOT` (default `/data/projects`)
- project path: `/data/projects/<project-slug>/`
- mirror db: `/data/projects/<project-slug>/project.sqlite3`

The project DB stores:

- resource mirror rows (`resources`)
- resource API keys (`resource_api_keys`)
- ingested resource logs (`resource_logs`)

When a `Resource` is created/updated/deleted in Django, signals keep the project DB in sync.

## Access rules

- Superusers can view all projects.
- Non-superusers can only view projects where they have membership.
- Project/resource management POST endpoints are currently superuser-only.
- Shared media upload/delete is superuser-only.
- Public file reads under `/shared/<filename>` are available to anonymous users for embedding/link sharing.

## Important routes

- `/` home / landing / project navigation
- `/superuser/gallery/` dedicated shared media gallery (superuser UI)
- `/superuser/gallery/upload/` upload shared media (POST, superuser)
- `/superuser/gallery/delete/` delete shared media (POST, superuser)
- `/shared/<filename>` public shared media URL
- `/projects/create/` create project (POST, superuser)
- `/projects/<project-slug>/` project overview (canonical)
- `/projects/<project-uuid>/` project overview redirect to canonical slug URL
- `/projects/<project-uuid>/settings/` update project slug (POST, superuser)
- `/projects/<project-uuid>/members/add/` add member (POST, superuser)
- `/projects/<project-uuid>/resources/create/` create resource (POST, superuser)
- `/projects/<project-slug>/resources/<resource-slug>/` resource detail (canonical)
- `/projects/<project-uuid>/resources/<resource-uuid>/` resource detail
- `/projects/<project-uuid>/resources/<resource-uuid>/settings/` update resource slug (POST, superuser)
- `/projects/<project-uuid>/resources/<resource-uuid>/delete/` delete resource (POST, superuser)
- `/projects/<project-uuid>/resources/<resource-uuid>/api-keys/create/` create resource API key (POST, superuser)
- `/projects/<project-uuid>/resources/<resource-uuid>/api-keys/<key-uuid>/revoke/` revoke resource API key (POST, superuser)
- `/projects/<project-uuid>/resources/<resource-uuid>/logs/` ingest resource logs (POST, API key auth)
- `/auth/login/` AJAX login
- `/auth/signup/` AJAX signup
- `/auth/logout/` logout
- `/accounts/` allauth endpoints

### Resource log ingest payload

`POST /projects/<project-uuid>/resources/<resource-uuid>/logs/`

- auth header: `X-Resource-API-Key: <api-key>` (or `Authorization: Bearer <api-key>`)
- levels: `debug`, `info`, `warning`, `error`, `alert` (case-insensitive on input)
- body:
  - single log object:
    - `level` (required)
    - `message` (required)
    - `source` (optional)
    - `metadata` object (optional)
    - `timestamp`/`occurred_at` ISO-8601 (optional)
  - or batch:
    - `{ "logs": [ ...same log objects... ] }`

## Docker run

From `orb-chat-ui/`:

```bash
docker compose up --build
```

Open: `http://localhost:5173`

For live development sync/restart (from `orb-chat-ui/`), run:

```bash
docker compose watch
```

Compose mapping includes persistent data:

- host: `../data`
- container: `/data`

So both global DB (`/data/db.sqlite3`) and project mirror DBs (`/data/projects/*`) persist.

Shared media defaults to:

- `/data/shared` when `/data` exists (Docker path)
- `<repo>/data/shared` otherwise (local fallback)

Override with environment variable:

- `SHARED_MEDIA_ROOT`
- `SHARED_MEDIA_MAX_UPLOAD_BYTES` (default `26214400`, 25 MB)

## Microsoft login (allauth)

- Provider enabled: `allauth.socialaccount.providers.microsoft`
- Direct provider login is enabled (`SOCIALACCOUNT_LOGIN_ON_GET = True`)
- Landing page only renders active Microsoft button if a SocialApp exists for current `SITE_ID`
- Social account adapter enforces allowlisted/provisioned local superuser email

Typical callback URLs:

- `http://localhost:5173/accounts/microsoft/login/callback/`
- `https://cavazos.ai/accounts/microsoft/login/callback/`

## Local non-Docker run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open `http://127.0.0.1:8000`.
