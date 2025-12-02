# System Redesign - Course-Centric Architecture

## Overview
The attendance system has been completely redesigned from a student-centric to a course-centric architecture. Students are now added directly to courses, and attendance is tracked per course.

## Major Changes

### 1. Database Schema Changes

#### Before:
```python
students: {
    student_id: str,
    name: str,
    enrolled_courses: [str]  # Array of course codes
}

courses: Hardcoded in courses.py (15 predefined courses)
```

#### After:
```python
students: {
    student_id: str,
    name: str,
    course_code: str  # Single course code
}
# Composite unique index: (course_code, student_id)
# Same roll number can exist in different courses

courses: {
    course_code: str (unique),
    course_name: str,
    created_at: datetime
}

embeddings: {
    student_id: str,
    embedding: array,
    course_code: str  # Added to associate with course
}
```

### 2. Backend Changes

#### database.py
- **Added**: `courses_collection` 
- **Modified**: `add_student()` - now accepts `course_code` instead of `enrolled_courses`
- **Modified**: `get_all_embeddings()` - now accepts optional `course_code` filter
- **Added**: New methods:
  - `create_course(course_code, course_name)`
  - `get_all_courses()`
  - `get_course_by_code(course_code)`
  - `get_students_in_course(course_code)`
  - `delete_course(course_code)`

#### app.py
- **Modified**: `/api/courses` - Now supports both GET and POST
  - GET: List all courses
  - POST: Create new course with `course_code` and `course_name`
- **Added**: `/api/courses/<course_code>/students` - Get students in a course
- **Modified**: `/api/students/add` - Now requires `course_code` instead of `enrolled_courses`
- **Modified**: `/api/process-attendance` - Changed parameter from `class_name` to `course_code`

#### attendance_controller.py
- **Modified**: `process_attendance(image_path, course_code)` - Filters by course_code
- **Modified**: `add_student()` - Requires `course_code` parameter
- **Modified**: `submit_attendance()` - Now saves `manually_marked` array
- **Added**: New methods:
  - `create_course(course_code, course_name)`
  - `get_all_courses()`
  - `get_course_by_code(course_code)`
  - `get_students_in_course(course_code)`

### 3. Frontend Changes

#### New Components

**Courses.js** - Main course management component
- Lists all courses in a grid
- Click course to view enrolled students
- Create Course button opens modal for adding new courses
- Add Student button in course detail view
- Integrated AddStudentModal for adding students to courses

**AddStudentModal** (inside Courses.js)
- Form with roll number, name, and image upload
- Validates student doesn't already exist in course
- Supports up to 5 images per student
- Shows image previews before upload

#### Modified Components

**App.js**
- Added new "Courses" tab in navigation
- Routes to Courses component

**ImageUpload.js**
- Changed API endpoint from `/api/courses` to `http://localhost:5000/api/courses`
- Changed form field from `class_name` to `course_code`
- Updated course mapping to use `course.course_code` and `course.course_name`

**AttendanceResults.js**
- Added manual marking feature for unrecognized faces
- Unrecognized face cards are now clickable
- Click opens modal to enter roll number
- Validates student exists in course before marking
- Displays manually marked students with "Manual" badge
- Updates present/absent counts to include manual marks
- Sends `manually_marked` array when submitting attendance

**AttendanceResults.css**
- Added styles for manual marking features:
  - `.manual-mark` - Background color for manually marked students
  - `.manual-badge` - Badge to indicate manual marking
  - `.face-card.clickable` - Hover effects for clickable faces
  - `.click-hint` - Hint text on unrecognized faces
  - Modal styles for manual marking form

### 4. Workflow Changes

#### Old Workflow:
1. Create student with name and roll number
2. Select multiple courses from checkboxes
3. Upload face images
4. Take attendance - system filters by enrolled courses

#### New Workflow:
1. Create a course (e.g., CS101 - Programming Fundamentals)
2. Navigate to the course
3. Click "Add Student" in course view
4. Enter student details and upload images
5. Student is added to that specific course only
6. Take attendance by selecting course from dropdown
7. Click unrecognized faces to manually mark attendance

### 5. Key Features

#### Dynamic Course Creation
- Courses are no longer hardcoded
- Admins can create courses with code and name
- Courses stored in MongoDB

#### Course-Centric Student Management
- Students belong to specific courses
- Same student ID can exist in multiple courses
- View all students in a course from course detail page

#### Manual Attendance Marking
- Unrecognized faces can be manually identified
- Click face → enter roll number → validate → mark present
- Manual marks distinguished with badge
- Included in final attendance submission

### 6. Database Migration

To migrate from old to new schema:

```bash
cd backend
python clear_database.py
# Type 'yes' to confirm
# Answer 'y' to delete attendance records (optional)
```

This will:
- Delete all students with old schema
- Delete all embeddings
- Delete all courses
- Optionally delete attendance history

After clearing:
1. Start the application
2. Go to "Courses" tab
3. Create your courses
4. Add students to each course
5. Register student faces
6. Take attendance

### 7. API Changes Summary

| Endpoint | Method | Old Params | New Params |
|----------|--------|------------|------------|
| `/api/courses` | GET | - | - (returns dynamic courses) |
| `/api/courses` | POST | N/A | `course_code`, `course_name` |
| `/api/courses/<code>/students` | GET | N/A | - |
| `/api/students/add` | POST | `enrolled_courses` | `course_code` |
| `/api/process-attendance` | POST | `class_name` | `course_code` |
| `/api/attendance/submit` | POST | - | Added `manually_marked` array |

### 8. Testing Checklist

- [ ] Clear old database data
- [ ] Start backend server
- [ ] Start frontend server
- [ ] Create a test course (e.g., CS101)
- [ ] Add 2-3 students to the course with images
- [ ] Take attendance for the course
- [ ] Verify face recognition works
- [ ] Test manual marking on unrecognized face
- [ ] Submit attendance
- [ ] Check attendance history
- [ ] Verify data saved correctly in MongoDB

## Files Changed

### Backend
- `backend/data_module/database.py` - Schema and methods updated
- `backend/app.py` - API endpoints modified
- `backend/application_module/attendance_controller.py` - Business logic updated
- `backend/clear_database.py` - Updated to clear courses collection

### Frontend
- `frontend/src/App.js` - Added Courses tab
- `frontend/src/components/Courses.js` - NEW: Course management
- `frontend/src/components/Courses.css` - NEW: Styles
- `frontend/src/components/ImageUpload.js` - Updated API calls
- `frontend/src/components/AttendanceResults.js` - Added manual marking
- `frontend/src/components/AttendanceResults.css` - Added manual marking styles

### Obsolete Files
- `backend/courses.py` - No longer used (courses now in database)

## Notes

- StudentManagement component still exists but may need removal/redesign
- All attendance history will use `class_name` field (which now contains course_code)
- Face recognition threshold and ML logic remain unchanged
- Manual marking validation prevents duplicate marking
- Course codes should be unique (enforced at database level)
