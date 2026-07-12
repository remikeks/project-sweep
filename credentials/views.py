from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Badge, Certificate


@login_required
def my_credentials(request):
    """Where a user views and downloads all their badges and certificates."""
    badges = Badge.objects.filter(user=request.user).select_related("course", "course__school")
    certificates = Certificate.objects.filter(user=request.user).select_related("school")

    context = {
        "badges": badges,
        "certificates": certificates,
    }
    return render(request, "credentials/credentials_list.html", context)
