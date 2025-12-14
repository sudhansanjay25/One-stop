"""
Database setup for Exam Scheduling System
Creates tables and populates with mock data
"""

import sqlite3
from datetime import datetime, timedelta

def create_database():
    """Create database and all required tables"""
    conn = sqlite3.connect('exam_scheduling.db')
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS schedule_violations')
    cursor.execute('DROP TABLE IF EXISTS exam_schedule')
    cursor.execute('DROP TABLE IF EXISTS holidays')
    cursor.execute('DROP TABLE IF EXISTS exam_cycles')
    cursor.execute('DROP TABLE IF EXISTS subjects')
    cursor.execute('DROP TABLE IF EXISTS students')
    
    # Create Students table
    cursor.execute('''
    CREATE TABLE students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_number TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        year INTEGER NOT NULL,
        semester INTEGER NOT NULL
    )
    ''')
    
    # Create Subjects table
    cursor.execute('''
    CREATE TABLE subjects (
        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT NOT NULL,
        subject_name TEXT NOT NULL,
        department TEXT NOT NULL,
        year INTEGER NOT NULL,
        semester INTEGER NOT NULL,
        semester_type TEXT NOT NULL,
        subject_type TEXT NOT NULL,
        exam_type TEXT NOT NULL,
        credits INTEGER,
        duration REAL,
        student_count INTEGER DEFAULT 0
    )
    ''')
    
    # Create Exam Cycles table
    cursor.execute('''
    CREATE TABLE exam_cycles (
        cycle_id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_type TEXT NOT NULL,
        year_group INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        created_date TEXT NOT NULL,
        status TEXT DEFAULT 'PENDING'
    )
    ''')
    
    # Create Holidays table
    cursor.execute('''
    CREATE TABLE holidays (
        holiday_id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_cycle_id INTEGER,
        holiday_date TEXT NOT NULL,
        reason TEXT,
        FOREIGN KEY (exam_cycle_id) REFERENCES exam_cycles(cycle_id)
    )
    ''')
    
    # Create Exam Schedule table
    cursor.execute('''
    CREATE TABLE exam_schedule (
        schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_cycle_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        department TEXT NOT NULL,
        exam_date TEXT NOT NULL,
        session TEXT NOT NULL,
        student_count INTEGER,
        FOREIGN KEY (exam_cycle_id) REFERENCES exam_cycles(cycle_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    )
    ''')
    
    # Create Constraint Violations Log table
    cursor.execute('''
    CREATE TABLE schedule_violations (
        violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_cycle_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        violation_type TEXT NOT NULL,
        description TEXT,
        severity TEXT,
        FOREIGN KEY (exam_cycle_id) REFERENCES exam_cycles(cycle_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    )
    ''')
    
    conn.commit()
    return conn

def populate_mock_data(conn):
    """Populate database with realistic mock data"""
    cursor = conn.cursor()
    
    # Insert mock students (60 students across 3 departments, Year 2)
    students_data = []
    departments = ['CSE', 'ECE', 'MECH']
    
    for dept in departments:
        for i in range(1, 21):  # 20 students per department
            roll_num = f"{dept}2023{i:03d}"
            name = f"Student_{dept}_{i}"
            students_data.append((roll_num, name, dept, 2, 3))  # Year 2, Semester 3
    
    cursor.executemany('''
    INSERT INTO students (roll_number, name, department, year, semester)
    VALUES (?, ?, ?, ?, ?)
    ''', students_data)
    
    # Insert mock subjects for Year 2 - ODD and EVEN semesters
    subjects_data = [
        # CSE ODD Semester (Semester 3) Subjects
        ('CS301', 'Data Structures', 'CSE', 2, 3, 'ODD', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('CS303', 'Computer Organization', 'CSE', 2, 3, 'ODD', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('CS305', 'Discrete Mathematics', 'CSE', 2, 3, 'ODD', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('CS307', 'Operating Systems', 'CSE', 2, 3, 'ODD', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('CS309', 'Software Engineering', 'CSE', 2, 3, 'ODD', 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('CS311', 'Web Technologies', 'CSE', 2, 3, 'ODD', 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('CS313', 'Computer Networks Lab', 'CSE', 2, 3, 'ODD', 'NONMAJOR', 'INTERNAL', 2, 1.5, 20),
        
        # CSE EVEN Semester (Semester 4) Subjects
        ('CS302', 'Database Systems', 'CSE', 2, 4, 'EVEN', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('CS304', 'Computer Networks', 'CSE', 2, 4, 'EVEN', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('CS306', 'Design and Analysis of Algorithms', 'CSE', 2, 4, 'EVEN', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('CS308', 'Theory of Computation', 'CSE', 2, 4, 'EVEN', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('CS310', 'Microprocessors', 'CSE', 2, 4, 'EVEN', 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('CS312', 'Data Analytics', 'CSE', 2, 4, 'EVEN', 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('CS314', 'Database Lab', 'CSE', 2, 4, 'EVEN', 'NONMAJOR', 'INTERNAL', 2, 1.5, 20),
        
        # ECE ODD Semester (Semester 3) Subjects
        ('EC301', 'Signals and Systems', 'ECE', 2, 3, 'ODD', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('EC303', 'Digital Electronics', 'ECE', 2, 3, 'ODD', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('EC305', 'Electronic Devices', 'ECE', 2, 3, 'ODD', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('EC307', 'Communication Systems', 'ECE', 2, 3, 'ODD', 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('EC309', 'Microprocessors', 'ECE', 2, 3, 'ODD', 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('EC311', 'Circuit Lab', 'ECE', 2, 3, 'ODD', 'NONMAJOR', 'INTERNAL', 2, 1.5, 20),
        
        # ECE EVEN Semester (Semester 4) Subjects
        ('EC302', 'Control Systems', 'ECE', 2, 4, 'EVEN', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('EC304', 'Electromagnetic Theory', 'ECE', 2, 4, 'EVEN', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('EC306', 'Digital Signal Processing', 'ECE', 2, 4, 'EVEN', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('EC308', 'VLSI Design', 'ECE', 2, 4, 'EVEN', 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('EC310', 'Embedded Systems', 'ECE', 2, 4, 'EVEN', 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('EC312', 'Communication Lab', 'ECE', 2, 4, 'EVEN', 'NONMAJOR', 'INTERNAL', 2, 1.5, 20),
        
        # MECH ODD Semester (Semester 3) Subjects
        ('ME301', 'Thermodynamics', 'MECH', 2, 3, 'ODD', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('ME303', 'Fluid Mechanics', 'MECH', 2, 3, 'ODD', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('ME305', 'Machine Design', 'MECH', 2, 3, 'ODD', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('ME307', 'Material Science', 'MECH', 2, 3, 'ODD', 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('ME309', 'Engineering Drawing', 'MECH', 2, 3, 'ODD', 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('ME311', 'Workshop Practice', 'MECH', 2, 3, 'ODD', 'NONMAJOR', 'INTERNAL', 2, 1.5, 20),
        
        # MECH EVEN Semester (Semester 4) Subjects
        ('ME302', 'Manufacturing Processes', 'MECH', 2, 4, 'EVEN', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('ME304', 'Heat Transfer', 'MECH', 2, 4, 'EVEN', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('ME306', 'Mechanics of Materials', 'MECH', 2, 4, 'EVEN', 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('ME308', 'Industrial Engineering', 'MECH', 2, 4, 'EVEN', 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('ME310', 'CAD/CAM', 'MECH', 2, 4, 'EVEN', 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('ME312', 'Manufacturing Lab', 'MECH', 2, 4, 'EVEN', 'NONMAJOR', 'INTERNAL', 2, 1.5, 20),
    ]
    
    cursor.executemany('''
    INSERT INTO subjects (subject_code, subject_name, department, year, semester, 
                         semester_type, subject_type, exam_type, credits, duration, student_count)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', subjects_data)
    
    conn.commit()
    print("✅ Database created and populated with mock data")
    print(f"   - {len(students_data)} students added")
    print(f"   - {len(subjects_data)} subjects added")

def print_database_summary(conn):
    """Print summary of database contents"""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("DATABASE SUMMARY")
    print("="*60)
    
    # Students summary
    cursor.execute('SELECT department, COUNT(*) FROM students GROUP BY department')
    print("\n📚 Students by Department:")
    for dept, count in cursor.fetchall():
        print(f"   {dept}: {count} students")
    
    # Subjects summary by semester type
    cursor.execute('''
    SELECT semester_type, department, subject_type, COUNT(*) 
    FROM subjects 
    WHERE exam_type IN ('SEMESTER', 'BOTH')
    GROUP BY semester_type, department, subject_type
    ORDER BY semester_type, department, subject_type
    ''')
    print("\n📖 Semester Exam Subjects:")
    current_sem = None
    current_dept = None
    for sem_type, dept, stype, count in cursor.fetchall():
        if sem_type != current_sem:
            print(f"\n   {sem_type} SEMESTER:")
            current_sem = sem_type
            current_dept = None
        if dept != current_dept:
            print(f"      {dept}:")
            current_dept = dept
        print(f"         {stype}: {count} subjects")
    
    cursor.execute('''
    SELECT department, COUNT(*) 
    FROM subjects 
    WHERE exam_type = 'INTERNAL' OR exam_type = 'BOTH'
    GROUP BY department
    ''')
    print("\n📝 Internal Exam Subjects:")
    for dept, count in cursor.fetchall():
        print(f"   {dept}: {count} subjects")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    print("Creating Exam Scheduling Database...")
    conn = create_database()
    populate_mock_data(conn)
    print_database_summary(conn)
    conn.close()
    print("\n✅ Database setup complete! File: exam_scheduling.db")
