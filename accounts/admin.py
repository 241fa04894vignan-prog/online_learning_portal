from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    ContactMessage,
    FAQ,
    InstructorProfile,
    Notification,
    StudentProfile,
    User,
    UserActivityLog,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_verified", "is_staff", "date_joined")
    list_filter = ("role", "is_verified", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name", "phone_number")
    fieldsets = UserAdmin.fieldsets + (
        (
            "Portal Details",
            {
                "fields": (
                    "profile_image",
                    "phone_number",
                    "bio",
                    "role",
                    "date_of_birth",
                    "is_verified",
                )
            },
        ),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "education_level", "created_at")
    search_fields = ("user__username", "user__email", "education_level")


@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "expertise", "years_of_experience", "is_approved")
    list_filter = ("is_approved",)
    search_fields = ("user__username", "user__email", "expertise")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("title", "message", "user__username")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "is_resolved", "created_at")
    list_filter = ("is_resolved", "created_at")
    search_fields = ("name", "email", "subject")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "is_active", "display_order")
    list_editable = ("is_active", "display_order")
    search_fields = ("question", "answer")


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "ip_address", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("action", "description", "user__username", "ip_address")
    readonly_fields = ("created_at",)

