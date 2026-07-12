from django.contrib import admin

from .models import School, SchoolExamChoice, SchoolExamQuestion


class SchoolExamChoiceInline(admin.TabularInline):
    model = SchoolExamChoice
    extra = 4


@admin.register(SchoolExamQuestion)
class SchoolExamQuestionAdmin(admin.ModelAdmin):
    list_display = ("text_preview", "school", "order")
    list_filter = ("school",)
    inlines = [SchoolExamChoiceInline]

    def text_preview(self, obj):
        return obj.text[:60]

    text_preview.short_description = "Question"


class SchoolExamQuestionInline(admin.StackedInline):
    model = SchoolExamQuestion
    extra = 1
    show_change_link = True


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "course_count", "exam_question_count", "passing_score", "is_active", "order")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")
    list_filter = ("is_active",)
    inlines = [SchoolExamQuestionInline]
