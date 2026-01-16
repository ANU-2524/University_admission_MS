import os
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from models import Applicant, Department
from ranking import generate_merit_list
from allocation import allocate_seats
from verification import reallocate_waiting
from notifications import notify
from admission_letter import generate_admission_pdf
from ocr_utils import verify_applicant_marks
import storage as db

app = Flask(__name__)
app.secret_key = "dev-secret"

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Mail Configuration (Mock)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-password'
mail = Mail(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, role, applicant_id=None):
        self.id = id
        self.username = username
        self.role = role
        self.applicant_id = applicant_id

@login_manager.user_loader
def load_user(user_id):
    u = db.get_user_by_id(user_id)
    if u:
        return User(u[0], u[1], u[3], u[4])
    return None

db.init_db()

# Seed departments if not present
default_departments = {
    "CS": Department("CS", 10, {"General": 5, "OBC": 3, "SC": 2}),
    "MECH": Department("MECH", 5, {"General": 3, "OBC": 2}),
    "CIVIL": Department("CIVIL", 5, {"General": 3, "EWS": 2})
}

existing = db.get_departments()
if not existing:
    db.seed_departments(default_departments)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        u = db.get_user(username)
        if u and check_password_hash(u[2], password):
            user_obj = User(u[0], u[1], u[3], u[4])
            login_user(user_obj)
            db.log_action(username, "Login", "User logged in successfully")
            if user_obj.role == 'admin':
                return redirect(url_for("dashboard"))
            else:
                return redirect(url_for("student_portal"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    db.log_action(current_user.username, "Logout", "User logged out")
    logout_user()
    return redirect(url_for("login"))

@app.route("/")
def index():
    reg_open = db.get_setting('reg_open') == 'true'
    deadline = db.get_setting('deadline')
    return render_template("index.html", reg_open=reg_open, deadline=deadline)

@app.route("/register", methods=["GET", "POST"])
def register():
    if db.get_setting('reg_open') != 'true':
        flash("Registration is currently closed.", "warning")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name")
        age = int(request.form.get("age"))
        marks = float(request.form.get("marks"))
        entrance = float(request.form.get("entrance"))
        category = request.form.get("category")
        prefs = request.form.getlist("prefs")
        password = request.form.get("password")

        marksheet = request.files.get('marksheet')
        scorecard = request.files.get('scorecard')

        marksheet_path = None
        scorecard_path = None

        if marksheet and allowed_file(marksheet.filename):
            filename = secure_filename(f"{name}_marksheet_{marksheet.filename}")
            marksheet_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            marksheet.save(marksheet_path)

        if scorecard and allowed_file(scorecard.filename):
            filename = secure_filename(f"{name}_scorecard_{scorecard.filename}")
            scorecard_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            scorecard.save(scorecard_path)

        applicant = db.add_applicant(name, age, marks, entrance, prefs, category)
        applicant.marksheet_path = marksheet_path
        applicant.scorecard_path = scorecard_path
        db.update_applicant(applicant)

        # Create student user account
        username = name.lower().replace(" ", "") + str(applicant.id)
        db.create_user(username, password, 'student', applicant.id)
        
        db.log_action(username, "Registration", f"New student registered: {name}")
        flash(f"Registration successful! Your username is: {username}", "success")
        return redirect(url_for("login"))

    return render_template("register.html", departments=db.get_departments().keys())

@app.route("/student/portal")
@login_required
def student_portal():
    if current_user.role != 'student':
        return redirect(url_for("dashboard"))
    
    applicant = db.get_applicant(current_user.applicant_id)
    return render_template("student_portal.html", applicant=applicant)

@app.route("/student/payment", methods=["GET", "POST"])
@login_required
def payment():
    if current_user.role != 'student':
        return redirect(url_for("dashboard"))
    
    applicant = db.get_applicant(current_user.applicant_id)
    if applicant.admission_status != 'Selected':
        flash("You are not eligible for payment yet.", "warning")
        return redirect(url_for("student_portal"))

    if request.method == "POST":
        # Simulate payment processing
        applicant.fee_status = "Paid"
        applicant.payment_id = f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        db.update_applicant(applicant)
        db.log_action(current_user.username, "Payment", f"Fee paid for {applicant.name}")
        flash("Payment successful! Your admission is now pending document verification.", "success")
        return redirect(url_for("student_portal"))

    return render_template("payment.html", applicant=applicant)

@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != 'admin':
        return redirect(url_for("student_portal"))

    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    applicants = db.get_all_applicants()
    
    if search:
        applicants = [a for a in applicants if search.lower() in a.name.lower()]
    if status_filter:
        applicants = [a for a in applicants if a.admission_status == status_filter]
        
    departments_local = db.get_departments()
    return render_template("dashboard.html", applicants=applicants, departments=departments_local)

@app.route("/admin/settings", methods=["GET", "POST"])
@login_required
def admin_settings():
    if current_user.role != 'admin':
        return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        reg_open = request.form.get("reg_open")
        deadline = request.form.get("deadline")
        db.update_setting('reg_open', reg_open)
        db.update_setting('deadline', deadline)
        
        # Add new department
        new_dept_name = request.form.get("new_dept_name")
        new_dept_seats = request.form.get("new_dept_seats")
        if new_dept_name and new_dept_seats:
            seats = int(new_dept_seats)
            db.seed_departments({new_dept_name: Department(new_dept_name, seats)})
            
        db.log_action(current_user.username, "SettingsUpdate", "Admin updated system settings")
        flash("Settings updated successfully", "success")

    settings = {
        'reg_open': db.get_setting('reg_open'),
        'deadline': db.get_setting('deadline')
    }
    departments = db.get_departments()
    return render_template("admin_settings.html", settings=settings, departments=departments)

@app.route("/admin/logs")
@login_required
def admin_logs():
    if current_user.role != 'admin':
        return redirect(url_for("dashboard"))
    logs = db.get_audit_logs()
    return render_template("admin_logs.html", logs=logs)

@app.route("/admin/export")
@login_required
def export_data():
    if current_user.role != 'admin':
        return redirect(url_for("dashboard"))
    
    applicants = db.get_all_applicants()
    data = []
    for a in applicants:
        data.append({
            'ID': a.id,
            'Name': a.name,
            'Age': a.age,
            '12th Marks': a.marks_12,
            'Entrance': a.entrance_score,
            'Category': a.category,
            'Rank': a.rank,
            'Status': a.admission_status,
            'Department': a.allocated_department,
            'Fee Status': a.fee_status
        })
    
    df = pd.DataFrame(data)
    export_path = os.path.join(UPLOAD_FOLDER, 'applicants_export.xlsx')
    df.to_excel(export_path, index=False)
    
    db.log_action(current_user.username, "Export", "Admin exported applicant data to Excel")
    return send_file(export_path, as_attachment=True)

@app.route("/generate")
@login_required
def generate():
    if current_user.role != 'admin':
        return redirect(url_for("dashboard"))
    
    applicants = db.get_all_applicants()
    generate_merit_list(applicants)
    for a in applicants:
        db.update_applicant(a)
    
    db.log_action(current_user.username, "GenerateMerit", "Admin generated the merit list")
    flash("Merit list generated", "info")
    return redirect(url_for("merit_list"))

@app.route("/merit")
def merit_list():
    applicants = db.get_all_applicants()
    applicants.sort(key=lambda x: x.rank if x.rank else 9999)
    return render_template("merit.html", applicants=applicants)

@app.route("/allocate")
@login_required
def allocate():
    if current_user.role != 'admin':
        return redirect(url_for("dashboard"))

    applicants = db.get_all_applicants()
    departments_local = db.get_departments()
    waiting_list = db.get_waiting_list()

    allocate_seats(applicants, departments_local, waiting_list)

    for name, dept in departments_local.items():
        db.update_department(dept)

    for app_obj in applicants:
        db.update_applicant(app_obj)
        if app_obj.admission_status == "Selected":
            notify("SELECTED", app_obj, mail)

    db.log_action(current_user.username, "AllocateSeats", "Admin ran seat allocation")
    flash("Seat allocation completed", "success")
    return redirect(url_for("dashboard"))

@app.route("/verify")
@login_required
def verify():
    if current_user.role != 'admin':
        return redirect(url_for("dashboard"))
    selected = [a for a in db.get_all_applicants() if a.admission_status == "Selected"]
    return render_template("verify.html", selected=selected)

@app.route("/verify/<int:app_id>", methods=["POST"])
@login_required
def verify_action(app_id):
    if current_user.role != 'admin':
        return redirect(url_for("dashboard"))
        
    action = request.form.get("action")
    candidate = db.get_applicant(app_id)
    if not candidate:
        flash("Applicant not found", "danger")
        return redirect(url_for("verify"))

    if action == "ocr":
        success, message = verify_applicant_marks(candidate)
        if success:
            candidate.ocr_verified = True
            db.update_applicant(candidate)
            flash(message, "success")
        else:
            flash(message, "warning")
        return redirect(url_for("verify"))

    if action == "approve":
        candidate.document_status = "Verified"
        candidate.admission_status = "Confirmed"
        notify("CONFIRMED", candidate, mail)
        db.update_applicant(candidate)
        db.log_action(current_user.username, "ApproveDocs", f"Admin approved documents for {candidate.name}")
        flash(f"Documents verified for {candidate.name}", "success")
    else:
        candidate.document_status = "Rejected"
        candidate.admission_status = "Cancelled"
        dept_name = candidate.allocated_department
        if dept_name:
            departments_db = db.get_departments()
            if dept_name in departments_db:
                departments_db[dept_name].filled_seats[candidate.category] -= 1
                db.update_department(departments_db[dept_name])
            candidate.allocated_department = None
        notify("CANCELLED", candidate, mail)
        db.update_applicant(candidate)
        db.log_action(current_user.username, "RejectDocs", f"Admin rejected documents for {candidate.name}")

        # Reallocate
        departments_db = db.get_departments()
        waiting = db.get_waiting_list()
        if reallocate_waiting(departments_db, waiting):
            for name, d in departments_db.items():
                db.update_department(d)
            for w in waiting:
                db.update_applicant(w)

        flash(f"Documents rejected for {candidate.name}", "warning")

    return redirect(url_for("verify"))

@app.route("/stats")
@login_required
def stats():
    if current_user.role != 'admin':
        return redirect(url_for("dashboard"))
    
    depts = db.get_departments()
    labels = list(depts.keys())
    filled = [sum(d.filled_seats.values()) for d in depts.values()]
    total = [d.total_seats for d in depts.values()]
    
    applicants = db.get_all_applicants()
    status_counts = {
        "Applied": len([a for a in applicants if a.admission_status == "Applied"]),
        "Selected": len([a for a in applicants if a.admission_status == "Selected"]),
        "Confirmed": len([a for a in applicants if a.admission_status == "Confirmed"]),
        "Waiting": len([a for a in applicants if a.admission_status == "Waiting"]),
        "Cancelled": len([a for a in applicants if a.admission_status == "Cancelled"])
    }
    
    return render_template("stats.html", labels=labels, filled=filled, total=total, status_counts=status_counts)

@app.route("/download_letter/<int:app_id>")
def download_letter(app_id):
    applicant = db.get_applicant(app_id)
    if not applicant or applicant.admission_status != "Confirmed":
        flash("Admission letter not available", "danger")
        return redirect(url_for("dashboard"))
    
    pdf_buffer = generate_admission_pdf(applicant)
    return send_file(pdf_buffer, as_attachment=True, download_name=f"Admission_Letter_{applicant.name}.pdf", mimetype='application/pdf')

if __name__ == "__main__":
    app.run(debug=True)
