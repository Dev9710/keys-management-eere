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
# DATABASE (MySQL via port NAS)
# -----------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MYSQL_DATABASE", "merchex"),
        "USER": os.environ.get("MYSQL_USER", "merchex"),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD", "password"),
        # Web Station => passe par le NAS (port exposé)
        "HOST": os.environ.get("MYSQL_HOST", "192.168.1.38"),
        "PORT": int(os.environ.get("MYSQL_PORT", "3307")),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# -----------------------------
# Reverse proxy HTTPS (NAS)
# -----------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Si tu testes en HTTP direct, laisse False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# -----------------------------
# Static
# -----------------------------
# Le site tourne sous Web Station (projet Python uWSGI), pas via notre
# Dockerfile : le code est monte sur /home/python/src et le front Web Station
# ne definit aucun alias /static. Avec DEBUG = False, Django refuse alors de
# servir /static -> les images des cartes de l'accueil repondaient 404.
#
# WhiteNoise fait servir /static par Django lui-meme, independamment de la
# configuration Web Station (donc reproductible depuis le depot). Le
# middleware est insere juste apres SecurityMiddleware, avant l'auth, pour
# court-circuiter les requetes statiques sans passer par la base.
MIDDLEWARE = list(MIDDLEWARE)
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
    "whitenoise.middleware.WhiteNoiseMiddleware",
)

# BASE_DIR = /home/python/src en prod : STATIC_ROOT vit donc a cote du code
# (sur le montage hote), et non dans le /app fige de l'image jamais servi.
STATIC_ROOT = os.environ.get("STATIC_ROOT", str(BASE_DIR / "staticfiles"))

# Sert directement depuis les dossiers static/ des apps : les images
# s'affichent meme si collectstatic n'a pas ete rejoue (Web Station ne le
# declenche pas de lui-meme).
WHITENOISE_USE_FINDERS = True

# -----------------------------
# LOGGING (stdout)
# -----------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "django.server": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django": {"handlers": ["console"], "level": "INFO"},
    },
}
