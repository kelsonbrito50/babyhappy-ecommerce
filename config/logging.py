"""
Structured logging configuration for BabyHappy e-commerce.

Usage:
    from config.logging import LOGGING_CONFIG
    LOGGING = LOGGING_CONFIG

Or in settings:
    from config.logging import get_logging_config
    LOGGING = get_logging_config(log_dir=BASE_DIR / "logs", sentry_dsn=SENTRY_DSN)
"""
import os
from pathlib import Path


def get_logging_config(log_dir: Path = None, sentry_dsn: str = None) -> dict:
    """
    Build a LOGGING dict compatible with Django's LOGGING setting.

    Args:
        log_dir:    Optional directory path for file handlers.
                    If None, file handlers are disabled.
        sentry_dsn: Optional Sentry DSN. If provided, adds SentryHandler.
    """
    if log_dir is not None:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": "ext://sys.stdout",
        },
    }

    if log_dir is not None:
        handlers["file_app"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "verbose",
            "filename": str(log_dir / "app.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "encoding": "utf-8",
        }
        handlers["file_error"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "verbose",
            "filename": str(log_dir / "error.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "level": "ERROR",
            "encoding": "utf-8",
        }

    if sentry_dsn:
        handlers["sentry"] = {
            "class": "sentry_sdk.integrations.logging.EventHandler",
            "level": "ERROR",
        }

    # Decide which handlers to use for app loggers
    app_handlers = ["console"]
    if log_dir is not None:
        app_handlers += ["file_app", "file_error"]
    if sentry_dsn:
        app_handlers.append("sentry")

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": (
                    "[%(asctime)s] %(levelname)s %(name)s "
                    "%(module)s:%(lineno)d — %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "%(levelname)s %(message)s",
            },
        },
        "filters": {
            "require_debug_false": {
                "()": "django.utils.log.RequireDebugFalse",
            },
            "require_debug_true": {
                "()": "django.utils.log.RequireDebugTrue",
            },
        },
        "handlers": handlers,
        "loggers": {
            # Django internals
            "django": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "django.request": {
                "handlers": app_handlers,
                "level": "WARNING",
                "propagate": False,
            },
            "django.security": {
                "handlers": app_handlers,
                "level": "WARNING",
                "propagate": False,
            },
            # Application loggers
            "apps": {
                "handlers": app_handlers,
                "level": "DEBUG",
                "propagate": False,
            },
            "apps.accounts": {
                "handlers": app_handlers,
                "level": "INFO",
                "propagate": False,
            },
            "apps.orders": {
                "handlers": app_handlers,
                "level": "INFO",
                "propagate": False,
            },
            "apps.payments": {
                "handlers": app_handlers,
                "level": "INFO",
                "propagate": False,
            },
            "config": {
                "handlers": app_handlers,
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    }

    return config


# Default configuration (no file handlers — suitable for containers/dev)
LOGGING_CONFIG = get_logging_config()
