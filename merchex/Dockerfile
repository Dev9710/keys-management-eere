FROM python:3.11-slim

WORKDIR /app

# Installer dépendances système MySQL
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev build-essential && \
    apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=merchex.settings
ENV PYTHONUNBUFFERED=1

# Collecte des fichiers statiques
RUN python manage.py collectstatic --noinput

# Démarrer Gunicorn
CMD ["gunicorn", "merchex.wsgi:application", "-b", "0.0.0.0:8000"]
