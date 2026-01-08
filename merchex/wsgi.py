import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # /home/python/src
PROJECT_DIR = os.path.join(BASE_DIR, "merchex")        # /home/python/src/merchex

# Ajoute /home/python/src
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Ajoute /home/python/src/merchex  (IMPORTANT)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "merchex.merchex.settings_nas")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
