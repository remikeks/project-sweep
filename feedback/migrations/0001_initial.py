import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Feedback",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "feedback_type",
                    models.CharField(
                        choices=[
                            ("suggestion", "Suggestion / idea"),
                            ("bug", "Something's not working"),
                            ("content", "Course or content issue"),
                            ("compliment", "Compliment"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=20,
                    ),
                ),
                ("message", models.TextField()),
                (
                    "email",
                    models.EmailField(
                        blank=True, help_text="Optional — provided by the submitter.", max_length=254
                    ),
                ),
                (
                    "page_url",
                    models.CharField(
                        blank=True,
                        help_text="Page the submitter was on, captured client-side.",
                        max_length=500,
                    ),
                ),
                ("email_sent", models.BooleanField(default=False)),
                ("email_error", models.CharField(blank=True, max_length=500)),
                ("is_reviewed", models.BooleanField(default=False)),
                ("admin_notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        help_text="Set automatically if the submitter was logged in.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="feedback_submissions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
