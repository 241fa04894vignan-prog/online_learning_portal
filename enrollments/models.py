import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


def certificate_upload_path(instance, filename):
    return f"certificates/user_{instance.student_id}/course_{instance.course_id}/{filename}"


class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        limit_choices_to={"role": "student"},
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "enrollments_enrollment"
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"
        ordering = ["-enrolled_at"]
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_student_course_enrollment")
        ]
        indexes = [
            models.Index(fields=["student", "completed"], name="idx_enroll_student_done"),
            models.Index(fields=["course", "completed"], name="idx_enroll_course_done"),
        ]

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"

    def save(self, *args, **kwargs):
        if self.completed and self.completion_date is None:
            self.completion_date = timezone.now()
        if not self.completed:
            self.completion_date = None
        super().save(*args, **kwargs)


class ProgressTracking(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_progress",
        limit_choices_to={"role": "student"},
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="progress_records",
    )
    lesson = models.ForeignKey(
        "courses.CourseLesson",
        on_delete=models.CASCADE,
        related_name="progress_records",
    )
    is_completed = models.BooleanField(default=False)
    progress_percentage = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    last_watched_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "enrollments_progress_tracking"
        verbose_name = "Progress Tracking"
        verbose_name_plural = "Progress Tracking"
        ordering = ["course", "lesson__order"]
        constraints = [
            models.UniqueConstraint(fields=["student", "lesson"], name="unique_student_lesson_progress")
        ]
        indexes = [
            models.Index(fields=["student", "course"], name="idx_progress_student_course"),
            models.Index(fields=["lesson", "is_completed"], name="idx_progress_lesson_done"),
        ]

    def __str__(self):
        return f"{self.student} - {self.lesson} ({self.progress_percentage}%)"

    def clean(self):
        if self.lesson_id and self.course_id and self.lesson.course_id != self.course_id:
            raise ValidationError({"lesson": "Selected lesson does not belong to this course."})

    def save(self, *args, **kwargs):
        if self.progress_percentage == 100:
            self.is_completed = True
        if self.is_completed and self.completed_at is None:
            self.completed_at = timezone.now()
        if not self.is_completed:
            self.completed_at = None
        self.full_clean()
        super().save(*args, **kwargs)


class Certificate(models.Model):
    certificate_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certificates",
        limit_choices_to={"role": "student"},
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="certificates",
    )
    certificate_file = models.FileField(upload_to=certificate_upload_path, blank=True, null=True)
    issue_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "enrollments_certificate"
        verbose_name = "Certificate"
        verbose_name_plural = "Certificates"
        ordering = ["-issue_date"]
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_student_course_certificate")
        ]
        indexes = [models.Index(fields=["certificate_id"], name="idx_certificate_id")]

    def __str__(self):
        return f"Certificate {self.certificate_id}"


class Wishlist(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
        limit_choices_to={"role": "student"},
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="wishlisted_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "enrollments_wishlist"
        verbose_name = "Wishlist Item"
        verbose_name_plural = "Wishlist Items"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_student_course_wishlist")
        ]
        indexes = [models.Index(fields=["student", "created_at"], name="idx_wishlist_student_time")]

    def __str__(self):
        return f"{self.student} saved {self.course}"

