from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "feedback_type",
        "message_preview",
        "email",
        "user",
        "page_url",
        "email_sent",
        "is_reviewed",
        "created_at",
    )
    list_filter = ("feedback_type", "email_sent", "is_reviewed", "created_at")
    list_editable = ("is_reviewed",)
    search_fields = ("message", "email", "user__username", "page_url")
    readonly_fields = (
        "feedback_type",
        "message",
        "email",
        "user",
        "page_url",
        "email_sent",
        "email_error",
        "created_at",
    )
    fields = (
        "feedback_type",
        "message",
        "email",
        "user",
        "page_url",
        "email_sent",
        "email_error",
        "created_at",
        "is_reviewed",
        "admin_notes",
    )

    def message_preview(self, obj):
        return obj.message[:70] + ("…" if len(obj.message) > 70 else "")

    message_preview.short_description = "Message"

    def has_add_permission(self, request):
        return False
