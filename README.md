# SWEEP Academy — Social Work E-Learning and Empowerment Platform

A Django platform for social work continuing education: schools of
courses with enrollment, progress tracking, quizzes, an AI course tutor,
badges, certificates, and a site-wide feedback widget.

**Tagline:** Learn · Lead · Transform

![Status](https://img.shields.io/badge/status-active--development-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Django](https://img.shields.io/badge/django-5.x-092E20)
![License](https://img.shields.io/badge/license-unspecified-lightgrey)

---

## Table of contents

- [Features](#features)
- [Feature map](#feature-map)
- [App layout](#app-layout)
- [Tech stack](#tech-stack)
- [Getting started](#getting-started)
- [Environment variables](#environment-variables)
- [Content management](#content-management)
- [Badge & certificate artwork](#badge--certificate-artwork)
- [AI Tutor](#ai-tutor)
- [Feedback widget](#feedback-widget)
- [Branding](#branding)
- [Deployment (Vercel)](#deployment-vercel)
- [Notes & next steps for production](#notes--next-steps-for-production)

---

## Features

- Browse schools, each offering multiple courses
- Search and enroll in a single course, or enroll in an entire school at once
- Per-user course progress (not started / in progress / completed), best score, and attempt history
- ParaLearn CBT-authoritative course assessment attempts, with signed result verification and idempotent badge awarding
- A certification exam per school, unlocked once every course in that school is complete
- Difficulty level and estimated time shown per course
- Auto-generated badges (per course) and certificates (per school), downloadable as PNG or PDF
- An AI Tutor that answers questions and summarizes lessons using each course's own content, with a per-user daily quota
- A floating feedback widget for suggestions, bug reports, and content issues, logged to the database with optional email notification

## Feature map

| Requirement | Where it lives |
|---|---|
| Schools, each with courses | `schools.School`, `courses.Course` (seeded by `seed_data`) |
| Search/enroll in a single course | `courses` app search + `learning.enroll_in_course` |
| Enroll in a whole school (= all its courses) | `learning.enroll_in_school`, triggered from the school detail page |
| Badge on course completion | `credentials.Badge` + `credentials/generator.py`, awarded only after a verified `CourseAssessmentAttempt` result |
| Certificate on school completion | `credentials.Certificate`, awarded in `learning/services.py::grade_school_exam` |
| Per-user course progress | `learning.CourseProgress` (not_started / in_progress / completed, best score, attempts) |
| Course assessment marks course complete | `learning.CourseAssessmentAttempt` + ParaLearn signed result webhook; legacy `Question`/`Choice` records are retained but non-authoritative |
| Certification exam unlocked after the school's last course | `schools.SchoolExamQuestion`/`SchoolExamChoice` + `learning/views.py::school_exam`, gated by `learning/services.py::school_completion_status` |
| Difficulty level & estimated time per course | `Course.difficulty`, `Course.estimated_minutes` |
| View/download badges & certificates | `credentials/views.py::my_credentials` → `templates/credentials/credentials_list.html` (PNG + PDF download links) |
| Ask-AI / summarize-lesson tutor | `ai_tutor` app (`CourseMaterial`, `TutorInteraction`, `services.py`, `tutor_ask` endpoint) |
| Site-wide feedback widget | `feedback` app (`Feedback` model, floating widget in `base.html`) |

## App layout

```
sweep/            project settings, root urls
accounts/         signup/login/logout
schools/          School model + browse/search/detail views
courses/          Course, CourseModule, Question, Choice models + search/detail/quiz views
learning/         Enrollment + progress models, business logic (services.py), dashboard
credentials/      Badge, Certificate models, PNG/PDF artwork generator, credentials page
ai_tutor/         Course-aware Q&A/summary tutor (CourseMaterial, TutorInteraction, quota)
feedback/         Floating feedback widget, Feedback model, optional email notification
core/             Landing page + dashboard template
templates/, static/   Shared templates and the design-token stylesheet
```

The grading/awarding logic is centralized in `learning/services.py` (course
quizzes) and reused by `credentials/services.py` (badge/certificate
rendering), rather than scattered across views, so the rules for "what counts
as passing" and "when does a badge/certificate get created" live in one
place each.

## Tech stack

- **Backend:** Django 5.x, Python 3.11
- **Database:** SQLite locally, PostgreSQL in production (`dj-database-url`, `psycopg`)
- **Static files:** WhiteNoise
- **AI Tutor:** `google-genai`, `anthropic` (course/module text + uploaded materials as context)
- **Document handling:** `python-docx`, `python-pptx`, `pypdf` (source material extraction for the AI Tutor), `Pillow` (badge/certificate artwork), `XlsxWriter`
- **Rendered/sanitized text:** `django-markdownify`, `bleach`
- **Server:** Gunicorn

## Getting started

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data       # creates schools + their courses/quizzes/exams

python manage.py runserver
```

Then visit:
- `http://127.0.0.1:8000/` — landing page / browse schools
- `http://127.0.0.1:8000/accounts/signup/` — create an account
- `http://127.0.0.1:8000/admin/` — manage schools, courses, questions, exam questions, AI Tutor materials, and feedback submissions

## Environment variables

| Variable | Purpose | Default (local) |
|---|---|---|
| `SECRET_KEY` | Django secret key | insecure dev key baked into settings — **replace before deploying** |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1,.vercel.app` |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins | empty |
| `DATABASE_URL` | Postgres connection string | unset → falls back to SQLite |
| `GOOGLE_API_KEY` / `ANTHROPIC_API_KEY` | AI Tutor model provider credentials | required only if the AI Tutor feature is enabled |
| `FEEDBACK_TO_EMAIL` | Optional notification address for new feedback | unset → feedback is still saved, just not emailed |
| `SUPABASE_URL`, `SUPABASE_STORAGE_BUCKET`, `SUPABASE_SERVICE_ROLE_KEY` | Server-only signed URLs for the content portal | unset → direct portal uploads disabled |
| `SUPABASE_JWT_ISSUER`, `SUPABASE_JWT_AUDIENCE`, `SUPABASE_JWKS_URL`, `SUPABASE_JWT_ALGORITHMS` | Verified Supabase JWT access to content APIs | unset → Supabase JWT access disabled (Django sessions still work) |
| `PARALEARN_*` | ParaLearn `/api/cbt` candidate provisioning, result-reconciliation, and webhook-secret settings | credentials unset → ParaLearn disabled |

## Content management

Everything content-related (schools, courses, course text, difficulty,
estimated time, legacy quiz questions/choices, and school exam questions/choices)
is editable in the Django admin — no code changes needed to add another
course or school. `seed_data` is there to give you a realistic starting
dataset; rerun it any time (it's idempotent) or pass `--flush` to wipe
schools/courses first.

Course resources have a dedicated workspace at `/courses/content/`. It uses
the Content Author, Content Reviewer, and Content Publisher groups to enforce
the draft → review → approval → publication workflow. Once migrations are
applied, create or refresh those groups with:

```bash
python manage.py bootstrap_content_roles
```

The workspace signs browser uploads on the server and sends file bytes
directly to Supabase Storage; it never exposes a service-role key. It also
supports secure previews, replacement drafts, atomic JSON imports, and
enrollment-checked learner downloads. Full API and deployment requirements,
including explicit JWT claim mapping and bucket CORS requirements, are in
[SUPABASE_CONTENT_PORTAL.md](SUPABASE_CONTENT_PORTAL.md). Do not enable the
Supabase values until the actual project URL, server secret, signing policy,
custom claim schema, and permitted portal origin have been agreed.

## ParaLearn CBT assessments

Course completion and new badge awards are now authority-gated by a verified
ParaLearn result. The old built-in quiz records remain intact for historical
reporting but no longer change completion state. The integration is deliberately
disabled until SWEEP has its own ParaLearn workspace credentials and webhook
secret. It provisions candidates at `https://pln.ng/api/cbt/candidates`, accepts
only HMAC-verified `exam.attempt.completed` webhooks, and redirects learners to
the provider's allow-listed hosted launch URL. See
[PARALEARN_CBT_INTEGRATION.md](PARALEARN_CBT_INTEGRATION.md) for the mapping,
configuration gate, and pre-enable checklist.

## Badge & certificate artwork

`credentials/generator.py` renders both a PNG and a PDF for every badge and
certificate using **Pillow only** (Pillow can export an `Image` directly as a
PDF), so there's no external rendering service or headless browser
dependency. Artwork uses the same visual language as the rest of the site
(navy blue, gold seal accents, warm paper background — see [Branding](#branding)).

## AI Tutor

The `ai_tutor` app is a deliberately simple, course-aware Q&A/summary tutor:

- Course and module text already on `Course`/`CourseModule` is used directly as context.
- Staff can attach extra source documents (`CourseMaterial`: PDF, DOCX, PPTX, TXT, or MD) to a course or a specific module; text is extracted once at upload time and reused on every question.
- `TutorInteraction` logs every question and answer, and doubles as the basis for a per-user daily quota so a public-facing "Ask AI" button can't run up an unbounded API bill.
- Everything goes through one endpoint, `tutor_ask`, which accepts a course, an optional module, a mode (`chat` or `summary`), and a question.

There's no tool use, autonomy, or memory beyond the interaction log yet;
that's intentional for this iteration, with room to grow later without a
data-model rewrite.

## Feedback widget

A floating feedback button, available site-wide, lets any user report a bug,
suggest an idea, flag a content issue, or leave a compliment. Every
submission is saved to the database first; if `FEEDBACK_TO_EMAIL` is
configured, a notification email is also attempted, but a misconfigured mail
server or transient SMTP error never loses the feedback itself (check
`email_sent` / `email_error` on the `Feedback` record in the admin if
notifications seem to have stopped arriving.)

## Branding

The site uses the SWEEP Academy mark — an icon of a figure reaching toward a
sprouting leaf set against four quadrant colors, paired with the wordmark and
the tagline **Learn · Lead · Transform**.

| Token | Hex | Used for |
|---|---|---|
| `--primary` | `#0B2C7A` | Navy — nav, headings, primary buttons |
| `--primary-dark` | `#071D52` | Darker navy — gradients, footer, shadows |
| `--blue` | `#1E9BE0` | Bright blue accent |
| `--green` | `#4C8B1D` | Leaf green accent |
| `--gold` | `#F5A400` | Achievement gold — badges, seals, CTAs |
| `--clay` | `#F2650A` | Orange accent |
| `--danger` | `#C1440E` | Errors / destructive actions |

Logo and favicon assets live in `static/img/` and `static/favicon/`. The
current `logo.svg` wraps a raster export of the mark (there's no vector
source yet) — fine at the sizes used across the site, but a true vector
redraw is recommended before using the mark at large/print sizes.

## Deployment (Vercel)

Vercel detects this Django project from `manage.py`, uses the configured ASGI
application, collects static files during its build, and serves them from its
CDN. `vercel.json` extends the function timeout to 60 seconds for third-party
assessment and AI-tutor requests.

### Production environment

Set these values in Vercel's **Production** environment. Keep credentials in
Vercel's sensitive-variable store; do not add them to source control.

```text
SECRET_KEY=<long random server-only value>
DEBUG=False
ALLOWED_HOSTS=<your-project>.vercel.app,<your-custom-domain>
CSRF_TRUSTED_ORIGINS=https://<your-project>.vercel.app,https://<your-custom-domain>
DATABASE_URL=<Supabase transaction-pooler connection string>
DATABASE_CONN_MAX_AGE=0
SUPABASE_SERVICE_ROLE_KEY=<server-only value>
PARALEARN_API_KEY=<server-only value>
PARALEARN_WEBHOOK_SIGNING_SECRET=<server-only value>
```

Also configure the non-secret Supabase and ParaLearn settings listed in
[SUPABASE_CONTENT_PORTAL.md](SUPABASE_CONTENT_PORTAL.md) and
[PARALEARN_CBT_INTEGRATION.md](PARALEARN_CBT_INTEGRATION.md). The database
migrations are applied deliberately from a trusted environment; do not add
`migrate` to Vercel's build command because preview deployments share the
production Supabase database.

### Deploy and verify

1. Create or import the repository as a Vercel project, then add the
   production environment variables above.
2. Deploy a preview and verify sign-in, content upload, and a signed ParaLearn
   webhook against its preview URL.
3. Promote the verified deployment to production, set the exact Vercel URL in
   `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`, and register
   `https://<production-host>/courses/paralearn/webhook/` in ParaLearn.
4. Attach a custom domain only after its HTTPS certificate is active.

## Notes & next steps for production

- `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` in `sweep/settings.py` are set
  for local development only — replace them (env vars, `DEBUG=False`, a real
  allowed-hosts list) before deploying.
- Media files (badge/certificate PNG & PDF, uploaded AI Tutor materials) are
  served from local disk via `MEDIA_ROOT`/`MEDIA_URL` in development; in
  production, put them on something like S3 and front them with a CDN.
- The app uses SQLite by default; swap `DATABASES` in `sweep/settings.py`
  for Postgres/MySQL in production (already wired up via `DATABASE_URL`).
- There's currently one assessment attempt flow (no time limit, unlimited
  retakes). If you want cooldowns, question randomization/shuffling, or
  per-question weighting, that logic belongs in `learning/services.py`.
- The AI Tutor has no tool use, autonomy, or memory beyond its interaction
  log — a deliberate MVP scope, not a limitation of the data model.
- `logo.svg` currently embeds a raster image rather than true vector
  artwork; consider a vector redraw for large-format use.
