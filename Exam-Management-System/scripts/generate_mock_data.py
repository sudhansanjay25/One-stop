from db.mongo import db
import random

# ===================== CONSTANTS =====================

DEPARTMENTS = ["101", "201", "301", "401", "501"]
YEARS = [1, 2, 3, 4]
SEMESTERS = ["ODD", "EVEN"]
DEFAULT_PASSWORD = "password123"

# year -> year of joining
YEAR_OF_JOINING = {
    1: "25",
    2: "24",
    3: "23",
    4: "22"
}


# ===================== CLEAR OLD DATA =====================

db.students.delete_many({})
db.users.delete_many({})
db.faculty.delete_many({})
db.subjects.delete_many({})
db.halls.delete_many({})

print("Old data cleared")

# ===================== STUDENTS & USERS =====================

student_count = 0
user_count = 0

for dept in DEPARTMENTS:
    for year in YEARS:
        yoj = YEAR_OF_JOINING[year]

        for i in range(1, 101):  # 001 to 100
            regno = f"MLID{dept}{yoj}{str(i).zfill(3)}"

            student = {
                "regno": regno,
                "name": f"Student {i}",
                "department": dept,
                "year": year,
                "photo": "/static/default.jpeg"
            }

            user = {
                "email": f"{regno}@student.mlid.edu",
                "password": DEFAULT_PASSWORD,
                "role": "student",
                "ref_id": regno
            }

            db.students.insert_one(student)
            db.users.insert_one(user)

            student_count += 1
            user_count += 1

print(f"Students inserted: {student_count}")
print(f"Student users inserted: {user_count}")

# ===================== FACULTY & USERS =====================

faculty_count = 0

for i in range(1, 21):
    fac_id = f"FAC{str(i).zfill(2)}"
    dept = DEPARTMENTS[(i - 1) % len(DEPARTMENTS)]

    faculty = {
        "faculty_id": fac_id,
        "name": f"Faculty {i}",
        "department": dept
    }

    user = {
        "email": f"fac{str(i).zfill(2)}@mlid.edu",
        "password": DEFAULT_PASSWORD,
        "role": "faculty",
        "ref_id": fac_id
    }

    db.faculty.insert_one(faculty)
    db.users.insert_one(user)

    faculty_count += 1
    user_count += 1

print(f"Faculty inserted: {faculty_count}")

# ===================== COE USER =====================

coe_user = {
    "email": "coe@exam.com",
    "password": DEFAULT_PASSWORD,
    "role": "coe",
    "ref_id": "COE01"
}

db.users.insert_one(coe_user)
user_count += 1

print("COE user inserted")

# ===================== SUBJECTS =====================

subject_count = 0

for dept in DEPARTMENTS:
    for year in YEARS:
        for sem in SEMESTERS:
            total_subjects = random.choice([4, 5])

            for i in range(1, total_subjects + 1):
                subject_type = "HEAVY" if i <= 2 else "NONMAJOR"

                subject = {
                    "code": f"SUB{dept}{year}{sem[0]}{i}",
                    "name": f"Subject {i}",
                    "department": dept,
                    "year": year,
                    "semester": sem,
                    "type": subject_type
                }

                db.subjects.insert_one(subject)
                subject_count += 1

print(f"Subjects inserted: {subject_count}")

# ===================== HALLS =====================

hall_count = 0

for i in range(1, 21):
    hall = {
        "hall_no": f"H{i}",
        "capacity": random.randint(30, 35),
        "columns": random.randint(4, 6)
    }

    db.halls.insert_one(hall)
    hall_count += 1

print(f"Halls inserted: {hall_count}")

print("\nMock data generation COMPLETE")
