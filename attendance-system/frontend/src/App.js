import React, { useState } from 'react';
import './App.css';
import ImageUpload from './components/ImageUpload';
import AttendanceResults from './components/AttendanceResults';
import StudentManagement from './components/StudentManagement';
import AttendanceHistory from './components/AttendanceHistory';
import Courses from './components/Courses';

function App() {
  const [currentView, setCurrentView] = useState('attendance'); // 'attendance', 'manage', 'history', or 'courses'
  const [attendanceData, setAttendanceData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAttendanceProcessed = (data) => {
    setAttendanceData(data);
    setLoading(false);
  };

  const handleLoadingStart = () => {
    setLoading(true);
  };

  const handleReset = () => {
    setAttendanceData(null);
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-title">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="header-icon">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
            <path d="M12 2v5"/>
            <path d="M12 17v5"/>
            <path d="M5 10l-3 3 3 3"/>
            <path d="M19 10l3 3-3 3"/>
          </svg>
          <div>
            <h1>AI-Powered Attendance Management System</h1>
            <p className="subtitle">Face Recognition Based Attendance</p>
          </div>
        </div>
        
        <nav className="nav-tabs">
          <button 
            className={`nav-tab ${currentView === 'attendance' ? 'active' : ''}`}
            onClick={() => {
              setCurrentView('attendance');
              handleReset();
            }}
          >
            Take Attendance
          </button>
          <button 
            className={`nav-tab ${currentView === 'courses' ? 'active' : ''}`}
            onClick={() => {
              setCurrentView('courses');
              handleReset();
            }}
          >
            Courses
          </button>
          <button 
            className={`nav-tab ${currentView === 'manage' ? 'active' : ''}`}
            onClick={() => {
              setCurrentView('manage');
              handleReset();
            }}
          >
            Manage Students
          </button>
          <button 
            className={`nav-tab ${currentView === 'history' ? 'active' : ''}`}
            onClick={() => {
              setCurrentView('history');
              handleReset();
            }}
          >
            View History
          </button>
        </nav>
      </header>

      <main className="App-main">
        {currentView === 'attendance' && (
          <>
            {!attendanceData && !loading && (
              <ImageUpload 
                onAttendanceProcessed={handleAttendanceProcessed}
                onLoadingStart={handleLoadingStart}
              />
            )}

            {loading && (
              <div className="loading-container">
                <div className="spinner"></div>
                <p>Processing attendance... Please wait</p>
              </div>
            )}

            {attendanceData && !loading && (
              <AttendanceResults 
                data={attendanceData}
                onReset={handleReset}
              />
            )}
          </>
        )}

        {currentView === 'manage' && (
          <StudentManagement />
        )}

        {currentView === 'courses' && (
          <Courses />
        )}

        {currentView === 'history' && (
          <AttendanceHistory />
        )}
      </main>

      <footer className="App-footer">
        <p>Developed by Abdul Moqeet (bscs22147) & Amna Amir (bscs22059)</p>
      </footer>
    </div>
  );
}

export default App;
