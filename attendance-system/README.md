# AI-Powered Attendance Management System

An automated attendance management system using face recognition technology based on FaceNet and OpenCV.

## 👥 Team Members
- **Abdul Moqeet** (bscs22147)
- **Amna Amir** (bscs22059)

## 📋 Overview

This system automates classroom attendance using facial recognition technology. It detects and recognizes students in classroom images, generates attendance reports, and identifies unrecognized faces for manual review.

## 🏗️ Architecture

The system follows a **Layered Architecture** with four main modules:

1. **Presentation Module (Frontend)** - React-based UI for image upload and results display
2. **Application Module (Backend)** - Flask-based workflow coordinator
3. **Machine Learning Module** - FaceNet for face recognition, OpenCV for face detection
4. **Data Module** - MongoDB for data persistence

## ✨ Features

- ✅ Automated face detection and recognition using FaceNet
- ✅ Course enrollment system with 15 predefined CS courses
- ✅ Course-based attendance filtering (only enrolled students marked)
- ✅ Real-time attendance marking
- ✅ Generation of present/absent student lists
- ✅ Unrecognized faces detection for manual review
- ✅ Annotated classroom images with identified faces (green/orange boxes)
- ✅ CSV export of attendance records
- ✅ Attendance history tracking with filters
- ✅ Student management system with multi-image upload and course selection

## 🛠️ Technology Stack

### Frontend
- React 18.2.0
- Axios 1.6.0 for API calls
- PapaParse 5.4.1 for CSV generation

### Backend
- Flask 3.0.0
- OpenCV 4.12.0.88 for face detection
- TensorFlow 2.20.0 + Keras 3.12.0 + keras-facenet for FaceNet embeddings
- PyMongo 4.15.4 for MongoDB integration

## 📦 Installation & Setup

### Prerequisites
- **Python 3.8+** (Python 3.12 recommended)
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

4. **Install Python dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
   This installs:
   - Flask 3.0.0
   - opencv-python 4.12.0.88
   - tensorflow 2.20.0
   - keras-facenet (includes FaceNet model)
   - pymongo 4.15.4
   - python-dotenv 1.0.0

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

## 🚀 Usage

### 1. Register Students
1. Go to **"Manage Students"** tab
2. Enter student ID and name
3. **Select courses** the student is enrolled in (check all applicable courses)
4. Upload 2-3 clear face photos (different angles recommended)
5. Click **"Add Student"**
6. Wait for confirmation

### 2. Take Attendance
1. Go to **"Take Attendance"** tab
2. **Select course** from the dropdown (15 predefined CS courses available)
3. Upload classroom image
4. Click **"Process Attendance"**
5. View results:
   - **Green boxes** with roll numbers = Recognized students enrolled in the course
   - **Orange boxes** with "NO MATCH" = Unrecognized faces or students not enrolled
6. Click **"Submit Attendance"** to save to database

**Note**: Only students enrolled in the selected course will be marked present/absent. Students not enrolled in the course are ignored even if detected in the image.

### 3. View History
1. Go to **"View History"** tab
2. Filter by class name or date (optional)
3. Click on any record to expand details
4. View present/absent student lists with names

### 4. Export Data
- **CSV Export**: Click "Download CSV" button in results
- **Image Export**: Click "Download Annotated Image" button

---

## 📝 Important Notes

### Course Enrollment System
- **15 Predefined Courses**: CS101 to CS405 (Introduction to Programming, OOP, Data Structures, etc.)
- Students must be enrolled in a course to be marked present/absent in that course
- Multiple course enrollment supported - students can be enrolled in multiple courses
- Course-based filtering ensures accurate attendance for each class

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

**FaceNet model error:**
- keras-facenet will auto-download the model on first run
- Make sure you have sufficient disk space (~200MB)
- If C: drive is full, the model will be cached to `backend/ml_module/facenet_cache/`

**Frontend can't connect to backend:**
- Verify backend is running on port 5000
- Check `proxy` setting in `frontend/package.json` (should be `"proxy": "http://localhost:5000"`)

**Recognition not working:**
- Clear old student data: `python clear_database.py`
- Re-register all students with the current system
- Check threshold setting (default: 0.8 = 80% similarity)

---

## 📚 Project Structure

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

## 🤝 Contributing

This is an academic project for Software Engineering course at ITU.

---

## 📄 License

This project is created for educational purposes.

---

## 📧 Contact

For questions or issues, contact:
- Abdul Moqeet (bscs22147@itu.edu.pk)
- Amna Amir (bscs22059@itu.edu.pk)

---

**Developed with ❤️ by Abdul Moqeet & Amna Amir**
