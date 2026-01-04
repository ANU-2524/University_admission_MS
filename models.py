class Applicant:
    def __init__(self, app_id, name, age, marks_12, entrance_score, preferred_department):
        self.id = app_id
        self.name = name
        self.age = age
        self.marks_12 = marks_12
        self.entrance_score = entrance_score
        self.preferred_department = preferred_department

        # Computed / Dynamic
        self.final_score = 0
        self.rank = None
        self.allocated_department = None
        self.admission_status = "Applied"   # Applied | Selected | Waiting | Rejected | Cancelled
        self.document_status = None          # Pending | Verified | Rejected

    def __repr__(self):
        return (
            f"ID:{self.id} | {self.name} | Score:{self.final_score:.2f} | "
            f"Rank:{self.rank} | Status:{self.admission_status} | "
            f"Dept:{self.allocated_department} | Docs:{self.document_status}"
        )


class Department:
    def __init__(self, name, seats):
        self.name = name
        self.total_seats = seats
        self.available_seats = seats
