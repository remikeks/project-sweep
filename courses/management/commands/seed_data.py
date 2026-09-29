from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Choice, Course, CourseModule, Question
from schools.models import School, SchoolExamChoice, SchoolExamQuestion

SCHOOLS = [
    {
        "name": "School of Child & Family Welfare",
        "tagline": "Protecting children and strengthening families",
        "description": "Core practice skills for child protection, family preservation, "
        "kinship care, and permanency planning.",
        "courses": [
            {
                "title": "Foundations of Child Protection",
                "summary": "Recognizing abuse and neglect and understanding mandated reporting.",
                "difficulty": "beginner",
                "estimated_minutes": 45,
                "content": "This course introduces the legal and ethical framework for child "
                "protection work. You'll learn to recognize the signs of physical, emotional, "
                "and sexual abuse and neglect, understand mandated reporter obligations, and "
                "apply a trauma-informed lens from the very first contact with a family.",
                "questions": [
                    {
                        "text": "A mandated reporter who suspects child abuse should:",
                        "choices": [
                            ("Report it to the appropriate child protection authority", True),
                            ("Wait until they have absolute proof", False),
                            ("Only report if a colleague agrees", False),
                            ("Confront the caregiver directly first", False),
                        ],
                    },
                    {
                        "text": "Trauma-informed practice with families primarily emphasizes:",
                        "choices": [
                            ("Punitive case management", False),
                            ("Safety, trust, and collaboration", True),
                            ("Removing children in all cases", False),
                            ("Avoiding contact with caregivers", False),
                        ],
                    },
                ],
            },
            {
                "title": "Family Preservation & Kinship Care",
                "summary": "Keeping families together safely through in-home services.",
                "difficulty": "intermediate",
                "estimated_minutes": 60,
                "content": "Explore evidence-based family preservation models, safety planning, "
                "and how to assess and support kinship caregivers as a first placement option "
                "when children cannot safely remain with parents.",
                "questions": [
                    {
                        "text": "Kinship care is generally prioritized because it:",
                        "choices": [
                            ("Maintains family and cultural connections", True),
                            ("Is always the cheapest placement option", False),
                            ("Requires no assessment", False),
                            ("Avoids court oversight", False),
                        ],
                    },
                    {
                        "text": "A core goal of family preservation services is to:",
                        "choices": [
                            ("Reduce unnecessary removals through in-home support", True),
                            ("Replace foster care entirely", False),
                            ("Eliminate the need for safety plans", False),
                            ("Remove parental rights faster", False),
                        ],
                    },
                ],
            },
            {
                "title": "Permanency Planning & Reunification",
                "summary": "Guiding families toward safe, lasting permanency outcomes.",
                "difficulty": "advanced",
                "estimated_minutes": 75,
                "content": "This advanced course covers concurrent planning, reunification "
                "readiness assessment, and how to navigate adoption or guardianship when "
                "reunification is not viable, always centering the child's need for stability.",
                "questions": [
                    {
                        "text": "Concurrent planning means a caseworker:",
                        "choices": [
                            ("Works reunification and an alternative permanency plan at once", True),
                            ("Only plans for adoption", False),
                            ("Delays all planning until year two", False),
                            ("Ends services once a plan is chosen", False),
                        ],
                    },
                    {
                        "text": "The primary consideration in permanency planning is:",
                        "choices": [
                            ("The child's safety, well-being, and timely stability", True),
                            ("Agency caseload balance", False),
                            ("Parental convenience", False),
                            ("Court scheduling only", False),
                        ],
                    },
                ],
            },
        ],
        "exam_questions": [
            {
                "text": "The single most important priority across all child welfare decisions is:",
                "choices": [
                    ("The safety and well-being of the child", True),
                    ("Minimizing agency paperwork", False),
                    ("Speed of case closure", False),
                    ("Caregiver preference alone", False),
                ],
            },
            {
                "text": "Kinship care is prioritized over non-relative foster care primarily because it:",
                "choices": [
                    ("Preserves family and cultural ties", True),
                    ("Is legally required in all cases", False),
                    ("Never requires licensing", False),
                    ("Is always short-term", False),
                ],
            },
            {
                "text": "Reunification services should be paired with:",
                "choices": [
                    ("An alternative permanency plan (concurrent planning)", True),
                    ("No monitoring at all", False),
                    ("Immediate case closure", False),
                    ("Termination of all parental contact", False),
                ],
            },
        ],
    },
    {
        "name": "School of Mental Health & Clinical Practice",
        "tagline": "Evidence-based clinical care across the lifespan",
        "description": "Assessment, diagnosis, and intervention skills for clinical social "
        "work practice, from CBT foundations to crisis stabilization.",
        "courses": [
            {
                "title": "Biopsychosocial Assessment",
                "summary": "Conducting a whole-person clinical intake.",
                "difficulty": "beginner",
                "estimated_minutes": 50,
                "content": "Learn to structure a comprehensive biopsychosocial assessment, "
                "integrating biological, psychological, and social factors to build an "
                "accurate clinical picture and a collaborative treatment plan.",
                "questions": [
                    {
                        "text": "A biopsychosocial assessment integrates:",
                        "choices": [
                            ("Biological, psychological, and social factors", True),
                            ("Only medication history", False),
                            ("Only family history", False),
                            ("Only the presenting complaint", False),
                        ],
                    },
                    {
                        "text": "Which is a key purpose of a clinical intake?",
                        "choices": [
                            ("Building a collaborative treatment plan", True),
                            ("Assigning a diagnosis before meeting the client", False),
                            ("Skipping risk assessment to save time", False),
                            ("Avoiding client input", False),
                        ],
                    },
                ],
            },
            {
                "title": "Cognitive Behavioral Therapy Foundations",
                "summary": "Core CBT techniques for common presenting problems.",
                "difficulty": "intermediate",
                "estimated_minutes": 65,
                "content": "This course covers the cognitive triangle, thought records, "
                "behavioral activation, and how to structure a CBT session from agenda-setting "
                "to homework review.",
                "questions": [
                    {
                        "text": "The cognitive triangle links thoughts, feelings, and:",
                        "choices": [
                            ("Behaviors", True),
                            ("Medications", False),
                            ("Diagnoses", False),
                            ("Insurance codes", False),
                        ],
                    },
                    {
                        "text": "Behavioral activation is most associated with treating:",
                        "choices": [
                            ("Depression", True),
                            ("A broken bone", False),
                            ("Hypertension", False),
                            ("Seasonal allergies", False),
                        ],
                    },
                ],
            },
            {
                "title": "Crisis Stabilization & Safety Planning",
                "summary": "Responding to acute mental health crises.",
                "difficulty": "advanced",
                "estimated_minutes": 70,
                "content": "Covers suicide risk assessment, de-escalation techniques, and "
                "collaborative safety planning to stabilize clients in acute distress and "
                "connect them to an appropriate level of ongoing care.",
                "questions": [
                    {
                        "text": "A collaborative safety plan is developed:",
                        "choices": [
                            ("With the client, not imposed on them", True),
                            ("Only by the psychiatrist", False),
                            ("Without the client's knowledge", False),
                            ("Only after discharge", False),
                        ],
                    },
                    {
                        "text": "De-escalation techniques primarily aim to:",
                        "choices": [
                            ("Reduce immediate distress and risk", True),
                            ("End the session as quickly as possible", False),
                            ("Avoid asking about safety", False),
                            ("Replace all future treatment", False),
                        ],
                    },
                ],
            },
        ],
        "exam_questions": [
            {
                "text": "A biopsychosocial assessment is valuable because it:",
                "choices": [
                    ("Captures the whole person, not just symptoms", True),
                    ("Only tracks medication compliance", False),
                    ("Replaces the need for rapport", False),
                    ("Is only used once per client, ever", False),
                ],
            },
            {
                "text": "In CBT, thought records help clients:",
                "choices": [
                    ("Identify and test automatic thoughts", True),
                    ("Memorize diagnostic codes", False),
                    ("Avoid discussing emotions", False),
                    ("Schedule medication refills", False),
                ],
            },
            {
                "text": "Safety planning after a crisis should be:",
                "choices": [
                    ("Collaborative and specific to the client", True),
                    ("Generic and copied for every client", False),
                    ("Kept secret from the client", False),
                    ("Skipped if the client seems calm", False),
                ],
            },
        ],
    },
    {
        "name": "School of Substance Use & Addiction Recovery",
        "tagline": "Harm reduction, treatment, and recovery support",
        "description": "Screening, motivational interviewing, and recovery-oriented practice "
        "for substance use disorders.",
        "courses": [
            {
                "title": "Screening & Brief Intervention (SBIRT)",
                "summary": "Identifying risky substance use in everyday practice.",
                "difficulty": "beginner",
                "estimated_minutes": 40,
                "content": "SBIRT — Screening, Brief Intervention, and Referral to Treatment — "
                "equips practitioners to identify risky substance use early and intervene "
                "before it escalates into a diagnosable disorder.",
                "questions": [
                    {
                        "text": "SBIRT stands for:",
                        "choices": [
                            ("Screening, Brief Intervention, Referral to Treatment", True),
                            ("Substance Behavior Inpatient Recovery Team", False),
                            ("Standard Brief Intake Report Tool", False),
                            ("Social Behavioral Intervention Response Team", False),
                        ],
                    },
                    {
                        "text": "A brief intervention is best delivered:",
                        "choices": [
                            ("As soon as risky use is identified", True),
                            ("Only after a formal diagnosis", False),
                            ("Only in inpatient settings", False),
                            ("Only to court-mandated clients", False),
                        ],
                    },
                ],
            },
            {
                "title": "Motivational Interviewing",
                "summary": "Building intrinsic motivation for behavior change.",
                "difficulty": "intermediate",
                "estimated_minutes": 55,
                "content": "Learn the spirit and core skills of motivational interviewing — "
                "open questions, affirmations, reflections, and summaries (OARS) — to help "
                "clients resolve ambivalence about change.",
                "questions": [
                    {
                        "text": "OARS refers to:",
                        "choices": [
                            ("Open questions, Affirmations, Reflections, Summaries", True),
                            ("Outcomes, Assessment, Referral, Support", False),
                            ("Only reflective listening", False),
                            ("A medication protocol", False),
                        ],
                    },
                    {
                        "text": "Motivational interviewing works best when the practitioner:",
                        "choices": [
                            ("Rolls with resistance rather than arguing", True),
                            ("Insists the client is wrong", False),
                            ("Sets the client's goals for them", False),
                            ("Avoids asking open questions", False),
                        ],
                    },
                ],
            },
            {
                "title": "Recovery-Oriented Systems of Care",
                "summary": "Designing long-term, strengths-based recovery support.",
                "difficulty": "advanced",
                "estimated_minutes": 65,
                "content": "This course explores recovery capital, peer support models, and "
                "how to coordinate care across housing, employment, and clinical services to "
                "sustain long-term recovery.",
                "questions": [
                    {
                        "text": "\"Recovery capital\" refers to:",
                        "choices": [
                            ("Internal and external resources supporting recovery", True),
                            ("A client's bank balance only", False),
                            ("The cost of treatment", False),
                            ("A type of medication", False),
                        ],
                    },
                    {
                        "text": "Peer support specialists primarily contribute:",
                        "choices": [
                            ("Lived experience and recovery mentorship", True),
                            ("Medical diagnoses", False),
                            ("Legal representation", False),
                            ("Prescription authority", False),
                        ],
                    },
                ],
            },
        ],
        "exam_questions": [
            {
                "text": "SBIRT is designed to intervene:",
                "choices": [
                    ("Early, before risky use becomes a disorder", True),
                    ("Only after multiple relapses", False),
                    ("Only in the emergency room", False),
                    ("Only for adolescents", False),
                ],
            },
            {
                "text": "The spirit of motivational interviewing is best described as:",
                "choices": [
                    ("Collaborative and client-centered", True),
                    ("Confrontational", False),
                    ("Directive and prescriptive", False),
                    ("Purely educational", False),
                ],
            },
            {
                "text": "A recovery-oriented system of care coordinates:",
                "choices": [
                    ("Housing, employment, and clinical supports together", True),
                    ("Only detox services", False),
                    ("Only one provider for life", False),
                    ("Nothing beyond medication", False),
                ],
            },
        ],
    },
    {
        "name": "School of Gerontology & Aging Services",
        "tagline": "Supporting dignity and independence in later life",
        "description": "Practice with older adults across care settings, from independent "
        "living to long-term care.",
        "courses": [
            {
                "title": "Aging in Place & Independent Living",
                "summary": "Supporting older adults to remain safely at home.",
                "difficulty": "beginner",
                "estimated_minutes": 40,
                "content": "Covers home safety assessment, community-based supports, and "
                "care coordination that allow older adults to age in place with dignity.",
                "questions": [
                    {
                        "text": "\"Aging in place\" refers to:",
                        "choices": [
                            ("Remaining safely in one's own home and community", True),
                            ("Mandatory relocation to a nursing home", False),
                            ("Living only in assisted living", False),
                            ("A hospital discharge policy", False),
                        ],
                    },
                    {
                        "text": "A home safety assessment typically evaluates:",
                        "choices": [
                            ("Fall risks and accessibility barriers", True),
                            ("Only financial assets", False),
                            ("Only medication brand names", False),
                            ("Neighborhood property values", False),
                        ],
                    },
                ],
            },
            {
                "title": "Dementia Care & Caregiver Support",
                "summary": "Person-centered approaches to dementia care.",
                "difficulty": "intermediate",
                "estimated_minutes": 55,
                "content": "Explores person-centered dementia care, communication strategies "
                "for cognitive decline, and how to prevent caregiver burnout through respite "
                "and support services.",
                "questions": [
                    {
                        "text": "Person-centered dementia care focuses on:",
                        "choices": [
                            ("The individual's history, preferences, and remaining strengths", True),
                            ("Only managing behaviors with medication", False),
                            ("Standardizing care regardless of the person", False),
                            ("Limiting family involvement", False),
                        ],
                    },
                    {
                        "text": "Caregiver burnout is best addressed through:", 
                        "choices": [
                            ("Respite care and support services", True),
                            ("Ignoring caregiver needs", False),
                            ("Removing all support services", False),
                            ("Increasing caregiver isolation", False),
                        ],
                    },
                ],
            },
            {
                "title": "Elder Abuse Prevention & Long-Term Care Advocacy",
                "summary": "Protecting vulnerable older adults in all care settings.",
                "difficulty": "advanced",
                "estimated_minutes": 60,
                "content": "This course covers recognizing financial exploitation, neglect, "
                "and abuse of older adults, mandatory reporting duties, and how to advocate "
                "within long-term care systems.",
                "questions": [
                    {
                        "text": "Financial exploitation of an older adult is a form of:",
                        "choices": [
                            ("Elder abuse", True),
                            ("Standard estate planning", False),
                            ("Tax preparation", False),
                            ("Retirement counseling", False),
                        ],
                    },
                    {
                        "text": "Suspected elder abuse in a care facility should be:",
                        "choices": [
                            ("Reported to the appropriate protective services agency", True),
                            ("Handled only informally with the facility", False),
                            ("Ignored if the resident seems content", False),
                            ("Reported only if a family member insists", False),
                        ],
                    },
                ],
            },
        ],
        "exam_questions": [
            {
                "text": "Aging-in-place support is most effective when it:",
                "choices": [
                    ("Combines home safety, community services, and care coordination", True),
                    ("Relies on relocation alone", False),
                    ("Ignores home hazards", False),
                    ("Excludes family caregivers", False),
                ],
            },
            {
                "text": "Person-centered dementia care means:",
                "choices": [
                    ("Tailoring care to the individual's history and preferences", True),
                    ("Using one standard protocol for everyone", False),
                    ("Prioritizing medication over relationship", False),
                    ("Excluding the person from decisions entirely", False),
                ],
            },
            {
                "text": "Suspected elder abuse should always be:",
                "choices": [
                    ("Reported through mandated channels", True),
                    ("Kept confidential from authorities", False),
                    ("Resolved without documentation", False),
                    ("Left to the family to handle alone", False),
                ],
            },
        ],
    },
    {
        "name": "School of Community & Macro Practice",
        "tagline": "Organizing for systemic, community-level change",
        "description": "Community organizing, coalition building, and program development "
        "for macro-level social work practice.",
        "courses": [
            {
                "title": "Community Needs Assessment",
                "summary": "Mapping community assets and identifying priority needs.",
                "difficulty": "beginner",
                "estimated_minutes": 45,
                "content": "Learn to conduct a community needs assessment using both asset "
                "mapping and gap analysis to identify priorities that reflect the community's "
                "own voice.",
                "questions": [
                    {
                        "text": "Asset mapping identifies:",
                        "choices": [
                            ("Existing community strengths and resources", True),
                            ("Only problems and deficits", False),
                            ("Only government funding sources", False),
                            ("Individual client diagnoses", False),
                        ],
                    },
                    {
                        "text": "A strong needs assessment centers:",
                        "choices": [
                            ("The community's own voice and priorities", True),
                            ("The funder's preferences only", False),
                            ("A single expert's opinion", False),
                            ("National statistics exclusively", False),
                        ],
                    },
                ],
            },
            {
                "title": "Community Organizing & Coalition Building",
                "summary": "Mobilizing residents and partners around shared goals.",
                "difficulty": "intermediate",
                "estimated_minutes": 55,
                "content": "This course covers grassroots organizing strategies, building "
                "durable coalitions across organizations, and sustaining resident leadership "
                "over time.",
                "questions": [
                    {
                        "text": "Effective community organizing builds power primarily through:",
                        "choices": [
                            ("Relationships and collective action", True),
                            ("Top-down mandates", False),
                            ("A single charismatic leader acting alone", False),
                            ("Avoiding resident involvement", False),
                        ],
                    },
                    {
                        "text": "A coalition is most sustainable when:",
                        "choices": [
                            ("Partners share ownership of goals and decisions", True),
                            ("One organization controls everything", False),
                            ("Members never meet in person", False),
                            ("Goals are kept vague indefinitely", False),
                        ],
                    },
                ],
            },
            {
                "title": "Program Development & Evaluation",
                "summary": "Designing and evaluating community-level interventions.",
                "difficulty": "advanced",
                "estimated_minutes": 65,
                "content": "Covers logic models, theory of change, and how to design outcome "
                "evaluations that show whether a community program is achieving its goals.",
                "questions": [
                    {
                        "text": "A logic model primarily maps:",
                        "choices": [
                            ("Inputs, activities, outputs, and outcomes", True),
                            ("Only a program's budget", False),
                            ("Staff vacation schedules", False),
                            ("Office floor plans", False),
                        ],
                    },
                    {
                        "text": "Outcome evaluation is used to determine:",
                        "choices": [
                            ("Whether a program achieved its intended results", True),
                            ("How attractive the program's logo is", False),
                            ("Staff seniority", False),
                            ("Office rental costs", False),
                        ],
                    },
                ],
            },
        ],
        "exam_questions": [
            {
                "text": "A community needs assessment should be grounded in:",
                "choices": [
                    ("Both community assets and identified gaps", True),
                    ("Funder assumptions alone", False),
                    ("A single household survey", False),
                    ("National averages only", False),
                ],
            },
            {
                "text": "Durable coalitions are built on:",
                "choices": [
                    ("Shared ownership among partner organizations", True),
                    ("One dominant organization's control", False),
                    ("Infrequent, informal contact", False),
                    ("Avoiding conflict resolution entirely", False),
                ],
            },
            {
                "text": "A logic model is most useful for:",
                "choices": [
                    ("Clarifying how activities lead to intended outcomes", True),
                    ("Setting individual client goals", False),
                    ("Replacing the need for evaluation", False),
                    ("Managing payroll", False),
                ],
            },
        ],
    },
    {
        "name": "School of Medical & Health Social Work",
        "tagline": "Bridging social care and the healthcare system",
        "description": "Hospital discharge planning, chronic illness support, and "
        "interdisciplinary collaboration in medical settings.",
        "courses": [
            {
                "title": "Hospital Discharge Planning",
                "summary": "Coordinating safe transitions from hospital to home.",
                "difficulty": "beginner",
                "estimated_minutes": 40,
                "content": "This course covers discharge readiness assessment, coordinating "
                "home health and equipment needs, and preventing avoidable hospital "
                "readmissions.",
                "questions": [
                    {
                        "text": "Discharge planning should ideally begin:",
                        "choices": [
                            ("At or soon after admission", True),
                            ("Only the day of discharge", False),
                            ("After the patient has already left", False),
                            ("Only if the family requests it", False),
                        ],
                    },
                    {
                        "text": "A key goal of discharge planning is to:",
                        "choices": [
                            ("Reduce avoidable readmissions", True),
                            ("Discharge patients as fast as possible regardless of safety", False),
                            ("Avoid involving the patient's family", False),
                            ("Skip home safety considerations", False),
                        ],
                    },
                ],
            },
            {
                "title": "Chronic Illness & Adherence Support",
                "summary": "Helping patients manage long-term health conditions.",
                "difficulty": "intermediate",
                "estimated_minutes": 55,
                "content": "Explores the social and psychological barriers to treatment "
                "adherence in chronic illness, and practical strategies to support patients "
                "managing conditions like diabetes or heart disease.",
                "questions": [
                    {
                        "text": "Common barriers to treatment adherence include:",
                        "choices": [
                            ("Cost, health literacy, and competing life demands", True),
                            ("Only forgetfulness", False),
                            ("Only lack of willpower", False),
                            ("Nothing — adherence is always straightforward", False),
                        ],
                    },
                    {
                        "text": "Supporting adherence works best when it is:",
                        "choices": [
                            ("Individualized to the patient's circumstances", True),
                            ("The same rigid plan for every patient", False),
                            ("Focused only on scolding the patient", False),
                            ("Delivered without patient input", False),
                        ],
                    },
                ],
            },
            {
                "title": "Interdisciplinary Collaboration in Healthcare",
                "summary": "Working effectively within medical care teams.",
                "difficulty": "advanced",
                "estimated_minutes": 60,
                "content": "Covers the social worker's role on interdisciplinary care teams, "
                "communicating psychosocial assessments to medical staff, and navigating "
                "shared decision-making in complex cases.",
                "questions": [
                    {
                        "text": "On an interdisciplinary team, the social worker typically contributes:",
                        "choices": [
                            ("Psychosocial assessment and resource coordination", True),
                            ("Prescribing medication", False),
                            ("Performing surgery", False),
                            ("Reading diagnostic imaging", False),
                        ],
                    },
                    {
                        "text": "Effective interdisciplinary collaboration relies on:",
                        "choices": [
                            ("Clear communication across disciplines", True),
                            ("Each discipline working in isolation", False),
                            ("Avoiding case conferences", False),
                            ("One discipline overriding all others", False),
                        ],
                    },
                ],
            },
        ],
        "exam_questions": [
            {
                "text": "Discharge planning is most effective when it starts:",
                "choices": [
                    ("Early in the hospital stay", True),
                    ("Only after discharge", False),
                    ("Only when a bed is needed urgently", False),
                    ("Without patient or family input", False),
                ],
            },
            {
                "text": "Barriers to chronic illness treatment adherence often include:",
                "choices": [
                    ("Cost and health literacy challenges", True),
                    ("Only personal choice", False),
                    ("Nothing significant", False),
                    ("Only provider error", False),
                ],
            },
            {
                "text": "The medical social worker's role on a care team is primarily to:",
                "choices": [
                    ("Address psychosocial needs and coordinate resources", True),
                    ("Replace the physician", False),
                    ("Manage hospital billing exclusively", False),
                    ("Order lab tests", False),
                ],
            },
        ],
    },
    {
        "name": "School of School Social Work",
        "tagline": "Supporting students, families, and school systems",
        "description": "Practice within K-12 education settings, from individual student "
        "support to whole-school systems change.",
        "courses": [
            {
                "title": "Student Support & Attendance",
                "summary": "Addressing chronic absenteeism and student barriers to learning.",
                "difficulty": "beginner",
                "estimated_minutes": 40,
                "content": "Covers root-cause approaches to chronic absenteeism, "
                "family engagement strategies, and connecting students to needed resources "
                "inside and outside the school.",
                "questions": [
                    {
                        "text": "Chronic absenteeism is best addressed by:",
                        "choices": [
                            ("Identifying and addressing root causes", True),
                            ("Punishing students immediately", False),
                            ("Ignoring the pattern", False),
                            ("Suspending attendance tracking", False),
                        ],
                    },
                    {
                        "text": "Family engagement in school social work should be:",
                        "choices": [
                            ("Collaborative and respectful of family circumstances", True),
                            ("Avoided entirely", False),
                            ("One-directional, school to family only", False),
                            ("Limited to disciplinary meetings", False),
                        ],
                    },
                ],
            },
            {
                "title": "Behavioral & Emotional Support in Schools",
                "summary": "Trauma-informed behavior support in the classroom.",
                "difficulty": "intermediate",
                "estimated_minutes": 55,
                "content": "Explores tiered behavioral support models, de-escalation in the "
                "classroom, and how trauma affects student behavior and learning.",
                "questions": [
                    {
                        "text": "Tiered support models typically provide:",
                        "choices": [
                            ("Increasingly intensive support based on student need", True),
                            ("The same intervention for every student", False),
                            ("Support only for students with no needs", False),
                            ("No coordination between staff", False),
                        ],
                    },
                    {
                        "text": "A trauma-informed view of disruptive behavior asks first:",
                        "choices": [
                            ("What happened to this student?", True),
                            ("How can we suspend this student fastest?", False),
                            ("Is this student simply bad?", False),
                            ("Can we skip understanding the behavior?", False),
                        ],
                    },
                ],
            },
            {
                "title": "School-Wide Systems & Policy",
                "summary": "Influencing school climate and policy at the systems level.",
                "difficulty": "advanced",
                "estimated_minutes": 60,
                "content": "This course covers school climate assessment, restorative "
                "discipline policy, and how school social workers help shift practices at "
                "the building and district level.",
                "questions": [
                    {
                        "text": "Restorative discipline approaches emphasize:",
                        "choices": [
                            ("Repairing harm and rebuilding relationships", True),
                            ("Exclusion as the first response", False),
                            ("Ignoring the impact of harm", False),
                            ("Removing all accountability", False),
                        ],
                    },
                    {
                        "text": "School climate improvement typically requires:",
                        "choices": [
                            ("Building- and district-level collaboration", True),
                            ("Action from a single teacher only", False),
                            ("No data collection", False),
                            ("Ignoring student and staff input", False),
                        ],
                    },
                ],
            },
        ],
        "exam_questions": [
            {
                "text": "Chronic absenteeism interventions are most effective when they:",
                "choices": [
                    ("Address underlying root causes", True),
                    ("Focus only on punishment", False),
                    ("Ignore family circumstances", False),
                    ("Apply one identical plan to every student", False),
                ],
            },
            {
                "text": "A trauma-informed approach to student behavior starts by asking:",
                "choices": [
                    ("What happened to this student?", True),
                    ("What's wrong with this student?", False),
                    ("How fast can we remove this student?", False),
                    ("Should we skip understanding context?", False),
                ],
            },
            {
                "text": "Restorative discipline practices focus on:",
                "choices": [
                    ("Repairing harm and relationships", True),
                    ("Exclusion as a first resort", False),
                    ("Avoiding accountability altogether", False),
                    ("Ignoring the person harmed", False),
                ],
            },
        ],
    },
    {
        "name": "School of Criminal Justice & Forensic Social Work",
        "tagline": "Practice at the intersection of social work and the justice system",
        "description": "Reentry planning, diversion programs, and trauma-informed practice "
        "within courts and corrections.",
        "courses": [
            {
                "title": "Foundations of Forensic Social Work",
                "summary": "Understanding the social worker's role in justice settings.",
                "difficulty": "beginner",
                "estimated_minutes": 45,
                "content": "Introduces the range of forensic social work roles — from court "
                "liaison to correctional counseling — and the ethical tensions unique to "
                "practicing within justice systems.",
                "questions": [
                    {
                        "text": "Forensic social work is best described as practice:",
                        "choices": [
                            ("At the intersection of social work and the legal system", True),
                            ("Exclusively inside hospitals", False),
                            ("Only with children under 5", False),
                            ("Unrelated to the justice system", False),
                        ],
                    },
                    {
                        "text": "A key ethical tension in forensic settings is balancing:",
                        "choices": [
                            ("Client welfare with public safety and legal mandates", True),
                            ("Nothing — there are no unique tensions", False),
                            ("Only agency convenience", False),
                            ("Only client preference regardless of law", False),
                        ],
                    },
                ],
            },
            {
                "title": "Diversion Programs & Restorative Justice",
                "summary": "Alternatives to incarceration for eligible individuals.",
                "difficulty": "intermediate",
                "estimated_minutes": 55,
                "content": "Covers pretrial diversion, drug courts, and restorative justice "
                "circles as alternatives to traditional incarceration, along with eligibility "
                "and program design considerations.",
                "questions": [
                    {
                        "text": "Diversion programs aim to:",
                        "choices": [
                            ("Redirect eligible individuals away from incarceration", True),
                            ("Increase incarceration rates", False),
                            ("Eliminate all court oversight", False),
                            ("Apply only after conviction", False),
                        ],
                    },
                    {
                        "text": "Restorative justice circles primarily focus on:",
                        "choices": [
                            ("Repairing harm between the affected parties", True),
                            ("Maximizing punishment", False),
                            ("Excluding the victim from the process", False),
                            ("Avoiding any dialogue", False),
                        ],
                    },
                ],
            },
            {
                "title": "Reentry Planning & Community Reintegration",
                "summary": "Supporting successful transitions back into the community.",
                "difficulty": "advanced",
                "estimated_minutes": 65,
                "content": "This course covers reentry planning starting pre-release, "
                "addressing housing and employment barriers, and coordinating community "
                "supervision with social services to reduce recidivism.",
                "questions": [
                    {
                        "text": "Effective reentry planning should ideally begin:",
                        "choices": [
                            ("Before release, not after", True),
                            ("Only after recidivism occurs", False),
                            ("Only when housing is unavailable", False),
                            ("Never — it is not necessary", False),
                        ],
                    },
                    {
                        "text": "A major barrier to successful reentry is often:",
                        "choices": [
                            ("Lack of stable housing and employment", True),
                            ("Excess of community support", False),
                            ("Too much case coordination", False),
                            ("Overly generous reentry funding", False),
                        ],
                    },
                ],
            },
        ],
        "exam_questions": [
            {
                "text": "Forensic social work practice sits at the intersection of:",
                "choices": [
                    ("Social work values and the legal/justice system", True),
                    ("Retail and hospitality", False),
                    ("Only pediatric medicine", False),
                    ("Unrelated academic fields", False),
                ],
            },
            {
                "text": "Diversion programs are designed to:",
                "choices": [
                    ("Redirect eligible people away from incarceration", True),
                    ("Guarantee incarceration", False),
                    ("Bypass all legal oversight", False),
                    ("Apply only post-sentencing", False),
                ],
            },
            {
                "text": "Reentry planning is most effective when it begins:",
                "choices": [
                    ("Prior to release", True),
                    ("Only after multiple rearrests", False),
                    ("On the day of release with no prior planning", False),
                    ("Only if requested by a judge", False),
                ],
            },
        ],
    },
    {
        "name": "School of Disaster Response & Crisis Intervention",
        "tagline": "Rapid, compassionate support in emergencies",
        "description": "Preparedness, psychological first aid, and long-term recovery "
        "support following disasters and mass-casualty events.",
        "courses": [
            {
                "title": "Disaster Preparedness & Response Planning",
                "summary": "Building organizational readiness before disaster strikes.",
                "difficulty": "beginner",
                "estimated_minutes": 40,
                "content": "Covers emergency response planning, coordination with emergency "
                "management agencies, and how social workers fit into the broader disaster "
                "response structure.",
                "questions": [
                    {
                        "text": "Disaster preparedness planning should occur:",
                        "choices": [
                            ("Before a disaster occurs", True),
                            ("Only during the disaster", False),
                            ("Only after recovery is complete", False),
                            ("Never — response can be improvised", False),
                        ],
                    },
                    {
                        "text": "Social workers in disaster response typically coordinate with:",
                        "choices": [
                            ("Emergency management and relief agencies", True),
                            ("No other agencies", False),
                            ("Only private donors", False),
                            ("Only local media", False),
                        ],
                    },
                ],
            },
            {
                "title": "Psychological First Aid",
                "summary": "Immediate, compassionate support after traumatic events.",
                "difficulty": "intermediate",
                "estimated_minutes": 50,
                "content": "This course teaches the core actions of Psychological First Aid: "
                "ensuring safety and comfort, connecting people to information and resources, "
                "and supporting coping without pathologizing normal stress reactions.",
                "questions": [
                    {
                        "text": "Psychological First Aid primarily focuses on:",
                        "choices": [
                            ("Safety, comfort, and connection to resources", True),
                            ("Formal diagnosis on-site", False),
                            ("Long-term psychotherapy", False),
                            ("Avoiding contact with survivors", False),
                        ],
                    },
                    {
                        "text": "A core principle of Psychological First Aid is:", 
                        "choices": [
                            ("Not forcing survivors to talk about the event", True),
                            ("Requiring survivors to recount details immediately", False),
                            ("Diagnosing PTSD on the spot", False),
                            ("Ignoring basic needs like food and shelter", False),
                        ],
                    },
                ],
            },
            {
                "title": "Long-Term Disaster Recovery Support",
                "summary": "Sustaining communities through the long recovery process.",
                "difficulty": "advanced",
                "estimated_minutes": 60,
                "content": "Explores case management for long-term recovery, addressing "
                "unmet needs committees, and supporting community resilience long after the "
                "immediate emergency response ends.",
                "questions": [
                    {
                        "text": "Long-term disaster recovery work continues:",
                        "choices": [
                            ("Well beyond the initial emergency response", True),
                            ("Only for the first 48 hours", False),
                            ("Only until media coverage ends", False),
                            ("Not at all after evacuation", False),
                        ],
                    },
                    {
                        "text": "Unmet needs committees typically help:",
                        "choices": [
                            ("Coordinate resources for survivors' ongoing needs", True),
                            ("Distribute media statements only", False),
                            ("Replace all case management", False),
                            ("Exclude survivor input", False),
                        ],
                    },
                ],
            },
        ],
        "exam_questions": [
            {
                "text": "Disaster preparedness planning should happen:",
                "choices": [
                    ("Before disasters occur, not during", True),
                    ("Only in the middle of a crisis", False),
                    ("Only after full recovery", False),
                    ("Never, since disasters are unpredictable", False),
                ],
            },
            {
                "text": "Psychological First Aid emphasizes:",
                "choices": [
                    ("Safety, comfort, and connecting people to resources", True),
                    ("Immediate formal diagnosis", False),
                    ("Long, unstructured psychotherapy on-site", False),
                    ("Avoiding survivors until later", False),
                ],
            },
            {
                "text": "Long-term recovery support is needed because:",
                "choices": [
                    ("Community needs persist well after the initial response", True),
                    ("Needs disappear once media coverage ends", False),
                    ("Recovery is always complete within 48 hours", False),
                    ("Survivors need no ongoing coordination", False),
                ],
            },
        ],
    },
    {
        "name": "School of Social Policy & Advocacy",
        "tagline": "Shaping the systems that shape people's lives",
        "description": "Policy analysis, legislative advocacy, and using data to drive "
        "systemic change on behalf of the communities social workers serve.",
        "courses": [
            {
                "title": "Policy Analysis Fundamentals",
                "summary": "Breaking down how a policy affects the people it touches.",
                "difficulty": "beginner",
                "estimated_minutes": 45,
                "content": "Learn a structured framework for analyzing social policy: its "
                "goals, target population, funding mechanisms, and the equity implications "
                "of how it's implemented.",
                "questions": [
                    {
                        "text": "A thorough policy analysis should examine:",
                        "choices": [
                            ("Goals, target population, and equity implications", True),
                            ("Only the policy's title", False),
                            ("Only the date it was passed", False),
                            ("Only the agency's internal memo", False),
                        ],
                    },
                    {
                        "text": "Understanding a policy's funding mechanism helps identify:",
                        "choices": [
                            ("Whether it can be sustainably implemented", True),
                            ("Nothing useful", False),
                            ("Only the bill's sponsor", False),
                            ("The weather on the day it passed", False),
                        ],
                    },
                ],
            },
            {
                "title": "Legislative Advocacy & Coalition Building",
                "summary": "Influencing legislation on behalf of clients and communities.",
                "difficulty": "intermediate",
                "estimated_minutes": 55,
                "content": "Covers how to track legislation, build advocacy coalitions, and "
                "communicate policy positions effectively to lawmakers and the public.",
                "questions": [
                    {
                        "text": "Effective legislative advocacy typically involves:",
                        "choices": [
                            ("Building coalitions and communicating clear positions", True),
                            ("Acting alone with no coalition", False),
                            ("Avoiding any contact with lawmakers", False),
                            ("Ignoring public communication entirely", False),
                        ],
                    },
                    {
                        "text": "Tracking legislation helps advocates:",
                        "choices": [
                            ("Respond and mobilize at the right moments", True),
                            ("Ignore bill deadlines", False),
                            ("Avoid engaging with committees", False),
                            ("Skip stakeholder communication", False),
                        ],
                    },
                ],
            },
            {
                "title": "Using Data to Drive Policy Change",
                "summary": "Turning practice-level data into policy arguments.",
                "difficulty": "advanced",
                "estimated_minutes": 60,
                "content": "This course covers translating direct-practice data and lived "
                "experience into compelling, evidence-based policy arguments for legislators "
                "and funders.",
                "questions": [
                    {
                        "text": "Using practice-level data in advocacy helps:",
                        "choices": [
                            ("Ground policy arguments in real evidence", True),
                            ("Replace the need for any storytelling", False),
                            ("Confuse legislators intentionally", False),
                            ("Avoid any accountability", False),
                        ],
                    },
                    {
                        "text": "The most persuasive policy arguments typically combine:",
                        "choices": [
                            ("Data and lived experience", True),
                            ("Neither data nor stories", False),
                            ("Only anecdotes with no evidence", False),
                            ("Only statistics with no context", False),
                        ],
                    },
                ],
            },
        ],
        "exam_questions": [
            {
                "text": "A rigorous policy analysis should always examine:",
                "choices": [
                    ("The policy's goals, population, and equity impact", True),
                    ("Only its official title", False),
                    ("Only its passage date", False),
                    ("Nothing beyond a headline", False),
                ],
            },
            {
                "text": "Effective legislative advocacy relies on:",
                "choices": [
                    ("Coalitions and clear communication with lawmakers", True),
                    ("Working entirely alone", False),
                    ("Avoiding lawmakers altogether", False),
                    ("Ignoring bill timelines", False),
                ],
            },
            {
                "text": "The strongest policy arguments typically combine:",
                "choices": [
                    ("Solid data with lived experience", True),
                    ("Neither evidence nor stories", False),
                    ("Rumors only", False),
                    ("Unrelated statistics", False),
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Seed SWEEP with its 10 schools, courses, assessments, and certification exams."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing schools/courses before reseeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Flushing existing schools and courses…")
            School.objects.all().delete()

        for school_order, school_data in enumerate(SCHOOLS, start=1):
            school, _ = School.objects.update_or_create(
                name=school_data["name"],
                defaults={
                    "tagline": school_data["tagline"],
                    "description": school_data["description"],
                    "order": school_order,
                    "passing_score": 70,
                    "is_active": True,
                },
            )

            for course_order, course_data in enumerate(school_data["courses"], start=1):
                course, _ = Course.objects.update_or_create(
                    title=course_data["title"],
                    school=school,
                    defaults={
                        "summary": course_data["summary"],
                        "content": course_data["content"],
                        "difficulty": course_data["difficulty"],
                        "estimated_minutes": course_data["estimated_minutes"],
                        "order": course_order,
                        "passing_score": 70,
                        "is_active": True,
                    },
                )
                # The original catalogue predates CourseModule. Preserve any
                # editor-created modules, but supply a usable first lesson
                # for every legacy/seeded course that has none.
                if not course.modules.exists():
                    CourseModule.objects.create(
                        course=course,
                        title="Course learning material",
                        order=1,
                        duration=f"{course.estimated_minutes} min",
                        module_type=CourseModule.ModuleType.ARTICLE,
                        learning_mode=CourseModule.LearningMode.SELF_PACED,
                        overview=course.summary,
                        content=course.content,
                        module_summary="Review the key concepts before taking the assessment.",
                    )
                course.questions.all().delete()
                for q_order, q_data in enumerate(course_data["questions"], start=1):
                    question = Question.objects.create(
                        course=course, text=q_data["text"], order=q_order
                    )
                    for c_order, (choice_text, is_correct) in enumerate(q_data["choices"], start=1):
                        Choice.objects.create(
                            question=question,
                            text=choice_text,
                            is_correct=is_correct,
                            order=c_order,
                        )

            school.exam_questions.all().delete()
            for q_order, q_data in enumerate(school_data["exam_questions"], start=1):
                exam_question = SchoolExamQuestion.objects.create(
                    school=school, text=q_data["text"], order=q_order
                )
                for c_order, (choice_text, is_correct) in enumerate(q_data["choices"], start=1):
                    SchoolExamChoice.objects.create(
                        question=exam_question,
                        text=choice_text,
                        is_correct=is_correct,
                        order=c_order,
                    )

            self.stdout.write(self.style.SUCCESS(f"Seeded {school.name}"))

        self.stdout.write(self.style.SUCCESS(f"Done — seeded {len(SCHOOLS)} schools."))
