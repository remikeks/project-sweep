"""Management command to ingest production courseware files into AI Tutor CourseMaterial."""

import json
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from ai_tutor.models import CourseMaterial, _extract_docx, _extract_pdf, _extract_pptx
from courses.models import Course, CourseModule


class Command(BaseCommand):
    help = "Ingest verified release courseware into AI Tutor CourseMaterial for contextual grounding."

    def add_arguments(self, parser):
        parser.add_argument(
            "--release-dir",
            type=Path,
            default=Path("production_courseware/release-2026-10-03"),
            help="Path to the courseware release directory (default: production_courseware/release-2026-10-03)",
        )

    def handle(self, *args, **options):
        release_dir: Path = options["release_dir"]
        manifest_file = release_dir / "upload_manifest.json"

        if not manifest_file.exists():
            self.stderr.write(self.style.ERROR(f"Manifest file not found: {manifest_file}"))
            return

        with manifest_file.open("r", encoding="utf-8") as f:
            manifest_items = json.load(f)

        self.stdout.write(f"Found {len(manifest_items)} items in manifest.")
        created_count = 0
        updated_count = 0

        for item in manifest_items:
            slug = item.get("course_slug")
            try:
                course = Course.objects.get(slug=slug)
            except Course.DoesNotExist:
                self.stderr.write(self.style.WARNING(f"Course not found for slug: {slug}"))
                continue

            module = None
            mod_order = item.get("module_order")
            if mod_order not in (None, ""):
                try:
                    module = CourseModule.objects.filter(course=course, order=int(mod_order)).first()
                except (ValueError, TypeError):
                    pass

            file_rel_path = item.get("path")
            full_file_path = release_dir / file_rel_path
            if not full_file_path.exists():
                self.stderr.write(self.style.WARNING(f"File missing on disk: {full_file_path}"))
                continue

            data = full_file_path.read_bytes()
            name_lower = full_file_path.name.lower()
            text = ""
            error = ""

            try:
                if name_lower.endswith(".docx"):
                    text = _extract_docx(data)
                elif name_lower.endswith(".pdf"):
                    text = _extract_pdf(data)
                elif name_lower.endswith(".pptx"):
                    text = _extract_pptx(data)
                elif name_lower.endswith((".txt", ".md")):
                    text = data.decode("utf-8", errors="ignore")
            except Exception as exc:
                error = str(exc)

            title = item.get("title", full_file_path.name)
            content_file = ContentFile(data, name=full_file_path.name)

            obj, created = CourseMaterial.objects.update_or_create(
                course=course,
                module=module,
                title=title,
                defaults={
                    "file": content_file,
                    "extracted_text": text.strip(),
                    "char_count": len(text.strip()),
                    "extraction_error": error,
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed AI Tutor course material ingestion: {created_count} created, {updated_count} updated. "
                f"Total active in DB: {CourseMaterial.objects.filter(is_active=True).count()}"
            )
        )
