import React, { useState } from 'react';
import Papa from 'papaparse';
import axios from 'axios';
import './AttendanceResults.css';

function AttendanceResults({ data, onReset }) {
  const { present, absent, unrecognized, annotated_image, class_name, timestamp } = data;
  const [submitting, setSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState({ type: '', text: '' });

  const downloadCSV = () => {
    const csvData = [
      ['Class Name', class_name],
      ['Date & Time', new Date(timestamp).toLocaleString()],
      [''],
      ['Category', 'Student ID', 'Student Name', 'Status'],
      ...present.map(student => ['Present', student.student_id, student.name, 'Present']),
      ...absent.map(student => ['Absent', student.student_id, student.name, 'Absent']),
    ];

    const csv = Papa.unparse(csvData);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `attendance_${class_name}_${new Date(timestamp).toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const downloadAnnotatedImage = () => {
    const a = document.createElement('a');
    a.href = `data:image/jpeg;base64,${annotated_image}`;
    a.download = `annotated_${class_name}_${new Date(timestamp).toISOString().split('T')[0]}.jpg`;
    a.click();
  };

  const submitAttendance = async () => {
    setSubmitting(true);
    setSubmitMessage({ type: '', text: '' });

    try {
      const response = await axios.post('/api/attendance/submit', {
        class_name,
        timestamp,
        present: present.map(s => s.student_id),
        absent: absent.map(s => s.student_id),
        unrecognized_count: unrecognized.length
      });

      setSubmitMessage({ 
        type: 'success', 
        text: 'Attendance submitted successfully! Record saved to database.' 
      });
    } catch (error) {
      setSubmitMessage({ 
        type: 'error', 
        text: error.response?.data?.error || 'Failed to submit attendance' 
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="results-container">
      <div className="results-card">
        <div className="results-header">
          <h2>Attendance Results</h2>
          <p className="class-info">
            <strong>Class:</strong> {class_name} | <strong>Date:</strong> {new Date(timestamp).toLocaleString()}
          </p>
        </div>

        <div className="stats-grid">
          <div className="stat-card present-card">
            <div className="stat-number">{present.length}</div>
            <div className="stat-label">Present</div>
          </div>
          <div className="stat-card absent-card">
            <div className="stat-number">{absent.length}</div>
            <div className="stat-label">Absent</div>
          </div>
          <div className="stat-card unrecognized-card">
            <div className="stat-number">{unrecognized.length}</div>
            <div className="stat-label">Unrecognized</div>
          </div>
        </div>

        {annotated_image && (
          <div className="annotated-image-section">
            <h3>Annotated Classroom Image</h3>
            <img 
              src={`data:image/jpeg;base64,${annotated_image}`} 
              alt="Annotated classroom" 
              className="annotated-image"
            />
          </div>
        )}

        <div className="attendance-lists">
          <div className="list-section">
            <h3 className="list-title present-title">
              ✓ Present Students ({present.length})
            </h3>
            <div className="student-list">
              {present.length > 0 ? (
                present.map((student, index) => (
                  <div key={index} className="student-item present-item">
                    <span className="student-id">{student.student_id}</span>
                    <span className="student-name">{student.name}</span>
                    {student.confidence && (
                      <span className="confidence">
                        {(student.confidence * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>
                ))
              ) : (
                <p className="empty-list">No students marked present</p>
              )}
            </div>
          </div>

          <div className="list-section">
            <h3 className="list-title absent-title">
              ✗ Absent Students ({absent.length})
            </h3>
            <div className="student-list">
              {absent.length > 0 ? (
                absent.map((student, index) => (
                  <div key={index} className="student-item absent-item">
                    <span className="student-id">{student.student_id}</span>
                    <span className="student-name">{student.name}</span>
                  </div>
                ))
              ) : (
                <p className="empty-list">All students are present</p>
              )}
            </div>
          </div>

          {unrecognized.length > 0 && (
            <div className="list-section unrecognized-section">
              <h3 className="list-title unrecognized-title">
                ? Unrecognized Faces ({unrecognized.length})
              </h3>
              <div className="unrecognized-faces">
                {unrecognized.map((face, index) => (
                  <div key={index} className="face-card">
                    <img 
                      src={`data:image/jpeg;base64,${face}`} 
                      alt={`Unrecognized face ${index + 1}`}
                      className="face-thumbnail"
                    />
                    <p className="face-label">Face #{index + 1}</p>
                  </div>
                ))}
              </div>
              <p className="info-text">
                These faces were detected but not recognized. Please review and manually mark attendance if needed.
              </p>
            </div>
          )}
        </div>

        {submitMessage.text && (
          <div className={`submit-message ${submitMessage.type}`}>
            {submitMessage.text}
          </div>
        )}

        <div className="action-buttons">
          <button 
            className="btn btn-submit" 
            onClick={submitAttendance}
            disabled={submitting || submitMessage.type === 'success'}
          >
            {submitting ? '⏳ Submitting...' : submitMessage.type === 'success' ? '✓ Submitted' : '📤 Submit Attendance'}
          </button>
          <button className="btn btn-download" onClick={downloadCSV}>
            📥 Download CSV
          </button>
          <button className="btn btn-download" onClick={downloadAnnotatedImage}>
            📥 Download Image
          </button>
          <button className="btn btn-reset" onClick={onReset}>
            🔄 New Attendance
          </button>
        </div>
      </div>
    </div>
  );
}

export default AttendanceResults;
