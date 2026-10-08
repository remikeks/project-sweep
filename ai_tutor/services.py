"""
The AI Tutor's brain: builds course/module context from what's already
in the database (plus any ingested CourseMaterial), sends it to Gemini
alongside the learner's question, and logs the exchange.

Deliberately NOT agentic: one request in, one answer out, grounded only
in the context we hand it. That keeps it predictable and auditable for
an MVP. The same context-building functions here are the natural place
to plug in tool use / retrieval / multi-turn memory in a later
iteration — the interaction log (TutorInteraction) already gives it
somewhere to keep history.
"""

import logging
import os

from django.conf import settings
from django.utils import timezone

from .models import CourseMaterial, TutorInteraction

from google.genai import types

logger = logging.getLogger(__name__)

# gemini-2.0-flash was shut down by Google on 2026-06-01 — keep this in sync
# with the default in sweep/settings.py.
MODEL = getattr(settings, "AI_TUTOR_MODEL", "gemini-3.8-flash")
MAX_ANSWER_TOKENS = 700
MAX_CONTEXT_CHARS = 12000
DAILY_QUESTION_LIMIT = getattr(settings, "AI_TUTOR_DAILY_LIMIT", 30)

SYSTEM_PROMPT = (
    "You are the SWEEP AI Tutor, an assistant embedded in a social work "
    "e-learning platform. You help learners understand and review course "
    "material.\n\n"
    "Rules:\n"
    "- Answer using ONLY the course content provided in the message below. "
    "If the content doesn't cover the question, say so plainly and suggest "
    "the learner check with their instructor, rather than guessing or "
    "inventing facts.\n"
    "- Keep answers focused and appropriately concise for someone reading "
    "on a course page — a short paragraph or a few bullet points, not an "
    "essay.\n"
    "- Write in plain language. Avoid restating these instructions or "
    "mentioning that you were given context.\n"
    "- This is educational content about social work practice, not a "
    "substitute for clinical supervision or professional judgment; note "
    "that briefly if a question strays into needing individualized "
    "professional advice."
)


class TutorError(Exception):
    """Raised when the AI provider call itself fails."""


class TutorNotConfigured(Exception):
    """Raised when no API key is available."""


class TutorQuotaExceeded(Exception):
    """Raised when a user has hit their daily question limit."""


def _truncate(text, limit=MAX_CONTEXT_CHARS):
    text = text or ""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n[...content truncated...]"


def _get_api_key():
    api_key = (
        getattr(settings, "GEMINI_API_KEY", None)
        or getattr(settings, "GOOGLE_API_KEY", None)
        or os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
    )
    if not api_key:
        raise TutorNotConfigured(
            "No Gemini API key is configured. Set GEMINI_API_KEY or GOOGLE_API_KEY to enable the AI Tutor."
        )
    return api_key


def _get_client():
    api_key = _get_api_key()

    try:
        from google import genai
    except ImportError as exc:
        raise TutorNotConfigured(
            "The 'google-genai' package isn't installed."
        ) from exc

    return genai.Client(api_key=api_key)




def _call_gemini(user_message, max_tokens=MAX_ANSWER_TOKENS):
    client = _get_client()

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=max_tokens,
                temperature=0.3,
            ),
        )

    except Exception as exc:
        logger.exception("Gemini API call failed (model=%s)", MODEL)
        raise TutorError(str(exc)) from exc

    answer = (response.text or "").strip()

    if not answer:
        raise TutorError("The model returned an empty response.")

    return answer

# --------------------------------------------------------------------------
# Context building
# --------------------------------------------------------------------------

def _course_context(course):
    parts = []
    if course.summary:
        parts.append(f"Course summary: {course.summary}")
    if course.description:
        parts.append(f"Course description:\n{course.description}")
    if course.learning_objectives:
        parts.append(f"Learning objectives:\n{course.learning_objectives}")
    if course.content:
        parts.append(f"Course learning material:\n{course.content}")

    for module in course.modules.order_by("order", "id"):
        chunk = [f"### Module {module.order}: {module.title}"]
        if module.overview:
            chunk.append(module.overview)
        if module.content:
            chunk.append(module.content)
        if module.module_summary:
            chunk.append(f"Module recap: {module.module_summary}")
        parts.append("\n".join(chunk))

    materials = CourseMaterial.objects.filter(
        course=course, module__isnull=True, is_active=True
    ).exclude(extracted_text="")
    for material in materials:
        parts.append(f"### Uploaded material — {material.title}\n{material.extracted_text}")

    return _truncate("\n\n".join(parts))


def _module_context(module):
    parts = [f"Course: {module.course.title}", f"Module: {module.title}"]
    if module.overview:
        parts.append(f"Overview: {module.overview}")
    if module.content:
        parts.append(f"Content:\n{module.content}")
    if module.module_summary:
        parts.append(f"Existing summary: {module.module_summary}")
    if module.knowledge_check:
        parts.append(f"Knowledge check prompts:\n{module.knowledge_check}")

    materials = CourseMaterial.objects.filter(module=module, is_active=True).exclude(extracted_text="")
    for material in materials:
        parts.append(f"Uploaded material — {material.title}\n{material.extracted_text}")

    return _truncate("\n\n".join(parts))


# --------------------------------------------------------------------------
# Quota
# --------------------------------------------------------------------------

def enforce_daily_quota(user):
    today = timezone.now().date()
    count = TutorInteraction.objects.filter(user=user, created_at__date=today).count()
    if count >= DAILY_QUESTION_LIMIT:
        raise TutorQuotaExceeded(
            f"You've reached today's limit of {DAILY_QUESTION_LIMIT} AI Tutor questions. "
            "Please try again tomorrow."
        )


# --------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------

def _log(user, course, module, kind, question, answer, was_error=False):
    TutorInteraction.objects.create(
        user=user,
        course=course,
        module=module,
        kind=kind,
        question=question,
        answer=answer,
        was_error=was_error,
    )


# --------------------------------------------------------------------------
# Public entry points, used by ai_tutor/views.py
# --------------------------------------------------------------------------

def ask_course_question(user, course, question):
    context = _course_context(course)
    message = (
        f"Course: {course.title}\n\n"
        f"--- Course content ---\n{context}\n--- end content ---\n\n"
        f"Learner question: {question}"
    )
    answer = _call_gemini(message)
    _log(user, course, None, TutorInteraction.Kind.CHAT, question, answer)
    return answer


def summarize_course(user, course):
    context = _course_context(course)
    prompt_question = "What is this course all about?"
    message = (
        f"Course: {course.title}\n\n"
        f"--- Course content ---\n{context}\n--- end content ---\n\n"
        "A prospective learner just asked: \"What is this course all about?\" Give a "
        "friendly overview, readable in under a minute, covering what the course "
        "covers, who it's for, and what they'll be able to do afterward."
    )
    answer = _call_gemini(message)
    _log(user, course, None, TutorInteraction.Kind.SUMMARY, prompt_question, answer)
    return answer


def ask_module_question(user, course, module, question):
    context = _module_context(module)
    message = (
        f"--- Module content ---\n{context}\n--- end content ---\n\n"
        f"Learner question: {question}"
    )
    answer = _call_gemini(message)
    _log(user, course, module, TutorInteraction.Kind.CHAT, question, answer)
    return answer


def summarize_module(user, course, module):
    context = _module_context(module)
    prompt_question = "Summarise this lesson."
    message = (
        f"--- Module content ---\n{context}\n--- end content ---\n\n"
        "Summarise this lesson for a learner: a short set of plain-language bullet "
        "points covering the key ideas they should take away."
    )
    answer = _call_gemini(message)
    _log(user, course, module, TutorInteraction.Kind.SUMMARY, prompt_question, answer)
    return answer
