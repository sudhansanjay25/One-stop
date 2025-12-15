"""
Seating Integration Module
--------------------------
Bridges the exam schedule output with the Seating Arrangement system.

Responsibilities:
- Group scheduled exams by (date, session) to determine scope.
- For each slot, filter students to only the departments with exams.
- Invoke SeatingAllocationSystem to create seating allocations and PDFs.
- Return a concise summary of generated artifacts for logging.

This module expects the Seating Arrangement resources to live at:
  One-Stop-Hackathon/Seating Arangement/
with the following files available:
  - halls.csv
  - Teachers.csv
  - year{year}.csv (e.g., year2.csv)

Usage:
  from seating_integration import generate_seating_from_schedule
  results = generate_seating_from_schedule(schedule, exam_type, year)

Where:
  - schedule: list of dicts with keys ['date','session','department','subject_id','student_count', ...]
  - exam_type: 'SEMESTER' or 'INTERNAL' (as produced by scheduler/main)
  - year: int (1..4)
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Wire path to the Seating Arrangement module (kept outside this folder)
SEATING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Seating Arangement')
sys.path.append(SEATING_DIR)

# Outputs should be inside the Exam Scheduling Algorithm folder
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(WORK_DIR, 'Seating Outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

try:
    # Provided by attachments: Seating Arangement/seating_allocation.py
    from seating_allocation import SeatingAllocationSystem  # type: ignore
    _SEATING_AVAILABLE = True
except Exception:
    SeatingAllocationSystem = None  # type: ignore
    _SEATING_AVAILABLE = False


def _group_by_slot(schedule: List[Dict[str, Any]]):
    """Group schedule entries by (date, session)."""
    grouped: Dict[tuple, List[Dict[str, Any]]] = {}
    for item in schedule:
        key = (item['date'], item['session'])
        grouped.setdefault(key, []).append(item)
    # Sort by date asc, then session (FN before AN)
    def sort_key(k):
        date_str, sess = k
        return (datetime.strptime(date_str, '%d.%m.%Y'), {'FN': 0, 'SINGLE': 0, 'AN': 1}.get(sess, 2))
    return dict(sorted(grouped.items(), key=lambda kv: sort_key(kv[0])))


def generate_seating_from_schedule(schedule: List[Dict[str, Any]], exam_type: str, year: int,
                                   logger=print) -> List[Dict[str, Any]]:
    """Generate seating PDFs per date/session slot from the given schedule.

    Returns a list of results with keys:
      - date, session, departments, student_pdf, faculty_pdf, total_students
    """
    results: List[Dict[str, Any]] = []

    if not _SEATING_AVAILABLE:
        logger("   ℹ️  seating_allocation.py module not available. Skipping seating PDF generation.")
        return results

    # Validate required files
    halls_file = os.path.join(SEATING_DIR, 'halls.csv')
    teachers_file = os.path.join(SEATING_DIR, 'Teachers.csv')
    students_file = os.path.join(SEATING_DIR, f'year{year}.csv')

    for p in (halls_file, teachers_file, students_file):
        if not os.path.exists(p):
            logger(f"   ⚠️  Missing required seating resource: {p}")
            return results

    # Map exam type to SeatingAllocationSystem convention
    sa_exam_type = 'Internal' if exam_type == 'INTERNAL' else 'SEM'

    # Load all students once
    try:
        import pandas as pd  # local import to avoid hard dependency at import-time
        all_students_df = pd.read_csv(students_file, dtype={'Register Number': str})
    except Exception as e:
        logger(f"   ⚠️  Unable to load students file '{students_file}': {e}")
        return results

    # Process each slot
    by_slot = _group_by_slot(schedule)

    for (exam_date, session), exams in by_slot.items():
        try:
            depts = sorted(list({e['department'] for e in exams}))
            # Filter students for the departments present in this slot
            slot_students_df = all_students_df[all_students_df['Department'].isin(depts)].copy()

            # If no students match, skip gracefully
            if slot_students_df.empty:
                logger(f"   ℹ️  No students found for departments {depts} on {exam_date} {session}; skipping.")
                continue

            # Write temp students CSV for this slot
            # temp students file inside Exam Scheduling folder
            tmp_students_path = os.path.join(OUTPUT_DIR, f'_tmp_students_Y{year}_{exam_date}_{session}.csv')
            slot_students_df.to_csv(tmp_students_path, index=False)

            # Initialize seating system
            system = SeatingAllocationSystem(
                halls_file=halls_file,
                students_file=tmp_students_path,
                teachers_file=teachers_file,
                session=session,
                exam_type=sa_exam_type,
                year=year,
                internal_number=1,
            )

            # Run allocation pipeline
            system.allocate_seats_mixed_department()
            system.assign_teachers()

            # PDFs inside Exam Scheduling folder
            student_pdf = os.path.join(OUTPUT_DIR, f'seating_student_{exam_date}_{session}_Y{year}_{sa_exam_type}.pdf')
            faculty_pdf = os.path.join(OUTPUT_DIR, f'seating_faculty_{exam_date}_{session}_Y{year}_{sa_exam_type}.pdf')
            student_pdf = system.generate_student_pdf(output_file=student_pdf)
            faculty_pdf = system.generate_faculty_pdf(output_file=faculty_pdf)

            # Cleanup temp file
            try:
                os.remove(tmp_students_path)
            except Exception:
                pass

            total_students = len(system.allocations) if hasattr(system, 'allocations') else 0

            results.append({
                'date': exam_date,
                'session': session,
                'departments': depts,
                'student_pdf': student_pdf,
                'faculty_pdf': faculty_pdf,
                'total_students': total_students,
            })

            logger(f"      ✓ Seating PDFs created for {exam_date} {session}: {total_students} students")
        except Exception as e:
            logger(f"   ⚠️  Seating generation failed for {exam_date} {session}: {e}")

    return results
