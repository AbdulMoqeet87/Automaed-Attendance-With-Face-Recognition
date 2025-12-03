# AI-Powered Attendance Management System

An automated attendance management system using face recognition technology based on FaceNet and OpenCV.

## Team Members
- **Abdul Moqeet** (bscs22147)
- **Amna Amir** (bscs22059)

## Overview

This system automates classroom attendance using facial recognition technology. It detects and recognizes students in classroom images, generates attendance reports, and identifies unrecognized faces for manual review.

## Architecture

The system follows a **Layered Architecture** with four main modules:

1. **Presentation Module (Frontend)** - React-based UI for image upload and results display
2. **Application Module (Backend)** - Flask-based workflow coordinator
3. **Machine Learning Module** - FaceNet for face recognition, OpenCV for face detection
4. **Data Module** - MongoDB for data persistence

## Features

- Automated face detection and recognition using FaceNet
- Global student registration with degree year tracking
- Multi-course enrollment system
- Course-based attendance filtering (only enrolled students marked)
- Real-time attendance marking
- Generation of present/absent student lists
- Manual marking for unrecognized faces
- Annotated classroom images with identified faces (green/orange boxes)
- CSV export of attendance records
- Attendance history tracking with filters
- Student management system with multi-image upload

## Technology Stack

### Frontend
- React 18.2.0
- Axios 1.6.0 for API calls
- PapaParse 5.4.1 for CSV generation

### Backend
- Flask 3.0.0
- OpenCV 4.12.0.88 for face detection
- TensorFlow 2.20.0 + Keras 3.12.0 + keras-facenet for FaceNet embeddings
- PyMongo 4.15.4 for MongoDB integration

### Testing
- **Unit Testing** - Individual module testing for database operations, face recognition, and API endpoints
- **Integration Testing** - End-to-end workflow testing for attendance processing, student management, and course enrollment

## Installation & Setup

### Prerequisites
- **Python 3.10-3.12** (Python 3.12 recommended)
- **Node.js v16+** (for React frontend)
- **MongoDB** - Install locally OR use MongoDB Atlas (free cloud option)

---

## Step 1: MongoDB Setup

### Option A: MongoDB Atlas (Cloud - Recommended, FREE)
1. Go to https://www.mongodb.com/cloud/atlas/register
2. Create a free account
3. Create a **free M0 cluster** (takes 3-5 minutes)
4. Click **"Connect"** → **"Connect your application"**
5. Copy the connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)
6. Save it for Step 3

### Option B: Local MongoDB Installation
1. Download from: https://www.mongodb.com/try/download/community
2. Install MongoDB Community Server
3. Start MongoDB service:
   ```powershell
   # Windows (PowerShell as Administrator)
   net start MongoDB
   ```

---

## Step 2: Backend Setup

1. **Navigate to backend directory:**
   ```powershell
   cd backend
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate virtual environment:**
   ```powershell
   # Windows PowerShell
   venv\Scripts\activate
   
   # You should see (venv) before your prompt
   ```

4. **Upgrade pip and install dependencies:**
   ```powershell
   python -m pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```
   This installs:
   - Flask 3.0+
   - opencv-python 4.8+
   - tensorflow 2.15+
   - keras-facenet (includes FaceNet model)
   - pymongo 4.6+
   - numpy, Pillow, Werkzeug, and python-dotenv
   
   **Note:** The requirements.txt uses flexible versioning (>=) to automatically install compatible versions for your Python version.

5. **Configure MongoDB connection:**
   
   If using **MongoDB Atlas** (cloud):
   - Create `.env` file in backend folder:
     ```powershell
     echo MONGODB_URI=your_connection_string_here > .env
     ```
   - Replace `your_connection_string_here` with your Atlas connection string
   
   If using **Local MongoDB**:
   - No configuration needed (uses `mongodb://localhost:27017/` by default)

6. **Start the backend server:**
   ```powershell
   python app.py
   ```
   
   You should see:
   ```
   Loading FaceNet model...
   ✓ FaceNet model loaded successfully!
   ✓ Connected to MongoDB successfully!
   * Running on http://0.0.0.0:5000
   ```

---

## Step 3: Frontend Setup

1. **Open a NEW terminal** (keep backend running)

2. **Navigate to frontend directory:**
   ```powershell
   cd frontend
   ```

3. **Install Node.js dependencies:**
   ```powershell
   npm install
   ```
   This installs:
   - react 18.2.0
   - axios 1.6.0
   - papaparse 5.4.1

4. **Start the React development server:**
   ```powershell
   npm start
   ```
   
   The app will automatically open in your browser at: **http://localhost:3000**

---

## Usage Guide

### 1. Register Students
1. Navigate to the **"Manage Students"** tab
2. Enter the student ID, name, and select their degree starting year
3. Upload 2-3 clear face photos from different angles for better recognition accuracy
4. Click **"Add Student"** to register the student globally
5. The student is now registered and can be enrolled in courses

### 2. Enroll Students in Courses
1. Go to the **"Courses"** tab
2. Create a new course or select an existing course
3. Click **"Add Student"** on the course card
4. Filter students by degree year if needed
5. Select multiple students using checkboxes
6. Click **"Enroll Selected"** to add them to the course

### 3. Take Attendance
1. Navigate to the **"Take Attendance"** tab
2. Select the course from the dropdown menu
3. Upload a classroom image
4. Click **"Process Attendance"**
5. Review the results:
   - **Green boxes** with roll numbers indicate recognized students
   - **Orange boxes** with "NO MATCH" indicate unrecognized faces
6. Click on any unrecognized face to manually mark attendance by entering the student ID
7. Click **"Submit Attendance"** to save the record to the database

**Note**: Only students enrolled in the selected course will be marked present or absent. Students not enrolled in the course are ignored even if detected in the image.

### 4. View Attendance History
1. Go to the **"View History"** tab
2. Apply filters by course name or date if desired
3. Click on any record to expand and view details
4. Review present, absent, and manually marked student lists

### 5. Export Data
- **CSV Export**: Click the "Download CSV" button in attendance results
- **Image Export**: Click the "Download Annotated Image" button to save the processed image

---

## Important Notes

### Student and Course Management
- Students are registered globally with their degree starting year (e.g., 2022, 2023)
- After registration, students can be enrolled in multiple courses
- Only students enrolled in a specific course will be marked present/absent for that course
- Course-based filtering ensures accurate attendance tracking for each class
- Degree year filtering helps efficiently manage large student populations

### Face Recognition Accuracy
- **Threshold**: Currently set to 80% similarity (adjustable in `backend/ml_module/face_recognizer.py`)
- **Best Practices**:
  - Use clear, well-lit photos for registration
  - Register multiple images per student (2-3 from different angles)
  - Ensure classroom images are high quality

### Database Management
- **Clear all data**: Run `python clear_database.py` in backend folder
- **Check records**: Run `python check_attendance.py` in backend folder

### Troubleshooting

**Backend won't start:**
- Make sure virtual environment is activated: `venv\Scripts\activate`
- Check MongoDB is running (local) or connection string is correct (Atlas)
- Verify all dependencies installed: `pip install -r requirements.txt`
- If dependency issues persist, delete and recreate venv:
  ```powershell
  Remove-Item -Recurse -Force venv
  python -m venv venv
  venv\Scripts\activate
  python -m pip install --upgrade pip setuptools wheel
  pip install -r requirements.txt
  ```

**FaceNet model error:**
- keras-facenet will auto-download the model on first run
- Make sure you have sufficient disk space (~200MB)
- If C: drive is full, the model will be cached to `backend/ml_module/facenet_cache/`

**Python 3.12 compatibility issues:**
- If you encounter build errors with opencv-python or numpy, ensure pip/setuptools/wheel are up-to-date
- The requirements.txt uses flexible versioning to auto-select compatible versions
- For persistent issues, try installing packages individually: `pip install Flask flask-cors pymongo opencv-python numpy tensorflow`

**Frontend can't connect to backend:**
- Verify backend is running on port 5000
- Check `proxy` setting in `frontend/package.json` (should be `"proxy": "http://localhost:5000"`)

**Recognition not working:**
- Clear old student data: `python clear_database.py`
- Re-register all students with the current system
- Check threshold setting (default: 0.8 = 80% similarity)

---

## Project Structure

```
attendance-system/
├── backend/
│   ├── venv/                          # Virtual environment
│   ├── application_module/            # Business logic layer
│   │   └── attendance_controller.py
│   ├── ml_module/                     # Machine learning layer
│   │   ├── face_recognizer.py        # FaceNet + OpenCV
│   │   └── facenet_cache/            # Model cache folder
│   ├── data_module/                   # Data persistence layer
│   │   └── database.py               # MongoDB operations
│   ├── courses.py                    # 15 predefined CS courses
│   ├── app.py                        # Flask server entry point
│   ├── requirements.txt              # Python dependencies
│   ├── clear_database.py             # Utility to reset DB
│   └── .env                          # MongoDB connection string
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ImageUpload.js        # Attendance processing
    │   │   ├── AttendanceResults.js  # Results display
    │   │   ├── StudentManagement.js  # Student registration
    │   │   └── AttendanceHistory.js  # History viewer
    │   ├── App.js                    # Main application
    │   └── index.js                  # React entry point
    ├── package.json                  # Node.js dependencies
    └── public/                       # Static assets
```

---

## Contributing

This is an academic project developed for the Software Engineering course at Information Technology University (ITU).

---

## License

This project is created for educational purposes as part of academic coursework.

---

## Contact

For questions or issues regarding this project, please contact:
- Abdul Moqeet (bscs22147@itu.edu.pk)
- Amna Amir (bscs22059@itu.edu.pk)

---

**Developed by Abdul Moqeet and Amna Amir**
