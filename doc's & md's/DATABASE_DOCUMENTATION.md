# Документация базы данных пользователей и курсов

## Обзор
Система управления пользователями и курсами с отслеживанием прогресса обучения. База данных содержит информацию о пользователях, курсах, уроках и прогрессе каждого пользователя.

## Структура базы данных

### 1. Таблица `users` - Пользователи
Хранит основную информацию о пользователях системы.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Уникальный идентификатор пользователя (PK) |
| `username` | String(100) | Логин пользователя (уникальный) |
| `full_name` | String(200) | Полное имя пользователя |
| `department` | String(100) | Отдел, в котором работает пользователь |
| `email` | String(200) | Email пользователя (уникальный) |
| `is_active` | Boolean | Статус активности пользователя |
| `created_at` | DateTime | Дата создания записи |
| `updated_at` | DateTime | Дата последнего обновления |

### 2. Таблица `courses` - Курсы
Содержит информацию о доступных курсах обучения.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Уникальный идентификатор курса (PK) |
| `title` | String(200) | Название курса |
| `description` | Text | Описание курса |
| `total_lessons` | Integer | Общее количество уроков в курсе |
| `is_active` | Boolean | Статус активности курса |
| `created_at` | DateTime | Дата создания записи |
| `updated_at` | DateTime | Дата последнего обновления |

### 3. Таблица `lessons` - Уроки
Содержит информацию об уроках в рамках курсов.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Уникальный идентификатор урока (PK) |
| `course_id` | Integer | ID курса (FK) |
| `title` | String(200) | Название урока |
| `description` | Text | Описание урока |
| `lesson_number` | Integer | Номер урока в курсе |
| `content` | Text | Содержимое урока |
| `is_active` | Boolean | Статус активности урока |
| `created_at` | DateTime | Дата создания записи |
| `updated_at` | DateTime | Дата последнего обновления |

### 4. Таблица `user_course_progress` - Прогресс по курсам
Отслеживает прогресс пользователей по каждому курсу.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Уникальный идентификатор записи (PK) |
| `user_id` | Integer | ID пользователя (FK) |
| `course_id` | Integer | ID курса (FK) |
| `lessons_completed` | Integer | Количество пройденных уроков |
| `is_completed` | Boolean | Статус завершения курса |
| `started_at` | DateTime | Дата начала прохождения курса |
| `completed_at` | DateTime | Дата завершения курса |
| `updated_at` | DateTime | Дата последнего обновления |

### 5. Таблица `user_lesson_progress` - Прогресс по урокам
Детальное отслеживание прогресса по каждому уроку.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Уникальный идентификатор записи (PK) |
| `user_id` | Integer | ID пользователя (FK) |
| `lesson_id` | Integer | ID урока (FK) |
| `is_completed` | Boolean | Статус завершения урока |
| `completed_at` | DateTime | Дата завершения урока |
| `created_at` | DateTime | Дата создания записи |
| `updated_at` | DateTime | Дата последнего обновления |

## Связи между таблицами

```
users (1) ←→ (N) user_course_progress (N) ←→ (1) courses
users (1) ←→ (N) user_lesson_progress (N) ←→ (1) lessons
courses (1) ←→ (N) lessons
```

## API Endpoints

### Пользователи
- `GET /api/users` - Получить список всех пользователей
- `GET /api/users/{id}` - Получить информацию о конкретном пользователе
- `GET /api/users/{id}/progress` - Получить детальный прогресс пользователя

### Курсы
- `GET /api/courses` - Получить список всех курсов
- `GET /api/courses/{id}` - Получить информацию о конкретном курсе
- `GET /api/courses/{id}/users` - Получить список пользователей курса

### Отделы
- `GET /api/departments` - Получить список всех отделов

### Статистика
- `GET /api/statistics` - Получить общую статистику системы

### Текущий пользователь
- `GET /api/current-user` - Получить информацию о текущем аутентифицированном пользователе

## Примеры запросов

### Получить всех пользователей
```bash
curl http://localhost:5000/api/users
```

### Получить пользователей определенного отдела
```bash
curl "http://localhost:5000/api/users?department=IT%20отдел"
```

### Поиск пользователей
```bash
curl "http://localhost:5000/api/users?search=Иван"
```

### Получить прогресс пользователя
```bash
curl http://localhost:5000/api/users/1/progress
```

### Получить статистику
```bash
curl http://localhost:5000/api/statistics
```

## Тестовые данные

Система автоматически создает тестовые данные при первом запуске:

### Пользователи
- Иван Петров (IT отдел)
- Мария Сидорова (HR отдел)
- Алексей Кузнецов (Финансовый отдел)
- Елена Волкова (Маркетинг)

### Курсы
1. **Основы информационной безопасности** (5 уроков)
2. **Работа с корпоративными системами** (8 уроков)
3. **Управление проектами** (6 уроков)
4. **Клиентский сервис** (4 урока)

### Прогресс
Каждому пользователю случайным образом назначается прогресс по всем курсам.

## Настройка

### Переменные окружения
- `DATABASE_URL` - URL подключения к базе данных (по умолчанию: `sqlite:///users_courses.db`)
- `DATABASE_INIT_SAMPLE_DATA` - Инициализировать тестовые данные (по умолчанию: `true`)

### Поддерживаемые базы данных
- SQLite (по умолчанию)
- PostgreSQL
- MySQL
- SQL Server

## Использование в коде

### Получение сессии базы данных
```python
from backend.models import db_manager

session = db_manager.get_session()
try:
    # Работа с базой данных
    users = session.query(User).all()
finally:
    session.close()
```

### Создание нового пользователя
```python
from backend.models import User

user = User(
    username='new.user',
    full_name='Новый Пользователь',
    department='IT отдел',
    email='new.user@company.com'
)
session.add(user)
session.commit()
```

### Обновление прогресса пользователя
```python
from backend.models import UserCourseProgress

progress = session.query(UserCourseProgress).filter(
    UserCourseProgress.user_id == user_id,
    UserCourseProgress.course_id == course_id
).first()

if progress:
    progress.lessons_completed += 1
    if progress.lessons_completed == progress.course.total_lessons:
        progress.is_completed = True
        progress.completed_at = datetime.now()
    session.commit()
```

## Мониторинг и обслуживание

### Резервное копирование
```bash
# SQLite
cp users_courses.db users_courses_backup_$(date +%Y%m%d).db

# PostgreSQL
pg_dump -h localhost -U username -d database_name > backup.sql
```

### Очистка неактивных записей
```python
# Деактивация старых пользователей
session.query(User).filter(
    User.updated_at < datetime.now() - timedelta(days=365)
).update({'is_active': False})
session.commit()
```

### Статистика использования
```python
# Количество активных пользователей
active_users = session.query(User).filter(User.is_active == True).count()

# Средний прогресс по курсам
avg_progress = session.query(
    func.avg(UserCourseProgress.lessons_completed)
).scalar()
```

## Безопасность

- Все API endpoints требуют аутентификации через Windows Authentication
- Данные пользователей защищены от несанкционированного доступа
- Регулярное резервное копирование данных
- Логирование всех операций с базой данных

## Расширение функциональности

### Добавление новых полей
1. Обновите модель в `backend/models.py`
2. Создайте миграцию базы данных
3. Обновите API endpoints при необходимости

### Добавление новых типов курсов
1. Добавьте поле `course_type` в таблицу `courses`
2. Обновите модель `Course`
3. Добавьте фильтрацию в API

### Интеграция с внешними системами
- Active Directory для синхронизации пользователей
- LMS системы для импорта курсов
- HR системы для обновления информации о сотрудниках
