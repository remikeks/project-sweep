from django.contrib import admin
from django.utils.html import format_html

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
    list_display = ("poster_thumbnail", "name", "course_count", "exam_question_count", "passing_score", "is_active", "order")
    list_display_links = ("name",)
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")
    list_filter = ("is_active",)
    readonly_fields = ("poster_preview",)
    fields = (
        "name", "slug", "tagline", "description",
        "poster", "poster_preview",
        "passing_score", "is_active", "order",
    )
    inlines = [SchoolExamQuestionInline]

    def poster_thumbnail(self, obj):
        if obj.poster_available:
            return format_html(
                '<img src="{}" style="width:40px;height:53px;object-fit:cover;'
                'border-radius:4px;">',
                obj.poster.url,
            )
        return "—"

    poster_thumbnail.short_description = "Poster"

    def poster_preview(self, obj):
        if obj.poster_available:
            return format_html(
                '<img src="{}" style="width:180px;height:240px;object-fit:cover;'
                'border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.25);">',
                obj.poster.url,
            )
        return "No poster uploaded yet — the card and hero section will show the default emblem instead."

    poster_preview.short_description = "Preview"
