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
    full_name = Column(String(200), nullable=False)
    department = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
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
            'full_name': self.full_name,
            'department': self.department,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'courses_completed': len([cp for cp in self.course_progress if cp.is_completed]),
            'total_lessons_completed': sum(cp.lessons_completed for cp in self.course_progress)
        }


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
        Base.metadata.create_all(bind=self.engine)

    def cleanup_legacy_and_kerberos(self):
        """Удалить устаревшие таблицы (например, mac_users) и очистить kerberos_users."""
        with self.engine.begin() as conn:
            try:
                # Удаляем таблицу mac_users, если она существует
                conn.execute(text("DROP TABLE IF EXISTS mac_users"))
            except Exception:
                pass
            try:
                # Очищаем таблицу kerberos_users
                conn.execute(text("DELETE FROM kerberos_users"))
                # Сбрасывать AUTOINCREMENT у SQLite не обязательно, но можно
                conn.execute(text("DELETE FROM sqlite_sequence WHERE name='kerberos_users'"))
            except Exception:
                pass
    
    def get_session(self):
        """Получить сессию базы данных."""
        return self.SessionLocal()
    
    def init_sample_data(self):
        """Инициализировать тестовые данные."""
        session = self.get_session()
        
        try:
            # Идёмпотентное наполнение: создаём только отсутствующие сущности
            
            # Создаем тестовых пользователей
            users_data = [
                {
                    'username': 'ivan.petrov',
                    'full_name': 'Иван Петров',
                    'department': 'IT отдел',
                    'email': 'ivan.petrov@company.com'
                },
                {
                    'username': 'maria.sidorova',
                    'full_name': 'Мария Сидорова',
                    'department': 'HR отдел',
                    'email': 'maria.sidorova@company.com'
                },
                {
                    'username': 'alex.kuznetsov',
                    'full_name': 'Алексей Кузнецов',
                    'department': 'Финансовый отдел',
                    'email': 'alex.kuznetsov@company.com'
                },
                {
                    'username': 'elena.volkova',
                    'full_name': 'Елена Волкова',
                    'department': 'Маркетинг',
                    'email': 'elena.volkova@company.com'
                }
            ]
            
            users = []
            for user_data in users_data:
                existing = session.query(User).filter(User.username == user_data['username'].lower()).first()
                if existing:
                    users.append(existing)
                else:
                    user = User(
                        username=user_data['username'].lower(),
                        full_name=user_data['full_name'],
                        department=user_data['department'],
                        email=user_data.get('email'),
                        is_active=True
                    )
                    session.add(user)
                    session.flush()
                    users.append(user)
            session.commit()
            
            # Создаем тестовые курсы
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
            
            # Создаем прогресс пользователей
            import random
            
            for user in users:
                for course in courses:
                    existing = session.query(UserCourseProgress).filter(
                        UserCourseProgress.user_id == user.id,
                        UserCourseProgress.course_id == course.id
                    ).first()
                    if existing:
                        continue
                    lessons_completed = random.randint(0, course.total_lessons)
                    is_completed = lessons_completed == course.total_lessons
                    session.add(UserCourseProgress(
                        user_id=user.id,
                        course_id=course.id,
                        lessons_completed=lessons_completed,
                        is_completed=is_completed,
                        completed_at=datetime.now() if is_completed else None
                    ))
            
            session.commit()
            print("✅ Тестовые данные успешно созданы!")

            # Создаем тестовые вопросы и ответы
            from random import choice
            # Берем существующих пользователей как авторов вопросов
            all_users = session.query(User).all()
            if all_users:
                # Проверим, есть ли уже такие вопросы
                def ensure_question(author, title, body, tags):
                    existing_q = session.query(Question).filter(Question.title == title).first()
                    if existing_q:
                        return existing_q
                    q = Question(author_id=author.id, title=title, body=body, tags=tags)
                    session.add(q)
                    session.flush()
                    return q

                q1 = ensure_question(all_users[0], 'Как обновить приложение?','Не получается обновить приложение до последней версии. Что делать?','Microsoft,Обновление,Word')
                author2 = all_users[1] if len(all_users) > 1 else all_users[0]
                q2 = ensure_question(author2, 'Где найти материалы по безопасности?','Ищу материалы из курса по ИБ.','ИБ,Материалы')
                session.commit()

                # Ответ от "админа" — в демо: первый пользователь
                existing_a = session.query(Answer).filter(Answer.question_id == q1.id).first()
                if not existing_a:
                    a1 = Answer(question_id=q1.id, author_id=all_users[0].id, body='Перейдите в раздел Настройки -> Обновления и нажмите "Проверить обновления".')
                    session.add(a1)
                    q1.is_resolved = True
                    session.commit()
            
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка при создании тестовых данных: {e}")
        finally:
            session.close()


class KerberosUser(Base):
    """Модель для Kerberos пользователей"""
    __tablename__ = 'kerberos_users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    principal = Column(String(200), nullable=False, unique=True, index=True)  # username@REALM
    realm = Column(String(100), nullable=False, index=True)
    full_name = Column(String(200), nullable=True)
    department = Column(String(100), nullable=True)
    email = Column(String(200), nullable=True)
    role = Column(String(20), nullable=False, default='user')
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<KerberosUser(username='{self.username}', principal='{self.principal}', role='{self.role}')>"


class KerberosSession(Base):
    """Модель для Kerberos сессий"""
    __tablename__ = 'kerberos_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(100), nullable=False, index=True)
    principal = Column(String(200), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<KerberosSession(session_id='{self.session_id}', username='{self.username}')>"


# Глобальный экземпляр менеджера базы данных
# Создается с правильным путем к БД в папке backend
db_manager = DatabaseManager()
