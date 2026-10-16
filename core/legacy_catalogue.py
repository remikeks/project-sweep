"""Stable destinations for retired Render-era catalogue URLs.

These records are intentionally redirects, not aliases for active courses.
Learner progress and credentials remain historical records and are never moved
to a current course merely because a browser follows one of these links.
"""

RENDER_ARCHIVE_PATH = "/archive/render/"

LEGACY_SCHOOL_REDIRECTS = {
    "foundation-of-social-work": RENDER_ARCHIVE_PATH,
    "professional-practice": RENDER_ARCHIVE_PATH,
    "environmental-and-climate-social-work": "/schools/school-of-disaster-response-crisis-intervention/",
    "child-and-family-wellbeing": "/schools/school-of-child-family-welfare/",
    "mental-health-and-psychosocial-support": "/schools/school-of-mental-health-clinical-practice/",
    "humanitarian-action": "/schools/school-of-disaster-response-crisis-intervention/",
    "governance-policy-and-advocacy": "/schools/school-of-social-policy-advocacy/",
    "digital-social-work": "/schools/school-of-community-macro-practice/",
    "leadership-and-management": "/schools/school-of-community-macro-practice/",
    "research-and-innovation": "/schools/school-of-community-macro-practice/",
}

LEGACY_COURSE_REDIRECTS = {
    "introduction-to-social-work": RENDER_ARCHIVE_PATH,
}

RETIRED_RENDER_SCHOOLS = (
    "Child and Family Wellbeing",
    "Digital Social Work",
    "Environmental and Climate Social Work",
    "Foundation of Social Work",
    "Governance Policy and Advocacy",
    "Humanitarian Action",
    "Leadership and Management",
    "Mental Health and Psychosocial Support",
    "Professional Practice",
    "Research and Innovation",
)
