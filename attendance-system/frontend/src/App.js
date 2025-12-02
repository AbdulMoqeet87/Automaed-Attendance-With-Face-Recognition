import React, { useState } from 'react';
import './App.css';
import ImageUpload from './components/ImageUpload';
import AttendanceResults from './components/AttendanceResults';
import StudentManagement from './components/StudentManagement';
import AttendanceHistory from './components/AttendanceHistory';

function App() {
  const [currentView, setCurrentView] = useState('attendance'); // 'attendance', 'manage', or 'history'
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
        <h1>AI-Powered Attendance Management System</h1>
        <p className="subtitle">Face Recognition Based Attendance</p>
        
        <nav className="nav-tabs">
          <button 
            className={`nav-tab ${currentView === 'attendance' ? 'active' : ''}`}
            onClick={() => {
              setCurrentView('attendance');
              handleReset();
            }}
          >
            📋 Take Attendance
          </button>
          <button 
            className={`nav-tab ${currentView === 'manage' ? 'active' : ''}`}
            onClick={() => {
              setCurrentView('manage');
              handleReset();
            }}
          >
            👤 Manage Students
          </button>
          <button 
            className={`nav-tab ${currentView === 'history' ? 'active' : ''}`}
            onClick={() => {
              setCurrentView('history');
              handleReset();
            }}
          >
            📊 View History
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
