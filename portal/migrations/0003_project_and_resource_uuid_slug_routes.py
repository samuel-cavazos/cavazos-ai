import uuid

from django.db import migrations, models
from django.utils.text import slugify


def populate_uuid_and_resource_slug(apps, schema_editor):
    project_model = apps.get_model("portal", "Project")
    resource_model = apps.get_model("portal", "Resource")

    for project in project_model.objects.filter(uuid__isnull=True).order_by("id").iterator():
        project_model.objects.filter(pk=project.pk).update(uuid=uuid.uuid4())

    for resource in resource_model.objects.order_by("project_id", "id").iterator():
        base_slug = slugify(resource.slug or resource.name) or "resource"
        candidate = base_slug
        suffix = 2
        while resource_model.objects.filter(project_id=resource.project_id, slug=candidate).exclude(pk=resource.pk).exists():
            candidate = f"{base_slug}-{suffix}"
            suffix += 1

        resource_model.objects.filter(pk=resource.pk).update(
            uuid=resource.uuid or uuid.uuid4(),
            slug=candidate,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0002_remove_resource_resource_team_names_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="uuid",
            field=models.UUIDField(db_index=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="resource",
            name="uuid",
            field=models.UUIDField(db_index=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="resource",
            name="slug",
            field=models.SlugField(blank=True, max_length=180),
        ),
        migrations.RunPython(populate_uuid_and_resource_slug, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="project",
            name="uuid",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name="resource",
            name="uuid",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddConstraint(
            model_name="resource",
            constraint=models.UniqueConstraint(fields=("project", "slug"), name="unique_resource_slug_per_project"),
        ),
    ]
