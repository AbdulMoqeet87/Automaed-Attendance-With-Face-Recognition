import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import API_URL from '../config';
import { SearchIcon, XIcon } from './Icons';
import './AttendanceHistory.css';

function AttendanceHistory() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterClass, setFilterClass] = useState('');
  const [filterDate, setFilterDate] = useState('');
  const [expandedRecord, setExpandedRecord] = useState(null);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      // add filters if they exist
      if (filterClass) params.class_name = filterClass;
      if (filterDate) params.date = filterDate;

      const response = await axios.get(`${API_URL}/api/attendance/history`, { params });
      setHistory(response.data);
    } catch (error) {
      console.error('Error fetching history:', error);
    }
    setLoading(false);
  }, [filterClass, filterDate]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  function handleFilter(e) {
    e.preventDefault();
    fetchHistory();
  }

  const clearFilters = () => {
    setFilterClass('');
    setFilterDate('');
    setTimeout(fetchHistory, 100); // small delay to let state update
  };

  // toggle showing details for a record
  function toggleRecord(index) {
    setExpandedRecord(expandedRecord === index ? null : index);
  }

  return (
    <div className="attendance-history">
      <div className="history-card">
        <h2>Attendance History</h2>
        <p className="subtitle">View and review past attendance records</p>

        <form className="filter-form" onSubmit={handleFilter}>
          <div className="filter-row">
            <input
              type="text"
              placeholder="Filter by class name"
              value={filterClass}
              onChange={(e) => setFilterClass(e.target.value)}
            />
            <input
              type="date"
              value={filterDate}
              onChange={(e) => setFilterDate(e.target.value)}
            />
            <button type="submit" className="btn btn-filter">
              <SearchIcon size={16} />
              <span style={{ marginLeft: '0.5rem' }}>Filter</span>
            </button>
            <button type="button" className="btn btn-clear" onClick={clearFilters}>
              <XIcon size={16} />
              <span style={{ marginLeft: '0.5rem' }}>Clear</span>
            </button>
          </div>
        </form>

        {loading ? (
          <div className="loading-state">
            <div className="spinner-small"></div>
            <p>Loading history...</p>
          </div>
        ) : history.length === 0 ? (
          <div className="empty-state">
            <p>No attendance records found</p>
            <p className="empty-hint">Submit attendance to see records here</p>
          </div>
        ) : (
          <div className="history-list">
            {history.map((record, index) => (
              <div key={index} className="history-item">
                <div className="history-header" onClick={() => toggleRecord(index)}>
                  <div className="history-info">
                    <h3>{record.class_name}</h3>
                    <p className="history-date">
                      {new Date(record.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <div className="history-stats">
                    <span className="stat present">{record.present?.length || 0} Present</span>
                    <span className="stat absent">{record.absent?.length || 0} Absent</span>
                    {record.unrecognized_count > 0 && (
                      <span className="stat unrecognized">? {record.unrecognized_count} Unknown</span>
                    )}
                  </div>
                  <span className="expand-icon">{expandedRecord === index ? '▲' : '▼'}</span>
                </div>

                {expandedRecord === index && (
                  <div className="history-details">
                    <div className="detail-section">
                      <h4 className="detail-title present-title">Present Students</h4>
                      {record.present && record.present.length > 0 ? (
                        <ul className="student-list">
                          {record.present.map((student, i) => (
                            <li key={i}>
                              {typeof student === 'string' ? student : `${student.student_id} - ${student.name}`}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="empty-list">No students marked present</p>
                      )}
                    </div>

                    <div className="detail-section">
                      <h4 className="detail-title absent-title">Absent Students</h4>
                      {record.absent && record.absent.length > 0 ? (
                        <ul className="student-list">
                          {record.absent.map((student, i) => (
                            <li key={i}>
                              {typeof student === 'string' ? student : `${student.student_id} - ${student.name}`}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="empty-list">All students present</p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default AttendanceHistory;
