"""
Configuration constants for Exam Scheduling System
"""

# Exam sessions
SEMESTER_SESSIONS = ['FN', 'AN']
INTERNAL_SESSIONS = ['FN', 'AN']  # Can use both sessions if needed

# Session timings
SESSION_TIMINGS = {
    'FN': '10:00 AM - 1:00 PM',
    'AN': '2:00 PM - 5:00 PM',
    'FN_INTERNAL': '9:00 AM - 10:30 AM',
    'AN_INTERNAL': '2:00 PM - 3:30 PM'
}

# Exam durations (in hours)
EXAM_DURATIONS = {
    'SEMESTER': 3.0,
    'INTERNAL': 1.5
}

# Subject types
SUBJECT_TYPES = {
    'HEAVY': 'Heavy/Major Subject',
    'NONMAJOR': 'Non-Major Subject'
}

# Gap requirements (in days)
GAP_REQUIREMENTS = {
    'HEAVY': 1,      # 1 full day gap after heavy subject
    'NONMAJOR': 0.5  # Half day gap (different session or next day)
}

# Violation severity levels
SEVERITY_LEVELS = {
    'LOW': 'Minor gap violation',
    'MEDIUM': 'Major gap violation', 
    'HIGH': 'Critical scheduling conflict'
}

# Exam types
EXAM_TYPES = ['SEMESTER', 'INTERNAL']

# Departments
DEPARTMENTS = ['CSE', 'ECE', 'MECH']

# Years
YEARS = [1, 2, 3, 4]

# Days of week (for weekend detection)
WEEKENDS = [6]  # Sunday only (0=Monday, 6=Sunday)

# Status values
STATUS_VALUES = {
    'PENDING': 'Schedule draft, not finalized',
    'COMPLETED': 'Schedule finalized and approved'
}
