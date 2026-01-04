def get_valid_int(prompt, min_val):
    while True:
        try:
            val = int(input(prompt))
            if val >= min_val:
                return val
        except ValueError:
            pass
        print("❌ Invalid input")


def get_valid_float(prompt, min_val=0, max_val=100):
    while True:
        try:
            val = float(input(prompt))
            if min_val <= val <= max_val:
                return val
        except ValueError:
            pass
        print("❌ Invalid input")


def get_valid_department(prompt, departments):
    while True:
        dept = input(prompt).upper()
        if dept in departments:
            return dept
        print("❌ Invalid department")
