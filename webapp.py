from flask import Flask, render_template, request, redirect, url_for, flash
from models import Applicant, Department
from ranking import generate_merit_list
from allocation import allocate_seats
from verification import reallocate_waiting
from notifications import notify
import storage as db

app = Flask(__name__)
app.secret_key = "dev-secret"

db.init_db()

# Seed departments if not present
default_departments = {
    "CS": Department("CS", 2),
    "MECH": Department("MECH", 1),
    "CIVIL": Department("CIVIL", 1)
}

existing = db.get_departments()
if not existing:
    db.seed_departments(default_departments)
    departments = default_departments
else:
    departments = existing


@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        age = int(request.form.get("age"))
        marks = float(request.form.get("marks"))
        entrance = float(request.form.get("entrance"))
        dept = request.form.get("dept")

        db.add_applicant(name, age, marks, entrance, dept)
        flash("Applicant registered", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html", departments=departments.keys())


@app.route("/dashboard")
def dashboard():
    applicants = db.get_all_applicants()
    # refresh departments from DB
    departments_local = db.get_departments() or departments
    return render_template("dashboard.html", applicants=applicants, departments=departments_local)


@app.route("/generate")
def generate():
    applicants = db.get_all_applicants()
    generate_merit_list(applicants)
    for a in applicants:
        db.update_applicant(a)
    flash("Merit list generated", "info")
    return redirect(url_for("merit_list"))


@app.route("/merit")
def merit_list():
    applicants = db.get_all_applicants()
    return render_template("merit.html", applicants=applicants)


@app.route("/allocate")
def allocate():
    applicants = db.get_all_applicants()
    departments_local = db.get_departments()
    waiting_list = db.get_waiting_list()

    allocate_seats(applicants, departments_local, waiting_list)

    # persist departments and applicants
    for name, dept in departments_local.items():
        db.update_department(dept)

    for app_obj in applicants:
        db.update_applicant(app_obj)
        if app_obj.admission_status == "Selected":
            notify("SELECTED", app_obj)

    flash("Seat allocation completed", "success")
    return redirect(url_for("dashboard"))


@app.route("/verify")
def verify():
    selected = [a for a in db.get_all_applicants() if a.admission_status == "Selected"]
    return render_template("verify.html", selected=selected)


@app.route("/verify/<int:app_id>", methods=["POST"])
def verify_action(app_id):
    action = request.form.get("action")
    candidate = db.get_applicant(app_id)
    if not candidate:
        flash("Applicant not found", "danger")
        return redirect(url_for("verify"))

    if action == "approve":
        candidate.document_status = "Verified"
        candidate.admission_status = "Confirmed"
        notify("CONFIRMED", candidate)
        db.update_applicant(candidate)
        flash(f"Documents verified for {candidate.name}", "success")

    else:
        candidate.document_status = "Rejected"
        candidate.admission_status = "Cancelled"
        dept = candidate.allocated_department
        if dept:
            # update DB department
            departments_db = db.get_departments()
            if dept in departments_db:
                departments_db[dept].available_seats += 1
                db.update_department(departments_db[dept])
            candidate.allocated_department = None
        notify("CANCELLED", candidate)
        db.update_applicant(candidate)

        # Try to allocate next waiting candidate
        applicants = db.get_all_applicants()
        departments_db = db.get_departments()
        waiting = db.get_waiting_list()
        reallocate_waiting(departments_db, waiting)
        # persist any changes after reallocation
        for name, d in departments_db.items():
            db.update_department(d)
        for w in waiting:
            db.update_applicant(w)

        flash(f"Documents rejected for {candidate.name}", "warning")

    return redirect(url_for("verify"))


if __name__ == "__main__":
    app.run(debug=True)
