from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from .permissions import ADMIN, INSTRUCTOR, STUDENT, has_role, is_admin_user


class SessionSecurityMiddleware:
    """
    Tracks activity, expires idle sessions, blocks inactive accounts, and applies
    coarse RBAC to high-risk URL sections.
    """

    PUBLIC_URL_NAMES = {
        "accounts:login",
        "accounts:logout",
        "accounts:register",
        "accounts:verify_email",
        "accounts:resend_verification",
        "accounts:password_reset",
        "accounts:password_reset_done",
        "accounts:password_reset_confirm",
        "accounts:password_reset_complete",
    }

    ROLE_PREFIX_RULES = (
        ("/admin/", (ADMIN,)),
        ("/accounts/admin/", (ADMIN,)),
        ("/accounts/instructor/", (INSTRUCTOR,)),
        ("/accounts/student/", (STUDENT,)),
        ("/payments/", (ADMIN, STUDENT)),
        ("/enrollments/", (STUDENT,)),
    )

    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout_seconds = getattr(settings, "SESSION_TIMEOUT_SECONDS", 30 * 60)

    def __call__(self, request):
        if request.user.is_authenticated:
            redirect_response = self._enforce_account_security(request)
            if redirect_response:
                return redirect_response
        return self.get_response(request)

    def _enforce_account_security(self, request):
        if not request.user.is_active:
            logout(request)
            messages.error(request, "Your account is inactive. Please contact support.")
            return redirect("accounts:login")

        if self._session_expired(request):
            logout(request)
            messages.warning(request, "Your session expired due to inactivity. Please log in again.")
            return redirect("accounts:login")

        request.session["last_activity"] = timezone.now().isoformat()

        if self._is_public_path(request):
            return None

        if not getattr(request.user, "is_verified", False) and not is_admin_user(request.user):
            messages.warning(request, "Please verify your email address before accessing your account.")
            return redirect("accounts:resend_verification")

        for prefix, roles in self.ROLE_PREFIX_RULES:
            if request.path.startswith(prefix) and not has_role(request.user, roles):
                messages.error(request, "You do not have permission to access that area.")
                return redirect("accounts:dashboard")
        return None

    def _session_expired(self, request):
        last_activity = request.session.get("last_activity")
        if not last_activity:
            return False
        try:
            last_seen = timezone.datetime.fromisoformat(last_activity)
            if timezone.is_naive(last_seen):
                last_seen = timezone.make_aware(last_seen)
        except ValueError:
            return False
        return timezone.now() - last_seen > timedelta(seconds=self.timeout_seconds)

    def _is_public_path(self, request):
        resolver_match = getattr(request, "resolver_match", None)
        if resolver_match and resolver_match.view_name in self.PUBLIC_URL_NAMES:
            return True
        public_paths = {
            reverse("accounts:login"),
            reverse("accounts:logout"),
            reverse("accounts:register"),
            reverse("accounts:password_reset"),
            reverse("accounts:password_reset_done"),
            reverse("accounts:password_reset_complete"),
            reverse("accounts:resend_verification"),
        }
        public_prefixes = (
            reverse("accounts:verify_email", kwargs={"uidb64": "uid", "token": "token"}).replace("uid/token/", ""),
            reverse("accounts:password_reset_confirm", kwargs={"uidb64": "uid", "token": "token"}).replace(
                "uid/token/", ""
            ),
        )
        return (
            request.path in public_paths
            or request.path.startswith(public_prefixes)
            or request.path.startswith("/static/")
            or request.path.startswith("/media/")
        )
