def verify_documents(applicants, departments, waiting_list):
    for app in applicants:
        if app.admission_status == "Selected":
            print(f"\nVerify documents for {app.name}")
            choice = input("Approve documents? (y/n): ").lower()

            if choice == "y":
                app.document_status = "Verified"
            else:
                app.document_status = "Rejected"
                app.admission_status = "Cancelled"

                # Free seat
                dept = app.allocated_department
                departments[dept].available_seats += 1
                app.allocated_department = None

                # Allocate next waiting candidate
                reallocate_waiting(departments, waiting_list)


def reallocate_waiting(departments, waiting_list):
    for candidate in waiting_list:
        dept = candidate.preferred_department

        if departments[dept].available_seats > 0:
            candidate.admission_status = "Selected"
            candidate.document_status = "Pending"
            candidate.allocated_department = dept
            departments[dept].available_seats -= 1
            waiting_list.remove(candidate)
            break
