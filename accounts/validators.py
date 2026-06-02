import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordComplexityValidator:
    """Require upper, lower, digit, and symbol characters in user passwords."""

    def validate(self, password, user=None):
        checks = (
            (r"[A-Z]", "one uppercase letter"),
            (r"[a-z]", "one lowercase letter"),
            (r"[0-9]", "one number"),
            (r"[^A-Za-z0-9]", "one special character"),
        )
        missing = [message for pattern, message in checks if not re.search(pattern, password)]
        if missing:
            raise ValidationError(
                _("Your password must contain at least %(requirements)s."),
                code="password_no_complexity",
                params={"requirements": ", ".join(missing)},
            )

    def get_help_text(self):
        return _("Your password must contain uppercase, lowercase, number, and special characters.")
