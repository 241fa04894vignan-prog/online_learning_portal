from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError

from reviews.models import Review

from .models import Course, CourseCategory, CourseLesson, Quiz


BOOTSTRAP_INPUT_CLASS = "form-control"
IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_COURSE_IMAGE_SIZE = 3 * 1024 * 1024


def apply_bootstrap(field, placeholder=""):
    field.widget.attrs.update({"class": BOOTSTRAP_INPUT_CLASS, "placeholder": placeholder})
    field.help_text = ""
    return field


class CourseForm(forms.ModelForm):
    duration = forms.DurationField(
        help_text="",
        widget=forms.TextInput(attrs={"placeholder": "HH:MM:SS, for example 10:30:00"}),
    )

    class Meta:
        model = Course
        fields = (
            "title",
            "category",
            "thumbnail",
            "description",
            "price",
            "discount_price",
            "duration",
            "level",
            "language",
            "requirements",
            "what_you_will_learn",
            "is_published",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "requirements": forms.Textarea(attrs={"rows": 4}),
            "what_you_will_learn": forms.Textarea(attrs={"rows": 4}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "title": "Course title",
            "category": "Choose category",
            "thumbnail": "",
            "description": "Course description",
            "price": "Course price",
            "discount_price": "Discount price",
            "duration": "HH:MM:SS",
            "level": "Choose level",
            "language": "Course language",
            "requirements": "Course requirements",
            "what_you_will_learn": "What students will learn",
        }
        self.fields["category"].queryset = CourseCategory.objects.filter(is_active=True).order_by("name")
        for name, field in self.fields.items():
            if name != "is_published":
                apply_bootstrap(field, placeholders.get(name, ""))
        self.fields["thumbnail"].widget.attrs.update({"accept": "image/png,image/jpeg,image/webp"})

    def clean_thumbnail(self):
        image = self.cleaned_data.get("thumbnail")
        if not image or isinstance(image, str):
            return image
        content_type = getattr(image, "content_type", "")
        if not content_type:
            return image
        if content_type not in IMAGE_CONTENT_TYPES:
            raise ValidationError("Upload a JPG, PNG, or WEBP course thumbnail.")
        if image.size > MAX_COURSE_IMAGE_SIZE:
            raise ValidationError("Course thumbnail must be 3 MB or smaller.")
        return image

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get("price")
        discount_price = cleaned_data.get("discount_price")
        duration = cleaned_data.get("duration")

        if price is not None and discount_price is not None and discount_price > price:
            self.add_error("discount_price", "Discount price cannot be greater than course price.")
        if isinstance(duration, timedelta) and duration.total_seconds() <= 0:
            self.add_error("duration", "Duration must be greater than zero.")
        return cleaned_data


class CourseLessonForm(forms.ModelForm):
    class Meta:
        model = CourseLesson
        fields = ("title", "description", "video_file", "video_url", "duration", "order", "is_preview")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "duration": forms.TextInput(attrs={"placeholder": "HH:MM:SS"}),
            "is_preview": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop("course", None)
        super().__init__(*args, **kwargs)
        placeholders = {
            "title": "Lesson title",
            "description": "Lesson description",
            "video_file": "",
            "video_url": "https://example.com/video",
            "duration": "HH:MM:SS",
            "order": "Lesson order",
        }
        for name, field in self.fields.items():
            if name != "is_preview":
                apply_bootstrap(field, placeholders.get(name, ""))
        self.fields["video_file"].widget.attrs.update({"accept": ".mp4,.mov,.avi,.mkv"})

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("video_file") and not cleaned_data.get("video_url"):
            raise ValidationError("Provide either a video file or a video URL.")
        return cleaned_data

    def save(self, commit=True):
        lesson = super().save(commit=False)
        if self.course:
            lesson.course = self.course
        if commit:
            lesson.save()
        return lesson


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ("lesson", "title", "description", "passing_score", "time_limit_minutes", "is_active")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop("course", None)
        super().__init__(*args, **kwargs)
        if self.course:
            self.fields["lesson"].queryset = self.course.lessons.all()
        placeholders = {
            "lesson": "Optional lesson",
            "title": "Quiz title",
            "description": "Quiz description",
            "passing_score": "Passing score",
            "time_limit_minutes": "Time limit in minutes",
        }
        for name, field in self.fields.items():
            if name != "is_active":
                apply_bootstrap(field, placeholders.get(name, ""))

    def clean_passing_score(self):
        score = self.cleaned_data["passing_score"]
        if score > 100:
            raise ValidationError("Passing score cannot be greater than 100.")
        return score

    def save(self, commit=True):
        quiz = super().save(commit=False)
        if self.course:
            quiz.course = self.course
        if commit:
            quiz.save()
        return quiz


class CourseSearchForm(forms.Form):
    q = forms.CharField(required=False, label="", max_length=120)
    category = forms.ModelChoiceField(required=False, queryset=CourseCategory.objects.none())
    level = forms.ChoiceField(required=False, choices=[("", "All levels"), *Course.Level.choices])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = CourseCategory.objects.filter(is_active=True).order_by("name")
        apply_bootstrap(self.fields["q"], "Search courses")
        apply_bootstrap(self.fields["category"], "Category")
        apply_bootstrap(self.fields["level"], "Level")


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "review")
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "review": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap(self.fields["rating"], "Rating from 1 to 5")
        apply_bootstrap(self.fields["review"], "Write your review")

    def clean_rating(self):
        rating = self.cleaned_data["rating"]
        if not 1 <= rating <= 5:
            raise ValidationError("Rating must be between 1 and 5.")
        return rating
