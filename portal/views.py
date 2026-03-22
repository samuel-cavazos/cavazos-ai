import json
import mimetypes
from datetime import datetime, timezone as datetime_timezone
from pathlib import Path
from urllib.parse import urlencode
from uuid import UUID

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Prefetch
from django.http import FileResponse, Http404, HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.text import get_valid_filename, slugify
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST

from .models import Project, ProjectMembership, Resource
from .project_storage import (
    authenticate_resource_api_key,
    create_resource_api_key,
    get_resource_record,
    list_resource_api_keys,
    revoke_resource_api_key,
    store_resource_logs,
)

SHARED_MEDIA_BLOCKED_EXTENSIONS = {
    ".bat",
    ".cgi",
    ".com",
    ".css",
    ".dll",
    ".exe",
    ".htm",
    ".html",
    ".jar",
    ".js",
    ".mjs",
    ".msi",
    ".php",
    ".pl",
    ".ps1",
    ".py",
    ".rb",
    ".scr",
    ".sh",
    ".svg",
    ".vbs",
    ".xhtml",
    ".xml",
}
SHARED_MEDIA_INLINE_MIME_PREFIXES = ("image/", "video/", "audio/")
SHARED_MEDIA_INLINE_MIME_TYPES = {"application/pdf"}
RESOURCE_LOG_ALLOWED_LEVELS = {"debug", "info", "warning", "error", "alert"}


def _projects_for_user(user):
    if not user.is_authenticated:
        return Project.objects.none()
    resources_prefetch = Prefetch("resources", queryset=Resource.objects.order_by("name"))
    if user.is_superuser:
        return Project.objects.prefetch_related(resources_prefetch).order_by("name")
    return Project.objects.filter(memberships__user=user).distinct().prefetch_related(resources_prefetch).order_by("name")


def _user_can_access_project(user, project: Project) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return project.memberships.filter(user=user).exists()


def _shared_media_root() -> Path:
    root = Path(settings.SHARED_MEDIA_ROOT)
    root.mkdir(parents=True, exist_ok=True)
    return root


def _normalize_shared_media_filename(raw_filename: str) -> str:
    normalized = get_valid_filename(Path(str(raw_filename)).name).replace(" ", "-")
    if not normalized or normalized in {".", ".."}:
        raise ValidationError("Provide a valid filename.")
    if Path(normalized).name != normalized:
        raise ValidationError("Filename must not include directories.")
    suffix = Path(normalized).suffix.lower()
    if not suffix:
        raise ValidationError("Filename must include a file extension.")
    if suffix in SHARED_MEDIA_BLOCKED_EXTENSIONS:
        raise ValidationError("This file type is blocked for security reasons.")
    return normalized


def _resolve_unique_shared_media_filename(root: Path, filename: str) -> str:
    stem = Path(filename).stem
    suffix = Path(filename).suffix.lower()
    candidate = f"{stem}{suffix}"
    index = 2
    while (root / candidate).exists():
        candidate = f"{stem}-{index}{suffix}"
        index += 1
    return candidate


def _is_inline_shared_media(content_type: str) -> bool:
    return any(content_type.startswith(prefix) for prefix in SHARED_MEDIA_INLINE_MIME_PREFIXES) or (
        content_type in SHARED_MEDIA_INLINE_MIME_TYPES
    )


def _shared_media_kind(content_type: str) -> str:
    if content_type.startswith("image/"):
        return "image"
    if content_type.startswith("video/"):
        return "video"
    if content_type.startswith("audio/"):
        return "audio"
    if content_type == "application/pdf":
        return "pdf"
    return "file"


def _format_byte_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    units = ("KB", "MB", "GB", "TB")
    value = float(size)
    for unit in units:
        value /= 1024
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}"
    return f"{size} B"


def _shared_media_items(request: HttpRequest) -> list[dict]:
    root = _shared_media_root()
    files = []
    for candidate in root.iterdir():
        if not candidate.is_file():
            continue
        try:
            stat = candidate.stat()
        except OSError:
            continue
        files.append((candidate, stat))

    files.sort(key=lambda item: item[1].st_mtime, reverse=True)

    items = []
    for media_path, stat in files:
        content_type = mimetypes.guess_type(media_path.name)[0] or "application/octet-stream"
        path = reverse("portal:shared-media-file", kwargs={"filename": media_path.name})
        modified_at = timezone.localtime(datetime.fromtimestamp(stat.st_mtime, tz=datetime_timezone.utc))
        items.append(
            {
                "name": media_path.name,
                "path": path,
                "absolute_url": request.build_absolute_uri(path),
                "content_type": content_type,
                "kind": _shared_media_kind(content_type),
                "size_display": _format_byte_size(stat.st_size),
                "modified_at": modified_at,
            }
        )
    return items


def _extract_resource_api_key(request: HttpRequest) -> str:
    header_token = str(request.headers.get("X-Resource-API-Key", "")).strip()
    if header_token:
        return header_token

    authorization = str(request.headers.get("Authorization", "")).strip()
    if authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return ""


def _parse_log_timestamp(raw_value):
    if raw_value in (None, ""):
        return timezone.now()

    parsed = parse_datetime(str(raw_value))
    if parsed is None:
        raise ValidationError("timestamp must be ISO-8601 when provided.")
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, datetime_timezone.utc)
    return parsed


def _normalize_log_entry(raw_entry) -> dict:
    if not isinstance(raw_entry, dict):
        raise ValidationError("Each log item must be an object.")

    level = str(raw_entry.get("level", "")).strip().lower()
    if level not in RESOURCE_LOG_ALLOWED_LEVELS:
        raise ValidationError("level must be one of: debug, info, warning, error, alert.")

    message = str(raw_entry.get("message", "")).strip()
    if not message:
        raise ValidationError("message is required.")

    source = str(raw_entry.get("source", "")).strip()[:160]
    metadata = raw_entry.get("metadata", {})
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise ValidationError("metadata must be an object when provided.")

    timestamp_raw = raw_entry.get("timestamp", raw_entry.get("occurred_at"))
    occurred_at = _parse_log_timestamp(timestamp_raw)
    return {
        "level": level,
        "message": message,
        "source": source,
        "metadata": metadata,
        "occurred_at": occurred_at,
    }


def home(request: HttpRequest) -> HttpResponse:
    next_url = _safe_next_url(request, request.GET.get("next", ""))
    social_login_error = str(request.GET.get("social_error", "")).strip()[:240]
    microsoft_login_url = "/accounts/microsoft/login/?process=login&next=/"
    microsoft_login_available = False

    try:
        from allauth.socialaccount.models import SocialApp

        microsoft_login_available = SocialApp.objects.filter(
            provider="microsoft",
            sites__id=settings.SITE_ID,
        ).exists()
    except Exception:
        microsoft_login_available = False

    return render(
        request,
        "portal/index.html",
        {
            "next_url": next_url,
            "is_authenticated": request.user.is_authenticated,
            "user_name": request.user.get_username() if request.user.is_authenticated else "",
            "social_login_error": social_login_error,
            "microsoft_login_url": microsoft_login_url,
            "microsoft_login_available": microsoft_login_available,
            "projects": _projects_for_user(request.user),
        },
    )


@login_required(login_url="/")
def ops_overview(request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        return redirect("portal:home")
    return render(request, "portal/ops.html")


@login_required(login_url="/")
def media_gallery(request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        return redirect("portal:home")

    uploaded_name = str(request.GET.get("uploaded", "")).strip()
    uploaded_url = ""
    if uploaded_name:
        try:
            normalized_uploaded_name = _normalize_shared_media_filename(uploaded_name)
        except ValidationError:
            normalized_uploaded_name = ""
        if normalized_uploaded_name:
            uploaded_path = _shared_media_root() / normalized_uploaded_name
            if uploaded_path.is_file():
                uploaded_url = request.build_absolute_uri(
                    reverse("portal:shared-media-file", kwargs={"filename": normalized_uploaded_name})
                )

    return render(
        request,
        "portal/media_gallery.html",
        {
            "media_items": _shared_media_items(request),
            "uploaded_url": uploaded_url,
            "max_upload_size": _format_byte_size(max(1, settings.SHARED_MEDIA_MAX_UPLOAD_BYTES)),
        },
    )


@login_required(login_url="/")
@require_POST
@csrf_protect
def media_gallery_upload(request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can upload media.")

    uploaded_file = request.FILES.get("media_file")
    if uploaded_file is None:
        messages.error(request, "Select a file to upload.")
        return redirect("portal:media-gallery")

    if uploaded_file.size > settings.SHARED_MEDIA_MAX_UPLOAD_BYTES:
        messages.error(
            request,
            f"File is too large. Max upload size is {_format_byte_size(settings.SHARED_MEDIA_MAX_UPLOAD_BYTES)}.",
        )
        return redirect("portal:media-gallery")

    try:
        normalized_filename = _normalize_shared_media_filename(uploaded_file.name)
    except ValidationError as exc:
        message = exc.messages[0] if exc.messages else "Invalid file name."
        messages.error(request, message)
        return redirect("portal:media-gallery")

    root = _shared_media_root()
    stored_filename = _resolve_unique_shared_media_filename(root, normalized_filename)
    target = root / stored_filename
    try:
        with target.open("wb") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
    except OSError:
        messages.error(request, "Upload failed while writing the file.")
        return redirect("portal:media-gallery")

    if stored_filename != normalized_filename:
        messages.info(request, f"Filename already existed, saved as {stored_filename}.")
    messages.success(request, f"{stored_filename} uploaded.")
    query = urlencode({"uploaded": stored_filename})
    return redirect(f"{reverse('portal:media-gallery')}?{query}")


@login_required(login_url="/")
@require_POST
@csrf_protect
def media_gallery_delete(request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can delete media.")

    raw_filename = str(request.POST.get("filename", "")).strip()
    if not raw_filename:
        messages.error(request, "No file was selected for deletion.")
        return redirect("portal:media-gallery")

    try:
        filename = _normalize_shared_media_filename(raw_filename)
    except ValidationError:
        messages.error(request, "Invalid file name.")
        return redirect("portal:media-gallery")

    target = _shared_media_root() / filename
    if not target.is_file():
        messages.error(request, "File was not found.")
        return redirect("portal:media-gallery")

    try:
        target.unlink()
    except OSError:
        messages.error(request, "Delete failed.")
        return redirect("portal:media-gallery")

    messages.success(request, f"{filename} deleted.")
    return redirect("portal:media-gallery")


def shared_media_file(request: HttpRequest, filename: str) -> HttpResponse:
    candidate = str(filename).strip()
    if not candidate or candidate in {".", ".."}:
        raise Http404("File not found.")
    if Path(candidate).name != candidate:
        raise Http404("File not found.")

    target = _shared_media_root() / candidate
    if not target.is_file():
        raise Http404("File not found.")

    content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
    is_inline = _is_inline_shared_media(content_type)

    try:
        handle = target.open("rb")
    except OSError as exc:
        raise Http404("File not found.") from exc

    response = FileResponse(
        handle,
        as_attachment=not is_inline,
        filename=target.name,
        content_type=content_type,
    )
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "public, max-age=31536000, immutable"
    return response


@login_required(login_url="/")
def project_overview(request: HttpRequest, project_slug: str) -> HttpResponse:
    project = get_object_or_404(Project, slug=project_slug)
    if not _user_can_access_project(request.user, project):
        messages.error(request, "You do not have access to that project.")
        return redirect("portal:home")

    can_manage_project = request.user.is_superuser

    return render(
        request,
        "portal/project_overview.html",
        {
            "project": project,
            "resources": project.resources.order_by("name"),
            "memberships": project.memberships.select_related("user").order_by("user__username"),
            "projects": _projects_for_user(request.user),
            "can_manage_project": can_manage_project,
        },
    )


@login_required(login_url="/")
def project_overview_by_uuid(request: HttpRequest, project_uuid: UUID) -> HttpResponse:
    project = get_object_or_404(Project, uuid=project_uuid)
    if not _user_can_access_project(request.user, project):
        messages.error(request, "You do not have access to that project.")
        return redirect("portal:home")
    return redirect("portal:project-overview", project_slug=project.slug)


def _resource_detail_response(request: HttpRequest, project: Project, resource: Resource) -> HttpResponse:
    if not _user_can_access_project(request.user, project):
        messages.error(request, "You do not have access to that project.")
        return redirect("portal:home")

    if resource.project_id != project.id:
        raise Http404("Resource not found.")

    project_record = get_resource_record(project.slug, resource.id)
    project_record_metadata = None
    if project_record and project_record.get("metadata_json"):
        try:
            project_record_metadata = json.dumps(
                json.loads(project_record["metadata_json"]),
                indent=2,
                sort_keys=True,
            )
        except (TypeError, ValueError):
            project_record_metadata = None

    log_ingest_path = reverse(
        "portal:resource-log-ingest",
        kwargs={"project_uuid": project.uuid, "resource_uuid": resource.uuid},
    )
    log_ingest_url = f"https://{request.get_host()}{log_ingest_path}"

    context = {
        "project": project,
        "resource": resource,
        "project_record": project_record,
        "project_record_metadata": project_record_metadata,
        "projects": _projects_for_user(request.user),
        "resource_log_ingest_url": log_ingest_url,
    }
    if request.user.is_superuser:
        created_api_key = request.session.pop("new_resource_api_key", None)
        if (
            isinstance(created_api_key, dict)
            and created_api_key.get("resource_uuid") == str(resource.uuid)
            and created_api_key.get("project_uuid") == str(project.uuid)
        ):
            context["new_resource_api_key"] = created_api_key
        context["resource_api_keys"] = list_resource_api_keys(project.slug, resource.id)

    return render(request, "portal/resource_detail.html", context)


@login_required(login_url="/")
def resource_detail(request: HttpRequest, project_uuid: UUID, resource_uuid: UUID) -> HttpResponse:
    project = get_object_or_404(Project, uuid=project_uuid)
    resource = get_object_or_404(Resource, uuid=resource_uuid)
    return _resource_detail_response(request, project, resource)


@login_required(login_url="/")
def resource_detail_by_slug(request: HttpRequest, project_slug: str, resource_slug: str) -> HttpResponse:
    project = get_object_or_404(Project, slug=project_slug)
    resource = get_object_or_404(Resource, project=project, slug=resource_slug)
    return _resource_detail_response(request, project, resource)


@login_required(login_url="/")
@require_POST
@csrf_protect
def create_resource_api_key_view(request: HttpRequest, project_uuid: UUID, resource_uuid: UUID) -> HttpResponse:
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can create resource API keys.")

    project = get_object_or_404(Project, uuid=project_uuid)
    resource = get_object_or_404(Resource, uuid=resource_uuid, project=project)

    key_name = str(request.POST.get("name", "")).strip()
    if not key_name:
        messages.error(request, "API key name is required.")
        return redirect("portal:resource-detail-slug", project_slug=project.slug, resource_slug=resource.slug)

    if len(key_name) > 120:
        messages.error(request, "API key name must be 120 characters or fewer.")
        return redirect("portal:resource-detail-slug", project_slug=project.slug, resource_slug=resource.slug)

    raw_key, key_record = create_resource_api_key(
        resource=resource,
        name=key_name,
        created_by=request.user.get_username(),
    )
    request.session["new_resource_api_key"] = {
        "project_uuid": str(project.uuid),
        "resource_uuid": str(resource.uuid),
        "name": key_record["name"],
        "key_prefix": key_record["key_prefix"],
        "value": raw_key,
    }
    messages.success(request, "Resource API key created. Copy the key now; it will be hidden after this page load.")
    return redirect("portal:resource-detail-slug", project_slug=project.slug, resource_slug=resource.slug)


@login_required(login_url="/")
@require_POST
@csrf_protect
def revoke_resource_api_key_view(
    request: HttpRequest, project_uuid: UUID, resource_uuid: UUID, key_id: UUID
) -> HttpResponse:
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can revoke resource API keys.")

    project = get_object_or_404(Project, uuid=project_uuid)
    resource = get_object_or_404(Resource, uuid=resource_uuid, project=project)
    revoked = revoke_resource_api_key(project.slug, resource.id, str(key_id))
    if revoked:
        messages.success(request, "Resource API key revoked.")
    else:
        messages.info(request, "Resource API key was already inactive or not found.")
    return redirect("portal:resource-detail-slug", project_slug=project.slug, resource_slug=resource.slug)


@require_POST
@csrf_exempt
def ingest_resource_logs(request: HttpRequest, project_uuid: UUID, resource_uuid: UUID) -> JsonResponse:
    project = get_object_or_404(Project, uuid=project_uuid)
    resource = get_object_or_404(Resource, uuid=resource_uuid, project=project)
    api_key = _extract_resource_api_key(request)
    if not authenticate_resource_api_key(project.slug, resource.id, api_key):
        return JsonResponse({"ok": False, "error": "Invalid or missing resource API key."}, status=401)

    if request.content_type and request.content_type.startswith("application/json"):
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except (UnicodeDecodeError, json.JSONDecodeError):
            return JsonResponse({"ok": False, "error": "Invalid JSON payload."}, status=400)
    else:
        payload = {key: value for key, value in request.POST.items()}

    if not isinstance(payload, dict):
        return JsonResponse({"ok": False, "error": "Payload must be a JSON object."}, status=400)

    if "logs" in payload:
        raw_logs = payload.get("logs")
        if not isinstance(raw_logs, list) or not raw_logs:
            return JsonResponse({"ok": False, "error": "logs must be a non-empty array."}, status=400)
    else:
        raw_logs = [payload]

    normalized_logs = []
    for index, raw_log in enumerate(raw_logs):
        try:
            normalized_logs.append(_normalize_log_entry(raw_log))
        except ValidationError as exc:
            message = exc.messages[0] if exc.messages else "Invalid log payload."
            return JsonResponse(
                {"ok": False, "error": f"log[{index}]: {message}"},
                status=400,
            )

    accepted = store_resource_logs(project.slug, resource.id, normalized_logs)
    return JsonResponse(
        {
            "ok": True,
            "accepted": accepted,
            "project_uuid": str(project.uuid),
            "resource_uuid": str(resource.uuid),
        },
        status=202,
    )


@login_required(login_url="/")
@require_POST
@csrf_protect
def create_project(request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can create projects.")

    project_name = str(request.POST.get("name", "")).strip()
    if not project_name:
        messages.error(request, "Project name is required.")
        return redirect("portal:home")

    try:
        project = Project.objects.create(name=project_name)
    except IntegrityError:
        messages.error(request, "A project with that name already exists.")
        return redirect("portal:home")

    messages.success(request, f"Project '{project.name}' created.")
    return redirect("portal:project-overview", project_slug=project.slug)


@login_required(login_url="/")
@require_POST
@csrf_protect
def update_project_settings(request: HttpRequest, project_uuid: UUID) -> HttpResponse:
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can update project settings.")

    project = get_object_or_404(Project, uuid=project_uuid)
    destination_slug = project.slug

    raw_slug = str(request.POST.get("slug", "")).strip()
    normalized_slug = slugify(raw_slug)
    if not normalized_slug:
        messages.error(request, "Project slug is required and must contain letters or numbers.")
        return redirect("portal:project-overview", project_slug=destination_slug)

    max_slug_length = Project._meta.get_field("slug").max_length
    if len(normalized_slug) > max_slug_length:
        messages.error(request, f"Project slug must be {max_slug_length} characters or fewer.")
        return redirect("portal:project-overview", project_slug=destination_slug)

    try:
        UUID(normalized_slug)
        messages.error(request, "Project slug must not be UUID-formatted.")
        return redirect("portal:project-overview", project_slug=destination_slug)
    except ValueError:
        pass

    if Project.objects.exclude(pk=project.pk).filter(slug=normalized_slug).exists():
        messages.error(request, "That project slug is already in use.")
        return redirect("portal:project-overview", project_slug=destination_slug)

    if normalized_slug == project.slug:
        messages.info(request, "Project slug was unchanged.")
        return redirect("portal:project-overview", project_slug=project.slug)

    project.slug = normalized_slug
    try:
        project.save()
    except IntegrityError:
        project.refresh_from_db(fields=["slug"])
        messages.error(request, "Unable to update project slug right now.")
        return redirect("portal:project-overview", project_slug=project.slug)

    messages.success(request, "Project slug updated.")
    return redirect("portal:project-overview", project_slug=project.slug)


@login_required(login_url="/")
@require_POST
@csrf_protect
def add_project_member(request: HttpRequest, project_uuid: UUID) -> HttpResponse:
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can add project members.")

    project = get_object_or_404(Project, uuid=project_uuid)
    identifier = str(request.POST.get("user_identifier", "")).strip()
    if not identifier:
        messages.error(request, "Provide a username or email.")
        return redirect("portal:project-overview", project_slug=project.slug)

    user_model = get_user_model()
    user = user_model.objects.filter(username=identifier).first()
    if user is None:
        user = user_model.objects.filter(email__iexact=identifier).first()
    if user is None:
        messages.error(request, "User was not found.")
        return redirect("portal:project-overview", project_slug=project.slug)

    _, created = ProjectMembership.objects.get_or_create(project=project, user=user)
    if created:
        messages.success(request, f"Added {user.get_username()} to {project.name}.")
    else:
        messages.info(request, f"{user.get_username()} is already in {project.name}.")
    return redirect("portal:project-overview", project_slug=project.slug)


def _normalize_resource_payload(request: HttpRequest) -> dict:
    name = str(request.POST.get("name", "")).strip()
    slug_input = str(request.POST.get("slug", "")).strip()
    slug_value = slugify(slug_input) if slug_input else ""
    if slug_input and not slug_value:
        raise ValidationError("Resource slug must contain letters or numbers.")
    resource_type = str(request.POST.get("resource_type", "")).strip().lower()
    if not name:
        raise ValidationError("Resource name is required.")
    valid_resource_types = {choice[0] for choice in Resource.RESOURCE_TYPE_CHOICES}
    if resource_type not in valid_resource_types:
        raise ValidationError("Invalid resource type.")

    target = str(request.POST.get("target", "")).strip()
    address = str(request.POST.get("address", "")).strip()
    healthcheck_url = str(request.POST.get("healthcheck_url", "")).strip()
    notes = str(request.POST.get("notes", "")).strip()
    db_type = str(request.POST.get("db_type", "")).strip()

    port = None
    raw_port = str(request.POST.get("port", "")).strip()
    if raw_port:
        if not raw_port.isdigit():
            raise ValidationError("Port must be numeric.")
        port = int(raw_port)

    access_scope = Resource.ACCESS_SCOPE_ACCOUNT

    github_raw = str(request.POST.get("github_repositories", "")).replace("\n", ",")
    github_repositories = []
    for candidate in github_raw.split(","):
        normalized = candidate.strip().strip("/")
        if normalized:
            github_repositories.append(normalized)
    deduped_repositories = []
    seen = set()
    for repo in github_repositories:
        key = repo.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped_repositories.append(repo)

    ssh_mode = str(request.POST.get("ssh_mode", "")).strip().lower()
    ssh_username = str(request.POST.get("ssh_username", "")).strip()
    ssh_key_name = str(request.POST.get("ssh_key_name", "")).strip()
    ssh_credential_id = str(request.POST.get("ssh_credential_id", "")).strip()
    ssh_credential_scope = str(request.POST.get("ssh_scope", "")).strip().lower()
    valid_scopes = {choice[0] for choice in Resource.ACCESS_SCOPE_CHOICES}
    if ssh_credential_scope and ssh_credential_scope not in valid_scopes:
        ssh_credential_scope = ""
    ssh_port = None
    raw_ssh_port = str(request.POST.get("ssh_port", "")).strip()
    if raw_ssh_port:
        if not raw_ssh_port.isdigit():
            raise ValidationError("SSH port must be numeric.")
        ssh_port = int(raw_ssh_port)
    elif ssh_username:
        ssh_port = 22

    if resource_type != Resource.TYPE_VM:
        ssh_mode = ""
        ssh_username = ""
        ssh_key_name = ""
        ssh_credential_id = ""
        ssh_credential_scope = ""
        ssh_port = None

    metadata = {}
    for key, value in request.POST.items():
        if key.startswith("meta_"):
            metadata[key[5:]] = value

    return {
        "name": name,
        "slug": slug_value,
        "resource_type": resource_type,
        "target": target,
        "notes": notes,
        "address": address,
        "port": port,
        "db_type": db_type,
        "healthcheck_url": healthcheck_url,
        "access_scope": access_scope,
        "github_repositories": deduped_repositories[:50],
        "ssh_mode": ssh_mode,
        "ssh_username": ssh_username,
        "ssh_port": ssh_port,
        "ssh_credential_id": ssh_credential_id,
        "ssh_credential_scope": ssh_credential_scope,
        "ssh_key_name": ssh_key_name,
        "resource_metadata": metadata,
    }


@login_required(login_url="/")
@require_POST
@csrf_protect
def create_project_resource(request: HttpRequest, project_uuid: UUID) -> HttpResponse:
    project = get_object_or_404(Project, uuid=project_uuid)
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can create resources.")
    if not _user_can_access_project(request.user, project):
        messages.error(request, "You do not have access to that project.")
        return redirect("portal:home")

    try:
        payload = _normalize_resource_payload(request)
        resource = Resource(
            project=project,
            created_by=request.user,
            **payload,
        )
        resource.save()
    except IntegrityError:
        messages.error(request, "A resource with that slug already exists in this project.")
        return redirect("portal:project-overview", project_slug=project.slug)
    except ValidationError as exc:
        message = exc.messages[0] if exc.messages else "Invalid resource payload."
        messages.error(request, message)
        return redirect("portal:project-overview", project_slug=project.slug)

    messages.success(request, f"Resource '{resource.name}' created.")
    return redirect("portal:project-overview", project_slug=project.slug)


@login_required(login_url="/")
@require_POST
@csrf_protect
def update_resource_settings(request: HttpRequest, project_uuid: UUID, resource_uuid: UUID) -> HttpResponse:
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can update resource settings.")

    project = get_object_or_404(Project, uuid=project_uuid)
    resource = get_object_or_404(Resource, uuid=resource_uuid, project=project)
    destination_kwargs = {"project_slug": project.slug, "resource_slug": resource.slug}

    raw_slug = str(request.POST.get("slug", "")).strip()
    normalized_slug = slugify(raw_slug)
    if not normalized_slug:
        messages.error(request, "Resource slug is required and must contain letters or numbers.")
        return redirect("portal:resource-detail-slug", **destination_kwargs)

    max_slug_length = Resource._meta.get_field("slug").max_length
    if len(normalized_slug) > max_slug_length:
        messages.error(request, f"Resource slug must be {max_slug_length} characters or fewer.")
        return redirect("portal:resource-detail-slug", **destination_kwargs)

    if Resource.objects.exclude(pk=resource.pk).filter(project=project, slug=normalized_slug).exists():
        messages.error(request, "That resource slug is already in use in this project.")
        return redirect("portal:resource-detail-slug", **destination_kwargs)

    resource.slug = normalized_slug
    try:
        resource.save()
    except IntegrityError:
        messages.error(request, "Unable to update resource slug right now.")
        resource.refresh_from_db(fields=["slug"])
    else:
        messages.success(request, "Resource slug updated.")

    return redirect("portal:resource-detail-slug", project_slug=project.slug, resource_slug=resource.slug)


@login_required(login_url="/")
@require_POST
@csrf_protect
def delete_project_resource(request: HttpRequest, project_uuid: UUID, resource_uuid: UUID) -> HttpResponse:
    project = get_object_or_404(Project, uuid=project_uuid)
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can delete resources.")
    if not _user_can_access_project(request.user, project):
        messages.error(request, "You do not have access to that project.")
        return redirect("portal:home")

    resource = get_object_or_404(Resource, uuid=resource_uuid, project=project)
    resource_name = resource.name
    resource.delete()
    messages.success(request, f"Resource '{resource_name}' deleted.")
    return redirect("portal:project-overview", project_slug=project.slug)


def _authenticate_with_username_or_email(
    request: HttpRequest,
    identifier: str,
    password: str,
):
    user = authenticate(request, username=identifier, password=password)
    if user is not None or "@" not in identifier:
        return user

    user_model = get_user_model()
    matched_user = user_model.objects.filter(email__iexact=identifier).order_by("id").first()
    if matched_user is None:
        return None
    return authenticate(request, username=matched_user.get_username(), password=password)


def _safe_next_url(request: HttpRequest, raw_next: str) -> str:
    candidate = str(raw_next or "").strip()
    default_next = reverse("portal:home")
    if not candidate:
        return default_next

    if url_has_allowed_host_and_scheme(
        url=candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate
    return default_next


def _post_login_redirect() -> str:
    return reverse("portal:home")


@require_POST
@csrf_protect
def ajax_login(request: HttpRequest) -> JsonResponse:
    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")

    if not username or not password:
        return JsonResponse(
            {"ok": False, "error": "Username/email and password are required."},
            status=400,
        )

    user = _authenticate_with_username_or_email(request, username, password)
    if user is None:
        return JsonResponse({"ok": False, "error": "Invalid login credentials."}, status=401)

    login(request, user)
    next_url = _post_login_redirect()
    return JsonResponse({"ok": True, "redirect_url": next_url})


@require_POST
@csrf_protect
def ajax_signup(request: HttpRequest) -> JsonResponse:
    user_model = get_user_model()
    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "")
    password_confirm = request.POST.get("password_confirm", "")

    if not username:
        return JsonResponse({"ok": False, "error": "Username is required."}, status=400)
    if " " in username:
        return JsonResponse({"ok": False, "error": "Username cannot contain spaces."}, status=400)
    if not email:
        return JsonResponse({"ok": False, "error": "Email is required."}, status=400)
    if not password:
        return JsonResponse({"ok": False, "error": "Password is required."}, status=400)
    if password != password_confirm:
        return JsonResponse({"ok": False, "error": "Passwords do not match."}, status=400)

    if user_model.objects.filter(username__iexact=username).exists():
        return JsonResponse({"ok": False, "error": "That username is already in use."}, status=409)
    if user_model.objects.filter(email__iexact=email).exists():
        return JsonResponse({"ok": False, "error": "That email is already in use."}, status=409)

    try:
        validate_password(password)
    except ValidationError as exc:
        message = exc.messages[0] if exc.messages else "Password does not meet security requirements."
        return JsonResponse({"ok": False, "error": message}, status=400)

    created_user = user_model.objects.create_user(
        username=username,
        email=email,
        password=password,
    )

    user = _authenticate_with_username_or_email(request, username, password) or created_user
    if not hasattr(user, "backend"):
        user.backend = "django.contrib.auth.backends.ModelBackend"
    login(request, user)

    next_url = _post_login_redirect()
    return JsonResponse({"ok": True, "redirect_url": next_url})


@require_POST
@csrf_protect
def ajax_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    redirect_url = reverse("portal:home")
    wants_json = request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get(
        "Accept", ""
    ).lower()
    if wants_json:
        return JsonResponse({"ok": True, "redirect_url": redirect_url})
    return redirect(redirect_url)
