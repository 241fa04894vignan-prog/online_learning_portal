from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


def profile_image_upload_path(instance, filename):
    return f"profile_pics/user_{instance.pk or 'new'}/{filename}"


class User(AbstractUser):
    """Custom user model for students, instructors, and admins."""

    class Role(models.TextChoices):
        STUDENT = "student", _("Student")
        INSTRUCTOR = "instructor", _("Instructor")
        ADMIN = "admin", _("Admin")

    profile_image = models.ImageField(
        upload_to=profile_image_upload_path,
        blank=True,
        null=True,
        help_text="Optional profile photo.",
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\+?[0-9]{10,15}$",
                message="Enter a valid phone number with 10 to 15 digits.",
            )
        ],
    )
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    date_of_birth = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["role"], name="idx_user_role"),
            models.Index(fields=["is_verified"], name="idx_user_verified"),
        ]

    def __str__(self):
        return self.get_full_name() or self.username


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    education_level = models.CharField(max_length=120, blank=True)
    interests = models.TextField(blank=True)
    learning_goal = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_student_profile"
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"
        ordering = ["user__username"]

    def __str__(self):
        return f"Student Profile - {self.user}"


class InstructorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="instructor_profile",
    )
    expertise = models.CharField(max_length=255)
    years_of_experience = models.PositiveSmallIntegerField(default=0)
    website = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_instructor_profile"
        verbose_name = "Instructor Profile"
        verbose_name_plural = "Instructor Profiles"
        ordering = ["user__username"]
        indexes = [models.Index(fields=["is_approved"], name="idx_instructor_approved")]

    def __str__(self):
        return f"Instructor Profile - {self.user}"


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=150)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_notification"
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"], name="idx_notify_user_read"),
            models.Index(fields=["created_at"], name="idx_notify_created"),
        ]

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=180)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "accounts_contact_message"
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["is_resolved"], name="idx_contact_resolved")]

    def __str__(self):
        return f"{self.subject} - {self.email}"


class FAQ(models.Model):
    question = models.CharField(max_length=255, unique=True)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_faq"
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ["display_order", "question"]
        indexes = [models.Index(fields=["is_active"], name="idx_faq_active")]

    def __str__(self):
        return self.question


class UserActivityLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
    )
    action = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_user_activity_log"
        verbose_name = "User Activity Log"
        verbose_name_plural = "User Activity Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"], name="idx_activity_user_time"),
            models.Index(fields=["action"], name="idx_activity_action"),
        ]

    def __str__(self):
        return f"{self.action} at {self.created_at:%Y-%m-%d %H:%M}"

