"""
Sends the "new feedback" notification email. Kept separate from
views.py so the failure mode is explicit and contained: if this raises,
the caller (views.submit_feedback) still has an already-saved Feedback
row and can record the failure on it rather than losing the submission.
"""

import logging

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def send_feedback_notification(feedback):
    """
    Email FEEDBACK_TO_EMAIL about a new Feedback submission.
    Returns True on success. On failure, logs the exception and returns
    False — never raises, so a broken mail server can't break the
    feedback endpoint itself.
    """
    subject = f"[SWEEP feedback] {feedback.get_feedback_type_display()}"

    body_lines = [
        f"Type: {feedback.get_feedback_type_display()}",
        f"Submitted: {feedback.created_at.strftime('%B %d, %Y %H:%M UTC') if feedback.created_at else 'just now'}",
        f"Page: {feedback.page_url or '(not captured)'}",
        f"Submitted by: {feedback.user if feedback.user_id else 'Anonymous / not logged in'}",
        f"Reply-to email given: {feedback.email or '(none provided)'}",
        "",
        "Message:",
        feedback.message,
    ]
    body = "\n".join(body_lines)

    try:
        message = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.FEEDBACK_TO_EMAIL],
            reply_to=[feedback.email] if feedback.email else None,
        )
        message.send(fail_silently=False)
        return True
    except Exception:
        logger.exception("Failed to send feedback notification email for Feedback id=%s", feedback.pk)
        return False
