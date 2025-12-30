import os
import sys

# Chemin vers la racine du projet (là où se trouve manage.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ajout explicite au PYTHONPATH (CRITIQUE pour Web Station)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Settings Django à utiliser
# Tu peux choisir settings.py ou settings.nas.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'merchex.settings_nas')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
