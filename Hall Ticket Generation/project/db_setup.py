import os
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name('students.db')

STUDENTS = []
DEPARTMENTS = [
    ('CSE', 'B.Tech', 'COMPUTER SCIENCE AND ENGINEERING'),
    ('ECE', 'B.Tech', 'ELECTRONICS AND COMMUNICATION ENGINEERING'),
    ('MECH', 'B.Tech', 'MECHANICAL ENGINEERING'),
]

# Create 20 students across 3 departments
counter = 1
for dept, deg, branch in DEPARTMENTS:
    for i in range(1, 8):  # 7 each for first two, 6 for last to make 20
        if dept == 'MECH' and i > 6:
            break
        reg_no = f"{dept}{i:03d}"
        STUDENTS.append({
            'reg_no': reg_no,
            'name': f"Student {counter}",
            'deg': deg,
            'branch': branch,
            'dob': f"01.{(i%12)+1:02d}.2005",
            'sem': '4',
            'gender': 'MALE' if i % 2 == 0 else 'FEMALE',
            'semtime': 'APR 2025',
            'department': dept,
        })
        counter += 1

# Subjects per department (mock)
SUBJECTS_BY_DEPT = {
    'CSE': [
        ('4', '04.06.2025', 'FN', '21CS401', 'Design and Analysis of Algorithms'),
        ('4', '31.05.2025', 'FN', '21CS402', 'Operating Systems'),
        ('4', '24.05.2025', 'FN', '21CS403', 'Computer Networks'),
        ('4', '21.05.2025', 'FN', '21CS404', 'Database Systems'),
    ],
    'ECE': [
        ('4', '04.06.2025', 'FN', '21EC401', 'Digital Signal Processing'),
        ('4', '31.05.2025', 'FN', '21EC402', 'Microprocessors and Microcontrollers'),
        ('4', '24.05.2025', 'FN', '21EC403', 'Communication Systems'),
        ('4', '21.05.2025', 'FN', '21EC404', 'Electromagnetic Theory'),
        ('4', '20.05.2022', 'FN', '21EC405', 'Digital Processing')
    ],
    'MECH': [
        ('4', '04.06.2025', 'FN', '21ME401', 'Strength of Materials'),
        ('4', '31.05.2025', 'FN', '21ME402', 'Thermodynamics'),
        ('4', '24.05.2025', 'FN', '21ME403', 'Machine Drawing'),
    ],
}

SCHEMA_STUDENTS = """
CREATE TABLE IF NOT EXISTS students (
    reg_no TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    deg TEXT NOT NULL,
    branch TEXT NOT NULL,
    dob TEXT NOT NULL,
    sem TEXT NOT NULL,
    gender TEXT NOT NULL,
    semtime TEXT NOT NULL,
    department TEXT NOT NULL
);
"""

SCHEMA_SUBJECTS = """
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reg_no TEXT NOT NULL,
    sem TEXT,
    date TEXT,
    session TEXT,
    code TEXT,
    name TEXT,
    FOREIGN KEY(reg_no) REFERENCES students(reg_no)
);
"""

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(SCHEMA_STUDENTS)
    cur.execute(SCHEMA_SUBJECTS)

    # Clear existing
    cur.execute('DELETE FROM subjects')
    cur.execute('DELETE FROM students')

    # Insert students
    cur.executemany(
        'INSERT INTO students(reg_no, name, deg, branch, dob, sem, gender, semtime, department) VALUES (?,?,?,?,?,?,?,?,?)',
        [(
            s['reg_no'], s['name'], s['deg'], s['branch'], s['dob'], s['sem'], s['gender'], s['semtime'], s['department']
        ) for s in STUDENTS]
    )

    # Insert subjects per student based on dept
    for s in STUDENTS:
        for sub in SUBJECTS_BY_DEPT[s['department']]:
            cur.execute(
                'INSERT INTO subjects(reg_no, sem, date, session, code, name) VALUES (?,?,?,?,?,?)',
                (s['reg_no'],) + sub
            )

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == '__main__':
    main()
