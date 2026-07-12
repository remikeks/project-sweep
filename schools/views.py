from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import School


def school_list(request):
    """Browse and search the 10 schools offered on SWEEP."""
    query = request.GET.get("q", "").strip()
    schools = School.objects.filter(is_active=True)

    if query:
        schools = schools.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(tagline__icontains=query)
        )

    enrolled_school_ids = set()
    if request.user.is_authenticated:
        enrolled_school_ids = set(
            request.user.school_enrollments.values_list("school_id", flat=True)
        )

    context = {
        "schools": schools,
        "query": query,
        "enrolled_school_ids": enrolled_school_ids,
    }
    return render(request, "schools/school_list.html", context)


def school_detail(request, slug):
    """
    Show a school's overview, its courses, the user's enrollment/progress
    state, and — once every course is complete — the certification exam.
    """
    school = get_object_or_404(School, slug=slug, is_active=True)
    courses = school.active_courses

    is_enrolled = False
    course_progress_map = {}
    completed_course_count = 0
    certificate = None
    exam_attempt = None

    if request.user.is_authenticated:
        is_enrolled = school.enrollments.filter(user=request.user).exists()

        from learning.models import CourseProgress
        from credentials.models import Certificate
        from learning.models import SchoolExamAttempt

        progresses = CourseProgress.objects.filter(
            user=request.user, course__school=school
        )
        course_progress_map = {p.course_id: p for p in progresses}
        completed_course_count = sum(
            1 for p in course_progress_map.values() if p.status == CourseProgress.Status.COMPLETED
        )
        certificate = Certificate.objects.filter(user=request.user, school=school).first()
        exam_attempt = (
            SchoolExamAttempt.objects.filter(user=request.user, school=school)
            .order_by("-submitted_at")
            .first()
        )

    all_courses_completed = bool(courses) and completed_course_count == courses.count()

    course_rows = []
    for course in courses:
        progress = course_progress_map.get(course.id)
        course_rows.append(
            {
                "course": course,
                "progress": progress,
                "is_completed": bool(progress and progress.status == "completed"),
            }
        )

    context = {
        "school": school,
        "courses": courses,
        "course_rows": course_rows,
        "is_enrolled": is_enrolled,
        "course_progress_map": course_progress_map,
        "completed_course_count": completed_course_count,
        "all_courses_completed": all_courses_completed,
        "certificate": certificate,
        "exam_attempt": exam_attempt,
        "has_exam_questions": school.exam_question_count > 0,
    }
    return render(request, "schools/school_detail.html", context)
