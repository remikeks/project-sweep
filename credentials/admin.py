from django.contrib import admin

from .models import Badge, Certificate


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "awarded_at")
    list_filter = ("course__school",)
    search_fields = ("user__username", "user__email")
    readonly_fields = ("uid", "awarded_at")


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("user", "school", "awarded_at")
    list_filter = ("school",)
    search_fields = ("user__username", "user__email")
    readonly_fields = ("uid", "awarded_at")
