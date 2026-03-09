# Courses — система управления курсами

Веб-приложение для создания и управления образовательными курсами. Курсы состоят из частей, тем и документов.

## Требования

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Запуск

### Локальная разработка (runserver)

```bash
docker compose up --build
```

Приложение: **http://localhost:8000**

### Prod / Dev сервер (Gunicorn + Nginx)

```bash
ENVIRONMENT=prod docker compose --profile prod up --build -d
```

Приложение: **http://localhost** (порт 80) или **http://localhost:8000** (напрямую)

Для CI/CD: push в `dev` или `main` запускает deploy (environment: develop или production).

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `ENVIRONMENT` | `local` = runserver, `dev`/`prod` = gunicorn | `local` |
| `POSTGRES_DB` | Имя базы данных | `courses_db` |
| `POSTGRES_USER` | Пользователь PostgreSQL | `courses_user` |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL | `courses_password` |
| `DJANGO_SECRET_KEY` | Секретный ключ Django | (dev-ключ) |
| `DJANGO_DEBUG` | Режим отладки | `True` |
| `DJANGO_ALLOWED_HOSTS` | Разрешённые хосты | `localhost,127.0.0.1,0.0.0.0` |

Подробнее: [.env.example](.env.example).

## SSL (когда появится домен)

1. Указать домен в `nginx/nginx.conf` и раскомментировать HTTPS-блок.
2. Первый запуск Certbot:
   ```bash
   docker compose --profile prod run --rm certbot certonly --webroot -w /var/www/certbot -d yourdomain.com
   ```
3. Перезапустить nginx.


| Часть | Назначение |
|-------|------------|
| docker compose --profile prod | Использовать сервисы с профилем prod (в т.ч. certbot) |
| run | Запустить одноразовый контейнер (не фоновый сервис) |
| --rm | Удалить контейнер после завершения |
| certbot | Имя сервиса из docker-compose.yml |
| certonly | Только получить сертификат, без автоконфигурации |
| --webroot | Режим проверки через веб-сервер (nginx отдаёт `/.well-known/acme-challenge/`) |
| -w /var/www/certbot | Каталог webroot (Certbot кладёт сюда challenge-файлы) |
| -d yourdomain.com | Домен, для которого запрашивается сертификат |

### Что происходит

1. Certbot создаёт файл в /var/www/certbot/.well-known/acme-challenge/.
2. Let's Encrypt обращается к http://yourdomain.com/.well-known/acme-challenge/....
3. Nginx отдаёт этот файл из volume certbot_www.
4. Let's Encrypt подтверждает владение доменом и выдаёт сертификат.
5. Сертификат сохраняется в volume certbot_conf (`/etc/letsencrypt`).
6. Контейнер завершается и удаляется (`--rm`).

### Важно

- Nginx должен быть запущен и слушать порт 80.
- Домен yourdomain.com должен указывать на IP сервера.
- Перед запуском команды нужно подставить свой домен вместо yourdomain.com.

## Структура проекта

```
courses-main/
├── courses/           # Django-приложение
├── nginx/             # Конфиг Nginx (prod)
├── src/               # Настройки Django
├── docker-compose.yml
├── Dockerfile
└── entrypoint.sh
```

## CI и тесты

При push/PR в `main` или `dev` запускается:
- **flake8** — проверка стиля кода
- **isort** — проверка порядка импортов
- **Django tests** — юнит-тесты

Локально:
```bash
pip install -r requirements-dev.txt
flake8 .
isort . --check-only
docker compose exec web python manage.py test
```

### Блокировка merge при падении CI

Settings → Branches → Add rule → включить **Require status checks to pass before merging** и выбрать `lint` и `test`.

## Deploy (dev / prod)

Один workflow `.github/workflows/deploy.yml`:
- push в `dev` → environment: **develop**, ENVIRONMENT=dev
- push в `main` → environment: **production**, ENVIRONMENT=prod

### Настройка GitHub Environments

Settings → Environments → создать `develop` и `production`.

В каждом environment добавить **Secrets**:

| Secret | Описание |
|--------|----------|
| `SERVER_HOST` | IP или домен сервера |
| `SERVER_USER` | SSH-пользователь |
| `SSH_PRIVATE_KEY` | Приватный SSH-ключ |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL |
| `DJANGO_SECRET_KEY` | Секретный ключ Django |
| `POSTGRES_DB` | Имя БД (опционально) |
| `POSTGRES_USER` | Пользователь БД (опционально) |
| `POSTGRES_PORT` | Порт PostgreSQL (опционально) |
| `DJANGO_DEBUG` | `True` / `False` |
| `DJANGO_ALLOWED_HOSTS` | Разрешённые хосты |
| `CSRF_TRUSTED_ORIGINS` | Для HTTPS (опционально) |
| `DEPLOY_PATH` | Путь на сервере (по умолчанию `/app/courses`) |

Для `production` можно включить **Required reviewers** — ручное подтверждение перед деплоем.

### Подготовка сервера

1. Установить Docker и Docker Compose
2. Создать директорию: `mkdir -p /app/courses` (или путь из `DEPLOY_PATH`)
3. Настроить SSH-ключ для доступа

## Возможности

- Создание, редактирование и удаление курсов
- Части курса, темы, документы
- Пагинация списка курсов
