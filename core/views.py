from django.shortcuts import render

from courses.models import Course
from schools.models import School

# Cap on how many courses the landing-page carousel pulls in, even once the
# catalog grows well past its current single course.
FEATURED_COURSE_LIMIT = 8


def home(request):
    schools = School.objects.filter(is_active=True)
    stats = {
        "school_count": schools.count(),
        "course_count": Course.objects.filter(is_active=True).count(),
    }
    # Randomly selected each time the page loads, so the "featured courses"
    # rail surfaces different courses as the catalog grows beyond today's
    # single course.
    featured_courses = list(
        Course.objects.filter(is_active=True)
        .select_related("school")
        .order_by("?")[:FEATURED_COURSE_LIMIT]
    )
    context = {"schools": schools, "stats": stats, "featured_courses": featured_courses}
    return render(request, "core/home.html", context)
