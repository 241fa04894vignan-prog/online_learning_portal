"""
URL configuration for online_learning_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import TemplateView
from registerpageapp import views as rv
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',rv.student_view),

    path('', include('accounts.urls')),
    path('accounts/', include('accounts.urls')),
    path('learning-courses/', include('courses.urls')),
    path('', include('homepageapp.urls')),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
    path('login/', include('loginpageapp.urls')),
    path('signup/', TemplateView.as_view(template_name='signup.html'), name='signup'),
    path('forgot-password/', TemplateView.as_view(template_name='forgot_password.html'), name='forgot_password'),
    path('register/', include('registerpageapp.urls')),
    path('dashboard/', include('dashboardapp.urls')),
    path('courses/', include('coursespageapp.urls')),
    path('courses/full-stack-django/', TemplateView.as_view(template_name='course_details.html'), name='course_details'),
    path('quiz/', include('quizpageapp.urls')),
    path('result/', include('resultpageapp.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
