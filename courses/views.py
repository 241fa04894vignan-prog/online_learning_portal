from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from enrollments.models import Enrollment
from reviews.models import Review

from .forms import CourseForm, CourseLessonForm, CourseSearchForm, QuizForm, ReviewForm
from .models import Course, Quiz


class InstructorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_staff or getattr(user, "role", "") == "instructor"

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("Only instructors can manage courses.")
        return super().handle_no_permission()


class CourseOwnerRequiredMixin(InstructorRequiredMixin):
    def test_func(self):
        if not super().test_func():
            return False
        course = self.get_object()
        return self.request.user.is_staff or course.instructor_id == self.request.user.id


class CourseListView(ListView):
    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"
    paginate_by = 9

    def get_queryset(self):
        queryset = (
            Course.objects.filter(is_published=True)
            .select_related("category", "instructor")
            .annotate(total_students=Count("enrollments", distinct=True), total_reviews=Count("course_reviews", distinct=True))
        )
        self.search_form = CourseSearchForm(self.request.GET or None)
        if self.search_form.is_valid():
            q = self.search_form.cleaned_data.get("q")
            category = self.search_form.cleaned_data.get("category")
            level = self.search_form.cleaned_data.get("level")
            if q:
                queryset = queryset.filter(
                    Q(title__icontains=q)
                    | Q(description__icontains=q)
                    | Q(category__name__icontains=q)
                    | Q(instructor__username__icontains=q)
                )
            if category:
                queryset = queryset.filter(category=category)
            if level:
                queryset = queryset.filter(level=level)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = getattr(self, "search_form", CourseSearchForm())
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        queryset = Course.objects.select_related("category", "instructor").prefetch_related(
            "lessons", "resources", "quizzes", "course_reviews__student"
        )
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset
        if self.request.user.is_authenticated:
            return queryset.filter(Q(is_published=True) | Q(instructor=self.request.user))
        return queryset.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        course = self.object
        context["reviews"] = course.course_reviews.select_related("student")[:10]
        context["review_form"] = ReviewForm()
        context["is_enrolled"] = False
        context["user_review"] = None
        if user.is_authenticated:
            context["is_enrolled"] = Enrollment.objects.filter(student=user, course=course).exists()
            context["user_review"] = Review.objects.filter(student=user, course=course).first()
        return context


class CourseCreateView(InstructorRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "courses/add_course.html"

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        messages.success(self.request, "Course created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("courses:detail", kwargs={"slug": self.object.slug})


class CourseUpdateView(CourseOwnerRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "courses/edit_course.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def form_valid(self, form):
        messages.success(self.request, "Course updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("courses:detail", kwargs={"slug": self.object.slug})


class CourseDeleteView(CourseOwnerRequiredMixin, DeleteView):
    model = Course
    template_name = "courses/delete_course.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("courses:list")

    def form_valid(self, form):
        messages.success(self.request, "Course deleted successfully.")
        return super().form_valid(form)


class CourseSearchView(CourseListView):
    pass


class LessonCreateView(InstructorRequiredMixin, CreateView):
    form_class = CourseLessonForm
    template_name = "courses/add_lesson.html"

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs["slug"])
        if not request.user.is_staff and self.course.instructor_id != request.user.id:
            raise PermissionDenied("You can only add lessons to your own courses.")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["course"] = self.course
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Lesson added successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("courses:detail", kwargs={"slug": self.course.slug})


class QuizCreateView(InstructorRequiredMixin, CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = "courses/add_quiz.html"

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs["slug"])
        if not request.user.is_staff and self.course.instructor_id != request.user.id:
            raise PermissionDenied("You can only add quizzes to your own courses.")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["course"] = self.course
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Quiz added successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("courses:detail", kwargs={"slug": self.course.slug})


class ReviewCreateView(LoginRequiredMixin, CreateView):
    form_class = ReviewForm
    http_method_names = ["post"]

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs["slug"], is_published=True)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        if getattr(user, "role", "") != "student":
            raise PermissionDenied("Only students can review courses.")
        if not Enrollment.objects.filter(student=user, course=self.course).exists():
            messages.error(self.request, "Enroll in the course before adding a review.")
            return redirect("courses:detail", slug=self.course.slug)
        review, created = Review.objects.update_or_create(
            student=user,
            course=self.course,
            defaults={"rating": form.cleaned_data["rating"], "review": form.cleaned_data["review"]},
        )
        self.object = review
        messages.success(self.request, "Review submitted successfully." if created else "Review updated successfully.")
        return redirect("courses:detail", slug=self.course.slug)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the review form and try again.")
        return redirect("courses:detail", slug=self.course.slug)
