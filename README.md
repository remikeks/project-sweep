# SWEEP — Social Work E-Learning and Empowerment Platform

A Django app for social work continuing education: 10 schools, each offering
several courses, with enrollment, progress tracking, quizzes, badges, and
certificates.

## Feature map

| Requirement | Where it lives |
|---|---|
| 10 schools, each with courses | `schools.School`, `courses.Course` (seeded by `seed_data`) |
| Search/enroll in a single course | `courses` app search + `learning.enroll_in_course` |
| Enroll in a whole school (= all its courses) | `learning.enroll_in_school`, triggered from the school detail page |
| Badge on course completion | `credentials.Badge` + `credentials/generator.py`, awarded in `learning/services.py::grade_course_quiz` |
| Certificate on school completion | `credentials.Certificate`, awarded in `learning/services.py::grade_school_exam` |
| Per-user course progress | `learning.CourseProgress` (not_started / in_progress / completed, best score, attempts) |
| Multiple-choice course assessment marks course complete | `courses.Question`/`Choice` + `courses/views.py::course_quiz` |
| Certification exam unlocked after the school's last course | `schools.SchoolExamQuestion`/`SchoolExamChoice` + `learning/views.py::school_exam`, gated by `learning/services.py::school_completion_status` |
| Difficulty level & estimated time per course | `Course.difficulty`, `Course.estimated_minutes` |
| View/download badges & certificates | `credentials/views.py::my_credentials` → `templates/credentials/credentials_list.html` (PNG + PDF download links) |

## App layout

```
sweep/            project settings, root urls
accounts/         signup/login/logout
schools/          School model + browse/search/detail views
courses/          Course, Question, Choice models + search/detail/quiz views
learning/         Enrollment + progress models, business logic (services.py), dashboard
credentials/      Badge, Certificate models, PNG/PDF artwork generator, credentials page
core/             Landing page + dashboard template
templates/, static/   Shared templates and the design-token stylesheet
```

The grading/awarding logic is centralized in `learning/services.py` (course
quizzes) and reused by `credentials/services.py` (badge/certificate
rendering), rather than scattered across views, so the rules for "what counts
as passing" and "when does a badge/certificate get created" live in one
place each.

## Badge & certificate artwork

`credentials/generator.py` renders both a PNG and a PDF for every badge and
certificate using **Pillow only** (Pillow can export an `Image` directly as a
PDF), so there's no external rendering service or headless browser
dependency. Artwork uses the same visual language as the rest of the site
(deep teal, gold seal accents, warm paper background).

## Setup

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data       # creates the 10 schools + their courses/quizzes/exams

python manage.py runserver
```

Then visit:
- `http://127.0.0.1:8000/` — landing page / browse schools
- `http://127.0.0.1:8000/accounts/signup/` — create an account
- `http://127.0.0.1:8000/admin/` — manage schools, courses, questions, and exam questions

## Content management

Everything content-related (schools, courses, course text, difficulty,
estimated time, quiz questions/choices, and school exam questions/choices)
is editable in the Django admin — no code changes needed to add course #31
or school #11. `seed_data` is there to give you a realistic starting dataset
across all 10 schools; rerun it any time (it's idempotent) or pass `--flush`
to wipe schools/courses first.

## Notes & next steps for production

- `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` in `sweep/settings.py` are set
  for local development only — replace them (env vars, `DEBUG=False`, a real
  allowed-hosts list) before deploying.
- Media files (badge/certificate PNG & PDF) are served from local disk via
  `MEDIA_ROOT`/`MEDIA_URL` in development; in production, put them on
  something like S3 and front them with a CDN.
- The app uses SQLite by default; swap `DATABASES` in `sweep/settings.py`
  for Postgres/MySQL in production.
- There's currently one assessment attempt flow (no time limit, unlimited
  retakes). If you want cooldowns, question randomization/shuffling, or a
  per-question weighting, that logic belongs in `learning/services.py`.
