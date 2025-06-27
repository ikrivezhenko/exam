from app import create_app, db
from app.models import (
    EngineeringSchool, User, Program, Question, 
    ExamDate, CommissionMember, StandardCommission,
    Applicant, Score
)

def create_database():
    app = create_app()
    with app.app_context():
        # Пересоздаем всю структуру базы данных
        db.drop_all()
        db.create_all()
        
        # Создаем тестовые данные
        school1 = EngineeringSchool(name='Школа энергетики')
        school2 = EngineeringSchool(name='Школа информационных технологий')
        school3 = EngineeringSchool(name='Школа машиностроения')
        
        db.session.add_all([school1, school2, school3])
        db.session.commit()
        
        # Пароли: admin, secretary1, commission1 (хэшированные)
        hashed_password = '$2b$12$7uWjK6T8d4eX2Z1vQ5yR3eYdSfGhJkLmNpOqRrSsTtUvWxYzAbCdE'
        
        users = [
            User(username='admin', password=hashed_password, 
                 full_name='Иванов Иван Иванович', position='Системный администратор', 
                 role='admin', school_id=None),
                 
            User(username='secretary1', password=hashed_password, 
                 full_name='Петрова Мария Сергеевна', position='Ответственный секретарь', 
                 role='secretary', school_id=school1.id),
                 
            User(username='commission1', password=hashed_password, 
                 full_name='Сидоров Алексей Николаевич', position='Профессор', 
                 role='commission', school_id=school1.id),
                 
            User(username='secretary2', password=hashed_password, 
                 full_name='Козлова Ольга Дмитриевна', position='Ответственный секретарь', 
                 role='secretary', school_id=school2.id),
                 
            User(username='commission2', password=hashed_password, 
                 full_name='Фёдоров Дмитрий Петрович', position='Доцент', 
                 role='commission', school_id=school2.id)
        ]
        
        db.session.add_all(users)
        db.session.commit()
        
        programs = [
            Program(code='ENE01', name='Энергетические системы', school_id=school1.id),
            Program(code='ENE02', name='Возобновляемые источники энергии', school_id=school1.id),
            Program(code='IT01', name='Программная инженерия', school_id=school2.id),
            Program(code='IT02', name='Искусственный интеллект', school_id=school2.id),
            Program(code='MCH01', name='Робототехника', school_id=school3.id)
        ]
        
        db.session.add_all(programs)
        db.session.commit()
        
        questions = [
            Question(text='Основные законы термодинамики', program_id=programs[0].id),
            Question(text='Принципы работы тепловых электростанций', program_id=programs[0].id),
            Question(text='Методы генерации энергии из возобновляемых источников', program_id=programs[1].id),
            Question(text='Основы ООП', program_id=programs[2].id),
            Question(text='Принципы проектирования баз данных', program_id=programs[2].id)
        ]
        
        db.session.add_all(questions)
        db.session.commit()
        
        exam_dates = [
            ExamDate(date=datetime(2025, 7, 15, 10, 0), program_id=programs[0].id),
            ExamDate(date=datetime(2025, 7, 16, 10, 0), program_id=programs[2].id),
            ExamDate(date=datetime(2025, 7, 17, 10, 0), program_id=programs[1].id)
        ]
        
        db.session.add_all(exam_dates)
        db.session.commit()
        
        commission_members = [
            CommissionMember(exam_date_id=exam_dates[0].id, user_id=users[2].id, role='председатель'),
            CommissionMember(exam_date_id=exam_dates[0].id, user_id=users[0].id, role='член'),
            CommissionMember(exam_date_id=exam_dates[1].id, user_id=users[4].id, role='председатель'),
            CommissionMember(exam_date_id=exam_dates[1].id, user_id=users[3].id, role='член')
        ]
        
        db.session.add_all(commission_members)
        db.session.commit()
        
        standard_commissions = [
            StandardCommission(program_id=programs[0].id, user_id=users[2].id, role='председатель'),
            StandardCommission(program_id=programs[0].id, user_id=users[0].id, role='член'),
            StandardCommission(program_id=programs[2].id, user_id=users[4].id, role='председатель'),
            StandardCommission(program_id=programs[2].id, user_id=users[3].id, role='член')
        ]
        
        db.session.add_all(standard_commissions)
        db.session.commit()
        
        applicants = [
            Applicant(full_name='Смирнов Андрей Викторович', program_id=programs[0].id, exam_date_id=exam_dates[0].id),
            Applicant(full_name='Кузнецова Елена Олеговна', program_id=programs[0].id, exam_date_id=exam_dates[0].id),
            Applicant(full_name='Попов Игорь Сергеевич', program_id=programs[2].id, exam_date_id=exam_dates[1].id),
            Applicant(full_name='Васильева Анна Дмитриевна', program_id=programs[2].id, exam_date_id=exam_dates[1].id)
        ]
        
        db.session.add_all(applicants)
        db.session.commit()
        
        scores = [
            Score(applicant_id=applicants[0].id, question_id=questions[0].id, score=25),
            Score(applicant_id=applicants[0].id, question_id=questions[1].id, score=30),
            Score(applicant_id=applicants[2].id, question_id=questions[3].id, score=40),
            Score(applicant_id=applicants[2].id, question_id=questions[4].id, score=35)
        ]
        
        db.session.add_all(scores)
        db.session.commit()
        
        print("База данных успешно создана с тестовыми данными!")

if __name__ == '__main__':
    from datetime import datetime
    create_database()