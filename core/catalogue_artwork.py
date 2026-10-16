"""Stable artwork identities, independent of database IDs and school ordering."""

SCHOOL_ARTWORK = {
    "school-of-child-family-welfare": "family",
    "school-of-mental-health-clinical-practice": "mental-health",
    "school-of-substance-use-addiction-recovery": "recovery",
    "school-of-gerontology-aging-services": "ageing",
    "school-of-community-macro-practice": "community",
    "school-of-medical-health-social-work": "health",
    "school-of-school-social-work": "education",
    "school-of-criminal-justice-forensic-social-work": "justice",
    "school-of-disaster-response-crisis-intervention": "disaster",
    "school-of-social-policy-advocacy": "policy",
}


def school_artwork_path(slug, width=960):
    key = SCHOOL_ARTWORK.get(slug, "community")
    return f"img/catalogue/{key}-{width}.webp"
