"""
Core Exam Scheduling Algorithm
Implements greedy scheduling with best-effort gap constraints
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import config

class ExamScheduler:
    def __init__(self, db_path='exam_scheduling.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
    def close(self):
        """Close database connection"""
        self.conn.close()
    
    def generate_available_dates(self, start_date: str, end_date: str, 
                                holidays: List[str]) -> List[str]:
        """
        Generate list of available dates excluding weekends and holidays
        
        Args:
            start_date: Start date in DD.MM.YYYY format
            end_date: End date in DD.MM.YYYY format
            holidays: List of holiday dates in DD.MM.YYYY format
            
        Returns:
            List of available dates in DD.MM.YYYY format
        """
        # Parse dates
        start = datetime.strptime(start_date, '%d.%m.%Y')
        end = datetime.strptime(end_date, '%d.%m.%Y')
        
        # Convert holidays to datetime objects
        holiday_dates = [datetime.strptime(h, '%d.%m.%Y') for h in holidays]
        
        available_dates = []
        current = start
        
        while current <= end:
            # Skip weekends (Saturday=5, Sunday=6)
            if current.weekday() not in config.WEEKENDS:
                # Skip holidays
                if current not in holiday_dates:
                    available_dates.append(current.strftime('%d.%m.%Y'))
            current += timedelta(days=1)
        
        return available_dates
    
    def get_subjects_for_year(self, year: int, exam_type: str, semester_type: str) -> List[Dict]:
        """
        Fetch subjects for given year, exam type, and semester type
        
        Args:
            year: Year group (1-4)
            exam_type: 'SEMESTER' or 'INTERNAL'
            semester_type: 'ODD' or 'EVEN'
            
        Returns:
            List of subject dictionaries
        """
        query = '''
        SELECT subject_id, subject_code, subject_name, department, 
               year, semester_type, subject_type, exam_type, student_count
        FROM subjects
        WHERE year = ? AND semester_type = ? AND (exam_type = ? OR exam_type = 'BOTH')
        ORDER BY subject_type DESC, department, subject_code
        '''
        
        self.cursor.execute(query, (year, semester_type, exam_type))
        rows = self.cursor.fetchall()
        
        subjects = []
        for row in rows:
            subjects.append({
                'subject_id': row[0],
                'subject_code': row[1],
                'subject_name': row[2],
                'department': row[3],
                'year': row[4],
                'semester_type': row[5],
                'subject_type': row[6],
                'exam_type': row[7],
                'student_count': row[8]
            })
        
        return subjects
    
    def build_conflict_graph(self, subjects: List[Dict]) -> Dict[int, List[int]]:
        """
        Build conflict graph where subjects from same department conflict
        
        Args:
            subjects: List of subject dictionaries
            
        Returns:
            Dictionary mapping subject_id to list of conflicting subject_ids
        """
        conflicts = {}
        
        for subject in subjects:
            subject_id = subject['subject_id']
            dept = subject['department']
            
            # Find all subjects from same department
            conflicting_ids = [
                s['subject_id'] for s in subjects 
                if s['department'] == dept and s['subject_id'] != subject_id
            ]
            
            conflicts[subject_id] = conflicting_ids
        
        return conflicts
    
    def validate_gap_constraint(self, last_exam: Optional[Dict], 
                               new_date: str, new_session: str) -> Tuple[bool, str]:
        """
        Validate gap constraints between exams
        
        Args:
            last_exam: Dictionary with last exam info or None
            new_date: New exam date (DD.MM.YYYY)
            new_session: New exam session (FN/AN/SINGLE)
            
        Returns:
            Tuple of (is_valid, violation_message)
        """
        if last_exam is None:
            return True, ""
        
        last_date = datetime.strptime(last_exam['date'], '%d.%m.%Y')
        new_date_dt = datetime.strptime(new_date, '%d.%m.%Y')
        last_session = last_exam['session']
        last_type = last_exam['subject_type']
        
        days_diff = (new_date_dt - last_date).days
        
        # Heavy subject constraint: Need 1 full day gap
        if last_type == 'HEAVY':
            if days_diff < 2:  # Less than 1 full day gap
                return False, f"Heavy subject needs 1 full day gap (only {days_diff} days)"
        
        # Non-major constraint: Need half-day gap
        if last_type == 'NONMAJOR':
            if days_diff == 0 and new_session == last_session:
                return False, "Same session on same day for non-major"
        
        # AN session rule: If last was AN, next must be AN (next day) or day after tomorrow
        if last_session == 'AN' and days_diff == 1:
            if new_session == 'FN':
                return False, "Cannot schedule FN next day after AN session"
        
        return True, ""
    
    def schedule_semester_exams(self, year: int, semester_type: str, start_date: str, end_date: str,
                               holidays: List[str]) -> Tuple[List[Dict], List[Dict]]:
        """
        Schedule semester exams for given year and semester type
        
        Args:
            year: Year group
            semester_type: 'ODD' or 'EVEN'
            start_date: Start date (DD.MM.YYYY)
            end_date: End date (DD.MM.YYYY)
            holidays: List of holiday dates
            
        Returns:
            Tuple of (schedule, violations)
        """
        # Generate available dates
        available_dates = self.generate_available_dates(start_date, end_date, holidays)
        
        if not available_dates:
            raise ValueError("No available dates for scheduling!")
        
        # Get subjects
        subjects = self.get_subjects_for_year(year, 'SEMESTER', semester_type)
        
        if not subjects:
            raise ValueError(f"No semester subjects found for year {year}")
        
        # Calculate total slots needed
        total_slots = len(available_dates) * 2  # FN + AN per day
        
        print(f"\n📊 Scheduling Analysis:")
        print(f"   Available dates: {len(available_dates)}")
        print(f"   Total slots: {total_slots}")
        print(f"   Subjects to schedule: {len(subjects)}")
        
        if len(subjects) > total_slots:
            print(f"   ⚠️  WARNING: Not enough slots! Need to extend date range.")
        
        # Build conflict graph
        conflicts = self.build_conflict_graph(subjects)
        
        # Initialize schedule and tracking
        schedule = []
        violations = []
        dept_last_exam = {}  # Track last exam per department
        dept_date_usage = {}  # Track which dates are used per department (entire day)
        
        # Create slots
        slots = []
        for date in available_dates:
            slots.append({'date': date, 'session': 'FN'})
            slots.append({'date': date, 'session': 'AN'})
        
        # Schedule each subject
        for subject in subjects:
            subject_id = subject['subject_id']
            dept = subject['department']
            
            scheduled = False
            best_slot = None
            violation_msg = None
            
            # Try to find valid slot
            for slot in slots:
                date_key = f"{dept}_{slot['date']}"
                
                # Check if this date already used for this department (block entire day)
                if date_key in dept_date_usage:
                    continue
                
                # Validate gap constraints
                last_exam = dept_last_exam.get(dept)
                is_valid, msg = self.validate_gap_constraint(
                    last_exam, slot['date'], slot['session']
                )
                
                if is_valid:
                    best_slot = slot
                    break
                elif best_slot is None:
                    # Keep track of first available slot even if constraint violated
                    best_slot = slot
                    violation_msg = msg
            
            if best_slot is None:
                raise ValueError(f"No slots available for {subject['subject_code']}")
            
            # Assign to best slot and block entire day for this department
            date_key = f"{dept}_{best_slot['date']}"
            dept_date_usage[date_key] = subject_id
            
            schedule.append({
                'subject_id': subject_id,
                'subject_code': subject['subject_code'],
                'subject_name': subject['subject_name'],
                'department': dept,
                'date': best_slot['date'],
                'session': best_slot['session'],
                'subject_type': subject['subject_type'],
                'student_count': subject['student_count']
            })
            
            # Update last exam for department
            dept_last_exam[dept] = {
                'date': best_slot['date'],
                'session': best_slot['session'],
                'subject_type': subject['subject_type']
            }
            
            # Log violation if any
            if violation_msg:
                violations.append({
                    'subject_id': subject_id,
                    'subject_code': subject['subject_code'],
                    'violation_type': 'GAP_CONSTRAINT',
                    'description': violation_msg,
                    'severity': 'MEDIUM'
                })
        
        return schedule, violations
    
    def schedule_internal_exams(self, year: int, semester_type: str, start_date: str, end_date: str,
                                holidays: List[str]) -> Tuple[List[Dict], List[Dict]]:
        """
        Schedule internal exams for given year and semester type
        
        Args:
            year: Year group
            semester_type: 'ODD' or 'EVEN'
            start_date: Start date (DD.MM.YYYY)
            end_date: End date (DD.MM.YYYY)
            holidays: List of holiday dates
            
        Returns:
            Tuple of (schedule, violations)
        """
        # Generate available dates
        available_dates = self.generate_available_dates(start_date, end_date, holidays)
        
        if not available_dates:
            raise ValueError("No available dates for scheduling!")
        
        # Get subjects
        subjects = self.get_subjects_for_year(year, 'INTERNAL', semester_type)
        
        if not subjects:
            raise ValueError(f"No internal subjects found for year {year}")
        
        # Group subjects by department to find max subjects per department
        dept_subjects = {}
        for subject in subjects:
            dept = subject['department']
            if dept not in dept_subjects:
                dept_subjects[dept] = []
            dept_subjects[dept].append(subject)
        
        # Find maximum subjects in any single department
        max_subjects_per_dept = max(len(subjs) for subjs in dept_subjects.values())
        
        print(f"\n📊 Scheduling Analysis:")
        print(f"   Available dates: {len(available_dates)}")
        print(f"   Total subjects: {len(subjects)}")
        print(f"   Max subjects per department: {max_subjects_per_dept}")
        for dept, subjs in sorted(dept_subjects.items()):
            print(f"      {dept}: {len(subjs)} subjects")
        
        # Determine scheduling strategy based on max subjects per department
        min_days_needed = (max_subjects_per_dept + 1) / 2  # Round up for minimum days
        
        if len(available_dates) < min_days_needed:
            raise ValueError(
                f"Cannot schedule - insufficient dates. "
                f"Need at least {int(min_days_needed)} days for {max_subjects_per_dept} subjects "
                f"(max in single department). Only {len(available_dates)} days available."
            )
        
        # Decide whether to use single or dual sessions based on max subjects per dept
        use_dual_sessions = len(available_dates) < max_subjects_per_dept
        
        if use_dual_sessions:
            print(f"   ℹ️  Using both FN and AN sessions (2 exams per day)")
            sessions = ['FN', 'AN']
        else:
            print(f"   ℹ️  Using only FN session (1 exam per day)")
            sessions = ['FN']
        
        # Build conflict graph
        conflicts = self.build_conflict_graph(subjects)
        
        # Initialize schedule and tracking
        schedule = []
        violations = []
        dept_date_session_usage = {}  # Track which date+session combinations are used per department
        
        # Create slots
        slots = []
        for date in available_dates:
            for session in sessions:
                slots.append({'date': date, 'session': session})
        
        # Schedule each subject
        for subject in subjects:
            subject_id = subject['subject_id']
            dept = subject['department']
            
            scheduled = False
            
            # Find first available slot for this department
            for slot in slots:
                slot_key = f"{dept}_{slot['date']}_{slot['session']}"
                
                if slot_key not in dept_date_session_usage:
                    # Assign to this slot
                    dept_date_session_usage[slot_key] = subject_id
                    
                    schedule.append({
                        'subject_id': subject_id,
                        'subject_code': subject['subject_code'],
                        'subject_name': subject['subject_name'],
                        'department': dept,
                        'date': slot['date'],
                        'session': slot['session'],
                        'subject_type': subject['subject_type'],
                        'student_count': subject['student_count']
                    })
                    
                    scheduled = True
                    break
            
            if not scheduled:
                violations.append({
                    'subject_id': subject_id,
                    'subject_code': subject['subject_code'],
                    'violation_type': 'NO_SLOT_AVAILABLE',
                    'description': 'Could not find available slot',
                    'severity': 'HIGH'
                })
        
        return schedule, violations
    
    def save_schedule_to_db(self, cycle_id: int, schedule: List[Dict], 
                           violations: List[Dict]):
        """
        Save generated schedule and violations to database
        
        Args:
            cycle_id: Exam cycle ID
            schedule: List of scheduled exams
            violations: List of constraint violations
        """
        # Insert schedule
        for item in schedule:
            self.cursor.execute('''
            INSERT INTO exam_schedule 
            (exam_cycle_id, subject_id, department, exam_date, session, student_count)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (cycle_id, item['subject_id'], item['department'], 
                  item['date'], item['session'], item['student_count']))
        
        # Insert violations
        for violation in violations:
            self.cursor.execute('''
            INSERT INTO schedule_violations
            (exam_cycle_id, subject_id, violation_type, description, severity)
            VALUES (?, ?, ?, ?, ?)
            ''', (cycle_id, violation['subject_id'], violation['violation_type'],
                  violation['description'], violation['severity']))
        
        self.conn.commit()
    
    def create_exam_cycle(self, exam_type: str, year: int, 
                         start_date: str, end_date: str) -> int:
        """
        Create a new exam cycle in database
        
        Returns:
            Cycle ID
        """
        created_date = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        
        self.cursor.execute('''
        INSERT INTO exam_cycles (exam_type, year_group, start_date, end_date, 
                                created_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (exam_type, year, start_date, end_date, created_date, 'COMPLETED'))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_schedule(self, cycle_id: int) -> List[Dict]:
        """Retrieve schedule for given cycle"""
        self.cursor.execute('''
        SELECT es.schedule_id, es.subject_id, s.subject_code, s.subject_name,
               es.department, es.exam_date, es.session, es.student_count
        FROM exam_schedule es
        JOIN subjects s ON es.subject_id = s.subject_id
        WHERE es.exam_cycle_id = ?
        ORDER BY es.exam_date, es.session, es.department
        ''', (cycle_id,))
        
        rows = self.cursor.fetchall()
        schedule = []
        
        for row in rows:
            schedule.append({
                'schedule_id': row[0],
                'subject_id': row[1],
                'subject_code': row[2],
                'subject_name': row[3],
                'department': row[4],
                'date': row[5],
                'session': row[6],
                'student_count': row[7]
            })
        
        return schedule
    
    def get_violations(self, cycle_id: int) -> List[Dict]:
        """Retrieve violations for given cycle"""
        self.cursor.execute('''
        SELECT sv.violation_id, sv.subject_id, s.subject_code, s.subject_name,
               sv.violation_type, sv.description, sv.severity
        FROM schedule_violations sv
        JOIN subjects s ON sv.subject_id = s.subject_id
        WHERE sv.exam_cycle_id = ?
        ''', (cycle_id,))
        
        rows = self.cursor.fetchall()
        violations = []
        
        for row in rows:
            violations.append({
                'violation_id': row[0],
                'subject_id': row[1],
                'subject_code': row[2],
                'subject_name': row[3],
                'violation_type': row[4],
                'description': row[5],
                'severity': row[6]
            })
        
        return violations
