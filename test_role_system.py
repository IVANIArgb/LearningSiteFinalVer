#!/usr/bin/env python3
"""
Тестовый скрипт для проверки системы ролевой маршрутизации.
"""

import os
import sys
import requests
from unittest.mock import patch

# Добавляем путь к модулям backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend import create_app


def test_app_boot():
    print("🔍 Тестирование запуска приложения...")
    app = create_app("development")
    assert app is not None
    print("✅ Приложение инициализируется")


def test_app_creation():
    """Тестируем создание приложения."""
    print("\n🔍 Тестирование создания приложения...")
    
    app = create_app("development")
    
    # Проверяем конфигурацию
    assert app.config['ADMIN_TEMPLATE_DIR'] == 'admin-pages'
    assert app.config['USER_TEMPLATE_DIR'] == 'user-pages'
    assert 'PROJECT_ROOT' in app.config
    
    print("✅ Приложение создается корректно!")
    return app


def test_template_paths():
    """Тестируем пути к шаблонам."""
    print("\n🔍 Тестирование путей к шаблонам...")
    
    app = create_app("development")
    project_root = app.config['PROJECT_ROOT']
    
    # Проверяем существование папок
    admin_path = os.path.join(project_root, 'admin-pages')
    user_path = os.path.join(project_root, 'user-pages')
    
    print(f"  Корневая папка проекта: {project_root}")
    print(f"  Папка админских шаблонов: {admin_path}")
    print(f"  Папка пользовательских шаблонов: {user_path}")
    
    assert os.path.exists(admin_path), f"Папка админских шаблонов не найдена: {admin_path}"
    assert os.path.exists(user_path), f"Папка пользовательских шаблонов не найдена: {user_path}"
    
    # Проверяем наличие основных страниц
    main_pages = ['main-pg', 'all-courses-pg', 'questions-pg']
    for page in main_pages:
        admin_page_path = os.path.join(admin_path, page)
        user_page_path = os.path.join(user_path, page)
        
        assert os.path.exists(admin_page_path), f"Админская страница не найдена: {admin_page_path}"
        assert os.path.exists(user_page_path), f"Пользовательская страница не найдена: {user_page_path}"
        
        # Проверяем наличие index.html
        admin_index = os.path.join(admin_page_path, 'index.html')
        user_index = os.path.join(user_page_path, 'index.html')
        
        assert os.path.exists(admin_index), f"Админский index.html не найден: {admin_index}"
        assert os.path.exists(user_index), f"Пользовательский index.html не найден: {user_index}"
    
    print("✅ Все пути к шаблонам корректны!")


def test_basic_requests():
    """Проверка, что основные страницы отдаются без ошибок (200)."""
    print("\n🔍 Базовая проверка запросов...")
    app = create_app("development")
    with app.test_client() as client:
        for path in [
            '/main-pg/',
            '/questions-pg/',
            '/users-info-pg/'
        ]:
            resp = client.get(path)
            print(f"  GET {path}: {resp.status_code}")
            assert resp.status_code == 200


def main():
    """Основная функция тестирования."""
    print("🚀 Запуск тестирования системы ролевой маршрутизации\n")
    
    try:
        test_app_boot()
        test_app_creation()
        test_template_paths()
        test_basic_requests()
        
        print("\n🎉 Все тесты прошли успешно!")
        print("\n📋 Инструкции по использованию:")
        print("1. Запустите сервер: python run.py")
        print("2. Откройте браузер и перейдите на http://127.0.0.1:5000")
        print("3. Для тестирования админского интерфейса используйте имя пользователя 'admin'")
        print("4. Для тестирования пользовательского интерфейса используйте любое другое имя")
        print("5. Проверьте /debug/auth для отладки аутентификации")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
