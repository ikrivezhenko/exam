from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, Optional, InputRequired
from .models import Program, User, EngineeringSchool
from datetime import date
from flask_wtf.file import FileField, FileRequired

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class EngineeringSchoolForm(FlaskForm):
    name = StringField('Название школы', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Добавить')

class ProgramForm(FlaskForm):
    code = StringField('Код программы', validators=[DataRequired(), Length(min=2, max=50)])
    name = StringField('Название программы', validators=[DataRequired(), Length(min=5, max=200)])
    school_id = SelectField('Инженерная школа', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self, *args, **kwargs):
        super(ProgramForm, self).__init__(*args, **kwargs)




class ExamDateForm(FlaskForm):
    date = DateField('Дата экзамена', format='%Y-%m-%d', validators=[DataRequired()])
    program_id = SelectField('Программа', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Создать')

    def __init__(self, *args, **kwargs):
        super(ExamDateForm, self).__init__(*args, **kwargs)
        self.program_id.choices = [(p.id, f"{p.code} {p.name}") for p in Program.query.all()]

class AssignCommissionForm(FlaskForm):
    user_id = SelectField('Член комиссии', coerce=int, validators=[DataRequired()])
    role = SelectField('Должность', choices=[
        ('председатель', 'Председатель'),
        ('заместитель', 'Заместитель председателя'),
        ('член', 'Член комиссии')
    ], validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self, *args, **kwargs):
        super(AssignCommissionForm, self).__init__(*args, **kwargs)
        self.user_id.choices = [(u.id, u.full_name) for u in User.query.filter(User.role.in_(['commission', 'secretary', 'admin'])).all()]

class ApplicantForm(FlaskForm):
    full_name = StringField('ФИО', validators=[DataRequired(), Length(min=5, max=200)])
    program_id = SelectField('Программа', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self, *args, **kwargs):
        super(ApplicantForm, self).__init__(*args, **kwargs)
        self.program_id.choices = [(p.id, f"{p.code} {p.name}") for p in Program.query.all()]


class EditApplicantForm(ApplicantForm):
    # Изменяем метку кнопки
    submit = SubmitField('Обновить')

    def __init__(self, *args, **kwargs):
        super(EditApplicantForm, self).__init__(*args, **kwargs)
class ScoreForm(FlaskForm):
    question_id = SelectField('Вопрос', coerce=int, validators=[DataRequired()])
    score = IntegerField('Балл', validators=[InputRequired()])
    submit = SubmitField('Добавить')


class UserForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Пароль')
    full_name = StringField('ФИО', validators=[DataRequired(), Length(min=5, max=100)])
    position = StringField('Должность', validators=[DataRequired(), Length(min=3, max=100)])
    role = SelectField('Роль', choices=[
        ('admin', 'Администратор'),
        ('secretary', 'Ответственный секретарь'),
        ('commission', 'Экзаменатор')
    ], validators=[DataRequired()])
    school_id = SelectField('Инженерная школа', coerce=int, validators=[Optional()])
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.school_id.choices = [(s.id, s.name) for s in EngineeringSchool.query.all()]
        self.school_id.choices.insert(0, (0, '-- Не выбрана --'))

class StandardCommissionForm(FlaskForm):
    program_id = SelectField('Программа', coerce=int, validators=[DataRequired()])
    user_id = SelectField('Член комиссии', coerce=int, validators=[DataRequired()])
    role = SelectField('Должность', choices=[
        ('председатель', 'Председатель'),
        ('заместитель', 'Заместитель председателя'),
        ('член', 'Член комиссии')
    ], validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self, *args, **kwargs):
        super(StandardCommissionForm, self).__init__(*args, **kwargs)
        self.program_id.choices = [(p.id, f"{p.code} {p.name}") for p in Program.query.all()]
        self.user_id.choices = [(u.id, u.full_name) for u in User.query.filter(User.role.in_(['commission', 'secretary', 'admin'])).all()]


class EditScoreForm(FlaskForm):
    score = IntegerField('Балл', validators=[InputRequired()])
    submit = SubmitField('Обновить')


class QuestionForm(FlaskForm):
    text = TextAreaField('Текст вопроса', validators=[DataRequired()])
    program_id = SelectField('Программа', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.program_id.choices = [(p.id, f"{p.code} {p.name}") for p in Program.query.all()]

class UploadApplicantsForm(FlaskForm):
    file = FileField('Файл с абитуриентами (CSV или Excel)', validators=[FileRequired()])
    submit = SubmitField('Загрузить')

class UploadScheduleForm(FlaskForm):
    file = FileField('Файл с расписанием (CSV или Excel)', validators=[FileRequired()])
    submit = SubmitField('Загрузить')

class ProgramForm(FlaskForm):
    code = StringField('Код программы', validators=[DataRequired(), Length(min=2, max=50)])
    name = StringField('Название программы', validators=[DataRequired(), Length(min=5, max=200)])
    oop = StringField("Название ООП", validators=[DataRequired(), Length(min=5, max=200)])
    school_id = SelectField('Инженерная школа', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self, *args, **kwargs):
        super(ProgramForm, self).__init__(*args, **kwargs)
