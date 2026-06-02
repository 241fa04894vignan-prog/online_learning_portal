from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """Token invalidates after verification, password change, or last login change."""

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.password}{user.last_login}{user.is_verified}"


email_verification_token = EmailVerificationTokenGenerator()
