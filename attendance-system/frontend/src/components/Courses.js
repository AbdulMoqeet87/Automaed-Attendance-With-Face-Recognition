import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PlusIcon, UserIcon, ArrowLeftIcon } from './Icons';
import './Courses.css';

const Courses = () => {
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showAddStudentModal, setShowAddStudentModal] = useState(false);
  const [newCourse, setNewCourse] = useState({ course_code: '', course_name: '' });

  // Fetch all courses on component mount
  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5000/api/courses');
      setCourses(response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch courses: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCourse = async (e) => {
    e.preventDefault();
    
    if (!newCourse.course_code || !newCourse.course_name) {
      setError('Course code and name are required');
      return;
    }

    try {
      setLoading(true);
      await axios.post('http://localhost:5000/api/courses', {
        course_code: newCourse.course_code.trim(),
        course_name: newCourse.course_name.trim()
      });
      
      setNewCourse({ course_code: '', course_name: '' });
      setShowCreateModal(false);
      fetchCourses();
      setError('');
    } catch (err) {
      setError('Failed to create course: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleCourseClick = async (course) => {
    try {
      setLoading(true);
      setSelectedCourse(course);
      const response = await axios.get(`http://localhost:5000/api/courses/${course.course_code}/students`);
      setStudents(response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch students: ' + (err.response?.data?.error || err.message));
      setStudents([]);
    } finally {
      setLoading(false);
    }
  };

  const handleBackToCourses = () => {
    setSelectedCourse(null);
    setStudents([]);
  };

  const handleAddStudent = () => {
    setShowAddStudentModal(true);
  };

  const refreshStudents = () => {
    if (selectedCourse) {
      handleCourseClick(selectedCourse);
    }
  };

  return (
    <div className="courses-container">
      <div className="courses-header">
        <h2>{selectedCourse ? `${selectedCourse.course_code} - ${selectedCourse.course_name}` : 'Courses'}</h2>
        {!selectedCourse && (
          <button className="create-course-btn" onClick={() => setShowCreateModal(true)}>
            <PlusIcon size={18} />
            <span style={{ marginLeft: '0.5rem' }}>Create Course</span>
          </button>
        )}
        {selectedCourse && (
          <div className="course-actions">
            <button className="add-student-btn" onClick={handleAddStudent}>
              <UserIcon size={18} />
              <span style={{ marginLeft: '0.5rem' }}>Add Student</span>
            </button>
            <button className="back-btn" onClick={handleBackToCourses}>
              <ArrowLeftIcon size={18} />
              <span style={{ marginLeft: '0.5rem' }}>Back to Courses</span>
            </button>
          </div>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading && <div className="loading">Loading...</div>}

      {!selectedCourse ? (
        <>
          {courses.length === 0 && !loading ? (
            <p className="no-data">No courses available. Create your first course!</p>
          ) : (
            <div className="courses-grid">
              {courses.map(course => (
                <div key={course.course_code} className="course-card" onClick={() => handleCourseClick(course)}>
                  <div className="course-code">{course.course_code}</div>
                  <div className="course-name">{course.course_name}</div>
                </div>
              ))}
            </div>
          )}
        </>
      ) : (
        <div className="students-list">
          {students.length === 0 && !loading && (
            <p className="no-data">No students enrolled in this course yet.</p>
          )}
          {students.length > 0 && (
            <table className="students-table">
              <thead>
                <tr>
                  <th>Roll No</th>
                  <th>Name</th>
                  <th>Embeddings</th>
                </tr>
              </thead>
              <tbody>
                {students.map(student => (
                  <tr key={student.student_id}>
                    <td>{student.student_id}</td>
                    <td>{student.name}</td>
                    <td>{student.embedding_count || 0}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Create Course Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Create New Course</h3>
            <form onSubmit={handleCreateCourse}>
              <div className="form-group">
                <label>Course Code:</label>
                <input
                  type="text"
                  value={newCourse.course_code}
                  onChange={(e) => setNewCourse({ ...newCourse, course_code: e.target.value })}
                  placeholder="e.g., CS101"
                  required
                />
              </div>
              <div className="form-group">
                <label>Course Name:</label>
                <input
                  type="text"
                  value={newCourse.course_name}
                  onChange={(e) => setNewCourse({ ...newCourse, course_name: e.target.value })}
                  placeholder="e.g., Introduction to Programming"
                  required
                />
              </div>
              <div className="modal-buttons">
                <button type="submit" className="submit-btn" disabled={loading}>
                  {loading ? 'Creating...' : 'Create'}
                </button>
                <button type="button" className="cancel-btn" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Student Modal */}
      {showAddStudentModal && selectedCourse && (
        <AddStudentModal
          courseCode={selectedCourse.course_code}
          onClose={() => setShowAddStudentModal(false)}
          onSuccess={refreshStudents}
        />
      )}
    </div>
  );
};

// AddStudentModal Component
const AddStudentModal = ({ courseCode, onClose, onSuccess }) => {
  const [students, setStudents] = useState([]);
  const [filteredStudents, setFilteredStudents] = useState([]);
  const [degreeYearFilter, setDegreeYearFilter] = useState('');
  const [selectedStudentIds, setSelectedStudentIds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from({length: 10}, (_, i) => currentYear - i);

  useEffect(() => {
    fetchStudents();
  }, []);

  useEffect(() => {
    if (degreeYearFilter) {
      setFilteredStudents(students.filter(s => s.degree_year === parseInt(degreeYearFilter)));
    } else {
      setFilteredStudents(students);
    }
  }, [degreeYearFilter, students]);

  const fetchStudents = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/students');
      setStudents(response.data);
      setFilteredStudents(response.data);
    } catch (err) {
      setError('Failed to fetch students: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleStudentToggle = (studentId) => {
    setSelectedStudentIds(prev => 
      prev.includes(studentId)
        ? prev.filter(id => id !== studentId)
        : [...prev, studentId]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (selectedStudentIds.length === 0) {
      setError('Please select at least one student');
      return;
    }

    try {
      setLoading(true);
      setError('');

      // Enroll all selected students
      const enrollPromises = selectedStudentIds.map(student_id =>
        axios.post(`http://localhost:5000/api/courses/${courseCode}/students`, {
          student_id
        })
      );

      await Promise.all(enrollPromises);

      onSuccess();
      onClose();
    } catch (err) {
      setError('Failed to enroll student(s): ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content add-student-modal" onClick={(e) => e.stopPropagation()}>
        <h3>Enroll Student in {courseCode}</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Filter by Degree Year:</label>
            <select
              value={degreeYearFilter}
              onChange={(e) => setDegreeYearFilter(e.target.value)}
            >
              <option value="">All Years</option>
              {yearOptions.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Select Students:</label>
            {filteredStudents.length === 0 ? (
              <p className="no-students">No students available. Add students in the "Manage Students" tab first.</p>
            ) : (
              <div className="students-list">
                {filteredStudents.map(student => (
                  <label key={student.student_id} className="student-option">
                    <input
                      type="checkbox"
                      checked={selectedStudentIds.includes(student.student_id)}
                      onChange={() => handleStudentToggle(student.student_id)}
                    />
                    <span className="student-info">
                      <strong>{student.student_id}</strong> - {student.name}
                      <small> (Year: {student.degree_year})</small>
                    </span>
                  </label>
                ))}
              </div>
            )}
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="modal-actions">
            <button type="submit" className="submit-btn" disabled={loading || selectedStudentIds.length === 0}>
              {loading ? 'Enrolling...' : `Enroll Selected (${selectedStudentIds.length})`}
            </button>
            <button type="button" className="cancel-btn" onClick={onClose}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Courses;
