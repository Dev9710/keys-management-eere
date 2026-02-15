import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # /home/python/src
PROJECT_DIR = os.path.join(BASE_DIR, "merchex")        # /home/python/src/merchex

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "merchex.settings_nas")
os.environ.setdefault("MYSQL_HOST", "merchex-db")
os.environ.setdefault("MYSQL_PORT", "3306")
os.environ.setdefault("MYSQL_DATABASE", "merchex")
os.environ.setdefault("MYSQL_USER", "merchex")
os.environ.setdefault("MYSQL_PASSWORD", "password")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
