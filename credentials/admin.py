from django.contrib import admin

from django.contrib import messages

from .models import Badge, Certificate
from .services import reissue_credential, revoke_credential


class CredentialLifecycleAdmin(admin.ModelAdmin):
    actions = ("revoke_selected_credentials", "reissue_selected_credentials")
    readonly_fields = ("uid", "awarded_at", "issued_to_name", "credential_title", "issuer_name", "revoked_at", "replaced_by")

    @admin.action(description="Revoke selected credentials")
    def revoke_selected_credentials(self, request, queryset):
        count = 0
        for credential in queryset.filter(status="active"):
            revoke_credential(credential, reason="Revoked by staff via Django admin.")
            count += 1
        self.message_user(request, f"Revoked {count} credential(s).", messages.SUCCESS)

    @admin.action(description="Reissue selected credentials")
    def reissue_selected_credentials(self, request, queryset):
        count = 0
        for credential in queryset.filter(status="active"):
            reissue_credential(credential, reason="Reissued by staff via Django admin.")
            count += 1
        self.message_user(request, f"Reissued {count} credential(s).", messages.SUCCESS)


@admin.register(Badge)
class BadgeAdmin(CredentialLifecycleAdmin):
    list_display = ("user", "course", "status", "awarded_at")
    list_filter = ("course__school",)
    search_fields = ("user__username", "user__email")

    def has_add_permission(self, request):
        # New badges must have a verified ParaLearn result; keep the admin as
        # an audit surface rather than a manual award bypass.
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Certificate)
class CertificateAdmin(CredentialLifecycleAdmin):
    list_display = ("user", "school", "status", "awarded_at")
    list_filter = ("school",)
    search_fields = ("user__username", "user__email")
