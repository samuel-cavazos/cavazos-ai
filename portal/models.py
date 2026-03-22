import uuid as uuid_lib

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.text import slugify

from .project_storage import (
    delete_resource_record,
    ensure_project_storage,
    get_project_db_path,
    get_project_directory,
    move_project_storage,
    upsert_resource_record,
)


class Project(models.Model):
    uuid = models.UUIDField(default=uuid_lib.uuid4, unique=True, editable=False, db_index=True)
    name = models.CharField(max_length=160, unique=True)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def _generate_unique_slug(self) -> str:
        base = slugify(self.name) or "project"
        candidate = base
        suffix = 2
        while Project.objects.exclude(pk=self.pk).filter(slug=candidate).exists():
            candidate = f"{base}-{suffix}"
            suffix += 1
        return candidate

    @property
    def project_directory(self):
        return get_project_directory(self.slug)

    @property
    def project_db_path(self):
        return get_project_db_path(self.slug)

    def save(self, *args, **kwargs):
        previous_slug = None
        if self.pk:
            previous_slug = Project.objects.filter(pk=self.pk).values_list("slug", flat=True).first()
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)
        if previous_slug and previous_slug != self.slug:
            move_project_storage(previous_slug, self.slug)
            for resource in self.resources.all():
                upsert_resource_record(resource)


class ProjectMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_memberships")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="memberships")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "project"], name="unique_user_project_membership"),
        ]
        ordering = ["project__name", "user__username"]

    def __str__(self) -> str:
        return f"{self.user} -> {self.project}"


class Resource(models.Model):
    TYPE_API = "api"
    TYPE_VM = "vm"
    TYPE_DATABASE = "database"
    TYPE_QUEUE = "queue"
    TYPE_SERVICE = "service"
    TYPE_OTHER = "other"

    RESOURCE_TYPE_CHOICES = [
        (TYPE_API, "API"),
        (TYPE_VM, "Virtual Machine"),
        (TYPE_DATABASE, "Database"),
        (TYPE_QUEUE, "Queue"),
        (TYPE_SERVICE, "Service"),
        (TYPE_OTHER, "Other"),
    ]

    ACCESS_SCOPE_ACCOUNT = "account"
    ACCESS_SCOPE_GLOBAL = "global"
    ACCESS_SCOPE_CHOICES = [
        (ACCESS_SCOPE_ACCOUNT, "Account"),
        (ACCESS_SCOPE_GLOBAL, "Global"),
    ]

    SSH_MODE_INLINE = "inline"
    SSH_MODE_SAVED = "saved"
    SSH_MODE_CHOICES = [
        (SSH_MODE_INLINE, "Inline Key"),
        (SSH_MODE_SAVED, "Saved Credential"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="resources")
    uuid = models.UUIDField(default=uuid_lib.uuid4, unique=True, editable=False, db_index=True)
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)
    target = models.CharField(max_length=512)
    notes = models.TextField(blank=True)

    address = models.CharField(max_length=255, blank=True)
    port = models.PositiveIntegerField(null=True, blank=True)
    db_type = models.CharField(max_length=80, blank=True)
    healthcheck_url = models.CharField(max_length=512, blank=True)

    access_scope = models.CharField(max_length=20, choices=ACCESS_SCOPE_CHOICES, default=ACCESS_SCOPE_ACCOUNT)

    github_repositories = models.JSONField(default=list, blank=True)

    ssh_mode = models.CharField(max_length=20, choices=SSH_MODE_CHOICES, blank=True)
    ssh_key_name = models.CharField(max_length=255, blank=True)
    ssh_username = models.CharField(max_length=160, blank=True)
    ssh_port = models.PositiveIntegerField(null=True, blank=True)
    ssh_credential_id = models.CharField(max_length=255, blank=True)
    ssh_credential_scope = models.CharField(max_length=20, choices=ACCESS_SCOPE_CHOICES, blank=True)

    resource_metadata = models.JSONField(default=dict, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_resources",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["project", "name"], name="unique_resource_name_per_project"),
            models.UniqueConstraint(fields=["project", "slug"], name="unique_resource_slug_per_project"),
        ]

    def __str__(self) -> str:
        return f"{self.project.name} / {self.name}"

    def _generate_unique_slug(self) -> str:
        base = slugify(self.name) or "resource"
        candidate = base
        suffix = 2
        while Resource.objects.exclude(pk=self.pk).filter(project=self.project, slug=candidate).exists():
            candidate = f"{base}-{suffix}"
            suffix += 1
        return candidate

    def normalize_target_fields(self) -> None:
        target = (self.target or "").strip()
        address = (self.address or "").strip()
        healthcheck_url = (self.healthcheck_url or "").strip()
        resource_type = (self.resource_type or "").strip()

        if resource_type == self.TYPE_API:
            if not healthcheck_url and target:
                healthcheck_url = target
            target = healthcheck_url

        elif resource_type == self.TYPE_VM:
            if not address and target:
                address = target
            target = address

        elif resource_type == self.TYPE_DATABASE:
            if not address:
                if ":" in target:
                    candidate_address, candidate_port = target.rsplit(":", 1)
                    address = candidate_address.strip()
                    if not self.port and candidate_port.strip().isdigit():
                        self.port = int(candidate_port.strip())
                else:
                    address = target
            target = f"{address}:{self.port}" if address and self.port else address

        self.target = (target or "").strip()
        self.address = address
        self.healthcheck_url = healthcheck_url

        if not self.target:
            raise ValidationError("Resource target could not be resolved from provided fields.")

    def save(self, *args, **kwargs):
        if self.slug:
            self.slug = slugify(self.slug)
        if not self.slug:
            self.slug = self._generate_unique_slug()
        self.normalize_target_fields()
        super().save(*args, **kwargs)


@receiver(post_save, sender=Project)
def ensure_project_directory(sender, instance: Project, **kwargs):
    ensure_project_storage(instance.slug)


@receiver(post_save, sender=Resource)
def sync_resource_to_project_database(sender, instance: Resource, **kwargs):
    upsert_resource_record(instance)


@receiver(post_delete, sender=Resource)
def remove_resource_from_project_database(sender, instance: Resource, **kwargs):
    if not instance.project or not instance.project.slug:
        return
    delete_resource_record(instance.project.slug, instance.id)
