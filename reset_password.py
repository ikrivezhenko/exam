from app import create_app, bcrypt, db
from app.models import User

app = create_app()

def reset_password(username, new_password):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            print(f"Пароль для {username} сброшен")
        else:
            print(f"Пользователь {username} не найден")

if __name__ == '__main__':
    reset_password("admin", "admin")