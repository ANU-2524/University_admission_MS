class Applicant:
    def __init__(self, app_id, name, age, marks_12, entrance_score, preferences, category="General"):
        self.id = app_id
        self.name = name
        self.age = age
        self.marks_12 = marks_12
        self.entrance_score = entrance_score
        self.preferences = preferences  # List of department names
        self.category = category        # General, OBC, SC, ST, EWS
        
        # Computed / Dynamic
        self.final_score = 0
        self.rank = None
        self.allocated_department = None
        self.admission_status = "Applied"   # Applied | Selected | Waiting | Rejected | Cancelled | Confirmed
        self.document_status = "Pending"    # Pending | Verified | Rejected
        self.fee_status = "Unpaid"          # Unpaid | Paid
        self.ocr_verified = False
        self.payment_id = None
        self.marksheet_path = None
        self.scorecard_path = None

    def __repr__(self):
        return (
            f"ID:{self.id} | {self.name} | Score:{self.final_score:.2f} | "
            f"Rank:{self.rank} | Status:{self.admission_status} | "
            f"Dept:{self.allocated_department} | Docs:{self.document_status}"
        )


class Department:
    def __init__(self, name, total_seats, quotas=None):
        self.name = name
        self.total_seats = total_seats
        # Quotas: {"General": 10, "OBC": 5, ...}
        self.quotas = quotas if quotas else {"General": total_seats}
        self.filled_seats = {"General": 0, "OBC": 0, "SC": 0, "ST": 0, "EWS": 0}

    @property
    def available_seats(self):
        return self.total_seats - sum(self.filled_seats.values())

    def can_admit(self, category):
        # Check if category quota is available or if general seats are available
        category_filled = self.filled_seats.get(category, 0)
        category_total = self.quotas.get(category, 0)
        
        if category_filled < category_total:
            return True
        return False
