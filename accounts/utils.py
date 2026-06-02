from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes

from .tokens import email_verification_token


LOGIN_ATTEMPT_LIMIT = getattr(settings, "LOGIN_ATTEMPT_LIMIT", 5)
LOGIN_LOCKOUT_SECONDS = getattr(settings, "LOGIN_LOCKOUT_SECONDS", 15 * 60)


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def normalize_login_identifier(identifier):
    return (identifier or "").strip().lower()


def login_attempt_cache_key(request, identifier):
    ip_address = get_client_ip(request)
    normalized_identifier = normalize_login_identifier(identifier)
    return f"auth:login_attempts:{ip_address}:{normalized_identifier}"


def is_login_locked(request, identifier):
    return cache.get(login_attempt_cache_key(request, identifier), 0) >= LOGIN_ATTEMPT_LIMIT


def record_failed_login(request, identifier):
    key = login_attempt_cache_key(request, identifier)
    attempts = cache.get(key, 0) + 1
    cache.set(key, attempts, LOGIN_LOCKOUT_SECONDS)
    return attempts


def clear_login_attempts(request, identifier):
    cache.delete(login_attempt_cache_key(request, identifier))


def make_email_verification_url(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    path = reverse("accounts:verify_email", kwargs={"uidb64": uid, "token": token})
    return request.build_absolute_uri(path)


def get_user_from_uid(uidb64):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None


def send_verification_email(request, user):
    verification_url = make_email_verification_url(request, user)
    context = {"user": user, "verification_url": verification_url}
    subject = "Verify your Online Learning Portal account"

    try:
        text_body = render_to_string("emails/verify_email.txt", context)
    except Exception:
        text_body = f"Hello {user.get_full_name() or user.username}, verify your account: {verification_url}"

    try:
        html_body = render_to_string("emails/verify_email.html", context)
    except Exception:
        html_body = None

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[user.email],
    )
    if html_body:
        message.attach_alternative(html_body, "text/html")
    message.send(fail_silently=False)
    return verification_url
