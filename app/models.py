from . import db
from flask_login import UserMixin

class EngineeringSchool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    programs = db.relationship('Program', backref='school', lazy=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'secretary', 'commission'
    school_id = db.Column(db.Integer, db.ForeignKey('engineering_school.id'))
    commission_members = db.relationship('CommissionMember', back_populates='user', cascade='all, delete-orphan')
    standard_commissions = db.relationship('StandardCommission', back_populates='user', cascade='all, delete-orphan')

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('engineering_school.id'))
    questions = db.relationship('Question', backref='program', lazy=True, cascade='all, delete-orphan')
    standard_commission = db.relationship('StandardCommission', backref='program', lazy=True, cascade='all, delete-orphan')
    applicants = db.relationship('Applicant', backref='program', lazy=True)
    exam_dates = db.relationship('ExamDate', backref='program', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)

class ExamDate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    commission = db.relationship('CommissionMember', backref='exam_date', lazy=True, cascade='all, delete-orphan')
    applicants = db.relationship('Applicant', backref='exam_date', lazy=True)

class CommissionMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_date_id = db.Column(db.Integer, db.ForeignKey('exam_date.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'председатель', 'заместитель', 'член'
    user = db.relationship('User', back_populates='commission_members')

class StandardCommission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'председатель', 'заместитель', 'член'
    user = db.relationship('User', back_populates='standard_commissions')

class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    exam_date_id = db.Column(db.Integer, db.ForeignKey('exam_date.id'))
    scores = db.relationship('Score', backref='applicant', lazy=True, cascade='all, delete-orphan')

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    question = db.relationship('Question')