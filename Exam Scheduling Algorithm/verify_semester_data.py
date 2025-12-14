"""
Verification script to show odd/even semester subjects
"""
import sqlite3

conn = sqlite3.connect('exam_scheduling.db')
cursor = conn.cursor()

print("\n" + "="*70)
print("SEMESTER SUBJECTS VERIFICATION")
print("="*70)

# Count by semester type
cursor.execute("""
    SELECT semester_type, COUNT(*) as count 
    FROM subjects 
    WHERE exam_type IN ('SEMESTER', 'BOTH')
    GROUP BY semester_type
""")
print("\n📊 Subject Count by Semester Type:")
for row in cursor.fetchall():
    print(f"   {row[0]} Semester: {row[1]} subjects")

# List all ODD semester subjects
cursor.execute("""
    SELECT department, subject_code, subject_name, subject_type
    FROM subjects 
    WHERE semester_type = 'ODD' AND exam_type IN ('SEMESTER', 'BOTH')
    ORDER BY department, subject_type DESC, subject_code
""")
print("\n📗 ODD SEMESTER SUBJECTS:")
current_dept = None
for dept, code, name, stype in cursor.fetchall():
    if dept != current_dept:
        print(f"\n   {dept}:")
        current_dept = dept
    print(f"      {code} - {name} ({stype})")

# List all EVEN semester subjects
cursor.execute("""
    SELECT department, subject_code, subject_name, subject_type
    FROM subjects 
    WHERE semester_type = 'EVEN' AND exam_type IN ('SEMESTER', 'BOTH')
    ORDER BY department, subject_type DESC, subject_code
""")
print("\n📘 EVEN SEMESTER SUBJECTS:")
current_dept = None
for dept, code, name, stype in cursor.fetchall():
    if dept != current_dept:
        print(f"\n   {dept}:")
        current_dept = dept
    print(f"      {code} - {name} ({stype})")

print("\n" + "="*70)
conn.close()
