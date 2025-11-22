import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

# Создаем экземпляры расширений
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app(test_config=None):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, 'templates')
    static_path = os.path.join(base_dir, 'static')
    app = Flask(__name__, template_folder=template_path, static_folder=static_path)

    # Базовая конфигурация
    app.config['SECRET_KEY'] = 'your_very_secret_key_here_change_this_in_production'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 час
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['TEMPLATES_FOLDER'] = os.path.join(base_dir, 'word_templates')
    app.config['WTF_CSRF_ENABLED'] = False  # Важно для тестов

    # OAuth TPU Configuration
    app.config['OAUTH_TPU_CLIENT_ID'] = 'my-app-221-50473644'
    app.config['OAUTH_TPU_CLIENT_SECRET'] = 'NGit4Z0U'
    app.config['OAUTH_TPU_REDIRECT_URI'] = 'http://localhost:5000/oauth/callback'
    app.config['OAUTH_TPU_AUTHORIZE_URL'] = 'https://oauth.tpu.ru/authorize'
    app.config['OAUTH_TPU_ACCESS_TOKEN_URL'] = 'https://oauth.tpu.ru/access_token'
    app.config['OAUTH_TPU_USER_INFO_URL'] = 'https://oauth.tpu.ru/user'
    app.config['OAUTH_TPU_CHECK_TOKEN_URL'] = 'https://oauth.tpu.ru/check-token'

    # Если передан тестовый конфиг, используем его
    if test_config:
        app.config.update(test_config)
    else:
        # Только для продакшена используем файловую БД
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_system.db'

    # Создаем папки, если не существуют
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    login_manager.login_view = 'routes.login'

    # User loader
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Регистрация blueprint
    from .routes import routes as main_blueprint
    app.register_blueprint(main_blueprint)

    # Обработчики ошибок
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled Exception: {str(e)}")
        return render_template('500.html'), 500

    # Создание таблиц (только если не в тестовом режиме)
    if not test_config:
        with app.app_context():
            db.create_all()

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    return app