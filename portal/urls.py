from django.urls import path
from django.views.generic import RedirectView

from . import views


app_name = "portal"

urlpatterns = [
    path("", views.home, name="home"),
    path("superuser/gallery/", views.media_gallery, name="media-gallery"),
    path("superuser/gallery/upload/", views.media_gallery_upload, name="media-gallery-upload"),
    path("superuser/gallery/delete/", views.media_gallery_delete, name="media-gallery-delete"),
    path("shared/<path:filename>", views.shared_media_file, name="shared-media-file"),
    path("projects/create/", views.create_project, name="project-create"),
    path("projects/<uuid:project_uuid>/", views.project_overview_by_uuid, name="project-overview-uuid"),
    path("projects/<slug:project_slug>/", views.project_overview, name="project-overview"),
    path("projects/<uuid:project_uuid>/settings/", views.update_project_settings, name="project-settings-update"),
    path("projects/<uuid:project_uuid>/members/add/", views.add_project_member, name="project-member-add"),
    path("projects/<uuid:project_uuid>/resources/create/", views.create_project_resource, name="project-resource-create"),
    path(
        "projects/<uuid:project_uuid>/resources/<uuid:resource_uuid>/api-keys/create/",
        views.create_resource_api_key_view,
        name="resource-api-key-create",
    ),
    path(
        "projects/<uuid:project_uuid>/resources/<uuid:resource_uuid>/api-keys/<uuid:key_id>/revoke/",
        views.revoke_resource_api_key_view,
        name="resource-api-key-revoke",
    ),
    path(
        "projects/<uuid:project_uuid>/resources/<uuid:resource_uuid>/logs/",
        views.ingest_resource_logs,
        name="resource-log-ingest",
    ),
    path(
        "projects/<uuid:project_uuid>/resources/<uuid:resource_uuid>/settings/",
        views.update_resource_settings,
        name="resource-settings-update",
    ),
    path(
        "projects/<uuid:project_uuid>/resources/<uuid:resource_uuid>/delete/",
        views.delete_project_resource,
        name="project-resource-delete",
    ),
    path(
        "projects/<uuid:project_uuid>/resources/<uuid:resource_uuid>/",
        views.resource_detail,
        name="resource-detail",
    ),
    path(
        "projects/<slug:project_slug>/resources/<slug:resource_slug>/",
        views.resource_detail_by_slug,
        name="resource-detail-slug",
    ),
    path("ops/", views.ops_overview, name="ops"),
    path("chat/", RedirectView.as_view(pattern_name="portal:home", permanent=True), name="chat"),
    path("auth/login/", views.ajax_login, name="ajax-login"),
    path("auth/signup/", views.ajax_signup, name="ajax-signup"),
    path("auth/logout/", views.ajax_logout, name="ajax-logout"),
]
