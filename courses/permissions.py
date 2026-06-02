from django.core.exceptions import PermissionDenied

from accounts.permissions import is_admin_user, is_instructor_user, is_student_user, owns_course


def can_create_course(user):
    return is_instructor_user(user)


def can_manage_course(user, course):
    return owns_course(user, course)


def can_enroll_in_course(user, course):
    return bool(is_student_user(user) and getattr(course, "is_published", False))


def can_review_course(user, course):
    return can_enroll_in_course(user, course)


def require_course_owner(user, course):
    if not can_manage_course(user, course):
        raise PermissionDenied("You can only manage your own courses.")
    return True


def require_course_enrollment_role(user, course):
    if not can_enroll_in_course(user, course) and not is_admin_user(user):
        raise PermissionDenied("Only students can access this course action.")
    return True
