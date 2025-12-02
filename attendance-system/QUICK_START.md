# Quick Start Guide - Redesigned System

## 1. Clear Old Database (Required for Migration)

```bash
cd backend
python clear_database.py
# Type 'yes' when prompted
# Type 'y' to also delete attendance history (optional)
```

## 2. Start Backend Server

```bash
cd backend
python app.py
```

Backend will run on: `http://localhost:5000`

## 3. Start Frontend Server

```bash
cd frontend
npm start
```

Frontend will run on: `http://localhost:3000`

## 4. Create Your First Course

1. Open `http://localhost:3000` in your browser
2. Click the "📚 Courses" tab
3. Click "Create Course" button
4. Enter:
   - Course Code: `CS101`
   - Course Name: `Introduction to Programming`
5. Click "Create"

## 5. Add Students to Course

1. Click on the newly created course card (CS101)
2. Click "Add Student" button
3. Fill in the form:
   - Roll Number: `2021-CS-001`
   - Name: `John Doe`
   - Upload 2-5 images of the student's face (clear, front-facing)
4. Click "Add Student"
5. Repeat for more students

## 6. Take Attendance

1. Click "📋 Take Attendance" tab
2. Select course from dropdown: `CS101 - Introduction to Programming`
3. Upload a classroom image with student faces
4. Click "Process Attendance"
5. Wait for face recognition to complete

## 7. Review and Submit Attendance

### Recognized Students
- Green section shows automatically recognized students
- Each shows confidence percentage

### Unrecognized Faces
- Orange section shows faces that weren't recognized
- **Click on any face** to manually mark attendance
- Enter the student's roll number
- System validates the student exists in the course
- Manually marked students appear with a "Manual" badge

### Submit
1. Review all present/absent students
2. Manually mark any unrecognized students if needed
3. Click "📤 Submit Attendance"
4. Download CSV report if needed

## 8. View History

1. Click "📊 View History" tab
2. Select course and/or date to filter
3. View all past attendance records

## Features

### Dynamic Course Management
- Create unlimited courses
- No hardcoded course lists
- Each course tracks its own students

### Flexible Student Enrollment
- Students added directly to courses
- Same roll number can exist in different courses
- Easy to manage per-course enrollment

### Manual Attendance Marking
- Click unrecognized faces to identify
- Validates student exists in course
- Prevents duplicate marking
- Distinguishes manual vs automatic recognition

### Face Recognition
- FaceNet-based recognition
- 80% similarity threshold
- Supports 1-5 images per student
- Real-time detection and annotation

## Common Issues

### Port Already in Use
```bash
# Backend (kill process on port 5000)
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Frontend (kill process on port 3000)
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### MongoDB Connection Error
- Ensure MongoDB is running
- Check connection string in `.env` file
- Default: `mongodb://localhost:27017/attendance_db`

### CORS Errors
- Backend app.py already has CORS enabled
- Ensure backend is running on port 5000
- Check browser console for specific errors

### Face Not Detected
- Ensure image has clear, front-facing faces
- Good lighting conditions
- Minimum face size: 30x30 pixels
- Supported formats: JPEG, PNG

### Student Not Found (Manual Marking)
- Verify student exists in the selected course
- Check roll number matches exactly
- Case-sensitive matching

## Tips

### Best Face Images
- Clear, front-facing portraits
- Good lighting
- No sunglasses or masks
- Multiple angles help improve accuracy
- 2-5 images per student recommended

### Classroom Photos
- Well-lit environment
- Students facing camera
- Minimum resolution: 640x480
- Higher resolution = better detection

### Course Codes
- Use consistent naming: CS101, CS102, etc.
- Keep codes short and memorable
- Cannot be changed after creation

## System Architecture

```
Frontend (React)
    ↓
Backend (Flask REST API)
    ↓
Attendance Controller (Business Logic)
    ↓
├── Face Recognizer (FaceNet + OpenCV)
└── Database (MongoDB)
```

## Support

For issues or questions:
1. Check REDESIGN_SUMMARY.md for detailed changes
2. Check console logs (browser and terminal)
3. Verify MongoDB is running and accessible
4. Ensure all dependencies are installed
