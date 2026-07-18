from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Feedback(models.Model):
    """
    A single feedback submission from the site-wide floating widget.

    Always saved to the database first, independent of whether the
    notification email to FEEDBACK_TO_EMAIL succeeds — so a misconfigured
    mail server or a transient SMTP error never loses feedback, it just
    means the (optional) email notification didn't go out. Check
    email_sent / email_error in the admin if notifications seem to have
    stopped arriving.
    """

    class FeedbackType(models.TextChoices):
        SUGGESTION = "suggestion", "Suggestion / idea"
        BUG = "bug", "Something's not working"
        CONTENT = "content", "Course or content issue"
        COMPLIMENT = "compliment", "Compliment"
        OTHER = "other", "Other"

    feedback_type = models.CharField(
        max_length=20, choices=FeedbackType.choices, default=FeedbackType.OTHER
    )
    message = models.TextField()
    email = models.EmailField(blank=True, help_text="Optional — provided by the submitter.")
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="feedback_submissions",
        help_text="Set automatically if the submitter was logged in.",
    )
    page_url = models.CharField(
        max_length=500, blank=True, help_text="Page the submitter was on, captured client-side."
    )

    email_sent = models.BooleanField(default=False)
    email_error = models.CharField(max_length=500, blank=True)

    is_reviewed = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_feedback_type_display()} — {self.message[:60]}"
