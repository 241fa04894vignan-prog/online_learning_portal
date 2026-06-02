from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "user", "course", "amount", "payment_status", "payment_method")
    list_filter = ("payment_status", "payment_method", "payment_date")
    search_fields = ("transaction_id", "user__username", "user__email", "course__title")
    readonly_fields = ("payment_date", "updated_at")

