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
            # Skip only Sunday (weekday 6) - Saturday is working day
            if current.weekday() != 6:
                # Skip holidays
                if current not in holiday_dates:
                    available_dates.append(current.strftime('%d.%m.%Y'))
            current += timedelta(days=1)
        
        return available_dates
    
    def get_subjects_for_year(self, year: int, exam_type: str, semester_type: str) -> List[Dict]:
        """
        Fetch subjects for given year, exam type, and semester type
        Includes both regular semester subjects AND opposite semester subjects with arrears
        
        Args:
            year: Year group (1-4)
            exam_type: 'SEMESTER' or 'INTERNAL'
            semester_type: 'ODD' or 'EVEN'
            
        Returns:
            List of subject dictionaries (includes arrear subjects for SEMESTER exams)
        """
        # For SEMESTER exams, include arrear subjects from opposite semester
        if exam_type == 'SEMESTER':
            opposite_semester = 'EVEN' if semester_type == 'ODD' else 'ODD'
            
            # Get regular subjects for current semester
            query_regular = '''
            SELECT subject_id, subject_code, subject_name, department, 
                   year, semester_type, subject_type, exam_type, student_count,
                   'REGULAR' as subject_track
            FROM subjects
            WHERE year = ? AND semester_type = ? AND (exam_type = ? OR exam_type = 'BOTH')
            '''
            
            # Get arrear subjects from opposite semester (only if students have arrears)
            query_arrear = '''
            SELECT DISTINCT s.subject_id, s.subject_code, s.subject_name, s.department,
                   s.year, s.semester_type, s.subject_type, s.exam_type,
                   COUNT(DISTINCT ss.student_id) as student_count,
                   'ARREAR' as subject_track
            FROM subjects s
            JOIN student_subjects ss ON s.subject_id = ss.subject_id
            WHERE s.year = ? AND s.semester_type = ? 
                  AND (s.exam_type = ? OR s.exam_type = 'BOTH')
                  AND ss.is_arrear = 1
            GROUP BY s.subject_id
            HAVING student_count > 0
            '''
            
            # Fetch both regular and arrear subjects
            self.cursor.execute(query_regular, (year, semester_type, exam_type))
            rows = self.cursor.fetchall()
            
            self.cursor.execute(query_arrear, (year, opposite_semester, exam_type))
            rows.extend(self.cursor.fetchall())
            
        else:
            # For INTERNAL exams, only include current semester (no arrears)
            query = '''
            SELECT subject_id, subject_code, subject_name, department, 
                   year, semester_type, subject_type, exam_type, student_count,
                   'REGULAR' as subject_track
            FROM subjects
            WHERE year = ? AND semester_type = ? AND (exam_type = ? OR exam_type = 'BOTH')
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
                'student_count': row[8],
                'subject_track': row[9]  # 'REGULAR' or 'ARREAR'
            })
        
        # Sort: Regular subjects first, then by subject_type, department, subject_code
        subjects.sort(key=lambda x: (
            0 if x['subject_track'] == 'REGULAR' else 1,  # Regular first
            0 if x['subject_type'] == 'THEORY' else 1,  # Theory before Lab
            x['department'],
            x['subject_code']
        ))
        
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
        Schedule semester exams - simple alternating approach
        
        SIMPLE LOGIC:
        - Alternates between ODD and EVEN semester subjects
        - Pattern: ODD1, EVEN1, ODD2, EVEN2, ODD3, EVEN3...
        - Fills available dates sequentially until subjects run out
        
        Args:
            year: Year group
            semester_type: 'ODD' or 'EVEN' (which semester to start with)
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
        
        # Get subjects for BOTH semesters (ODD and EVEN)
        odd_subjects = self.get_subjects_for_year(year, 'SEMESTER', 'ODD')
        even_subjects = self.get_subjects_for_year(year, 'SEMESTER', 'EVEN')
        
        # Group by department
        odd_by_dept = {}
        even_by_dept = {}
        
        for subject in odd_subjects:
            dept = subject['department']
            if dept not in odd_by_dept:
                odd_by_dept[dept] = []
            odd_by_dept[dept].append(subject)
        
        for subject in even_subjects:
            dept = subject['department']
            if dept not in even_by_dept:
                even_by_dept[dept] = []
            even_by_dept[dept].append(subject)
        
        # Find max subjects per department
        max_odd = max(len(subjs) for subjs in odd_by_dept.values()) if odd_by_dept else 0
        max_even = max(len(subjs) for subjs in even_by_dept.values()) if even_by_dept else 0
        
        print(f"\n📊 Simple Alternating Schedule:")
        print(f"   ODD subjects: {len(odd_subjects)} total, max {max_odd} per dept")
        print(f"   EVEN subjects: {len(even_subjects)} total, max {max_even} per dept")
        print(f"   Available dates: {len(available_dates)}")
        print(f"   Starting with: {semester_type} semester")
        
        # Initialize schedule
        schedule = []
        violations = []
        date_index = 0
        session = 'FN'  # Use same session throughout
        
        # Determine which semester to start with
        if semester_type == 'ODD':
            primary_subjects = odd_by_dept
            secondary_subjects = even_by_dept
            max_primary = max_odd
            max_secondary = max_even
            primary_sem = 'ODD'
            secondary_sem = 'EVEN'
        else:
            primary_subjects = even_by_dept
            secondary_subjects = odd_by_dept
            max_primary = max_even
            max_secondary = max_odd
            primary_sem = 'EVEN'
            secondary_sem = 'ODD'
        
        # Alternate between primary and secondary
        round_num = 0
        max_rounds = max(max_primary, max_secondary)
        
        while round_num < max_rounds and date_index < len(available_dates):
            # Schedule primary semester (e.g., ODD1, ODD2, ODD3...)
            if round_num < max_primary and date_index < len(available_dates):
                exam_date = available_dates[date_index]
                
                for dept, subjs in sorted(primary_subjects.items()):
                    if round_num < len(subjs):
                        subject = subjs[round_num]
                        schedule.append({
                            'subject_id': subject['subject_id'],
                            'subject_code': subject['subject_code'],
                            'subject_name': subject['subject_name'],
                            'department': dept,
                            'date': exam_date,
                            'session': session,
                            'subject_type': subject['subject_type'],
                            'student_count': subject['student_count'],
                            'semester_type': primary_sem
                        })
                
                date_index += 1
            
            # Schedule secondary semester (e.g., EVEN1, EVEN2, EVEN3...)
            if round_num < max_secondary and date_index < len(available_dates):
                exam_date = available_dates[date_index]
                
                for dept, subjs in sorted(secondary_subjects.items()):
                    if round_num < len(subjs):
                        subject = subjs[round_num]
                        schedule.append({
                            'subject_id': subject['subject_id'],
                            'subject_code': subject['subject_code'],
                            'subject_name': subject['subject_name'],
                            'department': dept,
                            'date': exam_date,
                            'session': session,
                            'subject_type': subject['subject_type'],
                            'student_count': subject['student_count'],
                            'semester_type': secondary_sem
                        })
                
                date_index += 1
            
            round_num += 1
        
        print(f"\n✅ Scheduled {len(schedule)} exams using {date_index} dates")
        print(f"   {primary_sem} exams: {len([s for s in schedule if s.get('semester_type') == primary_sem])}")
        print(f"   {secondary_sem} exams: {len([s for s in schedule if s.get('semester_type') == secondary_sem])}")
        
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
            INSERT INTO schedules 
            (cycle_id, subject_id, exam_date, session)
            VALUES (?, ?, ?, ?)
            ''', (cycle_id, item['subject_id'], item['date'], item['session']))
        
        # Insert violations
        for violation in violations:
            self.cursor.execute('''
            INSERT INTO schedule_violations
            (cycle_id, subject_id, violation_type, description, severity)
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
        ''', (exam_type, year, start_date, end_date, created_date, 'ACTIVE'))
        
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
