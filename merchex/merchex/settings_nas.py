from django.contrib.messages import constants as messages
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# SECURITY
# -----------------------------
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "change-me-in-prod")

DEBUG = False  # ⚠️ En production : toujours False

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "www.egliseevangeliqueparis12.org",     # Ton domaine interne
    "egliseevangeliqueparis12.org"
]
CSRF_TRUSTED_ORIGINS = [
    "https://egliseevangeliqueparis12.org",
    "https://www.egliseevangeliqueparis12.org",
]


# -----------------------------
# APPLICATIONS
# -----------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'listings.apps.ListingsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
     'listings.middleware.LoginRequiredMiddleware',
    'listings.middleware.HistoryMiddleware',
    'listings.middleware.NoIndexMiddleware',
]

ROOT_URLCONF = 'merchex.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'merchex.wsgi.application'

# -----------------------------
# DATABASE
# Utilisation de MySQL dans Docker
# -----------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get("MYSQL_DATABASE", "merchex"),
        'USER': os.environ.get("MYSQL_USER", "merchex"),
        'PASSWORD': os.environ.get("MYSQL_PASSWORD", "password"),
        'HOST': os.environ.get("MYSQL_HOST", "db"),  # Service Docker
        'PORT': 3306,
        'OPTIONS': {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}

# -----------------------------
# PASSWORD VALIDATION
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -----------------------------
# INTERNATIONALISATION
# -----------------------------
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# -----------------------------
# STATIC FILES
# -----------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Collectstatic en production

# -----------------------------
# USER MODEL
# -----------------------------
AUTH_USER_MODEL = 'listings.Owner'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/home/'
LOGOUT_REDIRECT_URL = '/login/'

# -----------------------------
# MESSAGES
# -----------------------------
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# -----------------------------
# SESSIONS
# -----------------------------
SESSION_COOKIE_AGE = 1209600  # 2 semaines
SESSION_SAVE_EVERY_REQUEST = True

# -----------------------------
# EMAIL (désactivé)
# -----------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = "noreply@eere.com"

# -----------------------------
# HISTORIQUE
# -----------------------------
HISTORY_RETENTION_DAYS = 365


SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True


ROBOTS_META_TAG = "noindex, nofollow, noarchive"

