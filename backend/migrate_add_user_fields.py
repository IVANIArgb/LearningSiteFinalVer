"""
Скрипт миграции для добавления новых полей в таблицы users и kerberos_users.
Добавляет поля: surname, fst_name, sec_name, position
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from models import db_manager


def migrate_database():
    """Добавляет новые поля в существующие таблицы."""
    print("🔄 Начинаем миграцию базы данных...")
    
    with db_manager.engine.begin() as conn:
        try:
            # Миграция таблицы users
            print("📝 Обновляем таблицу users...")
            
            # Проверяем существующие колонки
            users_columns = conn.execute(text("PRAGMA table_info('users')")).fetchall()
            existing_users_columns = {col[1] for col in users_columns}
            
            # Добавляем новые колонки если их нет
            if 'surname' not in existing_users_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN surname VARCHAR(100)"))
                print("  ✅ Добавлено поле surname")
            
            if 'fst_name' not in existing_users_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN fst_name VARCHAR(100)"))
                print("  ✅ Добавлено поле fst_name")
            
            if 'sec_name' not in existing_users_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN sec_name VARCHAR(100)"))
                print("  ✅ Добавлено поле sec_name")
            
            if 'position' not in existing_users_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN position VARCHAR(100)"))
                print("  ✅ Добавлено поле position")
            
            # Делаем full_name nullable если нужно
            full_name_info = [col for col in users_columns if col[1] == 'full_name']
            if full_name_info and full_name_info[0][3] == 1:  # 3 = notnull, 1 = NOT NULL
                try:
                    # SQLite не поддерживает ALTER COLUMN, поэтому пропускаем
                    print("  ℹ️  Поле full_name уже существует (SQLite не поддерживает изменение nullable)")
                except Exception:
                    pass
            
            # Миграция таблицы kerberos_users
            print("📝 Обновляем таблицу kerberos_users...")
            
            # Проверяем существующие колонки
            kerberos_columns = conn.execute(text("PRAGMA table_info('kerberos_users')")).fetchall()
            existing_kerberos_columns = {col[1] for col in kerberos_columns} if kerberos_columns else set()
            
            # Добавляем новые колонки если их нет
            if 'surname' not in existing_kerberos_columns:
                conn.execute(text("ALTER TABLE kerberos_users ADD COLUMN surname VARCHAR(100)"))
                print("  ✅ Добавлено поле surname")
            
            if 'fst_name' not in existing_kerberos_columns:
                conn.execute(text("ALTER TABLE kerberos_users ADD COLUMN fst_name VARCHAR(100)"))
                print("  ✅ Добавлено поле fst_name")
            
            if 'sec_name' not in existing_kerberos_columns:
                conn.execute(text("ALTER TABLE kerberos_users ADD COLUMN sec_name VARCHAR(100)"))
                print("  ✅ Добавлено поле sec_name")
            
            if 'position' not in existing_kerberos_columns:
                conn.execute(text("ALTER TABLE kerberos_users ADD COLUMN position VARCHAR(100)"))
                print("  ✅ Добавлено поле position")
            
            print("✅ Миграция завершена успешно!")
            
        except Exception as e:
            print(f"❌ Ошибка при миграции: {e}")
            raise


if __name__ == "__main__":
    migrate_database()

