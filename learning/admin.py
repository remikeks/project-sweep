from django.contrib import admin

from .models import (
    CourseEnrollment,
    CourseAssessmentAttempt,
    CourseProgress,
    ParaLearnLearnerIdentity,
    ParaLearnWebhookEvent,
    QuizAttempt,
    SchoolEnrollment,
    SchoolExamAttempt,
)


@admin.register(SchoolEnrollment)
class SchoolEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "school", "enrolled_at")
    list_filter = ("school",)
    search_fields = ("user__username", "user__email")


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "via_school_enrollment", "enrolled_at")
    list_filter = ("course__school",)
    search_fields = ("user__username", "user__email")


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "status", "best_score", "attempts_count", "completed_at")
    list_filter = ("status", "course__school")
    search_fields = ("user__username",)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "score", "passed", "submitted_at")
    list_filter = ("passed", "course__school")
    search_fields = ("user__username",)


@admin.register(CourseAssessmentAttempt)
class CourseAssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "course", "provider", "status", "score", "passed",
        "provider_candidate_id", "provider_attempt_id", "created_at", "result_verified_at",
    )
    list_filter = ("provider", "status", "passed", "course__school")
    search_fields = (
        "id", "user__username", "user__email", "course__title", "provider_candidate_id",
        "provider_attempt_id", "provider_result_id",
    )
    readonly_fields = (
        "id", "launch_idempotency_key", "provider_candidate_id", "provider_attempt_id", "provider_result_id", "status", "score", "passed",
        "launch_count", "reconciliation_count", "launched_at", "result_received_at", "result_verified_at", "completed_at",
        "last_reconciled_at", "last_launch_error", "last_reconciliation_error", "result_payload", "created_at", "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # Provider callbacks and reconciliation services are the authority;
        # staff may inspect but must not hand-edit a verified result.
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ParaLearnWebhookEvent)
class ParaLearnWebhookEventAdmin(admin.ModelAdmin):
    list_display = ("event_id", "attempt", "received_at", "signature_verified_at", "processed_at", "has_error")
    search_fields = ("event_id", "attempt__id", "attempt__user__username")
    readonly_fields = (
        "event_id", "attempt", "payload_sha256", "payload", "received_at", "signature_verified_at", "processed_at", "processing_error",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(boolean=True, description="Processing error")
    def has_error(self, obj):
        return bool(obj.processing_error)


@admin.register(ParaLearnLearnerIdentity)
class ParaLearnLearnerIdentityAdmin(admin.ModelAdmin):
    list_display = ("user", "external_id", "created_at")
    search_fields = ("user__username", "user__email", "external_id")
    readonly_fields = ("user", "external_id", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SchoolExamAttempt)
class SchoolExamAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "school", "score", "passed", "submitted_at")
    list_filter = ("passed", "school")
    search_fields = ("user__username",)
