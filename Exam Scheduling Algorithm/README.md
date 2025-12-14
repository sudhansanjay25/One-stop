# Exam Scheduling Algorithm

Automated exam timetable generation system with intelligent constraint handling for college examinations.

## Features

- **Two Exam Types**: Semester exams (3 hours) and Internal exams (1.5 hours)
- **Semester Selection**: Separate scheduling for odd and even semesters
- **Dual Session Support**: Automatic FN/AN session allocation for internal exams
- **Constraint-Based Scheduling**: Intelligent gap requirements between exams
- **Department-wise Scheduling**: Independent scheduling per department
- **Conflict Detection**: Prevents scheduling conflicts within departments
- **Weekend Management**: Excludes Sundays from scheduling (Saturdays included)
- **Professional PDF Export**: Automatic generation with institutional formatting
- **Matrix Display**: Compact matrix format for single-session schedules

## Exam Timings

### Internal Exams:
- **FN Session**: 9:00 AM - 10:30 AM
- **AN Session**: 2:00 PM - 3:30 PM
- **Smart Session Logic**: 
  - If available days < max subjects per department: Use both FN & AN sessions (2 exams/day)
  - If available days >= max subjects per department: Use only FN session (1 exam/day)
  - Minimum required days: (max subjects per department + 1) / 2

### Semester Exams:
- **FN Session**: 10:00 AM - 1:00 PM
- **AN Session**: 2:00 PM - 5:00 PM

## Database Schema

### Tables:
1. **students** - Student information by department and year
2. **subjects** - Subject details with classification (HEAVY/NONMAJOR) and semester type (ODD/EVEN)
3. **exam_cycles** - Exam scheduling sessions with metadata
4. **exam_schedule** - Generated timetables with session details
5. **holidays** - Holiday exclusions
6. **schedule_violations** - Constraint violation logs

## Gap Constraints

### Semester Exams:
- **Heavy subjects**: Minimum 1 full day gap
- **Non-major subjects**: Minimum half-day gap (different session or next day)
- **AN session rule**: If exam in AN, next exam must be AN (next day) or day after tomorrow

### Internal Exams:
- **One exam per department per day** (for FN-only schedules)
- **Two exams per department per day** (for FN+AN dual-session schedules)
- No gap constraints between internal exams

## Files Structure

- `db_setup.py` - Database initialization and mock data
- `config.py` - Configuration constants (timings, weekends, constraints)
- `scheduler.py` - Core scheduling algorithm with dual-session logic
- `main.py` - Interactive command-line interface
- `pdf_generator.py` - Professional PDF generation with ReportLab
- `exam_scheduling.db` - SQLite database

## Installation & Setup

### 1. Activate Virtual Environment
```bash
cd "c:\Users\Lenovo\Desktop\Project\One-Stop-Hackathon\ht\Scripts"
.\activate
cd "c:\Users\Lenovo\Desktop\Project\One-Stop-Hackathon\Exam Scheduling Algorithm"
```

### 2. Install Dependencies
```bash
pip install reportlab
```

### 3. Initialize Database
```bash
python db_setup.py
```

This creates the database with 38 subjects:
- 19 ODD semester subjects (across CSE, ECE, MECH)
- 19 EVEN semester subjects (across CSE, ECE, MECH)

## Usage

### Interactive Mode
```bash
python main.py
```

Follow the prompts:
1. Select exam type (Semester/Internal)
2. Select semester type (Odd/Even)
3. Choose year group (1-4)
4. Enter start date (DD.MM.YYYY)
5. Enter end date (DD.MM.YYYY)
6. Optionally specify holidays to exclude
7. Confirm and generate schedule

### Example Session
```
======================================================================
  EXAM SCHEDULING SYSTEM - Input Parameters
======================================================================

1. Select Exam Type:
   [1] Semester Exam
   [2] Internal Exam
   Enter choice (1/2): 2

2. Select Semester Type:
   [1] Odd Semester (1, 3, 5, 7)
   [2] Even Semester (2, 4, 6, 8)
   Enter choice (1/2): 2

3. Select Year Group:
   [1] First Year
   [2] Second Year
   [3] Third Year
   [4] Fourth Year
   Enter choice (1-4): 2

4. Enter Exam Period:
   Start Date (DD.MM.YYYY): 15.12.2025
   End Date (DD.MM.YYYY): 19.12.2025

5. Enter Holidays to Exclude: [Press Enter to skip]
```

## Algorithm Logic

### Phase 1: Date Preparation
- Generate available dates from user-specified range
- Exclude Sundays (weekend index 6)
- Exclude custom holidays
- Calculate total available days

### Phase 2: Subject Loading & Analysis
- Fetch subjects for selected year, exam type, and semester type (ODD/EVEN)
- Group subjects by department
- Calculate max subjects per department
- Determine if dual sessions needed (for internal exams)

### Phase 3: Session Assignment (Internal Exams)
- **Dual Session Logic**:
  - If `days < (max_subjects_per_dept + 1) / 2`: Error - insufficient dates
  - If `days < max_subjects_per_dept`: Use FN + AN sessions
  - If `days >= max_subjects_per_dept`: Use FN session only

### Phase 4: Scheduling Algorithm
- Assign subjects to earliest available dates
- Respect one-exam-per-department-per-day rule (single session)
- Respect two-exams-per-department-per-day rule (dual session)
- Validate gap constraints (semester exams only)
- Log violations when constraints cannot be satisfied
- Rotate through departments evenly

### Phase 5: Output Generation
- Save schedule to database with cycle ID
- Display formatted timetable:
  - **Matrix format** for single-session internal exams
  - **Dual matrix tables** (FN/AN) for dual-session internal exams
  - **List format** for semester exams
- Auto-generate professional PDF
- Report constraint violations (if any)

## Mock Data

### Departments: CSE, ECE, MECH

### EVEN Semester (Semester 2/4/6/8) - 19 Subjects:
**CSE (7 subjects)**:
- Microprocessors, Database Systems, Computer Networks, Theory of Computation
- Data Analytics, Database Lab, Design and Analysis of Algorithms

**ECE (6 subjects)**:
- Control Systems, Electromagnetic Theory, Digital Signal Processing
- VLSI Design, Embedded Systems, Communication Lab

**MECH (6 subjects)**:
- Manufacturing Processes, Heat Transfer, Mechanics of Materials
- Industrial Engineering, CAD/CAM, Manufacturing Lab

### ODD Semester (Semester 1/3/5/7) - 19 Subjects:
**CSE (7 subjects)**:
- Data Structures, Operating Systems, Discrete Mathematics
- Computer Organization, Software Engineering, Web Technologies, Programming Lab

**ECE (6 subjects)**:
- Signals and Systems, Digital Electronics, Electronic Devices
- Communication Systems, Microprocessors, Electronics Lab

**MECH (6 subjects)**:
- Thermodynamics, Fluid Mechanics, Machine Design
- Material Science, Engineering Drawing, Workshop Practice

### Students: 20 per department (60 total)

## PDF Output Formats

### Internal Exams - Matrix Format (Landscape A4)

#### Single Session (FN only):
- Departments in rows, dates in columns
- One table showing all exams
- Date headers: "15.12.2025\nMonday"
- Full subject names with automatic text wrapping

#### Dual Session (FN + AN):
- Two separate tables with yellow session headers
- **FN SESSION: 9:00 AM - 10:30 AM** (yellow background)
- **AN SESSION: 2:00 PM - 3:30 PM** (yellow background)
- Each table shows its respective session exams
- Complete schedule fits on one landscape page

### Semester Exams - List Format (Portrait A4)
- Department-wise sections
- Columns: Date, Session, Subject Code, Subject Name
- Tables kept together on pages when possible

### Common Features:
- Institutional header with college name
- Reference number and date
- Clean professional design with black borders
- Automatic filename: `exam_schedule_[type]_year[X]_[timestamp].pdf`

## Console Output Examples

### Dual Session Internal Exam:
```
📊 Scheduling Analysis:
   Available dates: 5
   Total subjects: 19
   Max subjects per department: 7
      CSE: 7 subjects
      ECE: 6 subjects
      MECH: 6 subjects
   ℹ️  Using both FN and AN sessions (2 exams per day)

======================================================================
  FN SESSION (9:00 AM - 10:30 AM)
======================================================================

Dept        15.12.2025     16.12.2025     17.12.2025     18.12.2025
/ Day         Monday         Tuesday       Wednesday      Thursday
----------------------------------------------------------------------
CSE        Microproce...  Database Lab   Computer N...  Theory of ...
ECE         VLSI Design   Communicat...  Electromag...        -
MECH       Industrial...  Manufactur...  Heat Transfer        -
----------------------------------------------------------------------

======================================================================
  AN SESSION (2:00 PM - 3:30 PM)
======================================================================

Dept           15.12.2025          16.12.2025          17.12.2025
/ Day            Monday             Tuesday            Wednesday
----------------------------------------------------------------------
CSE          Data Analytics     Database Systems   Design and Anal...
ECE         Embedded Systems    Control Systems    Digital Signal ...
MECH            CAD/CAM        Manufacturing P...  Mechanics of Ma...
----------------------------------------------------------------------
```

### Single Session Internal Exam:
```
📊 Scheduling Analysis:
   Available dates: 7
   Total subjects: 19
   Max subjects per department: 7
      CSE: 7 subjects
      ECE: 6 subjects
      MECH: 6 subjects
   ℹ️  Using only FN session (1 exam per day)

----------------------------------------------------------------------
Date            Session    Dept     Code       Subject
----------------------------------------------------------------------
15.12.2025      FN         CSE      CS310      Microprocessors
                FN         ECE      EC308      VLSI Design
                FN         MECH     ME308      Industrial Engineering
----------------------------------------------------------------------
```

## Key Technical Features

### ✅ Smart Session Allocation
- Automatically determines FN-only vs FN+AN based on available days
- Prevents scheduling errors with minimum day validation
- Distributes exams evenly across sessions

### ✅ Conflict-Free Scheduling
- One exam per department per day (single session)
- Two exams per department per day (dual session)
- No overlapping exams for same department students

### ✅ Professional PDF Generation
- Matrix tables for internal exams with proper cell wrapping
- Visible yellow headers for dual-session schedules
- Day names included in date headers
- Subject names (not codes) in internal exam PDFs
- Landscape orientation for better matrix display

### ✅ Flexible Date Management
- Sunday-only weekend exclusion
- Custom holiday support
- Automatic date range validation

### ✅ Enhanced User Experience
- Real-time scheduling analysis
- Clear error messages
- Constraint violation reporting
- Department-wise summaries

## Future Enhancements

- Web interface (Flask/Django)
- Room allocation based on capacity
- Invigilator duty roster generation
- Student hall ticket generation with QR codes
- Email/SMS notifications
- Calendar export (iCal format)
- Multi-year batch scheduling
- Common subject handling across departments
- Exam seating arrangement generation

## Requirements

- Python 3.7+
- SQLite3 (built-in)
- ReportLab library

## License

This project is part of the One-Stop-Hackathon submission for exam management system.
## License

This project is part of the One-Stop-Hackathon submission for exam management system.
