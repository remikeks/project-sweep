"""
Django settings for the SWEEP project
(Social Work E-learning and Empowerment Platform).
"""

import os
import json
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
    "feedback",
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
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            # Transaction poolers (commonly port 6543) must not receive a
            # connection Django keeps open between requests. Override this
            # only when using a session/direct connection intentionally.
            conn_max_age=int(os.environ.get("DATABASE_CONN_MAX_AGE", "600")),
        )
    }
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
AI_TUTOR_MODEL = os.environ.get("AI_TUTOR_MODEL", "gemini-2.5-flash")
# Simple per-user cap so a public-facing "Ask AI" button can't run up an
# unbounded API bill. Raise/lower via env var without a code change.
AI_TUTOR_DAILY_LIMIT = int(os.environ.get("AI_TUTOR_DAILY_LIMIT", "30"))

# --------------------------------------------------------------------------
# EMAIL
# --------------------------------------------------------------------------
# Real outbound email (used today by the feedback widget; anything else
# that needs to send mail later — password reset, notifications — will
# use this same config). Set EMAIL_HOST in the environment to send real
# email via SMTP; without it, email is printed to the console instead of
# sent, so nothing crashes in local dev if you haven't configured an SMTP
# provider yet.
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
if EMAIL_HOST:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "SWEEP <no-reply@sweepacademy.org>")

# --------------------------------------------------------------------------
# FEEDBACK
# --------------------------------------------------------------------------
# Where the site-wide feedback widget sends its notification email.
# Override via env var if this ever needs to change without a redeploy.
FEEDBACK_TO_EMAIL = os.environ.get("FEEDBACK_TO_EMAIL", "info@sweepacademy.org")

# --------------------------------------------------------------------------
# SUPABASE CONTENT PORTAL
# --------------------------------------------------------------------------
# These are intentionally public identifiers only. Do not expose a Supabase
# service-role key to a browser; the future portal authenticates through its
# own Supabase session and calls SWEEP with a separately verified service/JWT
# integration in production.
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_STORAGE_BUCKET = os.environ.get("SUPABASE_STORAGE_BUCKET", "sweep-course-assets")
SUPABASE_JWT_ISSUER = os.environ.get("SUPABASE_JWT_ISSUER", "")
SUPABASE_JWT_AUDIENCE = os.environ.get("SUPABASE_JWT_AUDIENCE", "authenticated")

# The secret key is deliberately server-only. It is used solely to create
# narrowly-scoped, short-lived Storage URLs; templates and JSON responses
# never contain it. Do not use a secret/service key in browser code.
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_STORAGE_SIGNED_URL_TTL = int(os.environ.get("SUPABASE_STORAGE_SIGNED_URL_TTL", "600"))

# JWT verification is intentionally disabled until every project-specific
# value below is set. In particular, do not "decode" an unverified bearer
# token or silently accept an unknown signing algorithm.
SUPABASE_JWKS_URL = os.environ.get("SUPABASE_JWKS_URL", "")
SUPABASE_JWT_ALGORITHMS = tuple(
    value.strip()
    for value in os.environ.get("SUPABASE_JWT_ALGORITHMS", "").split(",")
    if value.strip()
)
SUPABASE_JWT_PERMISSION_CLAIM = os.environ.get("SUPABASE_JWT_PERMISSION_CLAIM", "")
SUPABASE_JWT_ROLE_CLAIM = os.environ.get("SUPABASE_JWT_ROLE_CLAIM", "")
try:
    SUPABASE_JWT_ROLE_MAP = json.loads(os.environ.get("SUPABASE_JWT_ROLE_MAP", "{}"))
except json.JSONDecodeError:
    # Authentication code treats an invalid map as unavailable and fails
    # closed. Keeping startup alive makes a configuration error diagnosable.
    SUPABASE_JWT_ROLE_MAP = {}
SUPABASE_JWKS_CACHE_SECONDS = min(
    max(int(os.environ.get("SUPABASE_JWKS_CACHE_SECONDS", "300")), 1), 600
)

# Keep the portal's upload and import envelope bounded even when the actual
# bytes are sent directly from a browser to Supabase Storage.
CONTENT_PORTAL_MAX_UPLOAD_BYTES = int(
    os.environ.get("CONTENT_PORTAL_MAX_UPLOAD_BYTES", str(100 * 1024 * 1024))
)
CONTENT_PORTAL_MAX_IMPORT_BYTES = int(
    os.environ.get("CONTENT_PORTAL_MAX_IMPORT_BYTES", str(2 * 1024 * 1024))
)
CONTENT_PORTAL_MAX_IMPORT_ROWS = int(os.environ.get("CONTENT_PORTAL_MAX_IMPORT_ROWS", "250"))

# --------------------------------------------------------------------------
# PARALEARN CBT ASSESSMENTS
# --------------------------------------------------------------------------
# ParaLearn's documented CBT contract provisions candidates at /candidates,
# returns a hosted Candidate Gate URL, and sends final HMAC-signed webhooks.
# The real workspace API key and webhook secret remain deployment-only values:
# blank defaults keep all outbound calls and webhook processing disabled.
PARALEARN_API_BASE_URL = os.environ.get("PARALEARN_API_BASE_URL", "")
PARALEARN_API_KEY = os.environ.get("PARALEARN_API_KEY", "")
PARALEARN_API_KEY_HEADER = os.environ.get("PARALEARN_API_KEY_HEADER", "Authorization")
PARALEARN_API_KEY_PREFIX = os.environ.get("PARALEARN_API_KEY_PREFIX", "Bearer ")
PARALEARN_CANDIDATE_PROVISION_PATH = os.environ.get("PARALEARN_CANDIDATE_PROVISION_PATH", "/candidates")
PARALEARN_RESULT_PATH_TEMPLATE = os.environ.get(
    "PARALEARN_RESULT_PATH_TEMPLATE", "/attempts/{attempt_reference}/slip"
)
PARALEARN_HTTP_TIMEOUT_SECONDS = min(
    max(int(os.environ.get("PARALEARN_HTTP_TIMEOUT_SECONDS", "10")), 1),
    30,
)
PARALEARN_ALLOWED_LAUNCH_HOSTS = tuple(
    host.strip().lower()
    for host in os.environ.get("PARALEARN_ALLOWED_LAUNCH_HOSTS", "").split(",")
    if host.strip()
)
PARALEARN_WEBHOOK_SIGNING_SECRET = os.environ.get("PARALEARN_WEBHOOK_SIGNING_SECRET", "")
PARALEARN_WEBHOOK_SIGNATURE_HEADER = os.environ.get("PARALEARN_WEBHOOK_SIGNATURE_HEADER", "x-cbt-signature")
PARALEARN_WEBHOOK_SIGNATURE_PREFIX = os.environ.get("PARALEARN_WEBHOOK_SIGNATURE_PREFIX", "sha256=")
PARALEARN_WEBHOOK_SIGNATURE_ALGORITHM = os.environ.get(
    "PARALEARN_WEBHOOK_SIGNATURE_ALGORITHM", "hmac-sha256"
).lower()
PARALEARN_WEBHOOK_EVENT_HEADER = os.environ.get("PARALEARN_WEBHOOK_EVENT_HEADER", "x-cbt-event")
PARALEARN_WEBHOOK_EVENT_ID_HEADER = os.environ.get("PARALEARN_WEBHOOK_EVENT_ID_HEADER", "x-cbt-event-id")
PARALEARN_WEBHOOK_TIMESTAMP_HEADER = os.environ.get("PARALEARN_WEBHOOK_TIMESTAMP_HEADER", "x-cbt-timestamp")

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"
