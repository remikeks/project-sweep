from django.shortcuts import render

from courses.models import Course
from schools.models import School

from .models import Resource, TeamMember

# Cap on how many courses the landing-page carousel pulls in, even once the
# catalog grows well past its current single course.
FEATURED_COURSE_LIMIT = 8

# Full service catalog for the public "Services" page, drawn from the
# "Education, Enterprise and Professional Development Academy" positioning
# document. Categories are intentionally kept as A-O to match that source
# document's lettering.
SERVICE_GROUPS = [
    {
        "title": "A. Education and Professional Development",
        "items": [
            "Online professional certificate courses",
            "Continuing Professional Development (CPD)",
            "Diploma programmes",
            "Executive education",
            "Professional short courses",
            "Micro-credential programmes",
            "Digital badges",
            "Refresher courses",
            "Specialist certification programmes",
            "Master's preparation courses",
        ],
    },
    {
        "title": "B. Employability and Career Services",
        "items": [
            "Career coaching",
            "CV and résumé writing",
            "LinkedIn profile development",
            "Interview preparation",
            "Job readiness training",
            "Internship placement",
            "Apprenticeship placement",
            "Graduate employability bootcamps",
            "Career mentoring",
            "Job matching and recruitment",
        ],
    },
    {
        "title": "C. Enterprise and Entrepreneurship",
        "items": [
            "Social enterprise development",
            "Entrepreneurship training",
            "Business incubation",
            "Business acceleration",
            "Startup mentoring",
            "Business registration support",
            "Business model development",
            "Social innovation laboratory",
            "Enterprise coaching",
            "Freelancing skills development",
        ],
    },
    {
        "title": "D. Consultancy Services",
        "items": [
            "Social work consultancy",
            "Organisational development",
            "Policy development",
            "Strategic planning",
            "Curriculum development",
            "Project design",
            "Programme evaluation",
            "Monitoring and Evaluation (M&E)",
            "Needs assessments",
            "Social impact assessments",
        ],
    },
    {
        "title": "E. Research and Innovation",
        "items": [
            "Research consultancy",
            "Research methodology training",
            "Data collection",
            "Data analysis",
            "Academic writing support",
            "Journal publication mentoring",
            "Grant proposal writing",
            "Research ethics training",
            "Knowledge management",
            "Innovation research",
        ],
    },
    {
        "title": "F. Humanitarian and Community Development",
        "items": [
            "Humanitarian response training",
            "Disaster risk reduction",
            "Emergency response coordination",
            "Community mobilisation",
            "Livelihood restoration",
            "Child protection programming",
            "Gender-based violence response",
            "Peacebuilding",
            "Community resilience programmes",
            "Climate adaptation initiatives",
        ],
    },
    {
        "title": "G. Digital Learning Services",
        "items": [
            "E-learning platform",
            "Virtual classrooms",
            "Webinar hosting",
            "Learning Management System (LMS)",
            "Mobile learning",
            "AI-powered learning support",
            "Digital resource library",
            "Online examinations",
            "Digital certification",
            "Student learning analytics",
        ],
    },
    {
        "title": "H. Professional Practice Support",
        "items": [
            "Clinical supervision",
            "Fieldwork supervision",
            "Practice mentoring",
            "Professional licensing preparation",
            "Case management training",
            "Ethics and professional conduct training",
            "Supervised practice programmes",
            "Professional networking",
            "Communities of practice",
            "Alumni engagement",
        ],
    },
    {
        "title": "I. Leadership and Governance",
        "items": [
            "Leadership development",
            "Executive coaching",
            "Board governance training",
            "NGO management",
            "Public sector leadership",
            "Change management",
            "Conflict resolution",
            "Negotiation skills",
            "Advocacy and lobbying",
            "Public policy leadership",
        ],
    },
    {
        "title": "J. Mental Health and Well-being",
        "items": [
            "Mental health literacy",
            "Psychological first aid",
            "Trauma-informed care",
            "Employee wellness programmes",
            "Burnout prevention",
            "Eco-anxiety management",
            "Stress management",
            "Peer support facilitation",
            "Emotional resilience training",
            "Workplace well-being programmes",
        ],
    },
    {
        "title": "K. Environment and Sustainability",
        "items": [
            "Green social work",
            "Climate change education",
            "ESG awareness training",
            "Environmental justice",
            "Sustainability reporting",
            "Community environmental management",
            "Circular economy education",
            "Disaster resilience planning",
            "Climate adaptation planning",
            "Environmental advocacy",
        ],
    },
    {
        "title": "L. Conferences and Events",
        "items": [
            "Professional conferences",
            "Academic conferences",
            "Annual SWEEP Summit",
            "Workshops",
            "Seminars",
            "Symposia",
            "Masterclasses",
            "Public lectures",
            "Professional networking events",
            "Innovation competitions",
        ],
    },
    {
        "title": "M. Publishing and Knowledge Services",
        "items": [
            "Academic publishing",
            "Books and manuals",
            "Professional journals",
            "Policy briefs",
            "Technical reports",
            "Practice guidelines",
            "Toolkits",
            "Newsletters",
            "Research repositories",
            "Educational multimedia content",
        ],
    },
    {
        "title": "N. Youth and Workforce Development",
        "items": [
            "Youth empowerment",
            "Skills acquisition programmes",
            "Graduate transition programmes",
            "Employability assessments",
            "Workforce development",
            "Labour market intelligence",
            "Employer engagement",
            "Placement partnerships",
            "Career fairs",
            "Talent development programmes",
        ],
    },
    {
        "title": "O. Specialised Social Work Practice Areas",
        "items": [
            "Medical social work",
            "School social work",
            "Correctional social work",
            "Family and child welfare",
            "Gerontological social work",
            "Disability and inclusion services",
            "Substance use intervention",
            "Palliative and hospice social work",
            "Refugee and migration services",
            "Occupational and industrial social work",
        ],
    },
]


HOME_SCHOOL_LIMIT = 10


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
    context = {
        "schools": schools[:HOME_SCHOOL_LIMIT],
        "stats": stats,
        "featured_courses": featured_courses,
    }
    return render(request, "core/home.html", context)


def services(request):
    """Public services overview — no login required."""
    total_services = sum(len(group["items"]) for group in SERVICE_GROUPS)
    context = {
        "service_groups": SERVICE_GROUPS,
        "total_services": total_services,
    }
    return render(request, "core/services.html", context)


def about(request):
    """Public 'About' page — no login required."""
    stats = {
        "school_count": School.objects.filter(is_active=True).count(),
        "course_count": Course.objects.filter(is_active=True).count(),
    }
    return render(request, "core/about.html", {"stats": stats})


def team(request):
    """Public 'Our Team' page — no login required."""
    members = TeamMember.objects.filter(is_active=True)
    return render(request, "core/team.html", {"members": members})


def resources(request):
    """Public 'Resources' page — free downloadable guides and toolkits, no login required."""
    resource_list = Resource.objects.filter(is_active=True)
    return render(request, "core/resources.html", {"resources": resource_list})
