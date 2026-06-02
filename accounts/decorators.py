from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .permissions import has_role, is_admin_user, is_instructor_user, is_student_user


def role_required(*roles):
    """Require an authenticated user with at least one allowed portal role."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            if has_role(request.user, roles):
                return view_func(request, *args, **kwargs)
            messages.error(request, "You do not have permission to access this page.")
            raise PermissionDenied

        return wrapped

    return decorator


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(request, *args, **kwargs):
        if is_admin_user(request.user):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Administrator access is required.")
        raise PermissionDenied

    return wrapped


def instructor_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(request, *args, **kwargs):
        if is_instructor_user(request.user):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Instructor access is required.")
        raise PermissionDenied

    return wrapped


def student_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(request, *args, **kwargs):
        if is_student_user(request.user):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Student access is required.")
        raise PermissionDenied

    return wrapped
