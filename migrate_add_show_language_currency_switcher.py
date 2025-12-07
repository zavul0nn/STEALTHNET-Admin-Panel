#!/usr/bin/env python3
"""
Скрипт миграции для добавления поля show_language_currency_switcher в таблицу system_setting.
Добавляет колонку для управления видимостью переключателей языка и валюты в Dashboard.

Использование:
    python3 migrate_add_show_language_currency_switcher.py
"""

import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime

def find_database():
    """Находит путь к базе данных"""
    # Сначала пробуем найти через переменные окружения или стандартные пути
    possible_paths = [
        Path('instance/stealthnet.db'),
        Path('stealthnet.db'),
        Path('/var/www/stealthnet-api/instance/stealthnet.db'),
        Path('/var/www/stealthnet-api/stealthnet.db'),
    ]
    
    # Если есть .env, пробуем прочитать путь из него
    try:
        from dotenv import load_dotenv
        load_dotenv()
        db_uri = os.getenv('SQLALCHEMY_DATABASE_URI', '')
        if db_uri and db_uri.startswith('sqlite:///'):
            db_path = Path(db_uri.replace('sqlite:///', ''))
            if db_path.exists():
                return db_path
    except:
        pass
    
    # Ищем в стандартных путях
    for db_path in possible_paths:
        if db_path.exists():
            return db_path
    
    return None

# Находим базу данных
db_path = find_database()
if not db_path:
    print("❌ База данных не найдена. Проверьте следующие пути:")
    for p in [Path('instance/stealthnet.db'), Path('stealthnet.db')]:
        print(f"   - {p.absolute()}")
    sys.exit(1)

print(f"📦 Найдена база данных: {db_path.absolute()}")

# Подключаемся к базе данных
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

try:
    # Проверяем существующие колонки
    cursor.execute("PRAGMA table_info(system_setting)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"📋 Существующие колонки в system_setting: {', '.join(columns)}")
    print()
    
    changes_made = False
    
    # Проверяем, существует ли уже колонка
    if 'show_language_currency_switcher' not in columns:
        print("➕ Добавляем колонку show_language_currency_switcher...")
        cursor.execute("""
            ALTER TABLE system_setting 
            ADD COLUMN show_language_currency_switcher BOOLEAN DEFAULT 1 NOT NULL
        """)
        
        # Устанавливаем значение по умолчанию для существующих записей
        cursor.execute("""
            UPDATE system_setting 
            SET show_language_currency_switcher = 1 
            WHERE show_language_currency_switcher IS NULL
        """)
        
        print("✓ Колонка show_language_currency_switcher добавлена")
        changes_made = True
    else:
        print("✓ Колонка show_language_currency_switcher уже существует")
    
    # Сохраняем изменения
    if changes_made:
        conn.commit()
        print()
        print("✅ Миграция успешно завершена!")
        
        # Создаем резервную копию после успешной миграции
        backup_path = f"{db_path}.backup_{int(datetime.now().timestamp())}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"📝 Резервная копия сохранена: {backup_path}")
    else:
        print()
        print("✅ Колонка уже существует. Миграция не требуется.")
    
    # Показываем финальную структуру таблицы
    print()
    cursor.execute("PRAGMA table_info(system_setting)")
    final_columns = [row[1] for row in cursor.fetchall()]
    print(f"📋 Финальные колонки в system_setting: {', '.join(final_columns)}")
    
except sqlite3.Error as e:
    print(f"❌ Ошибка при выполнении миграции: {e}")
    conn.rollback()
    sys.exit(1)
finally:
    conn.close()

