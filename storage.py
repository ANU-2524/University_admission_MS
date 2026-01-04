import sqlite3
from pathlib import Path
from models import Applicant, Department

DB_PATH = Path(__file__).parent / "admissions.db"


def init_db(path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS departments (
            name TEXT PRIMARY KEY,
            total_seats INTEGER,
            available_seats INTEGER
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
            preferred_department TEXT,
            final_score REAL,
            rank INTEGER,
            allocated_department TEXT,
            admission_status TEXT,
            document_status TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def seed_departments(dept_map, path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    for name, dept in dept_map.items():
        cur.execute(
            "INSERT OR REPLACE INTO departments(name, total_seats, available_seats) VALUES (?, ?, ?)",
            (name, dept.total_seats, dept.available_seats),
        )
    conn.commit()
    conn.close()


def get_departments(path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT name, total_seats, available_seats FROM departments")
    rows = cur.fetchall()
    conn.close()
    return {name: Department(name, total) for (name, total, avail) in rows} if rows else {}


def update_department(dept: Department, path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        "UPDATE departments SET total_seats = ?, available_seats = ? WHERE name = ?",
        (dept.total_seats, dept.available_seats, dept.name),
    )
    conn.commit()
    conn.close()


def add_applicant(name, age, marks_12, entrance_score, preferred_department, path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO applicants(name, age, marks_12, entrance_score, preferred_department, final_score, rank, allocated_department, admission_status, document_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (name, age, marks_12, entrance_score, preferred_department, 0.0, None, None, 'Applied', None),
    )
    app_id = cur.lastrowid
    conn.commit()
    conn.close()
    return get_applicant(app_id)


def get_applicant(app_id, path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, age, marks_12, entrance_score, preferred_department, final_score, rank, allocated_department, admission_status, document_status FROM applicants WHERE id = ?",
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
    cur.execute(
        "SELECT id, name, age, marks_12, entrance_score, preferred_department, final_score, rank, allocated_department, admission_status, document_status FROM applicants"
    )
    rows = cur.fetchall()
    conn.close()
    return [_row_to_applicant(r) for r in rows]


def get_waiting_list(path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, age, marks_12, entrance_score, preferred_department, final_score, rank, allocated_department, admission_status, document_status FROM applicants WHERE admission_status = 'Waiting' ORDER BY rank"
    )
    rows = cur.fetchall()
    conn.close()
    return [_row_to_applicant(r) for r in rows]


def update_applicant(app: Applicant, path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE applicants SET name=?, age=?, marks_12=?, entrance_score=?, preferred_department=?, final_score=?, rank=?, allocated_department=?, admission_status=?, document_status=? WHERE id=?
        """,
        (
            app.name,
            app.age,
            app.marks_12,
            app.entrance_score,
            app.preferred_department,
            app.final_score,
            app.rank,
            app.allocated_department,
            app.admission_status,
            app.document_status,
            app.id,
        ),
    )
    conn.commit()
    conn.close()


def _row_to_applicant(row):
    (app_id, name, age, marks_12, entrance_score, preferred_department, final_score, rank, allocated_department, admission_status, document_status) = row
    app = Applicant(app_id, name, age, marks_12, entrance_score, preferred_department)
    app.final_score = final_score or 0.0
    app.rank = rank
    app.allocated_department = allocated_department
    app.admission_status = admission_status
    app.document_status = document_status
    return app
