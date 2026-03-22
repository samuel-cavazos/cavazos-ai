from django.contrib import admin

from .models import Project, ProjectMembership, Resource


class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 0
    autocomplete_fields = ["user"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    search_fields = ["name", "slug"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [ProjectMembershipInline]


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "resource_type", "target", "updated_at"]
    list_filter = ["resource_type", "project", "access_scope"]
    search_fields = ["name", "target", "notes"]
    autocomplete_fields = ["project", "created_by"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ["project", "user", "added_at"]
    list_filter = ["project"]
    search_fields = ["project__name", "user__username", "user__email"]
    autocomplete_fields = ["project", "user"]

