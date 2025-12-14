"""
Command-Line Interface for Exam Scheduling System
Allows admin to create and manage exam schedules
"""

import sys
import os
from datetime import datetime
from scheduler import ExamScheduler
from pdf_generator import generate_schedule_pdf
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
                session_str = config.SESSION_TIMINGS['SINGLE']
            
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
