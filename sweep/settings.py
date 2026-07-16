"""
Django settings for the SWEEP project
(Social Work E-learning and Empowerment Platform).
"""

import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Load a local .env file (if present) into the process environment. This is
# what makes GEMINI_API_KEY / SECRET_KEY / etc. actually take effect when
# they're set in a .env file for local development — Django itself never
# reads .env files on its own. Safe to leave in for production too: on
# Render (or anywhere without a .env file) this is just a no-op, since real
# env vars are already in os.environ before Python even starts.
try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

# --------------------------------------------------------------------------
# SECURITY
# --------------------------------------------------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-change-this-key-before-deploying-to-production")

DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = [host.strip() for host in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,.onrender.com").split(",") if host.strip()]
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]

# --------------------------------------------------------------------------
# APPLICATIONS
# --------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "whitenoise.runserver_nostatic",
    "django.contrib.humanize",
    "markdownify",

    # SWEEP apps
    "accounts",
    "schools",
    "courses",
    "learning",
    "credentials",
    "core",
    "ai_tutor",
]

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

ROOT_URLCONF = "sweep.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "sweep.wsgi.application"
ASGI_APPLICATION = "sweep.asgi.application"

# --------------------------------------------------------------------------
# DATABASE
# --------------------------------------------------------------------------
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

# --------------------------------------------------------------------------
# PASSWORD VALIDATION
# --------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------------------------------
# INTERNATIONALIZATION
# --------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------
# STATIC & MEDIA FILES
# --------------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------------------------------
# AUTH
# --------------------------------------------------------------------------
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"

# --------------------------------------------------------------------------
# SWEEP-SPECIFIC SETTINGS
# --------------------------------------------------------------------------
# Minimum percentage score required to pass a course assessment or a
# school certification exam, unless overridden on the individual model.
DEFAULT_PASSING_SCORE = 70

# --------------------------------------------------------------------------
# AI TUTOR
# --------------------------------------------------------------------------
# Uses the Gemini API (Google). Set GEMINI_API_KEY or GOOGLE_API_KEY in the
# environment to enable it; without it, the AI Tutor endpoints return a
# friendly "not configured" message instead of erroring.
# Uses the Gemini API (Google). Set GEMINI_API_KEY or GOOGLE_API_KEY in the
# environment to enable it; without it, the AI Tutor endpoints return a
# friendly "not configured" message instead of erroring.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
# NOTE: gemini-2.0-flash was shut down by Google on 2026-06-01 — requests to
# it now fail outright. gemini-2.5-flash is the current stable, GA default;
# override via AI_TUTOR_MODEL if you want a different tier (e.g.
# gemini-2.5-flash-lite for lower cost, or gemini-3-flash for more capable
# answers). Check https://ai.google.dev/gemini-api/docs/models for the
# current lineup before changing this, since Google retires models on a
# rolling basis.
AI_TUTOR_MODEL = os.environ.get("AI_TUTOR_MODEL", "gemini-3.5-flash")
# Simple per-user cap so a public-facing "Ask AI" button can't run up an
# unbounded API bill. Raise/lower via env var without a code change.
AI_TUTOR_DAILY_LIMIT = int(os.environ.get("AI_TUTOR_DAILY_LIMIT", "30"))
