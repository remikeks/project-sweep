import ai_tutor.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("courses", "0004_coursemodule"),
    ]

    operations = [
        migrations.CreateModel(
            name="CourseMaterial",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                (
                    "file",
                    models.FileField(
                        help_text="Supported for automatic text extraction: PDF, DOCX, PPTX, TXT, MD. "
                        "If you replace the file later, use the 'Re-run text extraction' admin action.",
                        upload_to=ai_tutor.models.course_material_upload_path,
                    ),
                ),
                ("extracted_text", models.TextField(blank=True)),
                ("char_count", models.PositiveIntegerField(default=0)),
                ("extraction_error", models.CharField(blank=True, max_length=500)),
                ("is_active", models.BooleanField(default=True)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ai_materials",
                        to="courses.course",
                    ),
                ),
                (
                    "module",
                    models.ForeignKey(
                        blank=True,
                        help_text="Leave blank to make this material available across the whole course.",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ai_materials",
                        to="courses.coursemodule",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="uploaded_materials",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-uploaded_at"],
            },
        ),
        migrations.CreateModel(
            name="TutorInteraction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("chat", "Question"), ("summary", "Summary")], default="chat", max_length=10)),
                ("question", models.TextField(blank=True)),
                ("answer", models.TextField(blank=True)),
                ("was_error", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tutor_interactions",
                        to="courses.course",
                    ),
                ),
                (
                    "module",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tutor_interactions",
                        to="courses.coursemodule",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tutor_interactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
