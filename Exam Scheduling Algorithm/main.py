"""
Command-Line Interface for Exam Scheduling System
Allows admin to create and manage exam schedules
"""

import sys
import os
from datetime import datetime
from scheduler import ExamScheduler
from pdf_generator import generate_schedule_pdf
from seating_integration import run_seating_allocation_for_schedule
import config

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_schedule_table(schedule, exam_type):
    """Print schedule in table format"""
    if not schedule:
        print("   No exams scheduled.")
        return
    
    # Check if internal exam has dual sessions
    sessions_used = set(item['session'] for item in schedule)
    is_internal_dual = exam_type == 'INTERNAL' and 'FN' in sessions_used and 'AN' in sessions_used
    
    if is_internal_dual:
        # Print two separate matrix tables for FN and AN
        print_internal_matrix_table(schedule, 'FN')
        print_internal_matrix_table(schedule, 'AN')
    else:
        # Original list format for semester or single-session internal
        print_schedule_list_format(schedule, exam_type)

def print_internal_matrix_table(schedule, session):
    """Print internal exam schedule in matrix format (dates as columns, depts as rows)"""
    # Filter schedule by session
    session_schedule = [item for item in schedule if item['session'] == session]
    
    if not session_schedule:
        return
    
    # Get unique dates and departments
    dates = sorted(set(item['date'] for item in session_schedule), 
                   key=lambda x: datetime.strptime(x, '%d.%m.%Y'))
    departments = sorted(set(item['department'] for item in session_schedule))
    
    # Create mapping: (dept, date) -> subject
    schedule_map = {}
    for item in session_schedule:
        key = (item['department'], item['date'])
        schedule_map[key] = f"{item['subject_code']}\n{item['subject_name']}"
    
    # Print session header
    session_time = config.SESSION_TIMINGS['FN_INTERNAL'] if session == 'FN' else config.SESSION_TIMINGS['AN_INTERNAL']
    print(f"\n{'='*70}")
    print(f"  {session} SESSION ({session_time})")
    print(f"{'='*70}")
    
    # Calculate column width
    col_width = max(15, (70 - 10) // len(dates))
    
    # Print header row with dates
    print(f"\n{'Dept':<10}", end='')
    for date in dates:
        # Show date and day of week
        date_obj = datetime.strptime(date, '%d.%m.%Y')
        date_short = date_obj.strftime('%d.%m.%Y')
        day_name = date_obj.strftime('%A')
        print(f"{date_short:^{col_width}}", end='')
    print()
    print(f"{'/ Day':<10}", end='')
    for date in dates:
        date_obj = datetime.strptime(date, '%d.%m.%Y')
        day_name = date_obj.strftime('%A')
        print(f"{day_name:^{col_width}}", end='')
    print()
    print("-" * 70)
    
    # Print each department row
    for dept in departments:
        print(f"{dept:<10}", end='')
        for date in dates:
            key = (dept, date)
            if key in schedule_map:
                subject_info = schedule_map[key]
                # Show subject name instead of code
                subject_name = subject_info.split('\n')[1]
                # Truncate if too long
                if len(subject_name) > col_width - 2:
                    subject_name = subject_name[:col_width-5] + "..."
                print(f"{subject_name:^{col_width}}", end='')
            else:
                print(f"{'-':^{col_width}}", end='')
        print()
    print("-" * 70)

def print_schedule_list_format(schedule, exam_type):
    """Print schedule in original list format"""
    # Group by date
    schedule_by_date = {}
    for item in schedule:
        date = item['date']
        if date not in schedule_by_date:
            schedule_by_date[date] = []
        schedule_by_date[date].append(item)
    
    # Print table header
    print("\n" + "-"*70)
    print(f"{'Date':<15} {'Session':<10} {'Dept':<8} {'Code':<10} {'Subject':<25}")
    print("-"*70)
    
    # Print schedule
    for date in sorted(schedule_by_date.keys(), key=lambda x: datetime.strptime(x, '%d.%m.%Y')):
        exams = schedule_by_date[date]
        
        # Sort by session then department
        session_order = {'FN': 0, 'AN': 1, 'SINGLE': 0}
        exams.sort(key=lambda x: (session_order.get(x['session'], 2), x['department']))
        
        for i, exam in enumerate(exams):
            date_str = date if i == 0 else ''
            session_str = exam['session']
            if exam_type == 'SEMESTER':
                session_str += f" ({config.SESSION_TIMINGS[exam['session']]})"
            elif exam_type == 'INTERNAL':
                # Use internal-specific timings
                if exam['session'] == 'FN':
                    session_str = f"FN ({config.SESSION_TIMINGS['FN_INTERNAL']})"
                elif exam['session'] == 'AN':
                    session_str = f"AN ({config.SESSION_TIMINGS['AN_INTERNAL']})"
                else:
                    session_str = f"{exam['session']}"
            
            # Truncate subject name if too long
            subject_name = exam['subject_name']
            if len(subject_name) > 25:
                subject_name = subject_name[:22] + "..."
            
            print(f"{date_str:<15} {session_str:<10} {exam['department']:<8} "
                  f"{exam['subject_code']:<10} {subject_name:<25}")
        
        if len(exams) > 0:
            print("-"*70)

def print_violations_table(violations):
    """Print violations in table format"""
    if not violations:
        print("   ✅ No constraint violations!")
        return
    
    print("\n" + "-"*70)
    print(f"{'Code':<10} {'Severity':<12} {'Issue':<48}")
    print("-"*70)
    
    for v in violations:
        description = v['description']
        if len(description) > 48:
            description = description[:45] + "..."
        
        print(f"{v['subject_code']:<10} {v['severity']:<12} {description:<48}")
    
    print("-"*70)

def get_user_input():
    """Get scheduling parameters from user"""
    print_header("EXAM SCHEDULING SYSTEM - Input Parameters")
    
    # Exam type
    print("\n1. Select Exam Type:")
    print("   [1] Semester Exam")
    print("   [2] Internal Exam")
    
    while True:
        choice = input("\n   Enter choice (1/2): ").strip()
        if choice == '1':
            exam_type = 'SEMESTER'
            break
        elif choice == '2':
            exam_type = 'INTERNAL'
            break
        else:
            print("   Invalid choice. Please enter 1 or 2.")
    
    # Semester type (Odd/Even)
    print("\n2. Select Semester Type:")
    print("   [1] Odd Semester (1, 3, 5, 7)")
    print("   [2] Even Semester (2, 4, 6, 8)")
    
    while True:
        choice = input("\n   Enter choice (1/2): ").strip()
        if choice == '1':
            semester_type = 'ODD'
            break
        elif choice == '2':
            semester_type = 'EVEN'
            break
        else:
            print("   Invalid choice. Please enter 1 or 2.")
    
    # Year group
    print("\n3. Select Year Group:")
    print("   [1] First Year")
    print("   [2] Second Year")
    print("   [3] Third Year")
    print("   [4] Fourth Year")
    
    while True:
        choice = input("\n   Enter choice (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            year = int(choice)
            break
        else:
            print("   Invalid choice. Please enter 1-4.")
    
    # Date range
    print("\n4. Enter Exam Period:")
    
    while True:
        start_date = input("   Start Date (DD.MM.YYYY): ").strip()
        try:
            datetime.strptime(start_date, '%d.%m.%Y')
            break
        except ValueError:
            print("   Invalid format. Please use DD.MM.YYYY")
    
    while True:
        end_date = input("   End Date (DD.MM.YYYY): ").strip()
        try:
            end_dt = datetime.strptime(end_date, '%d.%m.%Y')
            start_dt = datetime.strptime(start_date, '%d.%m.%Y')
            if end_dt >= start_dt:
                break
            else:
                print("   End date must be after start date.")
        except ValueError:
            print("   Invalid format. Please use DD.MM.YYYY")
    
    # Holidays
    print("\n5. Enter Holidays to Exclude:")
    print("   (Enter dates separated by commas, or press Enter to skip)")
    print("   Example: 20.12.2025, 25.12.2025")
    
    holidays_input = input("   Holidays: ").strip()
    holidays = []
    
    if holidays_input:
        for h in holidays_input.split(','):
            h = h.strip()
            try:
                datetime.strptime(h, '%d.%m.%Y')
                holidays.append(h)
            except ValueError:
                print(f"   Warning: Invalid date '{h}' ignored.")
    
    return exam_type, semester_type, year, start_date, end_date, holidays

def main():
    """Main CLI function"""
    print_header("EXAM SCHEDULING SYSTEM")
    print("   Automated exam timetable generation with constraint handling")
    
    # Initialize scheduler
    scheduler = ExamScheduler()
    
    try:
        # Get input
        exam_type, semester_type, year, start_date, end_date, holidays = get_user_input()
        
        # Display summary
        print_header("SCHEDULING PARAMETERS")
        print(f"\n   Exam Type: {exam_type}")
        print(f"   Semester Type: {semester_type}")
        print(f"   Year Group: {year}")
        print(f"   Start Date: {start_date}")
        print(f"   End Date: {end_date}")
        print(f"   Holidays: {', '.join(holidays) if holidays else 'None'}")
        
        # Confirm
        print("\n" + "-"*70)
        confirm = input("\n   Proceed with scheduling? (y/n): ").strip().lower()
        
        if confirm != 'y':
            print("\n   Scheduling cancelled.")
            scheduler.close()
            return
        
        # Generate schedule
        print_header("GENERATING SCHEDULE")
        print("   Please wait...")
        
        if exam_type == 'SEMESTER':
            schedule, violations = scheduler.schedule_semester_exams(
                year, semester_type, start_date, end_date, holidays
            )
        else:
            schedule, violations = scheduler.schedule_internal_exams(
                year, semester_type, start_date, end_date, holidays
            )
        
        # Create exam cycle and save
        cycle_id = scheduler.create_exam_cycle(exam_type, year, start_date, end_date)
        scheduler.save_schedule_to_db(cycle_id, schedule, violations)
        
        # Display results
        print_header(f"{exam_type} EXAM SCHEDULE - Year {year}")
        print(f"\n   Total Exams Scheduled: {len(schedule)}")
        print(f"   Constraint Violations: {len(violations)}")
        
        print_schedule_table(schedule, exam_type)
        
        if violations:
            print_header("CONSTRAINT VIOLATIONS")
            print(f"\n   ⚠️  {len(violations)} constraint violation(s) detected:")
            print_violations_table(violations)
            print("\n   Note: These violations occur due to insufficient time slots.")
            print("   Consider extending the exam period if possible.")
        else:
            print("\n   ✅ All constraints satisfied!")
        
        # Summary by department
        print_header("DEPARTMENT-WISE SUMMARY")
        dept_summary = {}
        for exam in schedule:
            dept = exam['department']
            if dept not in dept_summary:
                dept_summary[dept] = 0
            dept_summary[dept] += 1
        
        for dept, count in sorted(dept_summary.items()):
            print(f"   {dept}: {count} exams")
        
        print("\n" + "="*70)
        print(f"   Schedule saved to database (Cycle ID: {cycle_id})")
        print("="*70)
        
        # Generate seating allocations (per date+session scope)
        print("\n   Generating seating allocations...")
        try:
            generated_pdfs = run_seating_allocation_for_schedule(schedule, exam_type, year)
            print(f"   ✅ Seating allocations created for {len(generated_pdfs)} slot(s)")
            for (student_pdf, faculty_pdf) in generated_pdfs:
                print(f"      Student PDF: {student_pdf}")
                print(f"      Faculty PDF: {faculty_pdf}")
        except Exception as seat_err:
            print(f"   ⚠️  Seating allocation failed: {seat_err}")

        # Generate PDF
        print("\n   Generating PDF...")
        try:
            pdf_path = generate_schedule_pdf(
                schedule, violations, exam_type, year, 
                start_date, end_date
            )
            abs_path = os.path.abspath(pdf_path)
            print(f"   ✅ PDF generated: {abs_path}")
        except Exception as pdf_error:
            print(f"   ⚠️  PDF generation failed: {pdf_error}")
            print("   Schedule is still saved in database.")
        
    except ValueError as e:
        print(f"\n   ❌ Error: {e}")
    except Exception as e:
        print(f"\n   ❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scheduler.close()

if __name__ == "__main__":
    main()
