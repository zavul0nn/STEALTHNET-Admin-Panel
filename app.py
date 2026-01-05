"""
StealthNET Admin Panel - Main Application

Модульная структура:
- modules/models/     - SQLAlchemy модели
- modules/api/        - API эндпоинты по категориям
  - auth/             - Авторизация
  - admin/            - Администрирование
  - client/           - Клиентские функции
  - public/           - Публичные эндпоинты
  - payments/         - Платежи
  - webhooks/         - Вебхуки
  - miniapp/          - Telegram Mini App
  - support/          - Поддержка
  - bot/              - Telegram бот интеграция
"""

from flask import Flask, send_from_directory, request, jsonify
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Создаем основное приложение Flask
app = Flask(__name__,
            static_folder='frontend/build/static',
            static_url_path='/static')

# Инициализируем центральный модуль
from modules.core import init_app, get_db
init_app(app)
db = get_db()

# ============================================================================
# ИМПОРТ МОДЕЛЕЙ (для db.create_all())
# ============================================================================
from modules.models.user import User
from modules.models.payment import Payment, PaymentSetting
from modules.models.tariff import Tariff
from modules.models.promo import PromoCode
from modules.models.ticket import Ticket, TicketMessage
from modules.models.system import SystemSetting
from modules.models.branding import BrandingSetting
from modules.models.bot_config import BotConfig
from modules.models.referral import ReferralSetting
from modules.models.currency import CurrencyRate
from modules.models.tariff_feature import TariffFeatureSetting
from modules.models.auto_broadcast import AutoBroadcastMessage

# ============================================================================
# ИМПОРТ API МАРШРУТОВ
# ============================================================================
from modules.api.auth import routes as auth_routes
from modules.api.admin import routes as admin_routes
from modules.api.client import routes as client_routes
from modules.api.public import routes as public_routes
from modules.api.payments import routes as payment_routes
from modules.api.webhooks import routes as webhook_routes
from modules.api.miniapp import routes as miniapp_routes
from modules.api.support import routes as support_routes
from modules.api.bot import routes as bot_routes

# ============================================================================
# ADMIN PANEL - Отдача статических файлов админки
# ============================================================================

@app.route('/payment-success.html')
def payment_success():
    """Страница успешной оплаты с автоматическим редиректом в Telegram"""
    # Пробуем найти payment-success.html в разных местах
    base_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        # Docker путь (приоритет)
        '/app/frontend/build/miniapp-v2/payment-success.html',
        '/app/frontend/build/miniapp/payment-success.html',
        # Абсолютные пути
        '/opt/remnawave-STEALTHNET-Panel/frontend/build/miniapp-v2/payment-success.html',
        '/opt/remnawave-STEALTHNET-Panel/frontend/build/miniapp/payment-success.html',
        '/opt/remnawave-STEALTHNET-panel/frontend/build/miniapp-v2/payment-success.html',
        '/opt/remnawave-STEALTHNET-panel/frontend/build/miniapp/payment-success.html',
        '/opt/remnawave-STEALTHNET-PANEL/frontend/build/miniapp-v2/payment-success.html',
        '/opt/remnawave-STEALTHNET-PANEL/frontend/build/miniapp/payment-success.html',
        '/opt/admin/frontend/build/miniapp-v2/payment-success.html',
        '/opt/admin/frontend/build/miniapp/payment-success.html',
        # Относительные пути
        os.path.join(base_dir, 'frontend', 'build', 'miniapp-v2', 'payment-success.html'),
        os.path.join(base_dir, 'frontend', 'build', 'miniapp', 'payment-success.html'),
        os.path.join(base_dir, 'admin-panel', 'miniapp-v2', 'payment-success.html'),
        os.path.join(base_dir, 'admin-panel', 'miniapp', 'payment-success.html'),
        os.path.join(base_dir, 'admin-panel', 'payment-success.html')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            dir_path = os.path.dirname(path)
            file_name = os.path.basename(path)
            response = send_from_directory(dir_path, file_name)
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
    
    # Если не найдено, возвращаем 404
    return jsonify({"error": "payment-success.html not found"}), 404

@app.route('/miniapp-v2/', defaults={'path': ''}, methods=['GET', 'HEAD', 'POST', 'OPTIONS'])
@app.route('/miniapp-v2/<path:path>', methods=['GET', 'HEAD', 'POST', 'OPTIONS'])
def miniapp_v2_static(path):
    """Отдача статических файлов miniapp-v2 (новая версия)"""
    # Обработка CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, HEAD, POST, OPTIONS')
        return response
    
    def get_miniapp_v2_path():
        """Получить путь к папке miniapp-v2"""
        miniapp_path = os.getenv("MINIAPP_V2_PATH", "")
        if miniapp_path:
            miniapp_path = miniapp_path.strip()
            if miniapp_path and os.path.exists(miniapp_path):
                index_path = os.path.join(miniapp_path, 'index.html')
                if os.path.exists(index_path):
                    return miniapp_path
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Стандартные пути (в порядке приоритета)
        possible_paths = [
            # Docker путь
            '/app/frontend/build/miniapp-v2',
            # Абсолютные пути
            '/opt/remnawave-STEALTHNET-Panel/frontend/build/miniapp-v2',
            '/opt/remnawave-STEALTHNET-panel/frontend/build/miniapp-v2',
            '/opt/remnawave-STEALTHNET-PANEL/frontend/build/miniapp-v2',
            '/opt/admin/frontend/build/miniapp-v2',
            # Относительные пути
            os.path.join(base_dir, 'frontend', 'build', 'miniapp-v2'),
            os.path.join(base_dir, 'admin-panel', 'miniapp-v2'),
            os.path.join(base_dir, 'admin-panel', 'build', 'miniapp-v2'),
            '/opt/admin/admin-panel/miniapp-v2',
            '/opt/admin/admin-panel/build/miniapp-v2'
        ]
        
        for p in possible_paths:
            if os.path.exists(p):
                index_path = os.path.join(p, 'index.html')
                if os.path.exists(index_path):
                    return p
        
        return None
    
    miniapp_dir = get_miniapp_v2_path()
    
    if not miniapp_dir:
        # Возвращаем простой 404 без JSON, так как это может быть нормальной ситуацией
        from flask import abort
        abort(404)
    
    # Если путь пустой или заканчивается на /, отдаем index.html
    if not path or path.endswith('/'):
        index_path = os.path.join(miniapp_dir, 'index.html')
        if os.path.exists(index_path):
            response = send_from_directory(miniapp_dir, 'index.html')
            # Отключаем кэширование для index.html
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        return jsonify({"error": "index.html not found"}), 404
    
    # Безопасность: проверяем, что путь не выходит за пределы директории
    file_path = os.path.join(miniapp_dir, path)
    if not os.path.abspath(file_path).startswith(os.path.abspath(miniapp_dir)):
        return jsonify({"error": "Invalid path"}), 403
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        response = send_from_directory(miniapp_dir, path)
        # Для HTML файлов отключаем кэширование
        if path.endswith('.html'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response
    
    # Если файл не найден, отдаем index.html (для SPA)
    index_path = os.path.join(miniapp_dir, 'index.html')
    if os.path.exists(index_path):
        response = send_from_directory(miniapp_dir, 'index.html')
        # Отключаем кэширование для index.html
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    return jsonify({"error": "File not found"}), 404


@app.route('/miniapp/', defaults={'path': ''}, methods=['GET', 'HEAD', 'POST', 'OPTIONS'])
@app.route('/miniapp/<path:path>', methods=['GET', 'HEAD', 'POST', 'OPTIONS'])
def miniapp_static(path):
    """Отдача статических файлов miniapp"""
    # Обработка CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, HEAD, POST, OPTIONS')
        return response
    
    def get_miniapp_path():
        """Получить путь к папке miniapp"""
        miniapp_path = os.getenv("MINIAPP_PATH", "")
        if miniapp_path:
            miniapp_path = miniapp_path.strip()
            if miniapp_path and os.path.exists(miniapp_path):
                index_path = os.path.join(miniapp_path, 'index.html')
                if os.path.exists(index_path):
                    return miniapp_path
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Стандартные пути (в порядке приоритета)
        possible_paths = [
            # Docker путь
            '/app/frontend/build/miniapp',
            # Абсолютные пути
            '/opt/remnawave-STEALTHNET-Panel/frontend/build/miniapp',
            '/opt/remnawave-STEALTHNET-panel/frontend/build/miniapp',
            '/opt/remnawave-STEALTHNET-PANEL/frontend/build/miniapp',
            '/opt/admin/frontend/build/miniapp',
            # Относительные пути
            os.path.join(base_dir, 'frontend', 'build', 'miniapp'),
            os.path.join(base_dir, 'admin-panel', 'miniapp'),
            os.path.join(base_dir, 'admin-panel', 'build', 'miniapp'),
            os.path.join(base_dir, 'miniapp'),
            '/opt/admin/admin-panel/miniapp',
            '/opt/admin/admin-panel/build/miniapp',
            '/opt/admin/miniapp',
            '/var/www/admin-panel/miniapp',
            '/var/www/admin-panel/build/miniapp'
        ]
        
        for p in possible_paths:
            if os.path.exists(p):
                index_path = os.path.join(p, 'index.html')
                if os.path.exists(index_path):
                    return p
        
        return None
    
    miniapp_dir = get_miniapp_path()
    
    if not miniapp_dir:
        # Возвращаем простой 404 без JSON, так как это может быть нормальной ситуацией
        from flask import abort
        abort(404)
    
    # Если путь пустой или заканчивается на /, отдаем index.html
    if not path or path.endswith('/'):
        index_path = os.path.join(miniapp_dir, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(miniapp_dir, 'index.html')
        return jsonify({"error": "index.html not found"}), 404
    
    # Безопасность: проверяем, что путь не выходит за пределы директории
    file_path = os.path.join(miniapp_dir, path)
    if not os.path.abspath(file_path).startswith(os.path.abspath(miniapp_dir)):
        return jsonify({"error": "Invalid path"}), 403
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(miniapp_dir, path)
    
    # Если файл не найден, отдаем index.html (для SPA)
    index_path = os.path.join(miniapp_dir, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(miniapp_dir, 'index.html')
    
    return jsonify({"error": "File not found"}), 404


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_admin_panel(path):
    """
    Отдача админ-панели (React приложение)
    Все запросы не совпадающие с API роутами идут сюда
    """
    # Если запрос к API - пропускаем (Flask обработает через API роуты)
    if path.startswith('api/') or path.startswith('miniapp/'):
        from flask import abort
        abort(404)

    # Пробуем найти admin-panel или frontend/build
    base_dir = os.path.dirname(os.path.abspath(__file__))
    admin_panel_dir = None
    
    # Сначала пробуем frontend/build (для Docker)
    frontend_build = os.path.join(base_dir, 'frontend', 'build')
    if os.path.exists(frontend_build) and os.path.exists(os.path.join(frontend_build, 'index.html')):
        admin_panel_dir = frontend_build
    else:
        # Fallback на admin-panel/build
        admin_panel_dir = os.path.join(base_dir, 'admin-panel', 'build')

    # Если запрашивается конкретный файл
    if path and os.path.exists(os.path.join(admin_panel_dir, path)):
        return send_from_directory(admin_panel_dir, path)

    # Для всех остальных запросов (React Router) отдаем index.html
    return send_from_directory(admin_panel_dir, 'index.html')

# ============================================================================

if __name__ == '__main__':
    import logging
    from logging.handlers import RotatingFileHandler

    # Настройка логирования
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler('logs/api_verbose.log', maxBytes=10485760, backupCount=5),
            logging.StreamHandler()
        ]
    )

    app.logger.setLevel(logging.DEBUG)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.DEBUG)
    
    # Игнорируем ошибки "Bad request version" - это обычно попытки HTTPS подключения к HTTP серверу
    import logging
    class BadRequestVersionFilter(logging.Filter):
        def filter(self, record):
            return 'Bad request version' not in str(record.getMessage())
    
    werkzeug_logger.addFilter(BadRequestVersionFilter())

    # Создаем таблицы базы данных и выполняем миграцию при необходимости
    with app.app_context():
        # Проверяем, нужна ли миграция с SQLite на PostgreSQL
        use_postgresql = app.config.get('USE_POSTGRESQL', False)
        
        if use_postgresql:
            # Если используется PostgreSQL, проверяем миграцию
            # Ищем SQLite базу в правильном порядке: instance/stealthnet.db, затем stealthnet.db
            sqlite_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'stealthnet.db'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stealthnet.db')
            ]
            
            sqlite_path = None
            for path in sqlite_paths:
                if os.path.exists(path):
                    sqlite_path = path
                    break
            
            if sqlite_path:
                # SQLite база найдена - проверяем миграцию
                try:
                    from migrate_to_postgresql import check_migration_needed, migrate_data
                    needed, message = check_migration_needed()
                    if needed:
                        app.logger.info("=" * 60)
                        app.logger.info(f"Обнаружена SQLite база данных: {sqlite_path}")
                        app.logger.info("Запуск автоматической миграции в PostgreSQL...")
                        app.logger.info("=" * 60)
                        migration_success = migrate_data()
                        if migration_success:
                            app.logger.info("✅ Миграция завершена успешно")
                            
                            # После миграции данных исправляем sequences в PostgreSQL
                            try:
                                from fix_postgresql_sequences import fix_sequences
                                app.logger.info("🔧 Исправление последовательностей PostgreSQL...")
                                database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
                                if fix_sequences(database_url):
                                    app.logger.info("✅ Последовательности обновлены")
                                else:
                                    app.logger.warning("⚠️  Ошибка при исправлении последовательностей")
                            except Exception as e:
                                app.logger.warning(f"⚠️  Ошибка при исправлении последовательностей: {e}")
                        else:
                            app.logger.warning("⚠️  Миграция завершилась с ошибками")
                        app.logger.info("=" * 60)
                    else:
                        app.logger.info(f"ℹ️  {message}")
                except Exception as e:
                    app.logger.warning(f"⚠️  Ошибка при проверке миграции: {e}")
            else:
                # SQLite база не найдена - просто создаем новую базу в PostgreSQL
                app.logger.info("ℹ️  SQLite база данных не найдена, создается новая база в PostgreSQL")
        
        # Создаем таблицы в базе данных
        db.create_all()
        
        # Создаем дефолтные сообщения автоматических рассылок если их нет
        try:
            from modules.models.auto_broadcast import AutoBroadcastMessage
            subscription_msg = AutoBroadcastMessage.query.filter_by(
                message_type='subscription_expiring_3days'
            ).first()
            
            if not subscription_msg:
                subscription_msg = AutoBroadcastMessage(
                    message_type='subscription_expiring_3days',
                    message_text='Подписка заканчивается через 3 дня, не забудьте продлить',
                    enabled=True,
                    bot_type='both'
                )
                db.session.add(subscription_msg)
                app.logger.info("✅ Создано сообщение: subscription_expiring_3days")
            
            trial_msg = AutoBroadcastMessage.query.filter_by(
                message_type='trial_expiring'
            ).first()
            
            if not trial_msg:
                trial_msg = AutoBroadcastMessage(
                    message_type='trial_expiring',
                    message_text='Тестовый период заканчивается, не желаете купить подписку?',
                    enabled=True,
                    bot_type='both'
                )
                db.session.add(trial_msg)
                app.logger.info("✅ Создано сообщение: trial_expiring")
            
            db.session.commit()
        except Exception as e:
            app.logger.warning(f"⚠️  Ошибка при создании дефолтных сообщений: {e}")
        
        # Запускаем миграции схемы базы данных (добавление новых колонок)
        try:
            from run_schema_migrations import run_all_schema_migrations
            app.logger.info("🔧 Проверка миграций схемы базы данных...")
            run_all_schema_migrations(app)
        except Exception as e:
            app.logger.warning(f"⚠️  Ошибка при выполнении миграций схемы: {e}")
            # Не прерываем запуск приложения, продолжаем работу
        
        # Исправляем encrypted_password для пользователей из бота (если нужно)
        try:
            from fix_encrypted_passwords import fix_encrypted_passwords
            app.logger.info("🔧 Проверка encrypted_password для пользователей из бота...")
            fix_encrypted_passwords(app)
        except Exception as e:
            app.logger.warning(f"⚠️  Ошибка при исправлении encrypted_password: {e}")
            # Не прерываем запуск приложения, продолжаем работу
        
        app.logger.info("=" * 60)
        app.logger.info("StealthNET API Starting...")
        app.logger.info(f"Registered {len(list(app.url_map.iter_rules()))} endpoints")
        app.logger.info("=" * 60)

    # Запускаем приложение
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
