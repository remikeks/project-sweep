"""Curated, non-credit starting material shared by every SWEEP learner.

This deliberately condenses the archived Render Foundation of Social Work
course. It is not represented by a School or Course model so it cannot create
a second catalogue, assessment attempt, badge, or certificate.
"""


ORIENTATION_MODULES = (
    {
        "title": "Welcome to SWEEP and intentional learning",
        "duration": "About 5 minutes including reflection",
        "summary": (
            "Understand how to use self-paced learning responsibly, set a practical "
            "learning goal, and choose support when a topic exceeds your current role."
        ),
        "focus": (
            "Learning expectations, reflective practice, boundaries of competence, "
            "and a simple personal learning plan."
        ),
        "lesson": (
            "Start with a question you want to handle more thoughtfully in your current role. "
            "Turn it into a learning goal you can observe, such as explaining an access barrier "
            "or preparing questions for supervision. A goal to understand a topic is different "
            "from permission to perform a specialist task.",
            "Read the learning outcome before you enrol. Work through the lessons, try the "
            "activities and use feedback to revise your reasoning. Keep learning notes free of "
            "names and identifying case details. If a scenario raises an urgent concern, use "
            "the approved local route rather than waiting to finish the course.",
            "A SWEEP learning badge or certificate records the platform's stated learning "
            "achievement. It does not by itself grant professional registration, clinical "
            "authority or permission to work beyond your competence. Check the requirements "
            "for your role with your employer, supervisor or relevant professional body.",
        ),
        "activity": "Write one learning goal and one task you would still need supervision or authorisation to undertake.",
    },
    {
        "title": "The social-work lens",
        "duration": "About 5 minutes including reflection",
        "summary": (
            "Meet the profession's purpose, person-in-environment perspective, human "
            "dignity, social justice, and the difference between professional practice "
            "and informal helping."
        ),
        "focus": (
            "Values, human rights, ethical judgement, roles, and referral or supervision "
            "when a learner is not prepared to act alone."
        ),
        "lesson": (
            "A person-in-environment perspective considers the relationship between an "
            "individual's circumstances and the settings around them. When someone misses "
            "an appointment, ask about transport, cost, communication and the usefulness of "
            "the service before assuming a lack of motivation. Also ask about strengths, "
            "relationships and resources the person wants to draw on.",
            "Dignity and participation mean listening to how people describe their situation "
            "and explaining choices in understandable language. Confidentiality calls for "
            "careful information handling, with limits determined by applicable law and "
            "professional duties. Do not promise absolute secrecy or invent a universal "
            "reporting rule. Seek local advice when duties are unclear.",
            "For a fictional example, a resident cannot attend a daytime meeting. A "
            "respectful response explores their preferences and access needs, then considers "
            "a suitable alternative within the service's authority. This illustrates an "
            "ethical reasoning process; it is not a prescribed intervention for every case.",
        ),
        "activity": "For the missed-appointment example, name two explanations to check and a respectful question you could ask.",
    },
    {
        "title": "Choose a pathway and keep growing",
        "duration": "About 5 minutes including reflection",
        "summary": (
            "Identify the School most relevant to your current role or interest and make "
            "a realistic next-step plan for learning, wellbeing, and professional development."
        ),
        "focus": (
            "The ten Schools, specialist practice pathways, reflective self-care, and a "
            "first-course decision."
        ),
        "lesson": (
            "Choose a School by the capability you need, then compare course outcomes "
            "before enrolling. Related titles can address different levels of practice: "
            "supporting an individual, coordinating a service and influencing policy are "
            "not interchangeable. Begin with a course that fits your present role and "
            "read any stated limits or prerequisites.",
            "Make a small learning plan: identify the course, set a realistic study "
            "schedule, choose an activity that does not expose private information and "
            "decide how you will discuss uncertainty. After studying, record what you "
            "would do differently and what still needs supervision or local verification.",
            "Earlier Render materials are preserved as archive references. Historical "
            "completion does not automatically count as completion of a revised Vercel "
            "course. The shared orientation creates no enrolment, assessment or credential; "
            "continue to the live catalogue for the learning paths currently available.",
        ),
        "activity": "Select one current course and write a practical next step, a review date and a person or approved resource you can consult.",
    },
)


ORIENTATION_PROMPTS = (
    "What is one learning goal that matters in your present role or community?",
    "Which ethical value should guide how you pursue that goal?",
    "Which SWEEP School is the best next place to build that capability?",
)
