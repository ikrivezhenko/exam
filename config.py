import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///exam_system.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    TEMPLATES_FOLDER = 'app/word_templates'
    ALLOWED_EXTENSIONS = {'xlsx'}

    # Создаем папку для загрузок, если она не существует
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)