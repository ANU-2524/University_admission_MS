# University_admission_MS
Project 1 University_admission_management_system ; Console.success !

# University Admission Management System (CLI)

## Advanced Features
- Weighted merit ranking
- Waiting list & seat reallocation
- Input validation
- State-based workflow
- Event-driven notifications

## Concepts Demonstrated
- Sorting algorithms
- Greedy allocation
- State machines
- Defensive programming
- System design thinking

# University Admission Management System

Welcome to the University Admission Management System (UAMS). This project demonstrates a complete admission workflow: applicant registration, merit ranking, seat allocation with waiting lists, document verification, and a notification flow. It includes both a CLI interface and a modern Flask-based web UI backed by SQLite persistence.

Why this repo is useful
- Learn common admission-system algorithms: ranking, tie-breaking, greedy allocation.
- See a clear separation of concerns: models, storage layer, business logic, and UI.
- A practical starter kit to extend with authentication, email integration, REST API, tests, and CI.

Repository structure (key files)
- `main.py` — CLI interface for quick demonstrations and scripted runs.
- `webapp.py` — Flask application (web UI). Recommended for interactive usage.
- `storage.py` — SQLite persistence layer and helpers (`admissions.db`).
- `models.py` — Domain objects: `Applicant`, `Department`.
- `ranking.py` — Score calculation and merit list generation.
- `allocation.py` — Seat allocation and waiting-list logic.
- `verification.py` — Document verification and waiting-list reallocation helpers.
- `notifications.py` — Mock notification functions (prints to console). Replaceable with SMTP/API.
- `templates/`, `static/` — Web UI assets (Jinja2 templates, CSS, JS).
- `requirements.txt` — Python dependencies.

Quick start — run the web app (recommended)

1. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
python webapp.py
```

4. Visit the UI:

```
http://127.0.0.1:5000
```

Notes
- On first run `storage.py` creates `admissions.db` and seeds default departments (CS, MECH, CIVIL).
- The web UI persists applicants in SQLite so your data survives restarts.

Quick start — run the CLI (legacy)

```bash
python main.py
```

Core concepts & flows
- Merit generation: `ranking.calculate_final_score` uses a weighted formula (default: 60% 12th marks, 40% entrance). `generate_merit_list` assigns `final_score` and `rank`. Tie-breaker: higher `age` wins if `final_score` ties.
- Seat allocation: `allocate_seats` assigns seats greedily by preferred department. Full departments yield `Waiting` status for candidates.
- Document verification: Approve/Reject flow updates `document_status` and frees seats when documents are rejected. `reallocate_waiting` moves candidates from waiting into newly freed seats.
- Notifications: `notifications.notify` is a console mock; integrate SMTP or API services to send real emails.

Storage & data model
- Applicants table stores all applicant fields and admission/document statuses.
- Departments table tracks `total_seats` and `available_seats`.
- Use `storage.py` helpers: `init_db()`, `seed_departments()`, `add_applicant()`, `get_all_applicants()`, `update_applicant()`, `get_departments()`, `update_department()`.

Recommended next steps (good first contributions)
- Add unit tests (`pytest`) for `ranking.py`, `allocation.py`, and `verification.py`.
- Add admin authentication and an admin settings page to change seat counts.
- Add server-side filtering, sorting, and pagination for large applicant lists.
- Integrate real email (SMTP) and a notification logging table.
- Add REST API endpoints and optionally a React/Vue frontend.

Development notes
- When changing allocation or ranking logic:
	1) Recompute merit (`/generate`), then
	2) Run allocation (`/allocate`) so DB state remains consistent.
- Keep business logic in `ranking.py`, `allocation.py`, and `verification.py` so the UI can be lightweight.

How to test locally quickly
- Register a few applicants using the web UI or CLI.
- Click "Generate Merit" to compute scores and assign ranks.
- Click "Allocate Seats" to assign seats; use "Verify Docs" to approve or reject and observe reallocation.

Contact & license
- This project currently has no explicit license file. I can add an MIT `LICENSE` and `CONTRIBUTING.md` if you want to make it open-source-friendly.

If you'd like, I can now:
- add unit tests + CI,
- implement admin auth + settings UI, or
- enable real email notifications (SMTP/API).
Reply with which you prefer and I'll implement it next.
