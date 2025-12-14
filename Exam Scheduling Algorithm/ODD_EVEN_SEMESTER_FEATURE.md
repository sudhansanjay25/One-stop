# Odd/Even Semester Feature Implementation

## Overview
The exam scheduling algorithm has been enhanced to support separate scheduling for odd and even semesters. This allows the system to schedule exams for odd semester subjects (1, 3, 5, 7) or even semester subjects (2, 4, 6, 8) independently.

## Changes Made

### 1. Database Schema Update (`db_setup.py`)
- **Added `semester_type` column** to the `subjects` table with values `'ODD'` or `'EVEN'`
- Updated table schema:
  ```python
  CREATE TABLE subjects (
      ...
      semester INTEGER NOT NULL,
      semester_type TEXT NOT NULL,  # NEW FIELD
      subject_type TEXT NOT NULL,
      ...
  )
  ```

### 2. Mock Data Enhancement (`db_setup.py`)
- Created **38 subjects** total (previously 22)
- **19 subjects for ODD semester** (Semester 3):
  - CSE: 7 subjects (4 HEAVY, 3 NONMAJOR including 1 INTERNAL)
  - ECE: 6 subjects (3 HEAVY, 3 NONMAJOR including 1 INTERNAL)
  - MECH: 6 subjects (3 HEAVY, 3 NONMAJOR including 1 INTERNAL)

- **19 subjects for EVEN semester** (Semester 4):
  - CSE: 7 subjects (4 HEAVY, 3 NONMAJOR including 1 INTERNAL)
  - ECE: 6 subjects (3 HEAVY, 3 NONMAJOR including 1 INTERNAL)
  - MECH: 6 subjects (3 HEAVY, 3 NONMAJOR including 1 INTERNAL)

### 3. User Interface Update (`main.py`)
- **Added semester type selection** prompt:
  ```
  2. Select Semester Type:
     [1] Odd Semester (1, 3, 5, 7)
     [2] Even Semester (2, 4, 6, 8)
  ```
- Updated function signature: `get_user_input()` now returns `semester_type`
- Display semester type in scheduling parameters summary

### 4. Scheduler Logic Update (`scheduler.py`)
- **Modified `get_subjects_for_year()`** method:
  - Added `semester_type` parameter
  - Updated SQL query to filter by `semester_type`
  - Returns subjects matching the selected semester type

- **Updated scheduling methods**:
  - `schedule_semester_exams()`: Now accepts `semester_type` parameter
  - `schedule_internal_exams()`: Now accepts `semester_type` parameter
  - Both methods call `get_subjects_for_year()` with semester type filter

### 5. Documentation Update (`README.md`)
- Added "Semester Selection" to features list
- Updated database schema description
- Modified usage instructions to include semester type selection
- Updated mock data section with odd/even semester breakdown
- Added example showing differences between odd and even semester subjects

## Testing Results

### Test 1: ODD Semester (Semester Exam)
```
Input:
- Exam Type: SEMESTER
- Semester Type: ODD
- Year Group: 2
- Date Range: 16.12.2025 - 27.12.2025

Result: ✅ Successfully scheduled 16 exams
Subjects included:
- CS301 (Data Structures), CS303 (Computer Organization), CS305 (Discrete Mathematics)
- EC301 (Signals and Systems), EC303 (Digital Electronics)
- ME301 (Thermodynamics), ME303 (Fluid Mechanics), ME305 (Machine Design)
```

### Test 2: EVEN Semester (Semester Exam)
```
Input:
- Exam Type: SEMESTER
- Semester Type: EVEN
- Year Group: 2
- Date Range: 16.12.2025 - 27.12.2025

Result: ✅ Successfully scheduled 16 exams
Subjects included:
- CS302 (Database Systems), CS304 (Computer Networks), CS306 (Design and Analysis of Algorithms)
- EC302 (Control Systems), EC304 (Electromagnetic Theory)
- ME302 (Manufacturing Processes), ME304 (Heat Transfer), ME306 (Mechanics of Materials)
```

### Test 3: ODD Semester (Internal Exam)
```
Input:
- Exam Type: INTERNAL
- Semester Type: ODD
- Year Group: 2
- Date Range: 16.12.2025 - 20.12.2025

Result: ✅ Successfully scheduled 12 exams
Note: System correctly identified insufficient dates for all subjects and warned user
```

## Key Differences Between Odd and Even Semester

### ODD Semester Subjects (Example - Year 2, CSE)
| Code  | Subject Name              | Type      |
|-------|---------------------------|-----------|
| CS301 | Data Structures           | HEAVY     |
| CS303 | Computer Organization     | HEAVY     |
| CS305 | Discrete Mathematics      | HEAVY     |
| CS307 | Operating Systems         | HEAVY     |
| CS309 | Software Engineering      | NONMAJOR  |
| CS311 | Web Technologies          | NONMAJOR  |
| CS313 | Computer Networks Lab     | NONMAJOR  |

### EVEN Semester Subjects (Example - Year 2, CSE)
| Code  | Subject Name                          | Type      |
|-------|---------------------------------------|-----------|
| CS302 | Database Systems                      | HEAVY     |
| CS304 | Computer Networks                     | HEAVY     |
| CS306 | Design and Analysis of Algorithms     | HEAVY     |
| CS308 | Theory of Computation                 | HEAVY     |
| CS310 | Microprocessors                       | NONMAJOR  |
| CS312 | Data Analytics                        | NONMAJOR  |
| CS314 | Database Lab                          | NONMAJOR  |

## Benefits

1. **Accurate Semester Management**: Schedules only relevant subjects for the current semester
2. **Reduced Confusion**: Clear separation between odd and even semester courses
3. **Realistic Workflow**: Matches actual college exam scheduling practices
4. **Flexible Scheduling**: Can schedule both semesters independently
5. **Better Resource Planning**: Accurate subject count for date range calculation

## Usage Example

```bash
# Activate virtual environment
cd "c:\Users\Lenovo\Desktop\Project\One-Stop-Hackathon\ht\Scripts"
.\activate

# Navigate to project
cd "c:\Users\Lenovo\Desktop\Project\One-Stop-Hackathon\Exam Scheduling Algorithm"

# Run the scheduler
python main.py

# Follow prompts:
# 1. Select Exam Type: 1 (Semester) or 2 (Internal)
# 2. Select Semester Type: 1 (Odd) or 2 (Even)  ← NEW STEP
# 3. Select Year Group: 1-4
# 4. Enter date range
# 5. Enter holidays (optional)
# 6. Confirm and generate schedule
```

## Files Modified

1. ✅ `db_setup.py` - Database schema and mock data
2. ✅ `main.py` - User input and display logic
3. ✅ `scheduler.py` - Core scheduling algorithm
4. ✅ `README.md` - Documentation

## Backward Compatibility

⚠️ **Breaking Change**: The database schema has changed. Existing databases need to be recreated:
```bash
python db_setup.py
```

This will drop existing tables and create new ones with the updated schema.

## Future Enhancements

- Support for cross-semester common subjects
- Automatic semester detection based on current date
- Semester-wise academic calendar integration
- Subject prerequisite tracking across semesters
