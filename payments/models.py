from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        SUCCESS = "success", _("Success")
        FAILED = "failed", _("Failed")
        REFUNDED = "refunded", _("Refunded")

    class Method(models.TextChoices):
        CARD = "card", _("Card")
        UPI = "upi", _("UPI")
        NET_BANKING = "net_banking", _("Net Banking")
        WALLET = "wallet", _("Wallet")
        CASH = "cash", _("Cash")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    course = models.ForeignKey("courses.Course", on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    payment_status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    transaction_id = models.CharField(max_length=120, unique=True)
    payment_method = models.CharField(max_length=20, choices=Method.choices)
    payment_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments_payment"
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-payment_date"]
        indexes = [
            models.Index(fields=["user", "payment_status"], name="idx_payment_user_status"),
            models.Index(fields=["transaction_id"], name="idx_payment_transaction"),
        ]

    def __str__(self):
        return f"{self.transaction_id} - {self.payment_status}"

