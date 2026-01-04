def calculate_final_score(applicant):
    # Weighted formula (real-world style)
    return (applicant.marks_12 * 0.6) + (applicant.entrance_score * 0.4)


def generate_merit_list(applicants):
    for app in applicants:
        app.final_score = calculate_final_score(app)

    applicants.sort(
        key=lambda a: (
            -a.final_score,
            -a.age
        )
    )

    for idx, app in enumerate(applicants, start=1):
        app.rank = idx
