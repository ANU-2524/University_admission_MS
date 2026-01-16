def allocate_seats(applicants, departments, waiting_list):
    # Sort applicants by rank before allocation
    applicants.sort(key=lambda a: a.rank if a.rank else 999999)

    for app in applicants:
        if app.admission_status != "Applied":
            continue

        allocated = False
        for pref in app.preferences:
            if pref in departments:
                dept = departments[pref]
                if dept.can_admit(app.category):
                    app.admission_status = "Selected"
                    app.allocated_department = pref
                    app.document_status = "Pending"
                    dept.filled_seats[app.category] += 1
                    allocated = True
                    break
        
        if not allocated:
            # Check if any preference exists in departments to decide between Waiting and Rejected
            valid_prefs = [p for p in app.preferences if p in departments]
            if valid_prefs:
                app.admission_status = "Waiting"
                if app not in waiting_list:
                    waiting_list.append(app)
            else:
                app.admission_status = "Rejected"
