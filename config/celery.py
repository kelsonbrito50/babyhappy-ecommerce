"""
Celery application for BabyHappy e-commerce.

Workers are started via docker-compose or:
    celery -A config worker -l info
    celery -A config beat -l info
"""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

app = Celery("babyhappy")

# Read config from Django settings, using CELERY_ namespace
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Celery self-check task — useful for smoke testing the broker."""
    print(f"Request: {self.request!r}")
