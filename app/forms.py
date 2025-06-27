from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from .models import Program, User
from datetime import date


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class ProgramForm(FlaskForm):
    code = StringField('Код программы', validators=[DataRequired(), Length(min=2, max=50)])
    name = StringField('Название программы', validators=[DataRequired(), Length(min=5, max=200)])
    submit = SubmitField('Добавить')


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
        self.user_id.choices = [(u.id, u.full_name) for u in User.query.filter_by(role='commission').all()]


class ApplicantForm(FlaskForm):
    full_name = StringField('ФИО', validators=[DataRequired(), Length(min=5, max=200)])
    program_id = SelectField('Программа', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self, *args, **kwargs):
        super(ApplicantForm, self).__init__(*args, **kwargs)
        self.program_id.choices = [(p.id, f"{p.code} {p.name}") for p in Program.query.all()]


class ScoreForm(FlaskForm):
    question_id = SelectField('Вопрос', coerce=int, validators=[DataRequired()])
    score = IntegerField('Балл', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class UserForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Пароль')
    full_name = StringField('ФИО', validators=[DataRequired(), Length(min=5, max=100)])
    position = StringField('Должность', validators=[DataRequired(), Length(min=3, max=100)])
    role = SelectField('Роль', choices=[
        ('admin', 'Администратор'),
        ('commission', 'Член комиссии')
    ], validators=[DataRequired()])
    submit = SubmitField('Сохранить')


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
        self.user_id.choices = [(u.id, u.full_name) for u in User.query.filter_by(role='commission').all()]


class EditScoreForm(FlaskForm):
    score = IntegerField('Балл', validators=[DataRequired()])
    submit = SubmitField('Обновить')


class QuestionForm(FlaskForm):
    text = TextAreaField('Текст вопроса', validators=[DataRequired()])
    program_id = SelectField('Программа', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.program_id.choices = [(p.id, f"{p.code} {p.name}") for p in Program.query.all()]

from flask_wtf.file import FileField, FileRequired

class UploadApplicantsForm(FlaskForm):
    file = FileField('Файл с абитуриентами (CSV или Excel)', validators=[FileRequired()])
    submit = SubmitField('Загрузить')