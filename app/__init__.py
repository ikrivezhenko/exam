import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

# Создаем экземпляры расширений
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app():
    # Получаем абсолютный путь к директории приложения
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Формируем путь к папке с шаблонами
    template_path = os.path.join(base_dir, 'templates')

    app = Flask(__name__, template_folder=template_path)

    # Конфигурация
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_system.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['TEMPLATES_FOLDER'] = os.path.join(base_dir, 'word_templates')

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
    @app.errorhandler(404)
    def forbidden(e):
        return render_template('404.html')

    # Создание таблиц
    with app.app_context():
        db.create_all()

    return app