import os
from decimal import Decimal, InvalidOperation

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://students:students@localhost:5432/students",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

GENDERS = ("Female", "Male", "Non-binary", "Other", "Prefer not to say")


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(40), nullable=False)
    marks = db.Column(db.Numeric(5, 2), nullable=False)

    __table_args__ = (
        CheckConstraint("age >= 1 AND age <= 120", name="student_age_range"),
        CheckConstraint("marks >= 0 AND marks <= 100", name="student_marks_range"),
    )


def get_students():
    return db.session.execute(
        db.select(Student).order_by(Student.id.desc())
    ).scalars().all()


@app.get("/")
def index():
    return render_template(
        "index.html",
        students=get_students(),
        genders=GENDERS,
        form_data={},
        errors=[],
        saved=request.args.get("saved") == "1",
    )


@app.post("/students")
def create_student():
    form_data = {
        "name": request.form.get("name", "").strip(),
        "age": request.form.get("age", "").strip(),
        "gender": request.form.get("gender", ""),
        "marks": request.form.get("marks", "").strip(),
    }
    errors = []

    if not form_data["name"]:
        errors.append("Enter the student's name.")
    elif len(form_data["name"]) > 100:
        errors.append("The name must be 100 characters or fewer.")

    try:
        age = int(form_data["age"])
        if not 1 <= age <= 120:
            errors.append("Age must be between 1 and 120.")
    except ValueError:
        age = None
        errors.append("Enter a whole-number age.")

    if form_data["gender"] not in GENDERS:
        errors.append("Choose a gender from the list.")

    try:
        marks = Decimal(form_data["marks"])
        if not marks.is_finite() or not Decimal("0") <= marks <= Decimal("100"):
            errors.append("Marks must be between 0 and 100.")
        elif marks.as_tuple().exponent < -2:
            errors.append("Marks can have at most two decimal places.")
    except InvalidOperation:
        marks = None
        errors.append("Enter a valid mark.")

    if errors:
        return (
            render_template(
                "index.html",
                students=get_students(),
                genders=GENDERS,
                form_data=form_data,
                errors=errors,
                saved=False,
            ),
            400,
        )

    db.session.add(
        Student(
            name=form_data["name"],
            age=age,
            gender=form_data["gender"],
            marks=marks,
        )
    )
    db.session.commit()
    return redirect(url_for("index", saved="1"))


with app.app_context():
    db.create_all()
