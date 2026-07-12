from django.shortcuts import render

from courses.models import Course
from schools.models import School


def home(request):
    schools = School.objects.filter(is_active=True)
    stats = {
        "school_count": schools.count(),
        "course_count": Course.objects.filter(is_active=True).count(),
    }
    context = {"schools": schools, "stats": stats}
    return render(request, "core/home.html", context)
