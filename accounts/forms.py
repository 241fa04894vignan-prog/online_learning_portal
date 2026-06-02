from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError


User = get_user_model()


BOOTSTRAP_INPUT_CLASS = "form-control"
IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_PROFILE_IMAGE_SIZE = 2 * 1024 * 1024


def add_bootstrap_attrs(field, placeholder="", css_class=BOOTSTRAP_INPUT_CLASS):
    field.help_text = ""
    field.widget.attrs.update({"class": css_class, "placeholder": placeholder})
    return field


class UserRegistrationForm(UserCreationForm):
    """Secure registration form for the custom User model."""

    email = forms.EmailField(required=True)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "profile_image",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "username": "Choose a username",
            "first_name": "First name",
            "last_name": "Last name",
            "email": "Email address",
            "phone_number": "Phone number",
            "profile_image": "",
            "password1": "Create a strong password",
            "password2": "Confirm your password",
        }
        for name, field in self.fields.items():
            css_class = "form-control" if name != "profile_image" else "form-control"
            add_bootstrap_attrs(field, placeholders.get(name, ""), css_class)
        self.fields["profile_image"].widget.attrs.update({"accept": "image/png,image/jpeg,image/webp"})

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean_profile_image(self):
        image = self.cleaned_data.get("profile_image")
        if not image:
            return image
        content_type = getattr(image, "content_type", "")
        if not content_type:
            return image
        if content_type not in IMAGE_CONTENT_TYPES:
            raise ValidationError("Upload a JPG, PNG, or WEBP profile image.")
        if image.size > MAX_PROFILE_IMAGE_SIZE:
            raise ValidationError("Profile image must be 2 MB or smaller.")
        return image

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()
        user.role = getattr(User.Role, "STUDENT", "student")
        if commit:
            user.save()
        return user


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    """Login with either username or email address."""

    username = forms.CharField(label="Email or username", max_length=254)
    remember_me = forms.BooleanField(required=False)

    error_messages = {
        "invalid_login": "Please enter a correct email/username and password.",
        "inactive": "This account is inactive. Please contact support.",
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        add_bootstrap_attrs(self.fields["username"], "Email address or username")
        add_bootstrap_attrs(self.fields["password"], "Password")
        self.fields["password"].widget.attrs.update({"autocomplete": "current-password"})
        self.fields["remember_me"].widget.attrs.update({"class": "form-check-input"})

    def clean(self):
        login_value = self.cleaned_data.get("username", "").strip()
        password = self.cleaned_data.get("password")

        if login_value and password:
            username = login_value
            if "@" in login_value:
                user = User.objects.filter(email__iexact=login_value).only("username").first()
                if user:
                    username = user.get_username()

            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password,
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data



class UserProfileUpdateForm(forms.ModelForm):
    """Updates only fields that exist on the custom User model."""

    website = forms.URLField(required=False)
    linkedin_url = forms.URLField(required=False)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "bio",
            "profile_image",
            "website",
            "linkedin_url",
        )
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "first_name": "First name",
            "last_name": "Last name",
            "email": "Email address",
            "phone_number": "Phone number",
            "bio": "Short bio",
            "profile_image": "",
            "website": "https://example.com",
            "linkedin_url": "https://www.linkedin.com/in/username",
        }
        for name, field in self.fields.items():
            add_bootstrap_attrs(field, placeholders.get(name, ""))
        self.fields["profile_image"].widget.attrs.update({"accept": "image/png,image/jpeg,image/webp"})

        profile = getattr(self.instance, "instructor_profile", None)
        if profile:
            self.fields["website"].initial = profile.website
            self.fields["linkedin_url"].initial = profile.linkedin_url

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        exists = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists()
        if exists:
            raise ValidationError("This email address is already used by another account.")
        return email

    def clean_profile_image(self):
        image = self.cleaned_data.get("profile_image")
        if not image or isinstance(image, str):
            return image
        content_type = getattr(image, "content_type", "")
        if not content_type:
            return image
        if content_type not in IMAGE_CONTENT_TYPES:
            raise ValidationError("Upload a JPG, PNG, or WEBP profile image.")
        if image.size > MAX_PROFILE_IMAGE_SIZE:
            raise ValidationError("Profile image must be 2 MB or smaller.")
        return image

    def save(self, commit=True):
        user = super().save(commit=commit)
        profile = getattr(user, "instructor_profile", None)
        if profile:
            profile.website = self.cleaned_data.get("website", "")
            profile.linkedin_url = self.cleaned_data.get("linkedin_url", "")
            if commit:
                profile.save(update_fields=["website", "linkedin_url", "updated_at"])
        return user
