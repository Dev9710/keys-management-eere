from .settings_base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Local : SQLite pour démarrer sans rien installer
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Cookies non-secure en local (sinon login peut casser en http)
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Logging visible en local
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
    },
}
