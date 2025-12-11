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
            'regulation': '2015',
            'department': dept,
        })
        counter += 1

# Subjects per department (mock) - with varying counts to test overflow
SUBJECTS_BY_DEPT = {
    'CSE': [
        ('4', '04.06.2025', 'FN', '21CS401', 'Design and Analysis of Algorithms'),
        ('4', '31.05.2025', 'FN', '21CS402', 'Operating Systems'),
        ('4', '24.05.2025', 'FN', '21CS403', 'Computer Networks'),
        ('4', '21.05.2025', 'FN', '21CS404', 'Database Systems'),
        ('4', '19.05.2025', 'FN', '21CS405', 'Software Engineering'),
    ],
    'ECE': [
        # ECE has many subjects to test overflow pagination
        ('4', '04.06.2025', 'FN', '21EC401', 'Digital Signal Processing'),
        ('4', '31.05.2025', 'FN', '21EC402', 'Microprocessors and Microcontrollers'),
        ('4', '24.05.2025', 'FN', '21EC403', 'Communication Systems'),
        ('4', '21.05.2025', 'FN', '21EC404', 'Electromagnetic Theory'),
        ('4', '19.05.2025', 'FN', '21EC405', 'Control Systems'),
        ('3', '15.05.2025', 'AN', '21EC301', 'Signals and Systems'),
        ('3', '12.05.2025', 'AN', '21EC302', 'Analog Electronics'),
        ('3', '10.05.2025', 'AN', '21EC303', 'Digital Electronics'),
        ('3', '08.05.2025', 'AN', '21EC304', 'Network Analysis'),
        ('3', '06.05.2025', 'AN', '21EC305', 'Electronic Devices'),
        ('2', '04.05.2025', 'FN', '21EC201', 'Circuit Theory'),
        ('2', '02.05.2025', 'FN', '21EC202', 'Electronic Circuits'),
        ('2', '30.04.2025', 'FN', '21EC203', 'Electrical Engineering'),
        ('2', '28.04.2025', 'FN', '21EC204', 'Engineering Mathematics III'),
        ('2', '26.04.2025', 'FN', '21EC205', 'Data Structures'),
        ('1', '24.04.2025', 'AN', '21EC101', 'Engineering Physics'),
        ('1', '22.04.2025', 'AN', '21EC102', 'Engineering Chemistry'),
        ('1', '20.04.2025', 'AN', '21EC103', 'Engineering Drawing'),
        ('1', '18.04.2025', 'AN', '21EC104', 'English Communication'),
        ('1', '16.04.2025', 'AN', '21EC105', 'Engineering Mathematics I'),
        ('4', '', '', '21EC411', 'Digital Signal Processing Lab'),
        ('4', '', '', '21EC412', 'Microprocessors Lab'),
        ('4', '', '', '21EC413', 'Communication Systems Lab'),
        ('4', '', '', '21EC414', 'VLSI Design Lab'),
        ('4', '', '', '21EC415', 'Embedded Systems Lab'),
        ('3', '', '', '21EC311', 'Analog Electronics Lab'),
        ('3', '', '', '21EC312', 'Digital Electronics Lab'),
        ('3', '', '', '21EC313', 'Signals and Systems Lab'),
        ('2', '', '', '21EC211', 'Circuit Theory Lab'),
        ('2', '', '', '21EC212', 'Electronic Circuits Lab'),
        ('1', '', '', '21EC111', 'Physics Lab'),
        ('1', '', '', '21EC112', 'Chemistry Lab'),
        ('1', '', '', '21EC113', 'Engineering Workshop'),
        ('1', '', '', '21EC114', 'Computer Programming Lab'),
        ('1', '', '', '21EC115', 'Language Communication Lab'),
    ],
    'MECH': [
        ('4', '04.06.2025', 'FN', '21ME401', 'Strength of Materials'),
        ('4', '31.05.2025', 'FN', '21ME402', 'Thermodynamics'),
        ('4', '24.05.2025', 'FN', '21ME403', 'Machine Drawing'),
        ('4', '21.05.2025', 'FN', '21ME404', 'Manufacturing Processes'),
        ('4', '19.05.2025', 'FN', '21ME405', 'Fluid Mechanics'),
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
    regulation TEXT NOT NULL,
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
        'INSERT INTO students(reg_no, name, deg, branch, dob, sem, gender, semtime, regulation, department) VALUES (?,?,?,?,?,?,?,?,?,?)',
        [(
            s['reg_no'], s['name'], s['deg'], s['branch'], s['dob'], 
            s['sem'], s['gender'], s['semtime'], s['regulation'], s['department']
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
    
    print("=" * 60)
    print(f"✓ Database initialized successfully!")
    print(f"  Location: {DB_PATH}")
    print(f"  Students created: {len(STUDENTS)}")
    print("=" * 60)
    print("\nSample Register Numbers:")
    for dept, _, _ in DEPARTMENTS:
        print(f"  {dept}001, {dept}002, {dept}003...")
    print("\n✓ ECE students have 35+ subjects to test overflow")
    print("=" * 60)

if __name__ == '__main__':
    main()
