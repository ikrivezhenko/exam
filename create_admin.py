from app import create_app
from app.models import db, User
from flask_bcrypt import Bcrypt

app = create_app()
bcrypt = Bcrypt(app)


def create_admin():
    with app.app_context():
        # Проверяем, нет ли уже администратора
        admin_exists = User.query.filter_by(username='admin1').first()

        if admin_exists:
            print("Администратор уже существует в системе")
            return

        # Создаем администратора
        hashed_password = bcrypt.generate_password_hash('adminpassword').decode('utf-8')
        admin = User(
            username='admin',
            password=hashed_password,
            full_name='Администратор Системы',
            position='Главный администратор',
            role='admin'
        )

        # Добавляем в базу данных
        db.session.add(admin)
        db.session.commit()
        print("Администратор успешно создан!")


if __name__ == '__main__':
    create_admin()