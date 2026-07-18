import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from . import services
from .models import Feedback

VALID_TYPES = {choice for choice, _ in Feedback.FeedbackType.choices}


@require_POST
def submit_feedback(request):
    """
    Public endpoint (no login required) behind the floating feedback
    widget on every page. Expects a JSON body:

        {
          "feedback_type": "suggestion" | "bug" | "content" | "compliment" | "other",
          "message": "...",
          "email": "...",       # optional
          "page_url": "..."     # optional, captured client-side via window.location
        }

    Always persists the submission (if the message is non-empty) before
    attempting to send the notification email, so a mail-server hiccup
    never loses feedback — it only means the email notification didn't
    go out, which is recorded on the Feedback row for admins to notice.
    """
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "That request didn't make sense."}, status=400)

    feedback_type = (payload.get("feedback_type") or "").strip()
    message = (payload.get("message") or "").strip()
    email = (payload.get("email") or "").strip()
    page_url = (payload.get("page_url") or "").strip()[:500]

    if feedback_type not in VALID_TYPES:
        return JsonResponse({"ok": False, "error": "Please choose a feedback type."}, status=400)
    if not message:
        return JsonResponse({"ok": False, "error": "Please tell us a bit more before sending."}, status=400)

    feedback = Feedback.objects.create(
        feedback_type=feedback_type,
        message=message,
        email=email,
        user=request.user if request.user.is_authenticated else None,
        page_url=page_url,
    )

    email_sent = services.send_feedback_notification(feedback)
    if not email_sent:
        feedback.email_error = "Notification email failed to send — see server logs."
        feedback.save(update_fields=["email_error"])
    else:
        feedback.email_sent = True
        feedback.save(update_fields=["email_sent"])

    # Submission is a success from the user's point of view either way —
    # their feedback is safely saved. We don't surface email-delivery
    # plumbing to them.
    return JsonResponse({"ok": True})
