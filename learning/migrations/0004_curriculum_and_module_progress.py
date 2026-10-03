from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def snapshot_existing_curricula(apps, schema_editor):
    Enrollment = apps.get_model("learning", "SchoolEnrollment")
    CourseEnrollment = apps.get_model("learning", "CourseEnrollment")
    Requirement = apps.get_model("learning", "SchoolCurriculumRequirement")
    Course = apps.get_model("courses", "Course")
    Progress = apps.get_model("learning", "CourseProgress")
    Module = apps.get_model("courses", "CourseModule")
    ModuleProgress = apps.get_model("learning", "ModuleProgress")
    for enrollment in Enrollment.objects.all().iterator():
        course_ids = list(CourseEnrollment.objects.filter(via_school_enrollment_id=enrollment.id).values_list("course_id", flat=True))
        if not course_ids:
            course_ids = list(Course.objects.filter(school_id=enrollment.school_id, is_active=True).values_list("id", flat=True))
        for course in Course.objects.filter(id__in=course_ids):
            Requirement.objects.get_or_create(school_enrollment_id=enrollment.id, course_id=course.id, defaults={"order": course.order})
        completed_ids = Progress.objects.filter(user_id=enrollment.user_id, status="completed").values_list("course_id", flat=True)
        for module in Module.objects.filter(course_id__in=completed_ids):
            ModuleProgress.objects.get_or_create(user_id=enrollment.user_id, module_id=module.id)


class Migration(migrations.Migration):
    dependencies = [("learning", "0003_paralearn_identity_and_candidate")]

    operations = [
        migrations.CreateModel(
            name="ModuleProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("completed_at", models.DateTimeField(auto_now_add=True)),
                ("module", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="progress_records", to="courses.coursemodule")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="module_progress", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="SchoolCurriculumRequirement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="school_curriculum_requirements", to="courses.course")),
                ("school_enrollment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="curriculum_requirements", to="learning.schoolenrollment")),
            ],
            options={"ordering": ["order", "id"]},
        ),
        migrations.AddConstraint(model_name="moduleprogress", constraint=models.UniqueConstraint(fields=("user", "module"), name="unique_module_progress")),
        migrations.AddIndex(model_name="moduleprogress", index=models.Index(fields=["user", "module"], name="learning_mo_user_id_a136c9_idx")),
        migrations.AddConstraint(model_name="schoolcurriculumrequirement", constraint=models.UniqueConstraint(fields=("school_enrollment", "course"), name="unique_school_curriculum_course")),
        migrations.AddIndex(model_name="schoolcurriculumrequirement", index=models.Index(fields=["school_enrollment", "order"], name="learning_sc_school__6621ad_idx")),
        migrations.RunPython(snapshot_existing_curricula, migrations.RunPython.noop),
    ]
