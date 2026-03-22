import json
import shutil
import sqlite3
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Project, ProjectMembership, Resource
from .project_storage import get_project_db_path, list_resource_api_keys


@override_settings(PROJECTS_ROOT="/tmp/cavazos-projects-tests")
class ProjectResourceRoutingTests(TestCase):
    def setUp(self):
        projects_root = Path("/tmp/cavazos-projects-tests")
        if projects_root.exists():
            shutil.rmtree(projects_root)
        projects_root.mkdir(parents=True, exist_ok=True)

        user_model = get_user_model()
        self.superuser = user_model.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin-pass-123",
        )
        self.member = user_model.objects.create_user(
            username="member",
            email="member@example.com",
            password="member-pass-123",
        )

        self.project = Project.objects.create(name="Alpha Project")
        ProjectMembership.objects.create(project=self.project, user=self.member)

        self.resource = Resource.objects.create(
            project=self.project,
            name="Primary API",
            resource_type=Resource.TYPE_API,
            target="https://api.example.com/health",
            created_by=self.superuser,
        )

    def test_project_overview_slug_route_renders_for_member(self):
        self.client.force_login(self.member)
        response = self.client.get(reverse("portal:project-overview", kwargs={"project_slug": self.project.slug}))
        self.assertEqual(response.status_code, 200)

    def test_project_overview_uuid_route_redirects_to_slug(self):
        self.client.force_login(self.member)
        response = self.client.get(reverse("portal:project-overview-uuid", kwargs={"project_uuid": self.project.uuid}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], reverse("portal:project-overview", kwargs={"project_slug": self.project.slug}))

    def test_resource_detail_slug_route_renders(self):
        self.client.force_login(self.member)
        response = self.client.get(
            reverse(
                "portal:resource-detail-slug",
                kwargs={"project_slug": self.project.slug, "resource_slug": self.resource.slug},
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_resource_detail_uuid_route_renders(self):
        self.client.force_login(self.member)
        response = self.client.get(
            reverse(
                "portal:resource-detail",
                kwargs={"project_uuid": self.project.uuid, "resource_uuid": self.resource.uuid},
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_resource_uuid_route_with_wrong_project_returns_404(self):
        self.client.force_login(self.superuser)
        project_two = Project.objects.create(name="Beta Project")
        resource_two = Resource.objects.create(
            project=project_two,
            name="Beta Queue",
            resource_type=Resource.TYPE_QUEUE,
            target="redis://queue.internal:6379/0",
            created_by=self.superuser,
        )

        response = self.client.get(
            reverse(
                "portal:resource-detail",
                kwargs={"project_uuid": self.project.uuid, "resource_uuid": resource_two.uuid},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_legacy_chat_route_redirects_to_home_permanently(self):
        response = self.client.get(reverse("portal:chat"))
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers["Location"], reverse("portal:home"))

    def test_home_page_includes_global_assistant_widget(self):
        response = self.client.get(reverse("portal:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="assistantWidget"')

    def test_project_and_resource_pages_include_global_assistant_widget(self):
        self.client.force_login(self.member)

        project_response = self.client.get(reverse("portal:project-overview", kwargs={"project_slug": self.project.slug}))
        self.assertEqual(project_response.status_code, 200)
        self.assertContains(project_response, 'id="assistantWidget"')

        resource_response = self.client.get(
            reverse(
                "portal:resource-detail-slug",
                kwargs={"project_slug": self.project.slug, "resource_slug": self.resource.slug},
            )
        )
        self.assertEqual(resource_response.status_code, 200)
        self.assertContains(resource_response, 'id="assistantWidget"')

    def test_superuser_ops_and_gallery_pages_include_global_assistant_widget(self):
        self.client.force_login(self.superuser)

        ops_response = self.client.get(reverse("portal:ops"))
        self.assertEqual(ops_response.status_code, 200)
        self.assertContains(ops_response, 'id="assistantWidget"')

        gallery_response = self.client.get(reverse("portal:media-gallery"))
        self.assertEqual(gallery_response.status_code, 200)
        self.assertContains(gallery_response, 'id="assistantWidget"')

    def test_resource_detail_displays_full_https_log_ingest_url_for_superuser(self):
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse(
                "portal:resource-detail-slug",
                kwargs={"project_slug": self.project.slug, "resource_slug": self.resource.slug},
            )
        )
        self.assertEqual(response.status_code, 200)
        expected_url = (
            f"https://testserver/projects/{self.project.uuid}/resources/{self.resource.uuid}/logs/"
        )
        self.assertContains(response, expected_url)

    def test_uuid_management_routes_allow_superuser_posts(self):
        self.client.force_login(self.superuser)
        extra_user = get_user_model().objects.create_user(
            username="newmember",
            email="newmember@example.com",
            password="newmember-pass-123",
        )

        add_member_response = self.client.post(
            reverse("portal:project-member-add", kwargs={"project_uuid": self.project.uuid}),
            {"user_identifier": extra_user.username},
        )
        self.assertEqual(add_member_response.status_code, 302)
        self.assertTrue(ProjectMembership.objects.filter(project=self.project, user=extra_user).exists())

        create_resource_response = self.client.post(
            reverse("portal:project-resource-create", kwargs={"project_uuid": self.project.uuid}),
            {
                "name": "Worker Queue",
                "slug": "worker-queue",
                "resource_type": Resource.TYPE_QUEUE,
                "target": "redis://queue.internal:6379/0",
            },
        )
        self.assertEqual(create_resource_response.status_code, 302)
        created_resource = Resource.objects.get(project=self.project, slug="worker-queue")

        delete_resource_response = self.client.post(
            reverse(
                "portal:project-resource-delete",
                kwargs={"project_uuid": self.project.uuid, "resource_uuid": created_resource.uuid},
            )
        )
        self.assertEqual(delete_resource_response.status_code, 302)
        self.assertFalse(Resource.objects.filter(pk=created_resource.pk).exists())

    def test_uuid_management_routes_forbid_non_superuser(self):
        self.client.force_login(self.member)

        add_member_response = self.client.post(
            reverse("portal:project-member-add", kwargs={"project_uuid": self.project.uuid}),
            {"user_identifier": self.member.username},
        )
        self.assertEqual(add_member_response.status_code, 403)

        create_resource_response = self.client.post(
            reverse("portal:project-resource-create", kwargs={"project_uuid": self.project.uuid}),
            {
                "name": "Blocked Queue",
                "resource_type": Resource.TYPE_QUEUE,
                "target": "redis://queue.internal:6379/1",
            },
        )
        self.assertEqual(create_resource_response.status_code, 403)

    def test_project_slug_update_changes_canonical_url(self):
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse("portal:project-settings-update", kwargs={"project_uuid": self.project.uuid}),
            {"slug": "alpha-control"},
        )

        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertEqual(self.project.slug, "alpha-control")
        self.assertEqual(response.headers["Location"], reverse("portal:project-overview", kwargs={"project_slug": "alpha-control"}))

    def test_resource_slug_update_changes_slug_route(self):
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse(
                "portal:resource-settings-update",
                kwargs={"project_uuid": self.project.uuid, "resource_uuid": self.resource.uuid},
            ),
            {"slug": "primary-api-v2"},
        )

        self.assertEqual(response.status_code, 302)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.slug, "primary-api-v2")
        self.assertEqual(
            response.headers["Location"],
            reverse(
                "portal:resource-detail-slug",
                kwargs={"project_slug": self.project.slug, "resource_slug": "primary-api-v2"},
            ),
        )

    def test_old_integer_routes_are_not_supported(self):
        self.client.force_login(self.superuser)

        project_response = self.client.get(f"/projects/{self.project.id}/")
        self.assertEqual(project_response.status_code, 404)

        resource_response = self.client.get(f"/projects/{self.project.id}/resources/{self.resource.id}/")
        self.assertEqual(resource_response.status_code, 404)

    def test_superuser_can_create_resource_api_key(self):
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse(
                "portal:resource-api-key-create",
                kwargs={"project_uuid": self.project.uuid, "resource_uuid": self.resource.uuid},
            ),
            {"name": "vm-agent-prod"},
        )
        self.assertEqual(response.status_code, 302)

        session = self.client.session
        new_key = session.get("new_resource_api_key")
        self.assertIsNotNone(new_key)
        self.assertEqual(new_key["name"], "vm-agent-prod")
        self.assertTrue(str(new_key["value"]).startswith("rsk_"))

        keys = list_resource_api_keys(self.project.slug, self.resource.id)
        self.assertEqual(len(keys), 1)
        self.assertEqual(keys[0]["name"], "vm-agent-prod")
        self.assertEqual(keys[0]["is_active"], 1)

    def test_non_superuser_cannot_create_resource_api_key(self):
        self.client.force_login(self.member)
        response = self.client.post(
            reverse(
                "portal:resource-api-key-create",
                kwargs={"project_uuid": self.project.uuid, "resource_uuid": self.resource.uuid},
            ),
            {"name": "blocked-key"},
        )
        self.assertEqual(response.status_code, 403)

    def test_log_ingest_requires_resource_api_key(self):
        response = self.client.post(
            reverse(
                "portal:resource-log-ingest",
                kwargs={"project_uuid": self.project.uuid, "resource_uuid": self.resource.uuid},
            ),
            data=json.dumps({"level": "info", "message": "hello"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_log_ingest_accepts_alert_level_with_valid_api_key(self):
        self.client.force_login(self.superuser)
        self.client.post(
            reverse(
                "portal:resource-api-key-create",
                kwargs={"project_uuid": self.project.uuid, "resource_uuid": self.resource.uuid},
            ),
            {"name": "logs-writer"},
        )
        key_value = self.client.session["new_resource_api_key"]["value"]
        self.client.logout()

        ingest_response = self.client.post(
            reverse(
                "portal:resource-log-ingest",
                kwargs={"project_uuid": self.project.uuid, "resource_uuid": self.resource.uuid},
            ),
            data=json.dumps({"level": "Alert", "message": "CPU threshold exceeded", "source": "agent"}),
            content_type="application/json",
            HTTP_X_RESOURCE_API_KEY=key_value,
        )
        self.assertEqual(ingest_response.status_code, 202)
        self.assertEqual(ingest_response.json()["accepted"], 1)

        db_path = get_project_db_path(self.project.slug)
        with sqlite3.connect(db_path) as connection:
            row = connection.execute(
                """
                SELECT level, message, source
                FROM resource_logs
                WHERE global_resource_id = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (self.resource.id,),
            ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "alert")
        self.assertEqual(row[1], "CPU threshold exceeded")
        self.assertEqual(row[2], "agent")

    def test_log_ingest_rejects_invalid_level(self):
        self.client.force_login(self.superuser)
        self.client.post(
            reverse(
                "portal:resource-api-key-create",
                kwargs={"project_uuid": self.project.uuid, "resource_uuid": self.resource.uuid},
            ),
            {"name": "logs-writer"},
        )
        key_value = self.client.session["new_resource_api_key"]["value"]
        self.client.logout()

        ingest_response = self.client.post(
            reverse(
                "portal:resource-log-ingest",
                kwargs={"project_uuid": self.project.uuid, "resource_uuid": self.resource.uuid},
            ),
            data=json.dumps({"level": "critical", "message": "bad level"}),
            content_type="application/json",
            HTTP_X_RESOURCE_API_KEY=key_value,
        )
        self.assertEqual(ingest_response.status_code, 400)
