from django.contrib import admin

from .models import CourseMaterial, TutorInteraction


@admin.action(description="Re-run text extraction on selected materials")
def reextract_materials(modeladmin, request, queryset):
    for material in queryset:
        material.extract_text()
        material.save(update_fields=["extracted_text", "char_count", "extraction_error"])


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "module",
        "char_count",
        "extraction_status",
        "is_active",
        "uploaded_at",
    )
    list_filter = ("course__school", "course", "is_active")
    search_fields = ("title", "extracted_text", "course__title", "module__title")
    readonly_fields = ("extracted_text", "char_count", "extraction_error", "uploaded_at")
    autocomplete_fields = ("course", "module")
    actions = [reextract_materials]

    def extraction_status(self, obj):
        if obj.extraction_error:
            return f"⚠ {obj.extraction_error[:60]}"
        if obj.char_count:
            return "✓ extracted"
        return "—"

    extraction_status.short_description = "Extraction"

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TutorInteraction)
class TutorInteractionAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "module", "kind", "was_error", "created_at")
    list_filter = ("kind", "was_error", "course__school", "course")
    search_fields = ("user__username", "question", "answer")
    readonly_fields = ("user", "course", "module", "kind", "question", "answer", "was_error", "created_at")

    def has_add_permission(self, request):
        return False
