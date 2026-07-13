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

## Render deployment (free demo plan)

### 1) Prepare the app

Install the deployment dependencies:

```bash
pip install -r requirements.txt
```

### 2) Add Render deployment files

Create a file named `render.yaml` in the project root with:

```yaml
services:
  - type: web
    name: sweep-demo
    env: python
    plan: free
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn sweep.wsgi:application"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: False
      - key: ALLOWED_HOSTS
        value: sweep-demo.onrender.com
      - key: CSRF_TRUSTED_ORIGINS
        value: https://sweep-demo.onrender.com
```

Create a file named `Procfile` in the project root with:

```text
web: gunicorn sweep.wsgi:application
```

### 3) Update settings for Render

The project already includes the needed changes in [sweep/settings.py](sweep/settings.py):

- `SECRET_KEY` reads from the environment
- `DEBUG` defaults to `True` locally, but you can set it to `False` in Render
- `ALLOWED_HOSTS` includes `.onrender.com` by default
- `CSRF_TRUSTED_ORIGINS` is configurable from the environment
- `whitenoise.middleware.WhiteNoiseMiddleware` is enabled
- static files are collected via WhiteNoise
- PostgreSQL is used automatically when `DATABASE_URL` is present

If you want the exact settings block, use this version:

```python
import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-change-this-key-before-deploying-to-production")
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = [host.strip() for host in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,.onrender.com").split(",") if host.strip()]
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {"default": dj_database_url.config(default=DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

### 4) Create the database and run migrations

Render will provision Postgres automatically for the web service if you add a Postgres database in the Render dashboard, or you can attach one manually.

Before deploying, run locally:

```bash
python manage.py migrate
python manage.py collectstatic
python manage.py seed_data
```

### 5) Deploy to Render

1. Push the project to GitHub.
2. In Render, create a new Web Service.
3. Connect the GitHub repo.
4. Choose the branch to deploy.
5. Set the build command to:

```bash
pip install -r requirements.txt
```

6. Set the start command to:

```bash
gunicorn sweep.wsgi:application
```

7. Add environment variables:

```text
SECRET_KEY=replace-with-a-long-random-secret
DEBUG=False
ALLOWED_HOSTS=sweep-demo.onrender.com
CSRF_TRUSTED_ORIGINS=https://sweep-demo.onrender.com
```

8. Create a PostgreSQL database in Render and attach it as `DATABASE_URL`.

### 6) Optional: seed the demo data

If you want the demo to start with the content already populated, run the seed command once after the first deploy, either:

- from the Render shell, or
- from a one-off management command job

```bash
python manage.py seed_data
```

### 7) Expected behavior on the free plan

- The app will run with a Render web service on the free plan.
- The database will be a free Postgres instance (limited sleep behavior may apply).
- Static files will be served by WhiteNoise.
- For a simple demo, this is sufficient.

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
