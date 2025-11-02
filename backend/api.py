"""
API endpoints для работы с пользователями, курсами и прогрессом.
"""

from typing import List, Dict, Any, Optional
from flask import Blueprint, request, jsonify, g
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .models import (
    User, Course, Lesson,
    UserCourseProgress, UserLessonProgress, KerberosUser, KerberosSession,
    Question, Answer, QuestionAttachment, AnswerAttachment
)

# Создаем Blueprint для API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Глобальный менеджер базы данных
# Используем тот же экземпляр, что и в models.py
from .models import db_manager


def get_db_session() -> Session:
    """Получить сессию базы данных."""
    return db_manager.get_session()


@api_bp.route('/users', methods=['GET'])
def get_users():
    """Получить список всех пользователей."""
    session = get_db_session()
    try:
        # Параметры фильтрации
        department = request.args.get('department')
        search = request.args.get('search')
        
        query = session.query(User)
        
        # Фильтр по отделу
        if department:
            query = query.filter(User.department.ilike(f'%{department}%'))
        
        # Поиск по имени или логину
        if search:
            query = query.filter(
                or_(
                    User.full_name.ilike(f'%{search}%'),
                    User.username.ilike(f'%{search}%')
                )
            )
        
        users = query.all()
        
        return jsonify({
            'users': [user.to_dict() for user in users],
            'total': len(users)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id: int):
    """Получить информацию о конкретном пользователе."""
    session = get_db_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        # Получаем детальную информацию о прогрессе
        user_data = user.to_dict()
        
        # Добавляем информацию о курсах
        course_progress = []
        for progress in user.course_progress:
            course_data = progress.course.to_dict()
            progress_data = progress.to_dict()
            course_data.update(progress_data)
            course_progress.append(course_data)
        
        user_data['course_progress'] = course_progress
        
        return jsonify(user_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/users/<int:user_id>/progress', methods=['GET'])
def get_user_progress(user_id: int):
    """Получить детальный прогресс пользователя по всем курсам."""
    session = get_db_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        progress_data = []
        for progress in user.course_progress:
            course = progress.course
            progress_info = {
                'course_id': course.id,
                'course_title': course.title,
                'course_description': course.description,
                'total_lessons': course.total_lessons,
                'lessons_completed': progress.lessons_completed,
                'progress_percentage': progress.get_progress_percentage(),
                'is_completed': progress.is_completed,
                'started_at': progress.started_at.isoformat() if progress.started_at else None,
                'completed_at': progress.completed_at.isoformat() if progress.completed_at else None
            }
            progress_data.append(progress_info)
        
        return jsonify({
            'user_id': user_id,
            'username': user.username,
            'full_name': user.full_name,
            'department': user.department,
            'progress': progress_data,
            'summary': {
                'total_courses': len(progress_data),
                'completed_courses': len([p for p in progress_data if p['is_completed']]),
                'total_lessons_completed': sum(p['lessons_completed'] for p in progress_data),
                'average_progress': round(
                    sum(p['progress_percentage'] for p in progress_data) / len(progress_data) 
                    if progress_data else 0, 2
                )
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/courses', methods=['GET'])
def get_courses():
    """Получить список всех курсов."""
    session = get_db_session()
    try:
        courses = session.query(Course).filter(Course.is_active == True).all()
        
        return jsonify({
            'courses': [course.to_dict() for course in courses],
            'total': len(courses)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/courses/<int:course_id>', methods=['GET'])
def get_course(course_id: int):
    """Получить информацию о конкретном курсе."""
    session = get_db_session()
    try:
        course = session.query(Course).filter(Course.id == course_id).first()
        if not course:
            return jsonify({'error': 'Курс не найден'}), 404
        
        course_data = course.to_dict()
        
        # Добавляем информацию об уроках
        lessons = session.query(Lesson).filter(
            and_(Lesson.course_id == course_id, Lesson.is_active == True)
        ).order_by(Lesson.lesson_number).all()
        
        course_data['lessons'] = [lesson.to_dict() for lesson in lessons]
        
        return jsonify(course_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/courses/<int:course_id>/users', methods=['GET'])
def get_course_users(course_id: int):
    """Получить список пользователей, проходящих курс."""
    session = get_db_session()
    try:
        course = session.query(Course).filter(Course.id == course_id).first()
        if not course:
            return jsonify({'error': 'Курс не найден'}), 404
        
        # Получаем прогресс пользователей по курсу
        progress_data = []
        for progress in course.user_progress:
            user = progress.user
            progress_info = {
                'user_id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'department': user.department,
                'lessons_completed': progress.lessons_completed,
                'progress_percentage': progress.get_progress_percentage(),
                'is_completed': progress.is_completed,
                'started_at': progress.started_at.isoformat() if progress.started_at else None,
                'completed_at': progress.completed_at.isoformat() if progress.completed_at else None
            }
            progress_data.append(progress_info)
        
        # Сортируем по проценту выполнения (по убыванию)
        progress_data.sort(key=lambda x: x['progress_percentage'], reverse=True)
        
        return jsonify({
            'course_id': course_id,
            'course_title': course.title,
            'total_lessons': course.total_lessons,
            'users': progress_data,
            'summary': {
                'total_users': len(progress_data),
                'completed_users': len([p for p in progress_data if p['is_completed']]),
                'average_progress': round(
                    sum(p['progress_percentage'] for p in progress_data) / len(progress_data) 
                    if progress_data else 0, 2
                )
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/departments', methods=['GET'])
def get_departments():
    """Получить список всех отделов."""
    session = get_db_session()
    try:
        departments = session.query(User.department).distinct().all()
        department_list = [dept[0] for dept in departments if dept[0]]
        
        return jsonify({
            'departments': department_list,
            'total': len(department_list)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Получить общую статистику по системе."""
    session = get_db_session()
    try:
        # Общая статистика
        total_users = session.query(User).count()
        active_users = session.query(User).filter(User.is_active == True).count()
        total_courses = session.query(Course).filter(Course.is_active == True).count()
        
        # Статистика по отделам
        departments_stats = []
        departments = session.query(User.department).distinct().all()
        for dept in departments:
            if dept[0]:
                dept_users = session.query(User).filter(User.department == dept[0]).count()
                departments_stats.append({
                    'department': dept[0],
                    'users_count': dept_users
                })
        
        # Статистика по курсам
        courses_stats = []
        courses = session.query(Course).filter(Course.is_active == True).all()
        for course in courses:
            enrolled_users = len(course.user_progress)
            completed_users = len([p for p in course.user_progress if p.is_completed])
            courses_stats.append({
                'course_id': course.id,
                'course_title': course.title,
                'total_lessons': course.total_lessons,
                'enrolled_users': enrolled_users,
                'completed_users': completed_users,
                'completion_rate': round((completed_users / enrolled_users * 100) if enrolled_users > 0 else 0, 2)
            })
        
        return jsonify({
            'overview': {
                'total_users': total_users,
                'active_users': active_users,
                'total_courses': total_courses
            },
            'departments': departments_stats,
            'courses': courses_stats
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# ----------------------- Q&A Endpoints -----------------------

@api_bp.route('/questions', methods=['GET'])
def list_questions():
    """Список вопросов. Поддерживает фильтры: author_id, mine(true), search, resolved(true/false)."""
    session = get_db_session()
    try:
        from flask import g
        current_user = g.get('user_info', {})
        username = current_user.get('username')

        author_id = request.args.get('author_id', type=int)
        mine = request.args.get('mine') == 'true'
        search = request.args.get('search', type=str)
        resolved = request.args.get('resolved')

        query = session.query(Question).order_by(Question.created_at.desc())

        if author_id:
            query = query.filter(Question.author_id == author_id)
        elif mine and username:
            user = session.query(User).filter(User.username == username).first()
            if user:
                query = query.filter(Question.author_id == user.id)

        if search:
            like = f"%{search}%"
            query = query.filter(or_(Question.title.ilike(like), Question.body.ilike(like)))

        if resolved in ('true', 'false'):
            query = query.filter(Question.is_resolved == (resolved == 'true'))

        questions = query.all()
        return jsonify({'questions': [q.to_dict(include_relations=False) for q in questions]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/questions/<int:qid>', methods=['GET'])
def get_question(qid: int):
    session = get_db_session()
    try:
        q = session.query(Question).filter(Question.id == qid).first()
        if not q:
            return jsonify({'error': 'Вопрос не найден'}), 404
        return jsonify(q.to_dict(include_relations=True))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/questions', methods=['POST'])
def create_question():
    """Создать вопрос. Требуется аутентифицированный пользователь."""
    session = get_db_session()
    try:
        from flask import g
        current_user = g.get('user_info', {})
        username = current_user.get('username')
        if not username:
            return jsonify({'error': 'Пользователь не аутентифицирован'}), 401

        user = session.query(User).filter(User.username == username).first()
        if not user:
            return jsonify({'error': 'Пользователь не найден в БД'}), 404

        data = request.get_json() or {}
        title = (data.get('title') or '').strip()
        body = (data.get('body') or '').strip()
        tags = (data.get('tags') or [])
        if not title or not body:
            return jsonify({'error': 'Требуются заголовок и описание'}), 400

        question = Question(
            author_id=user.id,
            title=title,
            body=body,
            tags=','.join(tags) if isinstance(tags, list) else str(tags)
        )
        session.add(question)
        session.commit()
        return jsonify({'message': 'Вопрос создан', 'question': question.to_dict(include_relations=False)}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/questions/<int:qid>/answers', methods=['GET'])
def list_answers(qid: int):
    session = get_db_session()
    try:
        q = session.query(Question).filter(Question.id == qid).first()
        if not q:
            return jsonify({'error': 'Вопрос не найден'}), 404
        return jsonify({'answers': [a.to_dict() for a in q.answers]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/questions/<int:qid>/answers', methods=['POST'])
def create_answer(qid: int):
    """Создать ответ администратора."""
    session = get_db_session()
    try:
        from flask import g
        current_user = g.get('user_info', {})
        role = current_user.get('role', 'user')
        username = current_user.get('username')
        if role != 'admin':
            return jsonify({'error': 'Требуются права администратора'}), 403
        if not username:
            return jsonify({'error': 'Пользователь не аутентифицирован'}), 401

        user = session.query(User).filter(User.username == username).first()
        if not user:
            return jsonify({'error': 'Пользователь не найден в БД'}), 404

        q = session.query(Question).filter(Question.id == qid).first()
        if not q:
            return jsonify({'error': 'Вопрос не найден'}), 404

        data = request.get_json() or {}
        body = (data.get('body') or '').strip()
        if not body:
            return jsonify({'error': 'Пустой ответ недопустим'}), 400

        ans = Answer(question_id=q.id, author_id=user.id, body=body)
        session.add(ans)
        q.is_resolved = True
        session.commit()
        return jsonify({'message': 'Ответ добавлен', 'answer': ans.to_dict()}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/questions/<int:qid>/attachments', methods=['POST'])
def upload_question_attachment(qid: int):
    """Загрузка файлов к вопросу."""
    session = get_db_session()
    try:
        q = session.query(Question).filter(Question.id == qid).first()
        if not q:
            return jsonify({'error': 'Вопрос не найден'}), 404
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'Файл не передан'}), 400

        import os, secrets
        uploads_dir = os.path.join(api_bp.root_path, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        ext = os.path.splitext(file.filename)[1]
        stored = secrets.token_hex(16) + ext
        path = os.path.join(uploads_dir, stored)
        file.save(path)
        att = QuestionAttachment(
            question_id=q.id,
            stored_filename=stored,
            original_filename=file.filename,
            mime_type=file.mimetype,
            size_bytes=os.path.getsize(path),
        )
        session.add(att)
        session.commit()
        return jsonify({'attachment': att.to_dict()}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/answers/<int:aid>/attachments', methods=['POST'])
def upload_answer_attachment(aid: int):
    session = get_db_session()
    try:
        a = session.query(Answer).filter(Answer.id == aid).first()
        if not a:
            return jsonify({'error': 'Ответ не найден'}), 404
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'Файл не передан'}), 400

        import os, secrets
        uploads_dir = os.path.join(api_bp.root_path, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        ext = os.path.splitext(file.filename)[1]
        stored = secrets.token_hex(16) + ext
        path = os.path.join(uploads_dir, stored)
        file.save(path)
        att = AnswerAttachment(
            answer_id=a.id,
            stored_filename=stored,
            original_filename=file.filename,
            mime_type=file.mimetype,
            size_bytes=os.path.getsize(path),
        )
        session.add(att)
        session.commit()
        return jsonify({'attachment': att.to_dict()}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
@api_bp.route('/users/register', methods=['POST'])
def register_user():
    """Ручная регистрация пользователя (для тестирования)"""
    session = get_db_session()
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        
        # Проверяем, существует ли пользователь
        existing_user = session.query(User).filter(User.username == username.lower()).first()
        if existing_user:
            return jsonify({
                'message': 'User already exists',
                'user': existing_user.to_dict()
            }), 200
        
        # Создаем нового пользователя
        new_user = User(
            username=username.lower(),
            full_name=data.get('full_name', username),
            surname=data.get('surname', ''),
            fst_name=data.get('fst_name', ''),
            sec_name=data.get('sec_name', ''),
            department=data.get('department', 'Общий отдел'),
            position=data.get('position', ''),
            email=data.get('email', f"{username.lower()}@company.com"),
            role=data.get('role', 'user'),
            is_active=True
        )
        session.add(new_user)
        session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': new_user.to_dict()
        }), 201
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/users/check-registration', methods=['GET'])
def check_user_registration():
    """Проверить, зарегистрирован ли текущий пользователь"""
    session = get_db_session()
    try:
        from flask import g
        current_user_info = g.get('user_info', {})
        username = current_user_info.get('username')
        
        if not username:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Проверяем в основной таблице User
        user = session.query(User).filter(User.username == username).first()
        user_exists = user is not None
        
        # Проверяем в таблице KerberosUser
        kerberos_user = session.query(KerberosUser).filter(KerberosUser.username == username).first()
        kerberos_user_exists = kerberos_user is not None
        
        return jsonify({
            'username': username,
            'user_registered': user_exists,
            'kerberos_user_registered': kerberos_user_exists,
            'user_data': user.to_dict() if user else None,
            'kerberos_user_data': {
                'username': kerberos_user.username,
                'principal': kerberos_user.principal,
                'role': kerberos_user.role
            } if kerberos_user else None
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api_bp.route('/current-user', methods=['GET'])
def get_current_user_info():
    """Получить информацию о текущем пользователе (из Windows Auth)."""
    session = get_db_session()
    try:
        # Получаем информацию о текущем пользователе из g (установлено в auth.py)
        current_user_info = g.get('user_info', {})
        username = current_user_info.get('username')
        
        if not username:
            return jsonify({'error': 'Пользователь не аутентифицирован'}), 401
        
        # Ищем пользователя в базе данных
        user = session.query(User).filter(User.username == username).first()
        
        if not user:
            return jsonify({
                'authenticated': True,
                'username': username,
                'in_database': False,
                'message': 'Пользователь не найден в базе данных'
            })
        
        # Получаем детальную информацию о пользователе
        user_data = user.to_dict()
        
        # Добавляем информацию о курсах
        course_progress = []
        for progress in user.course_progress:
            course_data = progress.course.to_dict()
            progress_data = progress.to_dict()
            course_data.update(progress_data)
            course_progress.append(course_data)
        
        user_data['course_progress'] = course_progress
        user_data['authenticated'] = True
        user_data['in_database'] = True
        
        return jsonify(user_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


def init_api(app):
    """Инициализировать API для приложения."""
    app.register_blueprint(api_bp)
    
    # Инициализируем базу данных
    db_manager.create_tables()

    # Очищаем только устаревшие таблицы (mac_users), НЕ трогаем kerberos_users и users
    try:
        db_manager.cleanup_legacy_and_kerberos()
    except Exception:
        pass
    
    # Создаем тестовые данные если нужно
    if app.config.get('DATABASE_INIT_SAMPLE_DATA', True):
        db_manager.init_sample_data()
    
    return api_bp
