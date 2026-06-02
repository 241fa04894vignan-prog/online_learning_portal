from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _


def course_thumbnail_upload_path(instance, filename):
    return f"course_thumbnails/course_{instance.pk or 'new'}/{filename}"


def lesson_video_upload_path(instance, filename):
    return f"course_videos/course_{instance.course_id or 'new'}/{filename}"


def course_resource_upload_path(instance, filename):
    return f"course_resources/course_{instance.course_id or 'new'}/{filename}"


class CourseCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "courses_category"
        verbose_name = "Course Category"
        verbose_name_plural = "Course Categories"
        ordering = ["name"]
        indexes = [models.Index(fields=["slug"], name="idx_category_slug")]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    class Level(models.TextChoices):
        BEGINNER = "beginner", _("Beginner")
        INTERMEDIATE = "intermediate", _("Intermediate")
        ADVANCED = "advanced", _("Advanced")
        ALL_LEVELS = "all_levels", _("All Levels")

    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="courses_taught",
        limit_choices_to={"role": "instructor"},
    )
    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.PROTECT,
        related_name="courses",
    )
    thumbnail = models.ImageField(
        upload_to=course_thumbnail_upload_path,
        blank=True,
        null=True,
    )
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    duration = models.DurationField(help_text="Total course duration, for example 10:30:00.")
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER)
    language = models.CharField(max_length=80, default="English")
    requirements = models.TextField(blank=True)
    what_you_will_learn = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "courses_course"
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"], name="idx_course_slug"),
            models.Index(fields=["is_published"], name="idx_course_published"),
            models.Index(fields=["category", "is_published"], name="idx_course_category_pub"),
            models.Index(fields=["instructor"], name="idx_course_instructor"),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        if self.discount_price is not None and self.discount_price > self.price:
            raise ValidationError({"discount_price": "Discount price cannot be greater than price."})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        self.full_clean()
        super().save(*args, **kwargs)

    def get_average_rating(self):
        average = self.course_reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"]
        return round(average or 0, 1)

    def get_discount_percentage(self):
        if not self.discount_price or self.price <= 0:
            return 0
        discount = ((self.price - self.discount_price) / self.price) * 100
        return int(discount)

    def total_students_enrolled(self):
        return self.enrollments.count()


class CourseLesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    video_file = models.FileField(
        upload_to=lesson_video_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["mp4", "mov", "avi", "mkv"])],
    )
    video_url = models.URLField(blank=True)
    duration = models.DurationField(blank=True, null=True)
    order = models.PositiveIntegerField(default=1)
    is_preview = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "courses_lesson"
        verbose_name = "Course Lesson"
        verbose_name_plural = "Course Lessons"
        ordering = ["course", "order"]
        constraints = [
            models.UniqueConstraint(fields=["course", "order"], name="unique_lesson_order_per_course")
        ]
        indexes = [models.Index(fields=["course", "order"], name="idx_lesson_course_order")]

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def clean(self):
        if not self.video_file and not self.video_url:
            raise ValidationError("Provide either a video file or a video URL.")


class CourseResource(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="resources")
    lesson = models.ForeignKey(
        CourseLesson,
        on_delete=models.CASCADE,
        related_name="resources",
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=180)
    file = models.FileField(
        upload_to=course_resource_upload_path,
        validators=[FileExtensionValidator(["pdf", "doc", "docx", "ppt", "pptx", "zip", "txt"])],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "courses_resource"
        verbose_name = "Course Resource"
        verbose_name_plural = "Course Resources"
        ordering = ["course", "title"]
        indexes = [models.Index(fields=["course"], name="idx_resource_course")]

    def __str__(self):
        return self.title


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="quizzes")
    lesson = models.ForeignKey(
        CourseLesson,
        on_delete=models.CASCADE,
        related_name="quizzes",
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    passing_score = models.PositiveSmallIntegerField(default=60)
    time_limit_minutes = models.PositiveSmallIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "courses_quiz"
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"
        ordering = ["course", "title"]
        indexes = [models.Index(fields=["course", "is_active"], name="idx_quiz_course_active")]

    def __str__(self):
        return self.title

    def clean(self):
        if self.passing_score > 100:
            raise ValidationError({"passing_score": "Passing score cannot be greater than 100."})

    def total_points(self):
        return self.questions.aggregate(total=models.Sum("points"))["total"] or 0


class QuizQuestion(models.Model):
    class QuestionType(models.TextChoices):
        MCQ = "mcq", _("Multiple Choice")

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QuestionType.choices, default=QuestionType.MCQ)
    points = models.PositiveSmallIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "courses_quiz_question"
        verbose_name = "Quiz Question"
        verbose_name_plural = "Quiz Questions"
        ordering = ["quiz", "order"]
        constraints = [
            models.UniqueConstraint(fields=["quiz", "order"], name="unique_question_order_per_quiz")
        ]
        indexes = [models.Index(fields=["quiz", "order"], name="idx_question_quiz_order")]

    def __str__(self):
        return f"{self.quiz.title} - Question {self.order}"


class QuizAnswer(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name="answers")
    answer_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "courses_quiz_answer"
        verbose_name = "Quiz Answer"
        verbose_name_plural = "Quiz Answers"
        ordering = ["question", "order"]
        constraints = [
            models.UniqueConstraint(fields=["question", "order"], name="unique_answer_order_per_question")
        ]
        indexes = [models.Index(fields=["question", "is_correct"], name="idx_answer_question_correct")]

    def __str__(self):
        return self.answer_text

