from django.urls import path

from .views import (
    AdminDashboardView,
    DashboardView,
    InstructorDashboardView,
    ProfileUpdateView,
    RegisterView,
    ResendVerificationView,
    StudentDashboardView,
    UserLoginView,
    UserLogoutView,
    UserPasswordChangeView,
    UserPasswordResetCompleteView,
    UserPasswordResetConfirmView,
    UserPasswordResetDoneView,
    UserPasswordResetView,
    VerifyEmailView,
)


app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path("instructor/dashboard/", InstructorDashboardView.as_view(), name="instructor_dashboard"),
    path("student/dashboard/", StudentDashboardView.as_view(), name="student_dashboard"),
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
    path("verify-email/<uidb64>/<token>/", VerifyEmailView.as_view(), name="verify_email"),
    path("verify-email/resend/", ResendVerificationView.as_view(), name="resend_verification"),
    path("password/change/", UserPasswordChangeView.as_view(), name="password_change"),
    path("password/reset/", UserPasswordResetView.as_view(), name="password_reset"),
    path("password/reset/done/", UserPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password/reset/<uidb64>/<token>/", UserPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password/reset/complete/", UserPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
