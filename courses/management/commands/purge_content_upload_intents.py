from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from courses.models import ContentUploadIntent


class Command(BaseCommand):
    help = "Remove expired or long-consumed content upload authorizations."

    def add_arguments(self, parser):
        parser.add_argument(
            "--consumed-days",
            type=int,
            default=7,
            help="Keep consumed authorizations for this many days (default: 7).",
        )

    def handle(self, *args, **options):
        consumed_days = max(options["consumed_days"], 0)
        now = timezone.now()
        expired_count, _ = ContentUploadIntent.objects.filter(
            expires_at__lt=now,
            consumed_at__isnull=True,
        ).delete()
        consumed_count, _ = ContentUploadIntent.objects.filter(
            consumed_at__lt=now - timedelta(days=consumed_days),
        ).delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"Removed {expired_count} expired and {consumed_count} old consumed upload authorizations."
            )
        )
