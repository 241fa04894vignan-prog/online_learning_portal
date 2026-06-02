# Online Learning Portal Frontend

Modern Django-compatible frontend for a production-style EdTech platform.

## Included

- Shared `base.html`, `navbar.html`, and `footer.html`
- Home, about, courses, course details, contact, login, signup, forgot password, and dashboard pages
- Bootstrap 5 CDN and Font Awesome integration
- Responsive CSS with variables, grid, flexbox, media queries, glassmorphism, shadows, gradients, and dark mode
- JavaScript for validation, password strength, counters, course filtering, OTP inputs, toast notifications, loader, ripple buttons, and scroll effects

## Django Notes

The project already uses:

```python
TEMPLATES = [{"DIRS": [BASE_DIR / "templates"], "APP_DIRS": True}]
STATICFILES_DIRS = [BASE_DIR / "static"]
```

That means the root-level `templates/` and `static/` folders are ready for backend integration.

## Current Routes

- `/`
- `/about/`
- `/courses/`
- `/courses/full-stack-django/`
- `/contact/`
- `/login/`
- `/signup/`
- `/forgot-password/`
- `/register/`
- `/dashboard/`
