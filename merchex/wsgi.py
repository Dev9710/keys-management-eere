import os
from django.core.wsgi import get_wsgi_application

# pointe vers TON settings nas dans le package Django interne
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "merchex.settings_nas")

application = get_wsgi_application()
