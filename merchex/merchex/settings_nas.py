from .settings_base import *
import os

# -----------------------------
# PROD / NAS
# -----------------------------
DEBUG = False

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "egliseevangeliqueparis12.org",
    "www.egliseevangeliqueparis12.org",
]

CSRF_TRUSTED_ORIGINS = [
    "https://egliseevangeliqueparis12.org",
    "https://www.egliseevangeliqueparis12.org",
]

# -----------------------------
# DATABASE (MySQL Docker)
# -----------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MYSQL_DATABASE", "merchex"),
        "USER": os.environ.get("MYSQL_USER", "merchex"),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD", "password"),
        "HOST": os.environ.get("MYSQL_HOST", "db"),
        "PORT": int(os.environ.get("MYSQL_PORT", "3306")),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "charset": "utf8mb4",
        },
    }
}

# -----------------------------
# Reverse proxy HTTPS (NAS)
# -----------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Si tu testes en HTTP direct (http://IP:8002), mettre False temporairement
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# -----------------------------
# LOGGING (Docker stdout)
# -----------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}
