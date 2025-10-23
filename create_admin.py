from app import create_app
from app.models import db, User
from flask_bcrypt import Bcrypt

app = create_app()
bcrypt = Bcrypt(app)


def create_admin():
    with app.app_context():
        try:
            # Проверяем, нет ли уже администратора
            admin_exists = User.query.filter_by(username='admin').first()

            if admin_exists:
                print("Администратор уже существует в системе")
                return

            # Создаем администратора с ВСЕМИ обязательными полями
            hashed_password = bcrypt.generate_password_hash('adminpassword').decode('utf-8')
            admin = User(
                username='admin',
                password=hashed_password,
                full_name='Администратор Системы',
                position='Главный администратор',
                role='admin',
                email='admin@example.com'
                # school_id и tpu_id не обязательны, можно оставить NULL
            )

            # Добавляем в базу данных
            db.session.add(admin)
            db.session.commit()
            print("Администратор успешно создан!")
            print("Логин: admin")
            print("Пароль: adminpassword")
            print("Роль: admin")

        except Exception as e:
            print(f"Ошибка при создании администратора: {e}")
            db.session.rollback()


if __name__ == '__main__':
    create_admin()