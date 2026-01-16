import sqlite3
import json
from pathlib import Path
from models import Applicant, Department
from werkzeug.security import generate_password_hash

DB_PATH = Path(__file__).parent / "admissions.db"


def init_db(path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS departments (
            name TEXT PRIMARY KEY,
            total_seats INTEGER,
            quotas TEXT,
            filled_seats TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS applicants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            marks_12 REAL,
            entrance_score REAL,
            preferences TEXT,
            category TEXT,
            final_score REAL,
            rank INTEGER,
            allocated_department TEXT,
            admission_status TEXT,
            document_status TEXT,
            fee_status TEXT,
            ocr_verified INTEGER,
            payment_id TEXT,
            marksheet_path TEXT,
            scorecard_path TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            applicant_id INTEGER,
            FOREIGN KEY(applicant_id) REFERENCES applicants(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    
    # Default settings
    cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('reg_open', 'true')")
    cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('deadline', '2026-12-31T23:59')")
    
    # Create default admin if not exists
    cur.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cur.fetchone():
        admin_pass = generate_password_hash("admin123")
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", admin_pass, "admin"))

    conn.commit()
    conn.close()


def log_action(username, action, details, path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("INSERT INTO audit_logs (username, action, details) VALUES (?, ?, ?)", (username, action, details))
    conn.commit()
    conn.close()


def get_audit_logs(path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 100")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_setting(key, path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def update_setting(key, value, path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()


def seed_departments(dept_map, path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    for name, dept in dept_map.items():
        cur.execute(
            "INSERT OR REPLACE INTO departments(name, total_seats, quotas, filled_seats) VALUES (?, ?, ?, ?)",
            (name, dept.total_seats, json.dumps(dept.quotas), json.dumps(dept.filled_seats)),
        )
    conn.commit()
    conn.close()


def get_departments(path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT name, total_seats, quotas, filled_seats FROM departments")
    rows = cur.fetchall()
    conn.close()
    depts = {}
    for (name, total, quotas_json, filled_json) in rows:
        d = Department(name, total, json.loads(quotas_json))
        d.filled_seats = json.loads(filled_json)
        depts[name] = d
    return depts


def update_department(dept: Department, path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        "UPDATE departments SET total_seats = ?, quotas = ?, filled_seats = ? WHERE name = ?",
        (dept.total_seats, json.dumps(dept.quotas), json.dumps(dept.filled_seats), dept.name),
    )
    conn.commit()
    conn.close()


def add_applicant(name, age, marks_12, entrance_score, preferences, category, path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    prefs_str = ",".join(preferences)
    cur.execute(
        """
        INSERT INTO applicants(name, age, marks_12, entrance_score, preferences, category, final_score, rank, allocated_department, admission_status, document_status, fee_status, ocr_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (name, age, marks_12, entrance_score, prefs_str, category, 0.0, None, None, 'Applied', 'Pending', 'Unpaid', 0),
    )
    app_id = cur.lastrowid
    conn.commit()
    conn.close()
    return get_applicant(app_id)


def get_applicant(app_id, path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM applicants WHERE id = ?",
        (app_id,)
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return _row_to_applicant(row)


def get_all_applicants(path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM applicants")
    rows = cur.fetchall()
    conn.close()
    return [_row_to_applicant(r) for r in rows]


def get_waiting_list(path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM applicants WHERE admission_status = 'Waiting' ORDER BY rank"
    )
    rows = cur.fetchall()
    conn.close()
    return [_row_to_applicant(r) for r in rows]


def update_applicant(app: Applicant, path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    prefs_str = ",".join(app.preferences)
    cur.execute(
        """
        UPDATE applicants SET name=?, age=?, marks_12=?, entrance_score=?, preferences=?, category=?, final_score=?, rank=?, allocated_department=?, admission_status=?, document_status=?, fee_status=?, ocr_verified=?, payment_id=?, marksheet_path=?, scorecard_path=? WHERE id=?
        """,
        (
            app.name,
            app.age,
            app.marks_12,
            app.entrance_score,
            prefs_str,
            app.category,
            app.final_score,
            app.rank,
            app.allocated_department,
            app.admission_status,
            app.document_status,
            app.fee_status,
            1 if app.ocr_verified else 0,
            app.payment_id,
            app.marksheet_path,
            app.scorecard_path,
            app.id,
        ),
    )
    conn.commit()
    conn.close()


def _row_to_applicant(row):
    (app_id, name, age, marks_12, entrance_score, prefs_str, category, final_score, rank, allocated_dept, status, doc_status, fee_status, ocr_v, pay_id, marksheet, scorecard) = row
    prefs = prefs_str.split(",") if prefs_str else []
    app = Applicant(app_id, name, age, marks_12, entrance_score, prefs, category)
    app.final_score = final_score or 0.0
    app.rank = rank
    app.allocated_department = allocated_dept
    app.admission_status = status
    app.document_status = doc_status
    app.fee_status = fee_status
    app.ocr_verified = bool(ocr_v)
    app.payment_id = pay_id
    app.marksheet_path = marksheet
    app.scorecard_path = scorecard
    return app


def create_user(username, password, role, applicant_id=None, path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    hashed_pw = generate_password_hash(password)
    cur.execute("INSERT INTO users (username, password, role, applicant_id) VALUES (?, ?, ?, ?)", (username, hashed_pw, role, applicant_id))
    conn.commit()
    conn.close()


def get_user(username, path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT id, username, password, role, applicant_id FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row


def get_user_by_id(user_id, path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT id, username, password, role, applicant_id FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row
