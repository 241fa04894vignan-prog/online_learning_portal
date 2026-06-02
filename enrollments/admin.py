from django.contrib import admin

from .models import Certificate, Enrollment, ProgressTracking, Wishlist


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "completed", "enrolled_at", "completion_date")
    list_filter = ("completed", "enrolled_at")
    search_fields = ("student__username", "student__email", "course__title")


@admin.register(ProgressTracking)
class ProgressTrackingAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "lesson", "progress_percentage", "is_completed")
    list_filter = ("is_completed", "course")
    search_fields = ("student__username", "course__title", "lesson__title")


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("certificate_id", "student", "course", "issue_date")
    search_fields = ("certificate_id", "student__username", "course__title")
    readonly_fields = ("certificate_id", "issue_date")


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "created_at")
    search_fields = ("student__username", "course__title")

