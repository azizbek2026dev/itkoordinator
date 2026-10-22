import os
from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import func
from models import db, Student, Lesson, JournalEntry, Equipment, Ticket

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-before-deploy")

database_url = os.environ.get("DATABASE_URL", "sqlite:///emaktab_it.db")
# Render's older PostgreSQL URLs may start with postgres://; SQLAlchemy expects postgresql://.
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
db.init_app(app)

with app.app_context():
    db.create_all()


@app.template_filter("datefmt")
def datefmt(value, fmt="%d.%m.%Y"):
    return value.strftime(fmt) if value else "—"


@app.route("/")
def dashboard():
    stats = {
        "students": Student.query.count(),
        "equipment": Equipment.query.count(),
        "working": Equipment.query.filter_by(status="Soz").count(),
        "open_tickets": Ticket.query.filter(Ticket.status != "Yopildi").count(),
        "lessons": Lesson.query.count(),
    }
    latest_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all()
    equipment_alerts = Equipment.query.filter(Equipment.status != "Soz").limit(5).all()
    return render_template("dashboard.html", stats=stats, latest_tickets=latest_tickets,
                           equipment_alerts=equipment_alerts, page="dashboard")


@app.route("/students", methods=["GET", "POST"])
def students():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        class_name = request.form.get("class_name", "").strip()
        group_name = request.form.get("group_name", "").strip()
        if not name or not class_name:
            flash("O‘quvchi F.I.Sh. va sinf maydonlarini to‘ldiring.", "error")
        else:
            db.session.add(Student(name=name, class_name=class_name, group_name=group_name or "Asosiy"))
            db.session.commit()
            flash("O‘quvchi qo‘shildi.", "success")
        return redirect(url_for("students"))
    rows = Student.query.order_by(Student.class_name, Student.name).all()
    return render_template("students.html", students=rows, page="students")


@app.post("/students/<int:student_id>/delete")
def delete_student(student_id):
    student = db.get_or_404(Student, student_id)
    JournalEntry.query.filter_by(student_id=student.id).delete()
    db.session.delete(student)
    db.session.commit()
    flash("O‘quvchi o‘chirildi.", "success")
    return redirect(url_for("students"))


@app.route("/lessons", methods=["GET", "POST"])
def lessons():
    if request.method == "POST":
        topic = request.form.get("topic", "").strip()
        lesson_date = request.form.get("lesson_date", "")
        class_name = request.form.get("class_name", "").strip()
        quarter = request.form.get("quarter", "1-chorak")
        lesson_type = request.form.get("lesson_type", "Amaliy")
        if not topic or not lesson_date or not class_name:
            flash("Sana, sinf va mavzuni kiriting.", "error")
        else:
            try:
                parsed_date = date.fromisoformat(lesson_date)
                db.session.add(Lesson(date=parsed_date, topic=topic, class_name=class_name,
                                      quarter=quarter, lesson_type=lesson_type))
                db.session.commit()
                flash("Dars jadvalga qo‘shildi.", "success")
            except ValueError:
                flash("Sana formati noto‘g‘ri.", "error")
        return redirect(url_for("lessons"))
    rows = Lesson.query.order_by(Lesson.date.desc(), Lesson.id.desc()).all()
    students = Student.query.order_by(Student.class_name, Student.name).all()
    entries = {(e.lesson_id, e.student_id): e for e in JournalEntry.query.all()}
    return render_template("lessons.html", lessons=rows, students=students, entries=entries,
                           today=date.today().isoformat(), page="lessons")


@app.post("/lessons/<int:lesson_id>/entry")
def save_entry(lesson_id):
    lesson = db.get_or_404(Lesson, lesson_id)
    student_id = request.form.get("student_id", type=int)
    student = db.get_or_404(Student, student_id)
    attendance = request.form.get("attendance", "")
    grade = request.form.get("grade", "").strip()
    if attendance not in ("+", "q", "s", ""):
        flash("Davomat belgisi noto‘g‘ri.", "error")
        return redirect(url_for("lessons"))
    grade_value = int(grade) if grade in ("1", "2", "3", "4", "5") else None
    entry = JournalEntry.query.filter_by(lesson_id=lesson.id, student_id=student.id).first()
    if not entry:
        entry = JournalEntry(lesson_id=lesson.id, student_id=student.id)
        db.session.add(entry)
    entry.attendance = attendance or None
    entry.grade = grade_value
    db.session.commit()
    flash(f"{student.name} uchun jurnal saqlandi.", "success")
    return redirect(url_for("lessons"))


@app.post("/lessons/<int:lesson_id>/delete")
def delete_lesson(lesson_id):
    lesson = db.get_or_404(Lesson, lesson_id)
    JournalEntry.query.filter_by(lesson_id=lesson.id).delete()
    db.session.delete(lesson)
    db.session.commit()
    flash("Dars o‘chirildi.", "success")
    return redirect(url_for("lessons"))


@app.route("/inventory", methods=["GET", "POST"])
def inventory():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        serial_number = request.form.get("serial_number", "").strip()
        room = request.form.get("room", "").strip()
        status = request.form.get("status", "Soz")
        category = request.form.get("category", "Kompyuter")
        if not name:
            flash("Jihoz nomini kiriting.", "error")
        else:
            db.session.add(Equipment(name=name, serial_number=serial_number or None, room=room or None,
                                     status=status if status in ("Soz", "Ta'mirda", "Buzuq") else "Soz",
                                     category=category))
            db.session.commit()
            flash("Jihoz qo‘shildi.", "success")
        return redirect(url_for("inventory"))
    rows = Equipment.query.order_by(Equipment.name).all()
    return render_template("inventory.html", equipment=rows, page="inventory")


@app.post("/inventory/<int:item_id>/update")
def update_equipment(item_id):
    item = db.get_or_404(Equipment, item_id)
    status = request.form.get("status", "Soz")
    if status in ("Soz", "Ta'mirda", "Buzuq"):
        item.status = status
        db.session.commit()
        flash("Jihoz holati yangilandi.", "success")
    return redirect(url_for("inventory"))


@app.post("/inventory/<int:item_id>/delete")
def delete_equipment(item_id):
    item = db.get_or_404(Equipment, item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Jihoz o‘chirildi.", "success")
    return redirect(url_for("inventory"))


@app.route("/tickets", methods=["GET", "POST"])
def tickets():
    if request.method == "POST":
        teacher = request.form.get("teacher", "").strip()
        room = request.form.get("room", "").strip()
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "O‘rta")
        if not teacher or not title or not description:
            flash("Ism, muammo nomi va tavsifini to‘ldiring.", "error")
        else:
            db.session.add(Ticket(teacher=teacher, room=room or None, title=title,
                                  description=description,
                                  priority=priority if priority in ("Past", "O‘rta", "Yuqori") else "O‘rta"))
            db.session.commit()
            flash("Texnik yordam so‘rovi yuborildi.", "success")
        return redirect(url_for("tickets"))
    rows = Ticket.query.order_by(Ticket.created_at.desc()).all()
    return render_template("tickets.html", tickets=rows, page="tickets")


@app.post("/tickets/<int:ticket_id>/status")
def update_ticket(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    status = request.form.get("status", "Yangi")
    if status in ("Yangi", "Jarayonda", "Yopildi"):
        ticket.status = status
        db.session.commit()
        flash("So‘rov holati yangilandi.", "success")
    return redirect(url_for("tickets"))


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html", page=""), 404


if __name__ == "__main__":
    app.run(debug=True)
