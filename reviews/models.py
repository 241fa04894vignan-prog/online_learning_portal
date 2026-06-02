from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_reviews",
        limit_choices_to={"role": "student"},
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="course_reviews",
    )
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reviews_review"
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_student_course_review")
        ]
        indexes = [
            models.Index(fields=["course", "rating"], name="idx_review_course_rating"),
            models.Index(fields=["student"], name="idx_review_student"),
        ]

    def __str__(self):
        return f"{self.course} - {self.rating}/5 by {self.student}"

