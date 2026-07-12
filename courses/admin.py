from django.contrib import admin

from .models import Choice, Course, Question


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


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
    search_fields = ("title", "summary", "content")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [QuestionInline]
