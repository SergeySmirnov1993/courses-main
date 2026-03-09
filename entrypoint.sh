#!/bin/sh
# Entrypoint скрипт для Django приложения
# Ожидает готовности PostgreSQL, применяет миграции и запускает сервер

set -e

echo "Ожидаем готовности PostgreSQL..."
python scripts/wait_for_db.py || exit 1

echo "Применяем миграции..."
python manage.py migrate --noinput

if [ "$ENVIRONMENT" = "local" ]; then
  echo "Запускаем сервер..."
  python manage.py runserver 0.0.0.0:8000
else
  echo "Собираем статические файлы..."
  python manage.py collectstatic --noinput
  echo "Запускаем сервер..."
  gunicorn src.wsgi:application --bind 0.0.0.0:8000 --workers 2
fi