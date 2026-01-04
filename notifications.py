def notify(event, applicant):
    print("\n📧 EMAIL NOTIFICATION")
    print(f"To: {applicant.name}")

    if event == "SELECTED":
        print(f"Message: Provisional admission offered in {applicant.allocated_department}")

    elif event == "CONFIRMED":
        print("Message: Admission CONFIRMED. Welcome!")

    elif event == "CANCELLED":
        print("Message: Admission cancelled due to document rejection.")
