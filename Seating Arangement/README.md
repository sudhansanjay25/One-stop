# Seating Arrangement Allocation System

Automated seating arrangement system for exam hall allocations with intelligent student distribution and faculty assignments.

**Institution:** Marri Laxman Reddy Institute of Technology, Hyderabad - 43

## Features

- **Multi-Year Support**: First to Fourth Year students
- **Dual Exam Modes**: 
  - Internal (CIA): 2 students per bench from different departments
  - Semester (SEM): 1 student per bench with FN/AN sessions
- **Smart Allocation**: Randomized seating with minimum 2 departments per hall
- **Output**: Student PDFs (visual layouts), Faculty PDFs (summary), Excel reports
- **Quality**: Empty hall filtering, text overflow prevention, capacity normalization (30-35 benches)

## Requirements

**Python:** 3.7+

**Libraries:**
```bash
pip install pandas numpy matplotlib reportlab openpyxl
```

## Installation

```bash
cd "C:\path\to\Seating Arangement"
pip install pandas numpy matplotlib reportlab openpyxl
```

**Required Files:**
- `halls.csv` - Hall information
- `Teachers.csv` - Faculty list
- `year1.csv` to `year4.csv` - Student data

## File Structure

```
Seating Arangement/
├── seating_allocation.py
├── halls.csv
├── Teachers.csv
├── year1.csv, year2.csv, year3.csv, year4.csv
└── Output/
    ├── seating_student_*.pdf
    ├── seating_faculty_*.pdf
    └── seating_allocation_report.xlsx
```

## CSV Formats

### halls.csv
```csv
hallno,capacity,Columns
1,30,4
2,32,5
```
- `hallno`: Hall number
- `capacity`: Benches (30-35 recommended)
- `Columns`: Bench columns (4-6)

### Student Files (year1.csv, etc.)
```csv
Register Number,Name,Department
23R11A0501,John Doe,CSE
23R11A0502,Jane Smith,ECE
```

### Teachers.csv
```csv
Name,Department
Dr. A. Kumar,CSE
Prof. B. Sharma,ECE
```

## Usage

### Interactive Mode
```bash
python seating_allocation.py
```

**Prompts:**
1. Year: 1-4
2. Exam Type: Internal or SEM
3. Internal Number: 1 or 2 (if Internal)
4. Session: FN or AN (if SEM)

### Programmatic Usage
```python
from seating_allocation import SeatingAllocationSystem

system = SeatingAllocationSystem(
    halls_file='halls.csv',
    students_file='year3.csv',
    teachers_file='Teachers.csv',
    session='FN',
    exam_type='Internal',
    year=3,
    internal_number=1
)

allocations = system.allocate_seats_mixed_department()
system.assign_teachers()
student_pdf = system.generate_student_pdf()
faculty_pdf = system.generate_faculty_pdf()
system.print_statistics()
```

## Exam Types

### Internal Assessment (CIA)
- **Capacity**: 2 students per bench (different departments)
- **Session**: Morning only
- **Features**: Randomized, anti-cheating measures
- **Naming**: `seating_student_YYYY-MM-DD_Y{year}_I{number}.pdf`

### Semester End (SEM)
- **Capacity**: 1 student per bench
- **Session**: FN (Forenoon) or AN (Afternoon)
- **Features**: Maximum spacing, department diversity
- **Naming**: `seating_student_YYYY-MM-DD_Y{year}_SEM_{FN/AN}.pdf`

## Output Files

### Student PDF
- Landscape A4
- Visual hall grid layout
- Internal: Split cells "Left | Right"
- SEM: Single student per cell
- Department distribution per hall

### Faculty PDF
- Portrait A4
- Overall statistics
- Hall allocation summary table
- Teacher assignments
- Department breakdown (format: "CSE:25, ECE:20")

### Excel Report (Optional)
- Complete Allocation sheet
- Hall Summary sheet
- Department Summary sheet
- Individual hall sheets
- Formatted with color-coded headers

## Allocation Algorithm

### SEM Flow
1. Group students by department
2. Shuffle within departments (seed=42)
3. Select department ensuring min 2 depts/hall
4. Assign student, increment pointer
5. Move to next hall if full

### Internal Flow
1. Group and shuffle by department
2. For each bench:
   - Assign student 1 (ensure dept diversity)
   - Assign student 2 (different department)
   - Same seat number for bench-mates
3. Move to next hall if capacity × 2 reached

## Configuration

### Capacity Normalization
```python
# Benches clamped to 30-35 range
# Internal: capacity ÷ 2 if >= 50
# SEM: capacity as-is
```

### Customization
```python
# Date format
self.generation_date = datetime.now().strftime('%d-%m-%Y')

# Seating patterns
# Edit _allocate_sem_linear() or _allocate_internal_alternating()

# PDF styling
table.set_fontsize(9)
table.scale(1, 2)
```

## Troubleshooting

### Common Issues

**"No subjects found for the given year"**
- Ensure year{X}.csv exists
- Verify column names: "Register Number", "Name", "Department"

**"Ran out of halls!"**
- Add more halls to halls.csv
- Increase hall capacities
- Reduce student count

**Register numbers lose leading zeros**
- System auto-formats as text in Excel
- Check `_format_excel()` if persists

**Text overflow in PDFs**
- Uses compact format: "CSE:25,ECE:20"
- Department column width: 3.4 inches

**Empty halls in PDF**
- System filters empty halls automatically
- Only non-empty halls included

### Statistics Output
```
ALLOCATION STATISTICS
Department-wise allocation:
  CSE  : 120 students (Halls 1 to 8)
  ECE  : 115 students (Halls 2 to 9)

Hall utilization:
  Hall 1: 30/30 seats (100.0% utilized)
  Hall 2: 32/32 seats (100.0% utilized)
```

## Key Features

- **Department Diversity**: Min 2 depts per hall
- **Randomization**: Reproducible (seed=42)
- **Capacity Management**: Internal (benches × 2), SEM (benches × 1)
- **Empty Filtering**: No blank pages in PDFs

## Version

**v1.0** - Production ready with dual exam support, randomization, and quality controls

---

**Last Updated:** December 13, 2025  
**Developed for:** Marri Laxman Reddy Institute of Technology
