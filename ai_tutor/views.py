import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from courses.models import Course, CourseModule

from . import services


@login_required
@require_POST
def tutor_ask(request):
    """
    One endpoint behind every "Ask AI Tutor" / "Summarise this lesson" /
    "What's this course about?" button on the site. Expects a JSON body:

        {
          "course_slug": "foundations-of-child-protection",
          "module_order": 2,          # optional — omit for course-level
          "mode": "chat" | "summary", # "summary" ignores "question"
          "question": "..."           # required when mode == "chat"
        }

    Returns {"ok": true, "answer": "..."} or {"ok": false, "error": "..."}.
    """
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "That request didn't make sense."}, status=400)

    course_slug = (payload.get("course_slug") or "").strip()
    module_order = payload.get("module_order")
    question = (payload.get("question") or "").strip()
    mode = payload.get("mode") or "chat"

    if not course_slug:
        return JsonResponse({"ok": False, "error": "Missing course."}, status=400)

    course = get_object_or_404(Course, slug=course_slug, is_active=True)

    module = None
    if module_order not in (None, ""):
        module = get_object_or_404(CourseModule, course=course, order=module_order)

    try:
        services.enforce_daily_quota(request.user)

        if mode == "summary":
            if module:
                answer = services.summarize_module(request.user, course, module)
            else:
                answer = services.summarize_course(request.user, course)
        else:
            if not question:
                return JsonResponse({"ok": False, "error": "Type a question first."}, status=400)
            if module:
                answer = services.ask_module_question(request.user, course, module, question)
            else:
                answer = services.ask_course_question(request.user, course, question)

    except services.TutorNotConfigured:
        return JsonResponse(
            {"ok": False, "error": "The AI Tutor isn't set up yet — ask an administrator to add an API key."},
            status=503,
        )
    except services.TutorQuotaExceeded as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=429)
    except services.TutorError:
        return JsonResponse(
            {"ok": False, "error": "The AI Tutor couldn't answer that just now. Please try again shortly."},
            status=502,
        )

    return JsonResponse({"ok": True, "answer": answer})
