"""
Development settings for BabyHappy e-commerce.

Inherits from base.py. Suitable for local development with Docker Compose
(PostgreSQL + Redis containers) and standalone development.
"""
from .base import *  # noqa: F401,F403

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "*"]

# ---------------------------------------------------------------------------
# Security (relaxed for development)
# ---------------------------------------------------------------------------

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# ---------------------------------------------------------------------------
# Email (console backend for development)
# ---------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ---------------------------------------------------------------------------
# Debug Toolbar (optional — install django-debug-toolbar to enable)
# ---------------------------------------------------------------------------

try:
    import debug_toolbar  # noqa: F401
    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
    INTERNAL_IPS = ["127.0.0.1"]
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Celery (eager for synchronous dev testing)
# ---------------------------------------------------------------------------

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ---------------------------------------------------------------------------
# Logging (verbose console output in dev)
# ---------------------------------------------------------------------------

LOGGING["loggers"]["apps"]["level"] = "DEBUG"  # noqa: F405
