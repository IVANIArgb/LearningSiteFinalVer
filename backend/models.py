"""
Модели базы данных для системы управления пользователями и курсами.
"""

from datetime import datetime
import os
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Text, UniqueConstraint
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """Модель пользователя."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=True)  # Оставляем для обратной совместимости
    surname = Column(String(100), nullable=True)  # Фамилия
    fst_name = Column(String(100), nullable=True)  # Имя
    sec_name = Column(String(100), nullable=True)  # Отчество
    principal = Column(String(200), unique=True, nullable=True, index=True)
    realm = Column(String(100), nullable=True, index=True)
    department = Column(String(100), nullable=False)
    position = Column(String(100), nullable=True)  # Должность
    email = Column(String(200), unique=True, nullable=True)
    role = Column(String(20), nullable=False, default='user')
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Связи
    course_progress = relationship("UserCourseProgress", back_populates="user", cascade="all, delete-orphan")
    # Вопросы и ответы пользователя
    questions = relationship("Question", back_populates="author", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="author", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}', full_name='{self.full_name}', department='{self.department}')>"
    
    def to_dict(self):
        """Преобразование в словарь для JSON."""
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name or self._get_full_name_from_parts(),
            'surname': self.surname or '',
            'fst_name': self.fst_name or '',
            'sec_name': self.sec_name or '',
            'principal': self.principal or '',
            'realm': self.realm or '',
            'department': self.department,
            'position': self.position or '',
            'email': self.email,
            'is_active': self.is_active,
            'role': self.role,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'courses_completed': len([cp for cp in self.course_progress if cp.is_completed]),
            'total_lessons_completed': sum(cp.lessons_completed for cp in self.course_progress)
        }
    
    def _get_full_name_from_parts(self) -> str:
        """Собирает полное имя из частей."""
        parts = []
        if self.surname:
            parts.append(self.surname)
        if self.fst_name:
            parts.append(self.fst_name)
        if self.sec_name:
            parts.append(self.sec_name)
        return ' '.join(parts) if parts else ''


class Course(Base):
    """Модель курса."""
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    total_lessons = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Связи
    user_progress = relationship("UserCourseProgress", back_populates="course", cascade="all, delete-orphan")
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Course(title='{self.title}', total_lessons={self.total_lessons})>"
    
    def to_dict(self):
        """Преобразование в словарь для JSON."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'total_lessons': self.total_lessons,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'users_enrolled': len(self.user_progress)
        }


class Lesson(Base):
    """Модель урока."""
    __tablename__ = 'lessons'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    lesson_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Связи
    course = relationship("Course", back_populates="lessons")
    user_progress = relationship("UserLessonProgress", back_populates="lesson", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Lesson(title='{self.title}', course_id={self.course_id}, lesson_number={self.lesson_number})>"
    
    def to_dict(self):
        """Преобразование в словарь для JSON."""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'lesson_number': self.lesson_number,
            'content': self.content,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class UserCourseProgress(Base):
    """Модель прогресса пользователя по курсу."""
    __tablename__ = 'user_course_progress'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    lessons_completed = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Связи
    user = relationship("User", back_populates="course_progress")
    course = relationship("Course", back_populates="user_progress")
    
    def __repr__(self):
        return f"<UserCourseProgress(user_id={self.user_id}, course_id={self.course_id}, lessons_completed={self.lessons_completed})>"
    
    def to_dict(self):
        """Преобразование в словарь для JSON."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'lessons_completed': self.lessons_completed,
            'is_completed': self.is_completed,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'progress_percentage': self.get_progress_percentage()
        }
    
    def get_progress_percentage(self):
        """Получить процент выполнения курса."""
        if not self.course or self.course.total_lessons == 0:
            return 0
        return round((self.lessons_completed / self.course.total_lessons) * 100, 2)


class UserLessonProgress(Base):
    """Модель прогресса пользователя по уроку."""
    __tablename__ = 'user_lesson_progress'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Связи
    user = relationship("User")
    lesson = relationship("Lesson", back_populates="user_progress")
    
    def __repr__(self):
        return f"<UserLessonProgress(user_id={self.user_id}, lesson_id={self.lesson_id}, is_completed={self.is_completed})>"
    
    def to_dict(self):
        """Преобразование в словарь для JSON."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Question(Base):
    """Модель вопроса пользователя для страницы вопросов."""
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    tags = Column(String(500), nullable=True)  # строка тегов, разделённых запятой
    is_resolved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Связи
    author = relationship("User", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    attachments = relationship("QuestionAttachment", back_populates="question", cascade="all, delete-orphan")

    def to_dict(self, include_relations: bool = True):
        data = {
            'id': self.id,
            'author_id': self.author_id,
            'author_username': self.author.username if self.author else None,
            'author_full_name': self.author.full_name if self.author else None,
            'title': self.title,
            'body': self.body,
            'tags': [t.strip() for t in (self.tags or '').split(',') if t.strip()],
            'is_resolved': self.is_resolved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_relations:
            data['attachments'] = [a.to_dict() for a in self.attachments]
            data['answers'] = [ans.to_dict() for ans in self.answers]
        return data


class Answer(Base):
    """Ответ администратора на вопрос."""
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Связи
    question = relationship("Question", back_populates="answers")
    author = relationship("User", back_populates="answers")
    attachments = relationship("AnswerAttachment", back_populates="answer", cascade="all, delete-orphan")

    def to_dict(self, include_relations: bool = True):
        data = {
            'id': self.id,
            'question_id': self.question_id,
            'author_id': self.author_id,
            'author_username': self.author.username if self.author else None,
            'author_full_name': self.author.full_name if self.author else None,
            'body': self.body,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_relations:
            data['attachments'] = [a.to_dict() for a in self.attachments]
        return data


class QuestionAttachment(Base):
    """Прикреплённый файл к вопросу."""
    __tablename__ = 'question_attachments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False, index=True)
    stored_filename = Column(String(255), nullable=False)  # имя файла на диске
    original_filename = Column(String(255), nullable=False)  # исходное имя файла
    mime_type = Column(String(100), nullable=True)
    size_bytes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())

    question = relationship("Question", back_populates="attachments")

    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'stored_filename': self.stored_filename,
            'original_filename': self.original_filename,
            'mime_type': self.mime_type,
            'size_bytes': self.size_bytes,
            'url': f"/uploads/{self.stored_filename}",
        }


class AnswerAttachment(Base):
    """Прикреплённый файл к ответу."""
    __tablename__ = 'answer_attachments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    answer_id = Column(Integer, ForeignKey('answers.id'), nullable=False, index=True)
    stored_filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=True)
    size_bytes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())

    answer = relationship("Answer", back_populates="attachments")

    def to_dict(self):
        return {
            'id': self.id,
            'answer_id': self.answer_id,
            'stored_filename': self.stored_filename,
            'original_filename': self.original_filename,
            'mime_type': self.mime_type,
            'size_bytes': self.size_bytes,
            'url': f"/uploads/{self.stored_filename}",
        }

class DatabaseManager:
    """Менеджер базы данных."""
    
    def __init__(self, database_url: str | None = None):
        # По умолчанию размещаем БД в папке backend/users_courses.db (абсолютный путь)
        if not database_url:
            backend_dir = os.path.dirname(__file__)
            db_path = os.path.abspath(os.path.join(backend_dir, 'users_courses.db'))
            database_url = f"sqlite:///{db_path}"
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def _ensure_qa_schema(self):
        """Проверить и починить схему Q&A таблиц для SQLite.
        Если не хватает обязательных колонок, безопасно пересоздать таблицы.
        """
        required = {
            'questions': {'author_id', 'title', 'body', 'tags', 'is_resolved', 'created_at', 'updated_at'},
            'answers': {'question_id', 'author_id', 'body', 'created_at', 'updated_at'},
            'question_attachments': {'question_id', 'stored_filename', 'original_filename'},
            'answer_attachments': {'answer_id', 'stored_filename', 'original_filename'},
        }
        with self.engine.begin() as conn:
            for table, cols in required.items():
                try:
                    info = conn.execute(text(f"PRAGMA table_info('{table}')")).fetchall()
                    if not info:
                        continue  # таблицы нет — create_all создаст
                    existing = {row[1] for row in info}  # row[1] = name
                    if not cols.issubset(existing):
                        conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                except Exception:
                    # при любой ошибке пересоздаём таблицу
                    try:
                        conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                    except Exception:
                        pass

    def create_tables(self):
        """Создать все таблицы, предварительно проверив схему Q&A."""
        self._ensure_qa_schema()
        self._ensure_user_columns()
        Base.metadata.create_all(bind=self.engine)
        self._merge_kerberos_users()

    def cleanup_legacy_and_kerberos(self):
        """Удалить устаревшие таблицы (например, mac_users)."""
        with self.engine.begin() as conn:
            try:
                # Удаляем таблицу mac_users, если она существует
                conn.execute(text("DROP TABLE IF EXISTS mac_users"))
            except Exception:
                pass
    
    def get_session(self):
        """Получить сессию базы данных."""
        return self.SessionLocal()

    def _ensure_user_columns(self):
        """Добавить недостающие колонки в таблицу users."""
        with self.engine.begin() as conn:
            try:
                info = conn.execute(text("PRAGMA table_info('users')")).fetchall()
                if not info:
                    return
                existing = {row[1] for row in info}
                additions = []
                if 'role' not in existing:
                    additions.append("ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'")
                if 'principal' not in existing:
                    additions.append("ADD COLUMN principal VARCHAR(200)")
                if 'realm' not in existing:
                    additions.append("ADD COLUMN realm VARCHAR(100)")
                if 'last_login' not in existing:
                    additions.append("ADD COLUMN last_login DATETIME")
                for clause in additions:
                    conn.execute(text(f"ALTER TABLE users {clause}"))
            except Exception:
                pass

    def _merge_kerberos_users(self):
        """Перенести данные из legacy-таблицы kerberos_users в users и удалить её."""
        with self.engine.begin() as conn:
            legacy_exists = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='kerberos_users'")
            ).fetchone()
        if not legacy_exists:
            return

        session = self.get_session()
        try:
            rows = session.execute(text("""
                SELECT username, principal, realm, full_name, surname, fst_name, sec_name,
                       department, position, email, role, is_active, last_login
                FROM kerberos_users
            """)).mappings().all()

            for row in rows:
                username = (row.get('username') or '').lower()
                if not username:
                    continue
                user = session.query(User).filter(User.username == username).first()
                if not user:
                    user = User(username=username)
                    session.add(user)

                # Обновляем данными из legacy-таблицы, не затирая актуальные значения
                user.principal = row.get('principal') or user.principal
                user.realm = row.get('realm') or user.realm
                user.full_name = row.get('full_name') or user.full_name
                user.surname = row.get('surname') or user.surname
                user.fst_name = row.get('fst_name') or user.fst_name
                user.sec_name = row.get('sec_name') or user.sec_name
                user.department = row.get('department') or user.department or 'Общий отдел'
                user.position = row.get('position') or user.position
                user.email = row.get('email') or user.email
                user.role = row.get('role') or user.role or 'user'
                if row.get('is_active') is not None:
                    user.is_active = row.get('is_active')
                user.last_login = row.get('last_login') or user.last_login

            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

        with self.engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS kerberos_users"))
    
    def init_sample_data(self):
        """Инициализировать базовые учебные данные без создания тестовых пользователей."""
        session = self.get_session()
        
        try:
            # Создаем (или обновляем) только курсы и уроки, чтобы UI имел структуру.
            courses_data = [
                {
                    'title': 'Основы информационной безопасности',
                    'description': 'Курс по основам информационной безопасности для всех сотрудников',
                    'total_lessons': 5
                },
                {
                    'title': 'Работа с корпоративными системами',
                    'description': 'Обучение работе с внутренними корпоративными системами',
                    'total_lessons': 8
                },
                {
                    'title': 'Управление проектами',
                    'description': 'Основы управления проектами и планирования',
                    'total_lessons': 6
                },
                {
                    'title': 'Клиентский сервис',
                    'description': 'Обучение навыкам работы с клиентами',
                    'total_lessons': 4
                }
            ]
            
            courses = []
            for course_data in courses_data:
                existing = session.query(Course).filter(Course.title == course_data['title']).first()
                if existing:
                    courses.append(existing)
                else:
                    course = Course(**course_data)
                    session.add(course)
                    session.flush()
                    courses.append(course)
            session.commit()
            
            # Создаем уроки для курсов
            # Уроки — создаём по названию курса, без жёстких id
            course_title_to_lessons = {
                'Основы информационной безопасности': [
                    ('Введение в информационную безопасность', 1),
                    ('Пароли и аутентификация', 2),
                    ('Фишинг и социальная инженерия', 3),
                    ('Безопасность мобильных устройств', 4),
                    ('Инциденты безопасности', 5),
                ],
                'Работа с корпоративными системами': [
                    ('Введение в корпоративные системы', 1),
                    ('Система управления документами', 2),
                    ('CRM система', 3),
                    ('Система учета рабочего времени', 4),
                    ('Планировщик задач', 5),
                    ('Отчетность и аналитика', 6),
                    ('Интеграция систем', 7),
                    ('Резервное копирование', 8),
                ],
                'Управление проектами': [
                    ('Основы управления проектами', 1),
                    ('Планирование проекта', 2),
                    ('Управление ресурсами', 3),
                    ('Контроль выполнения', 4),
                    ('Управление рисками', 5),
                    ('Завершение проекта', 6),
                ],
                'Клиентский сервис': [
                    ('Основы клиентского сервиса', 1),
                    ('Коммуникация с клиентами', 2),
                    ('Решение конфликтов', 3),
                    ('Обратная связь и улучшения', 4),
                ],
            }

            for c in courses:
                lessons = course_title_to_lessons.get(c.title, [])
                for title, num in lessons:
                    exists = session.query(Lesson).filter(
                        Lesson.course_id == c.id,
                        Lesson.lesson_number == num
                    ).first()
                    if not exists:
                        session.add(Lesson(course_id=c.id, title=title, lesson_number=num))
            session.commit()
            print("✅ Базовые учебные данные обновлены (курсы и уроки).")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка при обновлении учебных данных: {e}")
        finally:
            session.close()


# Глобальный экземпляр менеджера базы данных
# Создается с правильным путем к БД в папке backend
db_manager = DatabaseManager()
