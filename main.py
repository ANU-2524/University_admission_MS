from models import Applicant, Department
from ranking import generate_merit_list
from allocation import allocate_seats
from verification import verify_documents
from notifications import notify
from utils import get_valid_int, get_valid_float, get_valid_department

applicants = []
waiting_list = []

departments = {
    "CS": Department("CS", 2),
    "MECH": Department("MECH", 1),
    "CIVIL": Department("CIVIL", 1)
}


def register_applicant():
    app_id = len(applicants) + 1
    name = input("Name: ")
    age = get_valid_int("Age (>=16): ", 16)
    marks = get_valid_float("12th Marks (0-100): ")
    entrance = get_valid_float("Entrance Score (0-100): ")
    dept = get_valid_department("Dept (CS/MECH/CIVIL): ", departments)

    applicants.append(
        Applicant(app_id, name, age, marks, entrance, dept)
    )
    print("✅ Applicant Registered")


def dashboard():
    print("\n===== DASHBOARD =====")
    for app in applicants:
        print(app)


def main():
    while True:
        print("\n1.Register 2.Generate Merit 3.Allocate Seats")
        print("4.Verify Docs 5.View Dashboard 6.Exit")

        choice = input("Choose: ")

        if choice == "1":
            register_applicant()

        elif choice == "2":
            generate_merit_list(applicants)
            print("✅ Merit list generated")

        elif choice == "3":
            allocate_seats(applicants, departments, waiting_list)
            print("✅ Seat allocation done")

        elif choice == "4":
            verify_documents(applicants, departments, waiting_list)

        elif choice == "5":
            dashboard()

        elif choice == "6":
            break

        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()
