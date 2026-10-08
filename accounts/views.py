import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .forms import SignUpForm

logger = logging.getLogger(__name__)
User = get_user_model()


def send_activation_email(request, user):
    """Generate a token and send an account activation link to the user's email."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_path = reverse("activate_account", kwargs={"uidb64": uid, "token": token})
    activation_url = request.build_absolute_uri(activation_path)

    subject = "Activate your SWEEP Academy account"
    body = render_to_string(
        "registration/activation_email.html",
        {"user": user, "activation_url": activation_url},
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as exc:
        logger.exception("Failed to send activation email to %s: %s", user.email, exc)
        return False


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    require_verification = getattr(settings, "ACCOUNT_EMAIL_VERIFICATION_REQUIRED", False)

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if require_verification:
                user.is_active = False
                user.save()
                send_activation_email(request, user)
                return render(request, "registration/activation_sent.html", {"email": user.email})
            else:
                user.is_active = True
                user.save()
                login(request, user)
                # Send welcome/verification notice in dev/console without blocking login
                try:
                    send_activation_email(request, user)
                except Exception:
                    pass
                messages.success(request, "Welcome to SWEEP Academy! Your account has been created.")
                return redirect("dashboard")
    else:
        form = SignUpForm()

    return render(request, "registration/signup.html", {"form": form})


def activate_account(request, uidb64, token):
    """Verify an email confirmation token and activate the user."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        login(request, user)
        messages.success(request, "Your email has been verified! Welcome to SWEEP Academy.")
        return redirect("dashboard")
    else:
        return render(request, "registration/activation_invalid.html", status=400)


def resend_activation(request):
    """Allow an unverified user to request a fresh activation link."""
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if email:
            user = User.objects.filter(email__iexact=email, is_active=False).first()
            if user:
                send_activation_email(request, user)
        # Always render the confirmation to avoid user enumeration
        return render(request, "registration/activation_sent.html", {"email": email})
    return render(request, "registration/resend_activation.html")
