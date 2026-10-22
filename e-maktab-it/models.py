from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    class_name = db.Column(db.String(30), nullable=False, index=True)
    group_name = db.Column(db.String(60), nullable=False, default="Asosiy")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    entries = db.relationship("JournalEntry", back_populates="student", cascade="all, delete-orphan")


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    topic = db.Column(db.String(240), nullable=False)
    class_name = db.Column(db.String(30), nullable=False)
    quarter = db.Column(db.String(20), nullable=False, default="1-chorak")
    lesson_type = db.Column(db.String(30), nullable=False, default="Amaliy")
    entries = db.relationship("JournalEntry", back_populates="lesson", cascade="all, delete-orphan")


class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lesson.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    attendance = db.Column(db.String(2))
    grade = db.Column(db.Integer)
    lesson = db.relationship("Lesson", back_populates="entries")
    student = db.relationship("Student", back_populates="entries")
    __table_args__ = (db.UniqueConstraint("lesson_id", "student_id", name="uq_lesson_student"),)


class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    category = db.Column(db.String(50), nullable=False, default="Kompyuter")
    serial_number = db.Column(db.String(100), unique=True)
    room = db.Column(db.String(60))
    status = db.Column(db.String(30), nullable=False, default="Soz")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher = db.Column(db.String(160), nullable=False)
    room = db.Column(db.String(60))
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default="O‘rta")
    status = db.Column(db.String(30), nullable=False, default="Yangi")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
