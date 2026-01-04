def allocate_seats(applicants, departments, waiting_list):
    for app in applicants:
        dept = app.preferred_department

        if dept in departments and departments[dept].available_seats > 0:
            app.admission_status = "Selected"
            app.allocated_department = dept
            app.document_status = "Pending"
            departments[dept].available_seats -= 1

        elif dept in departments:
            app.admission_status = "Waiting"
            waiting_list.append(app)

        else:
            app.admission_status = "Rejected"
