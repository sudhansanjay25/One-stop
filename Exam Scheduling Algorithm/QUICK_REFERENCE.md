# Quick Reference Guide: Odd/Even Semester Feature

## 🚀 Quick Start

```bash
# 1. Activate environment
cd "c:\Users\Lenovo\Desktop\Project\One-Stop-Hackathon\ht\Scripts"
.\activate

# 2. Navigate to project
cd "c:\Users\Lenovo\Desktop\Project\One-Stop-Hackathon\Exam Scheduling Algorithm"

# 3. Setup database (first time only)
python db_setup.py

# 4. Run scheduler
python main.py
```

## 📋 Input Flow

```
┌─────────────────────────────────────────────────────┐
│  STEP 1: Select Exam Type                          │
│  ─────────────────────────────                      │
│  [1] Semester Exam (3 hours)                        │
│  [2] Internal Exam (1.5 hours)                      │
└─────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  STEP 2: Select Semester Type ⭐ NEW               │
│  ─────────────────────────────                      │
│  [1] Odd Semester (1, 3, 5, 7)                      │
│  [2] Even Semester (2, 4, 6, 8)                     │
└─────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  STEP 3: Select Year Group                          │
│  ─────────────────────────────                      │
│  [1] First Year                                      │
│  [2] Second Year                                     │
│  [3] Third Year                                      │
│  [4] Fourth Year                                     │
└─────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  STEP 4: Enter Date Range                           │
│  ─────────────────────────────                      │
│  Start Date: DD.MM.YYYY                             │
│  End Date: DD.MM.YYYY                               │
└─────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  STEP 5: Enter Holidays (Optional)                  │
│  ─────────────────────────────────                  │
│  Format: 20.12.2025, 25.12.2025                     │
└─────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  STEP 6: Confirm and Generate                       │
│  ─────────────────────────────────                  │
│  Proceed with scheduling? (y/n)                     │
└─────────────────────────────────────────────────────┘
```

## 🎯 Example Scenarios

### Scenario 1: ODD Semester - Final Exams
```
Exam Type: [1] Semester Exam
Semester: [1] Odd
Year: [2] Second Year
Dates: 16.12.2025 - 27.12.2025
Holidays: (none)

Result:
✅ 16 exams scheduled
📄 PDF: exam_schedule_semester_year2_YYYYMMDD_HHMMSS.pdf
📊 Subjects: CS301, CS303, CS305, CS307, CS309, CS311 (CSE)
            EC301, EC303, EC305, EC307, EC309 (ECE)
            ME301, ME303, ME305, ME307, ME309 (MECH)
```

### Scenario 2: EVEN Semester - Final Exams
```
Exam Type: [1] Semester Exam
Semester: [2] Even
Year: [2] Second Year
Dates: 16.12.2025 - 27.12.2025
Holidays: (none)

Result:
✅ 16 exams scheduled
📄 PDF: exam_schedule_semester_year2_YYYYMMDD_HHMMSS.pdf
📊 Subjects: CS302, CS304, CS306, CS308, CS310, CS312 (CSE)
            EC302, EC304, EC306, EC308, EC310 (ECE)
            ME302, ME304, ME306, ME308, ME310 (MECH)
```

### Scenario 3: ODD Semester - Internal Exams
```
Exam Type: [2] Internal Exam
Semester: [1] Odd
Year: [2] Second Year
Dates: 16.12.2025 - 19.12.2025
Holidays: (none)

Result:
✅ 12 exams scheduled (need more dates for remaining)
📄 PDF: exam_schedule_internal_year2_YYYYMMDD_HHMMSS.pdf
⚠️  Warning: Insufficient dates for all subjects
```

## 📊 Subject Distribution

### ODD Semester (Semester 3)
```
┌──────────┬────────┬─────────────┬───────────┐
│   Dept   │ HEAVY  │  NONMAJOR   │   Total   │
├──────────┼────────┼─────────────┼───────────┤
│   CSE    │   4    │      2      │     6     │
│   ECE    │   3    │      2      │     5     │
│   MECH   │   3    │      2      │     5     │
├──────────┼────────┼─────────────┼───────────┤
│  TOTAL   │  10    │      6      │    16     │
└──────────┴────────┴─────────────┴───────────┘
```

### EVEN Semester (Semester 4)
```
┌──────────┬────────┬─────────────┬───────────┐
│   Dept   │ HEAVY  │  NONMAJOR   │   Total   │
├──────────┼────────┼─────────────┼───────────┤
│   CSE    │   4    │      2      │     6     │
│   ECE    │   3    │      2      │     5     │
│   MECH   │   3    │      2      │     5     │
├──────────┼────────┼─────────────┼───────────┤
│  TOTAL   │  10    │      6      │    16     │
└──────────┴────────┴─────────────┴───────────┘
```

## 🔧 Utility Scripts

### Verify Data
```bash
python verify_semester_data.py
```
**Shows:** Complete list of odd/even semester subjects

### View Demo
```bash
python demo_odd_even_feature.py
```
**Shows:** Feature overview and usage examples

## 📁 Generated Files

### After Setup (db_setup.py)
- ✅ `exam_scheduling.db` - SQLite database with 38 subjects

### After Scheduling (main.py)
- ✅ PDF file: `exam_schedule_[type]_year[X]_[timestamp].pdf`
- ✅ Database entries in exam_schedule table
- ✅ Violation logs (if any) in schedule_violations table

## 🎨 Output Formats

### Semester Exams (Portrait PDF)
```
┌──────────────────────────────────────────┐
│        INSTITUTION NAME                   │
│    SEMESTER EXAM SCHEDULE - Year 2        │
├────────┬─────────┬──────┬────────┬───────┤
│  Date  │ Session │ Dept │  Code  │Subject│
├────────┼─────────┼──────┼────────┼───────┤
│16.12   │   FN    │ CSE  │ CS309  │Soft..│
│        │         │ ECE  │ EC307  │Comm..│
│        │         │MECH  │ ME307  │Mate..│
└────────┴─────────┴──────┴────────┴───────┘
```

### Internal Exams (Landscape PDF)
```
┌─────────────────────────────────────────────────┐
│     INTERNAL EXAM SCHEDULE - Year 2             │
├──────┬─────────┬─────────┬─────────┬──────────┤
│ Dept │ 16.12   │ 17.12   │ 18.12   │  19.12   │
├──────┼─────────┼─────────┼─────────┼──────────┤
│ CSE  │ CS309   │ CS311   │ CS313   │  CS301   │
│ ECE  │ EC307   │ EC309   │ EC311   │  EC301   │
│MECH  │ ME307   │ ME309   │ ME311   │  ME301   │
└──────┴─────────┴─────────┴─────────┴──────────┘
```

## ⚠️ Common Issues

### Issue 1: "No subjects found"
**Cause:** Wrong semester type selected
**Solution:** Verify mock data has subjects for selected semester

### Issue 2: "Insufficient dates"
**Cause:** Date range too short
**Solution:** Extend end date or reduce number of holidays

### Issue 3: Database error
**Cause:** Old database schema
**Solution:** Run `python db_setup.py` to recreate database

## 📚 Documentation Files

- `README.md` - Main documentation
- `ODD_EVEN_SEMESTER_FEATURE.md` - Feature details
- `IMPLEMENTATION_SUMMARY.md` - Complete summary
- `QUICK_REFERENCE.md` - This guide

## ✅ Checklist for New Users

- [ ] Activate virtual environment
- [ ] Run `python db_setup.py`
- [ ] Verify database created: `exam_scheduling.db`
- [ ] Run `python verify_semester_data.py` to check data
- [ ] Run `python main.py` to generate schedule
- [ ] Check generated PDF file
- [ ] Review console output for violations

## 🎓 Understanding Semesters

**Odd Semesters:** 1, 3, 5, 7
- Usually run: July - November
- Academic year start

**Even Semesters:** 2, 4, 6, 8
- Usually run: December - April
- Academic year end

---

**Quick Help:** Run `python demo_odd_even_feature.py` for detailed overview
