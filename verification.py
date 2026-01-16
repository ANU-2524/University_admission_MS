def reallocate_waiting(departments, waiting_list):
    # Sort waiting list by rank
    waiting_list.sort(key=lambda a: a.rank if a.rank else 999999)
    
    for candidate in waiting_list:
        for pref in candidate.preferences:
            if pref in departments:
                dept = departments[pref]
                if dept.can_admit(candidate.category):
                    candidate.admission_status = "Selected"
                    candidate.document_status = "Pending"
                    candidate.allocated_department = pref
                    dept.filled_seats[candidate.category] += 1
                    waiting_list.remove(candidate)
                    return True # Reallocated one
    return False


def verify_documents_cli(applicants, departments, waiting_list):
    # This is for CLI usage
    for app in applicants:
        if app.admission_status == "Selected":
            print(f"\nVerify documents for {app.name}")
            choice = input("Approve documents? (y/n): ").lower()

            if choice == "y":
                app.document_status = "Verified"
                app.admission_status = "Confirmed"
            else:
                app.document_status = "Rejected"
                app.admission_status = "Cancelled"

                # Free seat
                dept_name = app.allocated_department
                if dept_name in departments:
                    departments[dept_name].filled_seats[app.category] -= 1
                app.allocated_department = None

                # Allocate next waiting candidate
                reallocate_waiting(departments, waiting_list)
