import hashlib
import json
import secrets
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings

RESOURCE_LOG_ALLOWED_LEVELS = {"debug", "info", "warning", "error", "alert"}


def get_project_directory(slug: str) -> Path:
    return Path(settings.PROJECTS_ROOT) / slug


def get_project_db_path(slug: str) -> Path:
    return get_project_directory(slug) / "project.sqlite3"


def ensure_project_storage(slug: str) -> Path:
    project_dir = get_project_directory(slug)
    project_dir.mkdir(parents=True, exist_ok=True)

    db_path = get_project_db_path(slug)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                global_resource_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                target TEXT NOT NULL,
                notes TEXT,
                metadata_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS resource_api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id TEXT UNIQUE NOT NULL,
                global_resource_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                key_prefix TEXT NOT NULL,
                key_hash TEXT UNIQUE NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                last_used_at TEXT,
                created_by TEXT,
                revoked_at TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS resource_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                global_resource_id INTEGER NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                source TEXT,
                metadata_json TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                received_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_resource_api_keys_resource_active
            ON resource_api_keys (global_resource_id, is_active)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_resource_logs_resource_occurred
            ON resource_logs (global_resource_id, occurred_at)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_resource_logs_level_occurred
            ON resource_logs (level, occurred_at)
            """
        )
        connection.commit()

    return db_path


def move_project_storage(old_slug: str, new_slug: str) -> Path:
    if not old_slug or old_slug == new_slug:
        return ensure_project_storage(new_slug)

    old_dir = get_project_directory(old_slug)
    new_dir = get_project_directory(new_slug)
    new_dir.parent.mkdir(parents=True, exist_ok=True)

    if old_dir.exists() and not new_dir.exists():
        old_dir.rename(new_dir)

    return ensure_project_storage(new_slug)


def upsert_resource_record(resource) -> None:
    db_path = ensure_project_storage(resource.project.slug)
    metadata_json = json.dumps(
        {
            "resource_metadata": resource.resource_metadata or {},
            "github_repositories": resource.github_repositories or [],
            "access_scope": resource.access_scope,
            "address": resource.address or "",
            "port": resource.port,
            "db_type": resource.db_type or "",
            "healthcheck_url": resource.healthcheck_url or "",
            "ssh_mode": resource.ssh_mode or "",
            "ssh_key_name": resource.ssh_key_name or "",
            "ssh_username": resource.ssh_username or "",
            "ssh_port": resource.ssh_port,
            "ssh_credential_id": resource.ssh_credential_id or "",
            "ssh_credential_scope": resource.ssh_credential_scope or "",
        },
        sort_keys=True,
    )
    created_at = resource.created_at.isoformat() if resource.created_at else ""
    updated_at = resource.updated_at.isoformat() if resource.updated_at else ""
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO resources (
                global_resource_id,
                name,
                resource_type,
                target,
                notes,
                metadata_json,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(global_resource_id) DO UPDATE SET
                name = excluded.name,
                resource_type = excluded.resource_type,
                target = excluded.target,
                notes = excluded.notes,
                metadata_json = excluded.metadata_json,
                updated_at = excluded.updated_at
            """,
            (
                resource.id,
                resource.name,
                resource.resource_type,
                resource.target,
                resource.notes or "",
                metadata_json,
                created_at,
                updated_at,
            ),
        )
        connection.commit()


def delete_resource_record(project_slug: str, resource_id: int) -> None:
    db_path = get_project_db_path(project_slug)
    if not db_path.exists():
        return
    with sqlite3.connect(db_path) as connection:
        connection.execute("DELETE FROM resources WHERE global_resource_id = ?", (resource_id,))
        connection.execute("DELETE FROM resource_api_keys WHERE global_resource_id = ?", (resource_id,))
        connection.execute("DELETE FROM resource_logs WHERE global_resource_id = ?", (resource_id,))
        connection.commit()


def get_resource_record(project_slug: str, resource_id: int):
    db_path = get_project_db_path(project_slug)
    if not db_path.exists():
        return None
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            "SELECT * FROM resources WHERE global_resource_id = ?",
            (resource_id,),
        ).fetchone()
        if row is None:
            return None
        return dict(row)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_resource_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def create_resource_api_key(resource, name: str, created_by: str = ""):
    db_path = ensure_project_storage(resource.project.slug)
    clean_name = str(name or "").strip()[:120] or "default"
    clean_created_by = str(created_by or "").strip()[:160]
    created_at = _utc_now_iso()

    while True:
        raw_key = f"rsk_{secrets.token_urlsafe(32)}"
        key_hash = _hash_resource_api_key(raw_key)
        key_prefix = raw_key[:16]
        key_id = str(uuid.uuid4())
        try:
            with sqlite3.connect(db_path) as connection:
                connection.execute(
                    """
                    INSERT INTO resource_api_keys (
                        key_id,
                        global_resource_id,
                        name,
                        key_prefix,
                        key_hash,
                        is_active,
                        created_by,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, 1, ?, ?)
                    """,
                    (
                        key_id,
                        resource.id,
                        clean_name,
                        key_prefix,
                        key_hash,
                        clean_created_by,
                        created_at,
                    ),
                )
                connection.commit()
            break
        except sqlite3.IntegrityError:
            continue

    return raw_key, {
        "key_id": key_id,
        "name": clean_name,
        "key_prefix": key_prefix,
        "is_active": 1,
        "created_by": clean_created_by,
        "created_at": created_at,
        "last_used_at": None,
        "revoked_at": None,
    }


def list_resource_api_keys(project_slug: str, resource_id: int):
    db_path = ensure_project_storage(project_slug)

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT
                key_id,
                name,
                key_prefix,
                is_active,
                created_by,
                created_at,
                last_used_at,
                revoked_at
            FROM resource_api_keys
            WHERE global_resource_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (resource_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def revoke_resource_api_key(project_slug: str, resource_id: int, key_id: str) -> bool:
    db_path = ensure_project_storage(project_slug)

    revoked_at = _utc_now_iso()
    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(
            """
            UPDATE resource_api_keys
            SET is_active = 0, revoked_at = ?
            WHERE key_id = ? AND global_resource_id = ? AND is_active = 1
            """,
            (revoked_at, key_id, resource_id),
        )
        connection.commit()
        return cursor.rowcount > 0


def authenticate_resource_api_key(project_slug: str, resource_id: int, raw_key: str) -> bool:
    key = str(raw_key or "").strip()
    if not key:
        return False

    db_path = ensure_project_storage(project_slug)

    key_hash = _hash_resource_api_key(key)
    now_iso = _utc_now_iso()
    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT id
            FROM resource_api_keys
            WHERE global_resource_id = ? AND key_hash = ? AND is_active = 1
            """,
            (resource_id, key_hash),
        ).fetchone()
        if row is None:
            return False

        connection.execute(
            "UPDATE resource_api_keys SET last_used_at = ? WHERE id = ?",
            (now_iso, row[0]),
        )
        connection.commit()
        return True


def store_resource_logs(project_slug: str, resource_id: int, logs: list[dict]) -> int:
    if not logs:
        return 0

    db_path = ensure_project_storage(project_slug)
    received_at = _utc_now_iso()
    rows = []
    for entry in logs:
        level = str(entry.get("level", "")).strip().lower()
        if level not in RESOURCE_LOG_ALLOWED_LEVELS:
            raise ValueError(f"Unsupported log level: {level}")

        message = str(entry.get("message", "")).strip()
        source = str(entry.get("source", "")).strip()[:160]
        metadata_json = json.dumps(entry.get("metadata", {}) or {}, sort_keys=True)
        occurred_at = entry.get("occurred_at")
        if isinstance(occurred_at, datetime):
            occurred_at_value = occurred_at.isoformat()
        else:
            occurred_at_value = str(occurred_at or received_at)

        rows.append(
            (
                resource_id,
                level,
                message,
                source,
                metadata_json,
                occurred_at_value,
                received_at,
            )
        )

    with sqlite3.connect(db_path) as connection:
        connection.executemany(
            """
            INSERT INTO resource_logs (
                global_resource_id,
                level,
                message,
                source,
                metadata_json,
                occurred_at,
                received_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        connection.commit()
    return len(rows)
