# IMPORTANT: Schema Change Implementation Guide

## What Changed:

### OLD System:
- Students were created WITH a course_code
- Students belonged to ONE course only
- Same student_id could NOT exist in multiple courses

### NEW System:
- Students are created GLOBALLY (no course association)
- Students have: student_id, name, degree_year, face_embeddings
- Students can be enrolled in MULTIPLE courses
- New collection: `enrollments` links students to courses

## Database Schema:

```
students: {
  student_id: unique,
  name: string,
  degree_year: int (e.g., 2022),
  created_at: datetime
}

enrollments: {
  student_id: string,
  course_code: string,
  enrolled_at: datetime,
  unique: (student_id, course_code)
}

embeddings: {
  student_id: string,
  embeddings: [[float]],
  created_at: datetime
}
```

## Steps to Complete Implementation:

### 1. Clear Database (REQUIRED)
```bash
cd backend
python
>>> from data_module.database import Database
>>> db = Database()
>>> db.students_collection.drop()
>>> db.enrollments_collection.drop()
>>> db.embeddings_collection.drop()
>>> db.attendance_collection.drop()
>>> exit()
```

### 2. Update Frontend - StudentManagement.js
Replace the entire file content with the new version that:
- Removes course selection checkboxes
- Adds degree_year dropdown (2015-2025)
- Posts to `/api/students/add` with: student_id, name, degree_year, images

### 3. Update Frontend - Courses.js AddStudentModal
Instead of uploading images, it should:
- Fetch all students: GET `/api/students?degree_year=2022` (with year filter)
- Show list of students with name, roll no, degree year
- Allow filtering by degree year
- On select: POST `/api/courses/{course_code}/students` with {student_id}

## New API Endpoints:

```
GET  /api/students?degree_year=2022  - Get all students (optionally filtered)
POST /api/students/add                - Add new student (student_id, name, degree_year, images)
GET  /api/courses/{code}/students     - Get enrolled students in course
POST /api/courses/{code}/students     - Enroll existing student (student_id)
```

## Workflow:

1. **Manage Students Tab**: Add student with ID, name, year, images
2. **Courses Tab**: 
   - Create course
   - Click course → "Add Student"
   - Select from existing students (filter by year)
   - Enroll selected student
3. **Take Attendance**: Works same as before

## Files Modified:
✅ backend/data_module/database.py - Schema changed
✅ backend/application_module/attendance_controller.py - Updated methods
✅ backend/app.py - API endpoints updated
⚠️  frontend/src/components/StudentManagement.js - NEEDS MANUAL UPDATE
⚠️  frontend/src/components/Courses.js - AddStudentModal NEEDS COMPLETE REWRITE

## To Complete:
1. Replace StudentManagement.js content (remove course checkboxes, add year dropdown)
2. Rewrite AddStudentModal in Courses.js to show student list with year filter
3. Clear database
4. Test: Add student → Create course → Enroll student → Take attendance
