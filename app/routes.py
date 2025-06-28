import pandas as pd
from flask import render_template, redirect, send_from_directory, url_for, flash, request, send_file, abort, Blueprint, current_app
from flask_login import login_user, logout_user, current_user, login_required
from . import db, bcrypt
from .models import (User, Program, ExamDate, CommissionMember, Applicant, 
                    Question, Score, StandardCommission, EngineeringSchool)
from .forms import (LoginForm, EngineeringSchoolForm, ProgramForm, ExamDateForm, 
                   AssignCommissionForm, ApplicantForm, ScoreForm, UserForm, 
                   StandardCommissionForm, EditScoreForm, QuestionForm, 
                   UploadApplicantsForm, UploadScheduleForm)
from .utils import generate_protocol, generate_vedomost
from datetime import datetime, date
import os
from io import BytesIO
from werkzeug.utils import secure_filename

routes = Blueprint('routes', __name__)

def allowed_file(filename):
    """Проверяет разрешенные расширения файлов"""
    allowed_extensions = {'xlsx', 'xls', 'csv', 'xlsm', 'xlsb'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Вспомогательная функция для проверки доступа к программе
def check_program_access(program_id):
    if current_user.role == 'admin':
        return True
    elif current_user.role == 'secretary':
        program = Program.query.get_or_404(program_id)
        return program.school_id == current_user.school_id
    return False

# Вспомогательная функция для проверки доступа к школе
def check_school_access(school_id):
    if current_user.role == 'admin':
        return True
    elif current_user.role == 'secretary':
        return school_id == current_user.school_id
    return False

@routes.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('routes.admin_dashboard'))
        elif current_user.role == 'secretary':
            return redirect(url_for('routes.secretary_dashboard'))
        else:
            return redirect(url_for('routes.enter_scores'))
    return redirect(url_for('routes.login'))

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        #if user:
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('routes.home'))
        flash('Неверный логин или пароль')
    return render_template('login.html', form=form)

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))

@routes.route('/static/cat.png')
def serve_cat():
    try:
        # Путь относительно папки app
        return send_from_directory('static/img', 'cat.png')
    except FileNotFoundError:
        abort(404)

# Дашборд администратора
@routes.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        abort(403)
    return render_template('admin_dashboard.html')

# Дашборд секретаря
@routes.route('/secretary')
@login_required
def secretary_dashboard():
    if current_user.role != 'secretary':
        abort(403)
    return render_template('secretary_dashboard.html')

# Управление инженерными школами (только админ)
@routes.route('/engineering_schools', methods=['GET', 'POST'])
@login_required
def engineering_schools():
    if current_user.role != 'admin':
        abort(403)
    
    form = EngineeringSchoolForm()
    if form.validate_on_submit():
        school = EngineeringSchool(name=form.name.data)
        db.session.add(school)
        db.session.commit()
        flash('Инженерная школа добавлена')
        return redirect(url_for('routes.engineering_schools'))
    
    schools = EngineeringSchool.query.all()
    return render_template('engineering_schools.html', form=form, schools=schools)

@routes.route('/delete_school/<int:school_id>', methods=['POST'])
@login_required
def delete_school(school_id):
    if current_user.role != 'admin':
        abort(403)
    
    school = EngineeringSchool.query.get_or_404(school_id)
    db.session.delete(school)
    db.session.commit()
    flash('Инженерная школа удалена')
    return redirect(url_for('routes.engineering_schools'))

# Управление программами

# Управление программами
@routes.route('/programs', methods=['GET', 'POST'])
@login_required
def programs():
    if current_user.role not in ['admin', 'secretary']:
        abort(403)
    
    form = ProgramForm()

    # Для секретаря - только его школа
    if current_user.role == 'secretary':
        form.school_id.data = current_user.school_id
        form.school_id.choices = [(s.id, s.name) for s in EngineeringSchool.query.order_by('name').all() if s.id == current_user.school_id]
    else:
        form.school_id.choices = [(s.id, s.name) for s in EngineeringSchool.query.order_by('name').all()]
    if form.validate_on_submit():
        program = Program(
            code=form.code.data,
            name=form.name.data,
            school_id=form.school_id.data
        )
        db.session.add(program)
        db.session.commit()
        flash('Программа добавлена')
        return redirect(url_for('routes.programs'))
    
    # Фильтрация программ
    if current_user.role == 'secretary':
        programs = Program.query.filter_by(school_id=current_user.school_id).all()
    else:  # admin
        programs = Program.query.all()
    
    return render_template('programs.html', form=form, programs=programs)

@routes.route('/delete_program/<int:program_id>', methods=['POST'])
@login_required
def delete_program(program_id):
    if current_user.role not in ['admin', 'secretary']:
        abort(403)
    
    if not check_program_access(program_id):
        abort(403)
    
    program = Program.query.get_or_404(program_id)
    db.session.delete(program)
    db.session.commit()
    flash('Программа удалена')
    return redirect(url_for('routes.programs'))

# Управление датами экзаменов
@routes.route('/exam_dates', methods=['GET', 'POST'])
@login_required
def exam_dates():
    if current_user.role not in ['admin', 'secretary']:
        abort(403)
    
    form = ExamDateForm()
    
    # Фильтрация программ для секретаря
    if current_user.role == 'secretary':
        form.program_id.choices = [
            (p.id, f"{p.code} {p.name}") 
            for p in Program.query.filter_by(school_id=current_user.school_id)
        ]
    
    if form.validate_on_submit():
        exam_date = ExamDate(
            date=form.date.data,
            program_id=form.program_id.data
        )
        db.session.add(exam_date)
        db.session.commit()
        flash('Дата экзамена добавлена')
        return redirect(url_for('routes.exam_dates'))
    
    exam_dates = ExamDate.query.all()
    return render_template('exam_dates.html', form=form, exam_dates=exam_dates)

# Назначение комиссии
@routes.route('/assign_commission/<int:exam_date_id>', methods=['GET', 'POST'])
@login_required
def assign_commission(exam_date_id):
    if current_user.role not in ['admin', 'secretary']:
        abort(403)
    
    exam_date = ExamDate.query.get_or_404(exam_date_id)
    form = AssignCommissionForm()
    
    if form.validate_on_submit():
        member = CommissionMember(
            exam_date_id=exam_date_id,
            user_id=form.user_id.data,
            role=form.role.data
        )
        db.session.add(member)
        db.session.commit()
        flash('Член комиссии добавлен')
        return redirect(url_for('routes.assign_commission', exam_date_id=exam_date_id))
    
    return render_template('assign_commission.html', form=form, exam_date=exam_date)

@routes.route('/delete_commission_member/<int:member_id>', methods=['POST'])
@login_required
def delete_commission_member(member_id):
    if current_user.role not in ['admin', 'secretary']:
        abort(403)
    
    member = CommissionMember.query.get_or_404(member_id)
    exam_date_id = member.exam_date_id
    db.session.delete(member)
    db.session.commit()
    flash('Член комиссии удален')
    return redirect(url_for('routes.assign_commission', exam_date_id=exam_date_id))

# Управление абитуриентами
@routes.route('/applicants', methods=['GET', 'POST'])
@login_required
def applicants():
    if current_user.role not in ['admin', 'secretary']:
        abort(403)
    
    form = ApplicantForm()
    upload_form = UploadApplicantsForm()
    
    # Фильтрация программ для секретаря
    if current_user.role == 'secretary':
        form.program_id.choices = [
            (p.id, f"{p.code} {p.name}") 
            for p in Program.query.filter_by(school_id=current_user.school_id)
        ]
    
    if form.validate_on_submit():
        applicant = Applicant(
            full_name=form.full_name.data,
            program_id=form.program_id.data
        )
        db.session.add(applicant)
        db.session.commit()
        flash('Абитуриент добавлен')
        return redirect(url_for('routes.applicants'))
    
    # Фильтрация абитуриентов
    if current_user.role == 'secretary':
        applicants = Applicant.query.join(Program).filter(
            Program.school_id == current_user.school_id
        ).all()
    else:  # admin
        applicants = Applicant.query.all()
    
    return render_template('applicants.html', form=form, upload_form=upload_form, applicants=applicants)

# Назначение абитуриентов на дату экзамена
@routes.route('/assign_applicants/<int:exam_date_id>', methods=['GET', 'POST'])
@login_required
def assign_applicants(exam_date_id):
    if current_user.role not in ['admin', 'secretary']:
        abort(403)
    
    exam_date = ExamDate.query.get_or_404(exam_date_id)
    program_id = exam_date.program_id
    
    if not check_program_access(program_id):
        abort(403)
    
    if request.method == 'POST':
        applicant_ids = request.form.getlist('applicant_ids')
        for applicant_id in applicant_ids:
            applicant = Applicant.query.get(applicant_id)
            applicant.exam_date_id = exam_date_id
        db.session.commit()
        flash('Абитуриенты назначены')
        return redirect(url_for('routes.assign_applicants', exam_date_id=exam_date_id))
    
    applicants = Applicant.query.filter_by(program_id=program_id, exam_date_id=None).all()
    return render_template('assign_applicants.html', exam_date=exam_date, applicants=applicants)

# Выставление баллов
@routes.route('/enter_scores')
@login_required
def enter_scores():
    if current_user.role not in ['admin', 'secretary', 'commission']:
        abort(403)
    
    today = date.today()
    exam_dates = ExamDate.query.join(CommissionMember).filter(
        db.func.date(ExamDate.date) == today,
        CommissionMember.user_id == current_user.id
    ).all()
    
    return render_template('enter_scores.html', exam_dates=exam_dates)

@routes.route('/enter_scores/<int:applicant_id>', methods=['GET', 'POST'])
@login_required
def applicant_scores(applicant_id):
    if current_user.role not in ['admin', 'secretary', 'commission']:
        abort(403)
    
    applicant = Applicant.query.get_or_404(applicant_id)
    exam_date = applicant.exam_date

    form = ScoreForm()
    form.question_id.choices = [(q.id, q.text) for q in Question.query.filter_by(program_id=applicant.program_id).all()]
    
    if form.validate_on_submit():
        total_score = sum(score.score for score in applicant.scores)
        if total_score + form.score.data > 100:
            flash('Сумма баллов не может превышать 100')
            return redirect(url_for('routes.applicant_scores', applicant_id=applicant_id))
        
        existing_score = Score.query.filter_by(
            applicant_id=applicant_id,
            question_id=form.question_id.data
        ).first()
        
        if existing_score:
            flash('Этот вопрос уже был задан абитуриенту')
        else:
            score = Score(
                applicant_id=applicant_id,
                question_id=form.question_id.data,
                score=form.score.data
            )
            db.session.add(score)
            db.session.commit()
            flash('Балл добавлен')
        
        return redirect(url_for('routes.applicant_scores', applicant_id=applicant_id))
    
    return render_template('enter_scores_detail.html', applicant=applicant, form=form)

    if current_user.role not in ['admin', 'secretary', 'commission']:
        abort(403)
    
    applicant = Applicant.query.get_or_404(applicant_id)
    exam_date = applicant.exam_date
    
    if exam_date.date.date() != date.today():
        flash('Выставление баллов возможно только в день экзамена')
        return redirect(url_for('routes.enter_scores'))
    
    form = ScoreForm()
    form.question_id.choices = [(q.id, q.text) for q in Question.query.filter_by(program_id=applicant.program_id).all()]
    
    if form.validate_on_submit():
        total_score = sum(score.score for score in applicant.scores)
        if total_score + form.score.data > 100:
            flash('Сумма баллов не может превышать 100')
            return redirect(url_for('routes.applicant_scores', applicant_id=applicant_id))
        
        existing_score = Score.query.filter_by(
            applicant_id=applicant_id,
            question_id=form.question_id.data
        ).first()
        
        if existing_score:
            flash('Этот вопрос уже был задан абитуриенту')
        else:
            score = Score(
                applicant_id=applicant_id,
                question_id=form.question_id.data,
                score=form.score.data
            )
            db.session.add(score)
            db.session.commit()
            flash('Балл добавлен')
        
        return redirect(url_for('routes.applicant_scores', applicant_id=applicant_id))
    
    return render_template('enter_scores_detail.html', applicant=applicant, form=form)

# Генерация протокола
@routes.route('/protocol/<int:applicant_id>')
@login_required
def view_protocol(applicant_id):
    applicant = Applicant.query.get_or_404(applicant_id)
    exam_date = applicant.exam_date
    
    # Проверка доступа
    if current_user.role == 'commission':
        if exam_date.date.date() != date.today():
            abort(403)
        # Проверяем, что пользователь в комиссии
        if not any(member.user_id == current_user.id for member in exam_date.commission):
            abort(403)
    
    doc = generate_protocol(applicant, exam_date)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    filename = f"protocol_{applicant.id}.docx"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

# Генерация ведомости
@routes.route('/vedomost/<int:exam_date_id>')
@login_required
def view_vedomost(exam_date_id):
    if current_user.role not in ['admin', 'secretary']:
        abort(403)
    
    exam_date = ExamDate.query.get_or_404(exam_date_id)
    
    # Проверка доступа для секретаря
    if current_user.role == 'secretary':
        if not check_program_access(exam_date.program_id):
            abort(403)
    
    doc = generate_vedomost(exam_date)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    filename = f"vedomost_{exam_date.id}.docx"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

# Управление пользователями (только админ)
@routes.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        abort(403)
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@routes.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        abort(403)
    
    form = UserForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            password=hashed_password,
            full_name=form.full_name.data,
            position=form.position.data,
            role=form.role.data,
            school_id=form.school_id.data if form.school_id.data != 0 else None
        )
        db.session.add(user)
        db.session.commit()
        flash('Пользователь добавлен')
        return redirect(url_for('routes.users'))
    return render_template('add_user.html', form=form)

@routes.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        abort(403)
    
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        user.username = form.username.data
        if form.password.data:
            user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.full_name = form.full_name.data
        user.position = form.position.data
        user.role = form.role.data
        user.school_id = form.school_id.data if form.school_id.data != 0 else None
        db.session.commit()
        flash('Данные пользователя обновлены')
        return redirect(url_for('routes.users'))
    
    return render_template('edit_user.html', form=form, user=user)

@routes.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        abort(403)
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Пользователь удален')
    return redirect(url_for('routes.users'))

# Стандартные комиссии
@routes.route('/standard_commission', methods=['GET', 'POST'])
@login_required
def standard_commission():
    if current_user.role not in ['admin', 'secretary']:
        abort(403)
    
    form = StandardCommissionForm()
    
    # Фильтрация программ для секретаря
    if current_user.role == 'secretary':
        form.program_id.choices = [
            (p.id, f"{p.code} {p.name}") 
            for p in Program.query.filter_by(school_id=current_user.school_id)
        ]
    
    if form.validate_on_submit():
        existing = StandardCommission.query.filter_by(
            program_id=form.program_id.data,
            user_id=form.user_id.data
        ).first()
        
        if existing:
            flash('Этот член комиссии уже добавлен для данной программы')
        else:
            commission = StandardCommission(
                program_id=form.program_id.data,
                user_id=form.user_id.data,
                role=form.role.data
            )
            db.session.add(commission)
            db.session.commit()
            flash('Стандартный член комиссии добавлен')
        
        return redirect(url_for('routes.standard_commission'))
    
    commissions = StandardCommission.query.all()
    return render_template('standard_commission.html', form=form, commissions=commissions)

@routes.route('/delete_standard_commission/<int:commission_id>', methods=['POST'])
@login_required
def delete_standard_commission(commission_id):
    if current_user.role not in ['admin', 'secretary']:
        abort(403)
    
    commission = StandardCommission.query.get_or_404(commission_id)
    db.session.delete(commission)
    db.session.commit()
    flash('Член стандартной комиссии удален')
    return redirect(url_for('routes.standard_commission'))

# Управление вопросами
@routes.route('/questions', methods=['GET', 'POST'])
@login_required
def questions():
    if current_user.role not in ['admin', 'secretary']:
        abort(403)
    
    form = QuestionForm()
    
    # Фильтрация программ для секретаря
    if current_user.role == 'secretary':
        form.program_id.choices = [
            (p.id, f"{p.code} {p.name}") 
            for p in Program.query.filter_by(school_id=current_user.school_id)
        ]
    
    if form.validate_on_submit():
        question = Question(
            text=form.text.data,
            program_id=form.program_id.data
        )
        db.session.add(question)
        db.session.commit()
        flash('Вопрос добавлен')
        return redirect(url_for('routes.questions'))
    
    # Фильтрация вопросов
    if current_user.role == 'secretary':
        questions = Question.query.join(Program).filter(
            Program.school_id == current_user.school_id
        ).all()
    else:  # admin
        questions = Question.query.all()
    
    return render_template('questions.html', form=form, questions=questions)

@routes.route('/delete_question/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    if current_user.role not in ['admin', 'secretary']:
        abort(403)
    
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Вопрос удален')
    return redirect(url_for('routes.questions'))

# Редактирование баллов
@routes.route('/edit_score/<int:score_id>', methods=['GET', 'POST'])
@login_required
def edit_score(score_id):
    if current_user.role not in ['admin', 'secretary', 'commission']:
        abort(403)
    
    score = Score.query.get_or_404(score_id)
    applicant = score.applicant
    exam_date = applicant.exam_date
    
    if exam_date.date.date() != date.today():
        flash('Редактирование баллов возможно только в день экзамена')
        return redirect(url_for('routes.enter_scores'))
    
    form = EditScoreForm()
    
    if form.validate_on_submit():
        total_score = sum(s.score for s in applicant.scores if s.id != score_id)
        if total_score + form.score.data > 100:
            flash('Сумма баллов не может превышать 100')
            return redirect(url_for('routes.edit_score', score_id=score_id))
        
        score.score = form.score.data
        db.session.commit()
        flash('Балл обновлен')
        return redirect(url_for('routes.applicant_scores', applicant_id=applicant.id))
    
    form.score.data = score.score
    return render_template('edit_score.html', form=form, score=score)

@routes.route('/delete_score/<int:score_id>', methods=['POST'])
@login_required
def delete_score(score_id):
    if current_user.role not in ['admin', 'secretary', 'commission']:
        abort(403)
    
    score = Score.query.get_or_404(score_id)
    applicant_id = score.applicant.id
    exam_date = score.applicant.exam_date
    
    if exam_date.date.date() != date.today():
        flash('Удаление баллов возможно только в день экзамена')
        return redirect(url_for('routes.enter_scores'))
    
    db.session.delete(score)
    db.session.commit()
    flash('Балл удален')
    return redirect(url_for('routes.applicant_scores', applicant_id=applicant_id))

# Загрузка абитуриентов
@routes.route('/upload_applicants', methods=['POST'])
@login_required
def upload_applicants():
    if current_user.role not in ['admin', 'secretary']:
        abort(403)
    
    form = UploadApplicantsForm()
    
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif filename.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                flash('Неподдерживаемый формат файла')
                return redirect(url_for('routes.applicants'))
            
            for index, row in df.iterrows():
                full_name = row['ФИО']
                program_code = row['Код']
                program_name = row['Направление']
                exam_date_str = row.get('Дата сдачи', None)
                
                # Находим программу
                program = Program.query.filter_by(code=program_code).first()
                
                # Для секретаря: создаем программу только в его школе
                if not program and current_user.role == 'secretary':
                    program = Program(
                        code=program_code, 
                        name=program_name,
                        school_id=current_user.school_id
                    )
                    db.session.add(program)
                    db.session.commit()
                
                # Пропуск если программа не найдена и не создана
                if not program:
                    flash(f'Программа с кодом {program_code} не найдена')
                    continue
                
                # Проверка доступа для секретаря
                if current_user.role == 'secretary' and program.school_id != current_user.school_id:
                    flash(f'Нет доступа к программе {program_code}')
                    continue
                
                exam_date = None
                if exam_date_str:
                    try:
                        exam_date_obj = datetime.strptime(exam_date_str, '%Y-%m-%d')
                        exam_date = ExamDate.query.filter_by(
                            date=exam_date_obj,
                            program_id=program.id
                        ).first()
                        
                        if not exam_date:
                            exam_date = ExamDate(
                                date=exam_date_obj, 
                                program_id=program.id
                            )
                            db.session.add(exam_date)
                            db.session.commit()
                    except ValueError:
                        flash(f'Ошибка формата даты в строке {index + 1}: {exam_date_str}')
                        continue
                
                applicant = Applicant(
                    full_name=full_name,
                    program_id=program.id,
                    exam_date_id=exam_date.id if exam_date else None
                )
                db.session.add(applicant)
            
            db.session.commit()
            flash('Абитуриенты успешно загружены')
        except Exception as e:
            flash(f'Ошибка при обработке файла: {str(e)}')
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        flash('Ошибка валидации формы')
    
    return redirect(url_for('routes.applicants'))

# Загрузка расписания (только секретарь и админ)
@routes.route('/upload_schedule', methods=['GET', 'POST'])
@login_required
def upload_schedule():
    if current_user.role not in ['admin', 'secretary']:
        abort(403)

    form = UploadScheduleForm()

    if form.validate_on_submit():
        if 'file' not in request.files:
            flash('Файл не был отправлен')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('Не выбран файл для загрузки')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(temp_path)

                # Чтение файла с учетом возможных разных форматов
                if filename.endswith('.csv'):
                    df = pd.read_csv(temp_path)
                else:
                    df = pd.read_excel(temp_path, engine='openpyxl')

                print("Колонки в файле:", df.columns.tolist())

                # Проверка обязательных столбцов
                required_columns = ['Дата/Время экз', 'Дисциплина', 'ООП']
                for col in required_columns:
                    if col not in df.columns:
                        raise ValueError(f"Отсутствует обязательная колонка: {col}")

                # Обработка данных
                for index, row in df.iterrows():
                    try:
                        # 1. Проверяем обязательные поля
                        if not all(pd.notna(row[field]) for field in ['Ф', 'И', 'О']):
                            raise ValueError("Отсутствует обязательное поле ФИО")

                        # 2. Собираем ФИО в одну строку
                        full_name = f"{row['Ф']} {row['И']} {row['О']}".strip()

                        # 3. Обработка программы (как было)
                        discipline_parts = str(row['Дисциплина']).split()
                        program_code = discipline_parts[0]
                        program_name = ' '.join(discipline_parts[1:])

                        program = Program.query.filter_by(code=program_code).first()
                        if not program:
                            program = Program(
                                code=program_code,
                                name=program_name,
                                school_id=current_user.school_id if current_user.role == 'secretary' else None
                            )
                            db.session.add(program)
                            db.session.commit()

                        # 4. Обработка даты экзамена
                        exam_datetime = pd.to_datetime(row['Дата/Время экз'])
                        exam_date = ExamDate.query.filter_by(
                            date=exam_datetime,
                            program_id=program.id
                        ).first()

                        if not exam_date:
                            exam_date = ExamDate(
                                date=exam_datetime,
                                program_id=program.id
                            )
                            db.session.add(exam_date)
                            db.session.commit()

                        # 5. Поиск абитуриента по полному имени и программе
                        applicant = Applicant.query.filter_by(
                            full_name=full_name,
                            program_id=program.id
                        ).first()

                        if not applicant:
                            # Создаем нового абитуриента
                            applicant = Applicant(
                                full_name=full_name,
                                program_id=program.id,
                                exam_date_id=exam_date.id if exam_date else None
                                # Другие поля, если они есть в вашей модели
                            )
                            db.session.add(applicant)

                        # 6. Обновляем дату экзамена, если нужно
                        if exam_date and not applicant.exam_date_id:
                            applicant.exam_date_id = exam_date.id

                    except Exception as e:
                        flash(f'Ошибка в строке {index + 2}: {str(e)}', 'error')
                        current_app.logger.error(f"Ошибка обработки строки {index + 2}", exc_info=e)
                        continue

                        db.session.commit()

                        # 4. Связываем абитуриента с экзаменом (если связь еще не существует)
                        if exam_date not in applicant.exams:
                            applicant.exams.append(exam_date)

                    except Exception as e:
                        flash(f'Ошибка в строке {index + 2}: {str(e)}', 'error')
                        current_app.logger.error(f"Ошибка в строке {index + 2}", exc_info=e)
                        continue

                        db.session.commit()

                        # 4. Связь абитуриента с экзаменом (если еще не связаны)
                        if applicant not in exam_date.applicants:
                            exam_date.applicants.append(applicant)

                    except Exception as e:
                        flash(f'Ошибка в строке {index + 2}: {str(e)}', 'error')
                        continue

                db.session.commit()
                flash('Расписание успешно загружено!', 'success')

            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка при обработке файла: {str(e)}', 'error')

            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            return redirect(url_for('routes.upload_schedule'))

        flash('Допустимые форматы: .xlsx, .xls, .csv', 'error')

    return render_template('upload_schedule.html', form=form)