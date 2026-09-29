from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the standard Content Author, Reviewer, and Publisher groups."

    def handle(self, *args, **options):
        permissions = Permission.objects.filter(content_type__app_label="courses", content_type__model="courseasset")
        by_codename = {permission.codename: permission for permission in permissions}
        role_permissions = {
            "Content Author": {"add_courseasset", "change_courseasset", "view_courseasset"},
            "Content Reviewer": {"view_courseasset", "review_courseasset"},
            "Content Publisher": {"view_courseasset", "publish_courseasset", "bulk_import_courseasset"},
        }
        for role, codenames in role_permissions.items():
            group, _ = Group.objects.get_or_create(name=role)
            group.permissions.set([by_codename[codename] for codename in codenames])
            self.stdout.write(self.style.SUCCESS(f"Configured {role}."))
