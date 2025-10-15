# Learning Site Final — установка и запуск

## Требования
- Python 3.12+
- pip
- (Опционально) Docker и Docker Compose
- Windows (поддержан упрощённый Kerberos/Windows Auth), но проект кроссплатформенный

## Быстрый старт (локально, без Docker)
1. Клонируйте репозиторий:
   - через GitHub Desktop или командой:
     ```bash
     git clone https://github.com/IVANIArgb/LearningSiteFinalVer.git
     ```
2. Перейдите в папку `site`:
   ```bash
   cd site
   ```
3. Создайте виртуальное окружение (опционально) и установите зависимости:
   ```bash
   python -m venv venv
   # Windows PowerShell:
   .\\venv\\Scripts\\Activate.ps1
   pip install -r requirements.txt
   ```
4. Запустите приложение:
   ```bash
   python run.py
   ```
5. Откройте в браузере:
   - http://127.0.0.1:5000

Примечания:
- При первом заходе пользователь будет автоматически зарегистрирован в БД как `user` (упрощённая Kerberos/Windows-аутентификация).
- Тестовые данные (пользователи, курсы, уроки, вопросы и ответы) создаются автоматически, наполнение идемпотентное.
- Проверка текущего пользователя: `GET /user/info-test` — возвращает JSON из контекста аутентификации (без обращений к БД).

## Запуск в Docker
1. Перейдите в папку `site` и соберите контейнер:
   ```bash
   docker compose build
   ```
2. Запустите:
   ```bash
   docker compose up -d
   ```
3. Откройте:
   - http://127.0.0.1:8000

Тома:
- `uploads` монтируется в `/app/backend/uploads`
- `logs` монтируется в `/app/backend/logs`

Переменные окружения (см. `docker-compose.yml`):
- `FLASK_ENV=production`
- `KERBEROS_AUTH_ENABLED=true`
- `KERBEROS_SERVICE_NAME=HTTP`
- `KERBEROS_REALM=EXAMPLE.COM`

## Основные эндпоинты
- Роутинг статических страниц с учётом роли: `/main`, `/questions`, `/users-info` и т.п.
- API (фрагмент):
  - `GET /api/current-user` — инфо о пользователе из БД
  - `GET /api/users` — список пользователей
  - `GET /api/courses` — список курсов
  - Q&A:
    - `GET /api/questions` — список вопросов (фильтры: `search`, `resolved`, `mine`)
    - `POST /api/questions` — создать вопрос (поля: `title`, `body`, `tags[]`)
    - `GET /api/questions/{id}` — получить вопрос с ответами и вложениями
    - `POST /api/questions/{id}/answers` — ответ администратора
    - `POST /api/questions/{id}/attachments` — вложения к вопросу
    - `POST /answers/{id}/attachments` — вложения к ответу
  - `GET /user/info-test` — JSON о текущем пользователе из контекста аутентификации

## Роли и аутентификация
- Контекст аутентификации формируется в `backend/simplified_real_kerberos_auth.py`.
- `g.user_info` содержит: `username`, `role`, `auth_method`, `ip_address`, `hostname`, `principal` (если есть).
- Если Kerberos/Windows недоступен — назначается гостевой пользователь `guest`.

## Структура проекта (кратко)
- `admin-pages/`, `user-pages/` — статические страницы для ролей (UI)
- `backend/` — Flask backend (API, маршруты, БД)
- `backend/models.py` — SQLAlchemy модели (включая Q&A)
- `backend/api.py` — API эндпоинты
- `backend/routes.py` — маршрутизация страниц и ассетов
- `backend/wsgi.py` — точка входа для Gunicorn
- `run.py` — запуск dev-сервера Flask

## База данных
- SQLite-файл: `backend/users_courses.db` (не хранится в git; см. `.gitignore`).
- При изменении моделей БД пересоздаётся схема Q&A при старте (автопроверка).

## Частые операции разработчика
- Установка зависимостей: `pip install -r requirements.txt`
- Запуск dev-сервера: `python run.py`
- Просмотр логов (Docker): `docker compose logs -f web`
- Очистка тестовых данных: удалите файл `backend/users_courses.db` при остановленном приложении — он будет создан заново при старте.

## Лицензия
- По умолчанию репозиторий приватный. Добавьте раздел лицензии при необходимости.
