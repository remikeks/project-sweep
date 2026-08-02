from django.contrib import admin
from django.utils.html import format_html

from .models import TeamMember


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("photo_thumbnail", "name", "role", "is_active", "order")
    list_display_links = ("name",)
    list_editable = ("order", "is_active")
    search_fields = ("name", "role", "bio")
    list_filter = ("is_active",)
    readonly_fields = ("photo_preview",)
    fields = ("name", "role", "bio", "photo", "photo_preview", "email", "linkedin_url", "order", "is_active")

    def photo_thumbnail(self, obj):
        if obj.photo_available:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;object-fit:cover;border-radius:50%;">',
                obj.photo.url,
            )
        return "—"

    photo_thumbnail.short_description = "Photo"

    def photo_preview(self, obj):
        if obj.photo_available:
            return format_html(
                '<img src="{}" style="width:160px;height:160px;object-fit:cover;'
                'border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.25);">',
                obj.photo.url,
            )
        return "No photo uploaded yet — the team page will show their initials instead."

    photo_preview.short_description = "Preview"
