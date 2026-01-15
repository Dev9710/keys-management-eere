#!/bin/sh
set -e

echo "Waiting for DB..."
python - <<'PY'
import os, time, socket
host=os.environ.get("MYSQL_HOST","db")
port=int(os.environ.get("MYSQL_PORT","3306"))
for i in range(60):
    try:
        socket.create_connection((host, port), timeout=2).close()
        print("DB is up")
        break
    except OSError:
        time.sleep(2)
else:
    raise SystemExit("DB not reachable")
PY

echo "Migrate..."
python manage.py migrate --noinput

# ✅ Import initial des données (une seule fois)
if [ -f "/app/data.json" ] && [ ! -f "/app/.data_loaded" ]; then
  echo "Loading initial data from /app/data.json..."
  python manage.py loaddata /app/data.json
  touch /app/.data_loaded
  echo "Data import done."
else
  echo "No data.json to import or already imported."
fi

echo "Collectstatic..."
python manage.py collectstatic --noinput || true

# (optionnel) créer un superuser automatiquement si variables définies
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
  echo "Ensuring superuser exists..."
  python manage.py shell -c "
from django.contrib.auth import get_user_model
User=get_user_model()
u='$DJANGO_SUPERUSER_USERNAME'
e='$DJANGO_SUPERUSER_EMAIL'
p='$DJANGO_SUPERUSER_PASSWORD'
if not User.objects.filter(username=u).exists():
    User.objects.create_superuser(username=u, email=e, password=p)
    print('Superuser created')
else:
    print('Superuser already exists')
"
fi

echo "Start uWSGI..."
uwsgi --ini /app/uwsgi.ini
