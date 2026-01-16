from flask_mail import Message

def notify(event, applicant, mail=None):
    subject = f"University Admission Update: {event}"
    body = f"Dear {applicant.name},\n\n"
    
    if event == "SELECTED":
        body += f"Congratulations! You have been selected for admission in the {applicant.allocated_department} department. Please log in to verify your documents."
    elif event == "CONFIRMED":
        body += f"Your admission to the {applicant.allocated_department} department has been confirmed. Welcome to the university!"
    elif event == "CANCELLED":
        body += "We regret to inform you that your admission has been cancelled due to document verification failure."
    elif event == "WAITING":
        body += "You are currently on the waiting list. We will notify you if a seat becomes available."

    body += "\n\nBest regards,\nUniversity Admission Team"

    print(f"[MOCK EMAIL to {applicant.name}] Subject: {subject}")
    
    if mail:
        try:
            msg = Message(subject, recipients=["student@example.com"], body=body) # In real app, use applicant.email
            mail.send(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")
