from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.db.models import Count, Prefetch, Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, View

from courses.models import Course
from enrollments.models import Enrollment, ProgressTracking, Wishlist
from payments.models import Payment
from reviews.models import Review

from .forms import EmailOrUsernameAuthenticationForm, UserProfileUpdateForm, UserRegistrationForm
from .models import Notification
from .permissions import AdminRequiredMixin, InstructorRequiredMixin, StudentRequiredMixin, VerifiedLoginRequiredMixin
from .tokens import email_verification_token
from .utils import (
    clear_login_attempts,
    get_user_from_uid,
    is_login_locked,
    record_failed_login,
    send_verification_email,
)


User = get_user_model()


class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.is_verified = False
        self.object.save()
        send_verification_email(self.request, self.object)
        messages.success(
            self.request,
            "Registration successful. Please verify your email address before logging in.",
        )
        return redirect(self.get_success_url())


class VerifyEmailView(View):
    def get(self, request, uidb64, token):
        user = get_user_from_uid(uidb64)
        if user and email_verification_token.check_token(user, token):
            user.is_verified = True
            user.save(update_fields=["is_verified", "updated_at"])
            messages.success(request, "Email verified successfully. You can now log in.")
            return redirect("accounts:login")
        messages.error(request, "The verification link is invalid or has expired.")
        return redirect("accounts:login")


class ResendVerificationView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to resend your verification email.")
            return redirect("accounts:login")
        if request.user.is_verified:
            return redirect("accounts:dashboard")
        send_verification_email(request, request.user)
        messages.success(request, "A new verification email has been sent.")
        logout(request)
        return redirect("accounts:login")


class UserLoginView(LoginView):
    authentication_form = EmailOrUsernameAuthenticationForm
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            identifier = request.POST.get("username", "")
            if is_login_locked(request, identifier):
                messages.error(request, "Too many failed login attempts. Please try again later.")
                return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        if not getattr(user, "is_verified", False) and not user.is_staff:
            messages.warning(self.request, "Please verify your email address before logging in.")
            send_verification_email(self.request, user)
            return redirect("accounts:login")

        clear_login_attempts(self.request, self.request.POST.get("username", ""))
        login(self.request, user)
        self.request.session.cycle_key()
        remember_me = form.cleaned_data.get("remember_me")
        self.request.session.set_expiry(60 * 60 * 24 * 30 if remember_me else 0)
        self.request.session["last_activity"] = ""
        messages.success(self.request, "You are now logged in.")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        record_failed_login(self.request, self.request.POST.get("username", ""))
        messages.error(self.request, "Invalid login details.")
        return super().form_invalid(form)


class UserLogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect("accounts:login")

    def get(self, request):
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect("accounts:login")


class UserPasswordResetView(PasswordResetView):
    template_name = "registration/password_reset.html"
    email_template_name = "emails/password_reset_email.html"
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")


class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"


class UserPasswordChangeView(VerifiedLoginRequiredMixin, PasswordChangeView):
    template_name = "registration/change_password.html"
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form):
        messages.success(self.request, "Your password has been changed.")
        return super().form_valid(form)


class ProfileUpdateView(VerifiedLoginRequiredMixin, UpdateView):
    form_class = UserProfileUpdateForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)


class DashboardView(VerifiedLoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["notifications"] = Notification.objects.filter(user=user).only(
            "title", "message", "is_read", "created_at"
        )[:8]

        if user.is_staff or getattr(user, "role", "") == "admin":
            context.update(self._admin_context())
        elif getattr(user, "role", "") == "instructor":
            context.update(self._instructor_context(user))
        else:
            context.update(self._student_context(user))
        return context

    def _admin_context(self):
        return {
            "dashboard_type": "admin",
            "total_users": User.objects.count(),
            "total_courses": Course.objects.count(),
            "published_courses_count": Course.objects.filter(is_published=True).count(),
            "total_students": Enrollment.objects.values("student").distinct().count(),
        }

    def _student_context(self, user):
        enrollments = (
            Enrollment.objects.filter(student=user)
            .select_related("course", "course__category", "course__instructor")
            .prefetch_related(
                Prefetch(
                    "course__progress_records",
                    queryset=ProgressTracking.objects.filter(student=user).only(
                        "course_id", "progress_percentage", "is_completed"
                    ),
                )
            )
        )
        progress_records = ProgressTracking.objects.filter(student=user)
        return {
            "dashboard_type": "student",
            "enrolled_courses": enrollments,
            "completed_courses": enrollments.filter(completed=True),
            "active_courses_count": enrollments.filter(completed=False).count(),
            "completed_courses_count": enrollments.filter(completed=True).count(),
            "average_progress": self._average_progress(progress_records),
            "wishlist": Wishlist.objects.filter(student=user).select_related("course", "course__category")[:8],
        }

    def _instructor_context(self, user):
        courses = (
            Course.objects.filter(instructor=user)
            .select_related("category")
            .annotate(student_count=Count("enrollments", distinct=True), review_count=Count("course_reviews", distinct=True))
        )
        earnings = Payment.objects.filter(
            course__instructor=user,
            payment_status=getattr(Payment.Status, "SUCCESS", "success"),
        ).aggregate(total=Sum("amount"))["total"] or 0
        return {
            "dashboard_type": "instructor",
            "published_courses": courses.filter(is_published=True),
            "published_courses_count": courses.filter(is_published=True).count(),
            "total_students": courses.aggregate(total=Count("enrollments__student", distinct=True))["total"] or 0,
            "earnings": earnings,
            "recent_reviews": Review.objects.filter(course__instructor=user).select_related("student", "course")[:8],
        }

    @staticmethod
    def _average_progress(progress_records):
        records = list(progress_records.values_list("progress_percentage", flat=True))
        if not records:
            return 0
        return round(sum(records) / len(records), 1)


class AdminDashboardView(AdminRequiredMixin, DashboardView):
    pass


class InstructorDashboardView(InstructorRequiredMixin, DashboardView):
    pass


class StudentDashboardView(StudentRequiredMixin, DashboardView):
    pass
