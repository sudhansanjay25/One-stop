from flask import Flask, render_template, request, redirect, session, url_for
from db.mongo import db
from datetime import datetime


app = Flask(__name__)
app.secret_key = "mock_secret_key"   # simple session key

# ---------------- LOGIN ----------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.users.find_one({
            "email": email,
            "password": password
        })

        if not user:
            return render_template("login.html", error="Invalid credentials")

        session["role"] = user["role"]
        session["ref_id"] = user["ref_id"]

        if user["role"] == "student":
            return redirect(url_for("student_dashboard"))
        elif user["role"] == "faculty":
            return redirect(url_for("faculty_dashboard"))
        elif user["role"] == "coe":
            return redirect(url_for("coe_dashboard"))

    return render_template("login.html")

# ---------------- DASHBOARDS ----------------

@app.route("/student")
def student_dashboard():
    if session.get("role") != "student":
        return redirect("/")
    return render_template("student.html", regno=session.get("ref_id"))

@app.route("/faculty")
def faculty_dashboard():
    if session.get("role") != "faculty":
        return redirect("/")
    return render_template("faculty.html", faculty_id=session.get("ref_id"))

@app.route("/coe")
def coe_dashboard():
    if session.get("role") != "coe":
        return redirect("/")
    return render_template("coe.html")

# ---------------- COE : CREATE EXAM SCHEDULE ----------------

@app.route("/coe/create-schedule", methods=["GET", "POST"])
def create_schedule():
    if session.get("role") != "coe":
        return redirect("/")

    if request.method == "POST":
        data = {
            "academic_year": request.form.get("academic_year"),
            "exam_type": request.form.get("exam_type"),
            "year": int(request.form.get("year")),
            "semester": request.form.get("semester"),
            "start_date": request.form.get("start_date"),
            "end_date": request.form.get("end_date"),
            "created_at": datetime.now(),
            "qr_enabled": False,
            "hall_ticket_enabled": False
        }

        db.exam_cycles.insert_one(data)
        return redirect("/coe")

    return render_template("create_schedule.html")


# ---------------- COE : VIEW SCHEDULES ----------------

@app.route("/coe/schedules")
def view_schedules():
    if session.get("role") != "coe":
        return redirect("/")

    schedules = list(db.exam_cycles.find())
    return render_template("coe.html", schedules=schedules)


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)
