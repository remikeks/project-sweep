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
    list_editable = ("status",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "school",
        "difficulty",
        "estimated_minutes",
        "question_count",
        "order",
        "is_active",
    )
    list_editable = ("order", "is_active")
    list_filter = ("school", "difficulty", "is_active")
    search_fields = ("title", "summary", "learning_objectives", "content")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ModuleInline, CourseAssetInline, QuestionInline]
