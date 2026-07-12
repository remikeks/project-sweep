from django.contrib import admin

from .models import (
    CourseEnrollment,
    CourseProgress,
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


@admin.register(SchoolExamAttempt)
class SchoolExamAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "school", "score", "passed", "submitted_at")
    list_filter = ("passed", "school")
    search_fields = ("user__username",)
