from django.contrib import admin

from .models import Choice, Course, CourseAsset, CourseModule, Question


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class ModuleInline(admin.StackedInline):
    model = CourseModule
    extra = 1
    show_change_link = True


class CourseAssetInline(admin.TabularInline):
    model = CourseAsset
    extra = 0


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text_preview", "course", "order")
    list_filter = ("course__school", "course")
    inlines = [ChoiceInline]

    def text_preview(self, obj):
        return obj.text[:60]

    text_preview.short_description = "Question"


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "duration", "module_type", "learning_mode")
    list_filter = ("course__school", "course", "module_type", "learning_mode")
    search_fields = ("title", "overview", "content", "module_summary", "knowledge_check", "practical_activity")


@admin.register(CourseAsset)
class CourseAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "module", "asset_type", "version", "status", "updated_at")
    list_filter = ("status", "asset_type", "course__school")
    search_fields = ("title", "course__title", "module__title")
    readonly_fields = (
        "status", "created_by", "reviewed_by", "reviewed_at", "published_by", "published_at",
        "retired_by", "retired_at", "replaces", "storage_path", "original_filename", "content_type", "size_bytes",
    )

    def has_module_permission(self, request):
        # The portal is the workflow authority. Keep non-superusers from using
        # Django admin to bypass its one-way status transitions.
        return request.user.is_superuser


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "school",
        "paralearn_assessment_id",
        "difficulty",
        "estimated_minutes",
        "question_count",
        "order",
        "is_active",
    )
    list_editable = ("order", "is_active")
    list_filter = ("school", "difficulty", "is_active")
    search_fields = ("title", "summary", "learning_objectives", "content", "paralearn_assessment_id")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ModuleInline, CourseAssetInline, QuestionInline]
