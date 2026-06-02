from django.contrib import admin

from .models import (
    Course,
    CourseCategory,
    CourseLesson,
    CourseResource,
    Quiz,
    QuizAnswer,
    QuizQuestion,
)


class CourseLessonInline(admin.TabularInline):
    model = CourseLesson
    extra = 1


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_editable = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "instructor", "category", "price", "discount_price", "is_published")
    list_filter = ("is_published", "level", "category", "language")
    search_fields = ("title", "description", "instructor__username")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CourseLessonInline]


@admin.register(CourseLesson)
class CourseLessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "is_preview")
    list_filter = ("is_preview", "course")
    search_fields = ("title", "course__title")


@admin.register(CourseResource)
class CourseResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "lesson", "created_at")
    search_fields = ("title", "course__title", "lesson__title")


class QuizAnswerInline(admin.TabularInline):
    model = QuizAnswer
    extra = 4


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "order", "points", "question_type")
    inlines = [QuizAnswerInline]
    search_fields = ("question_text", "quiz__title")


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "passing_score", "is_active")
    list_filter = ("is_active", "course")
    search_fields = ("title", "course__title")


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ("answer_text", "question", "is_correct", "order")
    list_filter = ("is_correct",)
    search_fields = ("answer_text", "question__question_text")

