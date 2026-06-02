from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


ADMIN = "admin"
INSTRUCTOR = "instructor"
STUDENT = "student"


def user_role(user):
    return getattr(user, "role", None)


def is_admin_user(user):
    return bool(user and user.is_authenticated and (user.is_superuser or user.is_staff or user_role(user) == ADMIN))


def is_instructor_user(user):
    return bool(user and user.is_authenticated and (is_admin_user(user) or user_role(user) == INSTRUCTOR))


def is_student_user(user):
    return bool(user and user.is_authenticated and (is_admin_user(user) or user_role(user) == STUDENT))


def has_role(user, roles):
    if is_admin_user(user):
        return True
    return bool(user and user.is_authenticated and user_role(user) in set(roles))


def owns_course(user, course):
    return bool(is_admin_user(user) or (user and course and course.instructor_id == user.id))


class VerifiedLoginRequiredMixin(LoginRequiredMixin):
    """Require login plus email verification for protected application pages."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not getattr(request.user, "is_verified", False) and not request.user.is_staff:
            raise PermissionDenied("Please verify your email address before continuing.")
        return super().dispatch(request, *args, **kwargs)


class RoleRequiredMixin(VerifiedLoginRequiredMixin, UserPassesTestMixin):
    allowed_roles = ()

    def test_func(self):
        return has_role(self.request.user, self.allowed_roles)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You do not have permission to access this page.")
        return super().handle_no_permission()


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = (ADMIN,)

    def test_func(self):
        return is_admin_user(self.request.user)


class InstructorRequiredMixin(RoleRequiredMixin):
    allowed_roles = (INSTRUCTOR,)

    def test_func(self):
        return is_instructor_user(self.request.user)


class StudentRequiredMixin(RoleRequiredMixin):
    allowed_roles = (STUDENT,)

    def test_func(self):
        return is_student_user(self.request.user)


class CourseOwnerRequiredMixin(InstructorRequiredMixin):
    """Allow staff/admin users or the instructor who owns the course object."""

    def test_func(self):
        if not is_instructor_user(self.request.user):
            return False
        course = self.get_object()
        return owns_course(self.request.user, course)
