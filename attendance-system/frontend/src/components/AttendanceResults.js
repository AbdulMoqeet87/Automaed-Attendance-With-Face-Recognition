import React, { useState, useRef } from 'react';
import Papa from 'papaparse';
import axios from 'axios';
import { SendIcon, DownloadIcon, ImageIcon, RefreshIcon } from './Icons';
import './AttendanceResults.css';

function AttendanceResults({ data, onReset }) {
  const { present, absent, unrecognized, annotated_image, class_name, timestamp } = data;
  const [submitting, setSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState({ type: '', text: '' });
  const [manuallyMarked, setManuallyMarked] = useState([]);
  const [markedFaceIndexes, setMarkedFaceIndexes] = useState([]); // Track which unrecognized faces have been marked
  const [showManualMarkModal, setShowManualMarkModal] = useState(false);
  const [selectedFaceIndex, setSelectedFaceIndex] = useState(null);
  const [manualRollNo, setManualRollNo] = useState('');
  const [modalError, setModalError] = useState('');
  const isSubmittingRef = useRef(false); // Use ref to track submission across renders

  const downloadCSV = () => {
    const csvData = [
      ['Class Name', class_name],
      ['Date & Time', new Date(timestamp).toLocaleString()],
      [''],
      ['Student ID', 'Student Name', 'Status'],
      ...present.map(student => [student.student_id, student.name, 'Present (Auto)']),
      ...manuallyMarked.map(student => [student.student_id, student.name, 'Present (Manual)']),
      ...absent.filter(student => !manuallyMarked.some(m => m.student_id === student.student_id)).map(student => [student.student_id, student.name, 'Absent']),
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
    // Prevent double submission using ref
    if (isSubmittingRef.current || submitting || submitMessage.type === 'success') {
      console.log('Submission blocked - already in progress or completed');
      return;
    }

    isSubmittingRef.current = true;
    setSubmitting(true);
    setSubmitMessage({ type: '', text: '' });

    try {
      // Combine auto-detected present and manually marked students
      const allPresentIds = [
        ...present.map(s => s.student_id),
        ...manuallyMarked.map(m => m.student_id)
      ];

      // Filter out manually marked students from absent list
      const actualAbsentIds = absent
        .filter(s => !manuallyMarked.some(m => m.student_id === s.student_id))
        .map(s => s.student_id);

      console.log('Submitting attendance once...');
      const response = await axios.post('http://localhost:5000/api/attendance/submit', {
        class_name,
        timestamp,
        present: allPresentIds,
        absent: actualAbsentIds,
        unrecognized_count: unrecognized.length - markedFaceIndexes.length
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
      isSubmittingRef.current = false; // Reset ref on error to allow retry
    } finally {
      setSubmitting(false);
    }
  };

  const handleFaceClick = (index) => {
    setSelectedFaceIndex(index);
    setShowManualMarkModal(true);
    setManualRollNo('');
    setModalError('');
  };

  const handleManualMark = async () => {
    if (!manualRollNo.trim()) {
      setModalError('Please enter a roll number');
      return;
    }

    try {
      // Fetch students in this course to validate
      const response = await axios.get(`http://localhost:5000/api/courses/${class_name}/students`);
      const students = response.data;
      
      const student = students.find(s => s.student_id === manualRollNo.trim());
      
      if (!student) {
        setModalError(`Student with roll number ${manualRollNo} not found in this course`);
        return;
      }

      // Check if already marked (either in present or manually_marked)
      const alreadyPresent = present.some(s => s.student_id === student.student_id);
      const alreadyManual = manuallyMarked.some(m => m.student_id === student.student_id);
      
      if (alreadyPresent || alreadyManual) {
        setModalError('This student is already marked present');
        return;
      }

      // Add to manually marked list
      setManuallyMarked([...manuallyMarked, {
        student_id: student.student_id,
        name: student.name,
        marked_manually: true
      }]);

      // Mark this face index as processed so it won't be displayed anymore
      setMarkedFaceIndexes([...markedFaceIndexes, selectedFaceIndex]);

      // Close modal
      setShowManualMarkModal(false);
      setModalError('');
    } catch (error) {
      setModalError('Failed to validate student: ' + (error.response?.data?.error || error.message));
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
            <div className="stat-number">{present.length + manuallyMarked.length}</div>
            <div className="stat-label">Present</div>
          </div>
          <div className="stat-card absent-card">
            <div className="stat-number">{absent.length - manuallyMarked.length}</div>
            <div className="stat-label">Absent</div>
          </div>
          <div className="stat-card unrecognized-card">
            <div className="stat-number">{unrecognized.length - markedFaceIndexes.length}</div>
            <div className="stat-label">Unrecognized</div>
          </div>
        </div>

        {annotated_image && (
          <div className="annotated-image-section">
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
              Present Students ({present.length + manuallyMarked.length})
            </h3>
            <div className="student-list">
              {present.length > 0 || manuallyMarked.length > 0 ? (
                <>
                  {present.map((student, index) => (
                    <div key={index} className="student-item present-item">
                      <span className="student-id">{student.student_id}</span>
                      <span className="student-name">{student.name}</span>
                      {student.confidence && (
                        <span className="confidence">
                          {(student.confidence * 100).toFixed(1)}%
                        </span>
                      )}
                    </div>
                  ))}
                  {manuallyMarked.map((student, index) => (
                    <div key={`manual-${index}`} className="student-item present-item manual-mark">
                      <span className="student-id">{student.student_id}</span>
                      <span className="student-name">{student.name}</span>
                      <span className="manual-badge">Manual</span>
                    </div>
                  ))}
                </>
              ) : (
                <p className="empty-list">No students marked present</p>
              )}
            </div>
          </div>

          <div className="list-section">
            <h3 className="list-title absent-title">
              Absent Students ({absent.length - manuallyMarked.length})
            </h3>
            <div className="student-list">
              {absent.filter(student => !manuallyMarked.some(m => m.student_id === student.student_id)).length > 0 ? (
                absent
                  .filter(student => !manuallyMarked.some(m => m.student_id === student.student_id))
                  .map((student, index) => (
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

          {unrecognized.filter((_, index) => !markedFaceIndexes.includes(index)).length > 0 && (
            <div className="list-section unrecognized-section">
              <h3 className="list-title unrecognized-title">
                ? Unrecognized Faces ({unrecognized.length - markedFaceIndexes.length})
              </h3>
              <div className="unrecognized-faces">
                {unrecognized.map((face, index) => (
                  !markedFaceIndexes.includes(index) && (
                    <div 
                      key={index} 
                      className="face-card clickable"
                      onClick={() => handleFaceClick(index)}
                    >
                      <img 
                        src={`data:image/jpeg;base64,${face}`} 
                        alt={`Unrecognized face ${index + 1}`}
                        className="face-thumbnail"
                      />
                      <p className="face-label">Face #{index + 1}</p>
                      <p className="click-hint">Click to mark manually</p>
                    </div>
                  )
                ))}
              </div>
              <p className="info-text">
                Click on any unrecognized face to manually mark attendance by entering the student's roll number.
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
            <SendIcon size={18} />
            <span style={{ marginLeft: '0.5rem' }}>
              {submitting ? 'Submitting...' : submitMessage.type === 'success' ? 'Submitted' : 'Submit Attendance'}
            </span>
          </button>
          <button className="btn btn-download" onClick={downloadCSV}>
            <DownloadIcon size={18} />
            <span style={{ marginLeft: '0.5rem' }}>Download CSV</span>
          </button>
          <button className="btn btn-download" onClick={downloadAnnotatedImage}>
            <ImageIcon size={18} />
            <span style={{ marginLeft: '0.5rem' }}>Download Image</span>
          </button>
          <button className="btn btn-reset" onClick={onReset}>
            <RefreshIcon size={18} />
            <span style={{ marginLeft: '0.5rem' }}>New Attendance</span>
          </button>
        </div>
      </div>

      {/* Manual Mark Modal */}
      {showManualMarkModal && (
        <div className="modal-overlay" onClick={() => setShowManualMarkModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Manually Mark Attendance</h3>
            {selectedFaceIndex !== null && (
              <div className="modal-face-preview">
                <img 
                  src={`data:image/jpeg;base64,${unrecognized[selectedFaceIndex]}`} 
                  alt="Selected face"
                  className="modal-face-image"
                />
              </div>
            )}
            <div className="form-group">
              <label>Enter Student Roll Number:</label>
              <input
                type="text"
                value={manualRollNo}
                onChange={(e) => setManualRollNo(e.target.value)}
                placeholder="e.g., 2021-CS-123"
                autoFocus
              />
            </div>
            {modalError && <div className="modal-error">{modalError}</div>}
            <div className="modal-buttons">
              <button className="btn-modal-submit" onClick={handleManualMark}>
                Mark Present
              </button>
              <button className="btn-modal-cancel" onClick={() => setShowManualMarkModal(false)}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AttendanceResults;
