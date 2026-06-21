# StudyLog

[![Tests](https://github.com/shlegeldavid/studylog-flask/actions/workflows/tests.yml/badge.svg)](https://github.com/shlegeldavid/studylog-flask/actions/workflows/tests.yml)

StudyLog - небольшой учебный веб-проект на Flask. Это микроблог для коротких заметок об учебе: пользователь может зарегистрироваться, войти, опубликовать заметку, открыть общую ленту, посмотреть профиль и подписаться на других пользователей.

## Стек

- Python 3.11 или 3.12
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Login
- Flask-WTF
- Gunicorn
- SQLite для локальной разработки
- PostgreSQL через переменную `DATABASE_URL`
- Pytest

## Что уже реализовано

- app factory и разделение на blueprints `auth` и `main`
- регистрация, вход и выход
- модель `User`, модель `Post` и связь подписок `followers`
- публикация коротких заметок
- персональная лента для авторизованного пользователя
- общая лента всех заметок
- профиль пользователя и редактирование профиля
- подписка и отписка от других пользователей
- route `/health` для проверки доступности приложения
- базовые HTML-шаблоны на Jinja2 и простой CSS
- минимальные тесты на `pytest`

## Структура проекта

```text
app/
  auth/
  main/
  static/
  templates/
tests/
config.py
requirements.txt
wsgi.py
```

## Локальный запуск

1. Создайте и активируйте виртуальное окружение:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` по примеру `.env.example`.

Основные переменные окружения:

- `SECRET_KEY` - секретный ключ Flask
- `DATABASE_URL` - строка подключения к SQLite или PostgreSQL
- `FLASK_ENV=development` и `FLASK_DEBUG=1` - удобно для локальной разработки

4. Инициализируйте базу данных:

```bash
flask --app wsgi init-db
```

5. Запустите сервер:

```bash
flask --app wsgi run
```

Проект будет доступен по адресу `http://127.0.0.1:5000`.

Проверка health endpoint:

```bash
curl http://127.0.0.1:5000/health
```

## Миграции

`Flask-Migrate` уже подключен. Если захотите вести таблицы через миграции, используйте:

```bash
flask --app wsgi db init
flask --app wsgi db migrate -m "Initial tables"
flask --app wsgi db upgrade
```

## Тесты

```bash
pytest
```

## Деплой на Railway

Для простого деплоя достаточно подключить репозиторий к Railway и добавить PostgreSQL-сервис, если хотите хранить данные не в SQLite.

## Деплой

Ссылка на деплой: https://studylog-flask-production.up.railway.app/

## Тестовые данные

После выполнения команды `flask --app wsgi seed-demo` можно войти под тестовым пользователем:

login: demo  
password: demo123

### Переменные окружения

Укажите в Railway:

- `SECRET_KEY` - свой случайный секретный ключ
- `DATABASE_URL` - Railway обычно подставит ее автоматически после подключения PostgreSQL
- `FLASK_ENV=production`

SQLite остается удобным вариантом только для локального запуска.

### Build command

```bash
pip install -r requirements.txt
```

### Start command

```bash
gunicorn --bind 0.0.0.0:${PORT:-8000} wsgi:app
```

### Инициализация базы

В проекте пока нет сохраненных миграций, поэтому для первого запуска проще выполнить инициализацию таблиц командой:

```bash
flask --app wsgi init-db
```

Если хотите сразу загрузить учебные демо-данные:

```bash
flask --app wsgi seed-demo
```

Эти команды удобно запускать через Railway Shell или как one-off command после первого деплоя.

### Файл конфигурации Railway

В репозиторий добавлен `railway.toml`. Railway сейчас использует `railway.toml` или `railway.json` для config-as-code, поэтому `railway.yaml` здесь не нужен.

## Что можно улучшить следующим коммитом

- добавить готовые файлы миграций в репозиторий после первого `flask --app wsgi db migrate`
- добавить больше тестов на валидацию форм и сценарии подписок
