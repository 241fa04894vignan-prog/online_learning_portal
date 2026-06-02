from django.urls import path

from .views import (
    CourseCreateView,
    CourseDeleteView,
    CourseDetailView,
    CourseListView,
    CourseSearchView,
    CourseUpdateView,
    LessonCreateView,
    QuizCreateView,
    ReviewCreateView,
)


app_name = "courses"

urlpatterns = [
    path("", CourseListView.as_view(), name="list"),
    path("search/", CourseSearchView.as_view(), name="search"),
    path("add/", CourseCreateView.as_view(), name="add"),
    path("<slug:slug>/", CourseDetailView.as_view(), name="detail"),
    path("<slug:slug>/edit/", CourseUpdateView.as_view(), name="edit"),
    path("<slug:slug>/delete/", CourseDeleteView.as_view(), name="delete"),
    path("<slug:slug>/lessons/add/", LessonCreateView.as_view(), name="add_lesson"),
    path("<slug:slug>/quizzes/add/", QuizCreateView.as_view(), name="add_quiz"),
    path("<slug:slug>/reviews/add/", ReviewCreateView.as_view(), name="add_review"),
]
