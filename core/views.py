from django.shortcuts import render

from courses.models import Course
from schools.models import School

# Cap on how many courses the landing-page carousel pulls in, even once the
# catalog grows well past its current single course.
FEATURED_COURSE_LIMIT = 8

# Placeholder service catalog for the public "Services" page. Grouped for
# readability; edit freely as real offerings firm up.
SERVICE_GROUPS = [
    {
        "title": "Learning & Curriculum",
        "items": [
            "Self-paced online courses across 10 specialty schools",
            "Multiple-choice assessments with instant feedback",
            "Difficulty-graded course tracks, beginner to advanced",
            "Estimated time-to-complete shown on every course",
            "Whole-school enrollment bundles",
            "Individual course search and enrollment",
        ],
    },
    {
        "title": "Credentialing & Recognition",
        "items": [
            "Digital badges for course completion",
            "Downloadable PNG and PDF certificates",
            "School-level certification exams",
            "Personal credentials dashboard",
            "Verifiable completion records",
            "Progress tracking across every enrolled course",
        ],
    },
    {
        "title": "AI-Assisted Learning",
        "items": [
            "AI Tutor for course-specific questions",
            "One-click lesson summaries",
            "AI-generated course overviews",
            "Course material ingestion for deeper AI context",
            "Usage-limited AI access to keep it available to everyone",
            "Continuous improvement of AI response quality",
        ],
    },
    {
        "title": "Learner Support",
        "items": [
            "Guided onboarding for new learners",
            "Dashboard-based progress overview",
            "Mobile-friendly learning experience",
            "Accessible design across devices",
            "Clear course search and filtering tools",
            "Responsive support for account and access issues",
        ],
    },
    {
        "title": "Platform & Trust",
        "items": [
            "Secure account management",
            "Regular content review and updates",
            "Transparent data and privacy practices",
            "Ongoing platform improvements based on learner feedback",
            "Practice-informed, ethics-centered course design",
            "Continuing-education-aligned curriculum standards",
        ],
    },
]


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


def services(request):
    """Public services overview — no login required."""
    return render(request, "core/services.html", {"service_groups": SERVICE_GROUPS})
