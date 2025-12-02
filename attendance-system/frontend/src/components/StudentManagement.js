import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './StudentManagement.css';

function StudentManagement() {
  const [studentId, setStudentId] = useState('');
  const [studentName, setStudentName] = useState('');
  const [images, setImages] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);
  const [courses, setCourses] = useState([]);
  const [selectedCourses, setSelectedCourses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Fetch available courses on component mount
  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const response = await axios.get('/api/courses');
        setCourses(response.data);
      } catch (error) {
        console.error('Error fetching courses:', error);
      }
    };
    fetchCourses();
  }, []);

  const handleCourseToggle = (courseCode) => {
    setSelectedCourses(prev => 
      prev.includes(courseCode)
        ? prev.filter(c => c !== courseCode)
        : [...prev, courseCode]
    );
  };

  const handleImageSelect = (e) => {
    const files = Array.from(e.target.files);
    
    if (files.length > 5) {
      setMessage({ type: 'error', text: 'Maximum 5 images allowed' });
      return;
    }

    setImages(files);
    
    // Create previews
    const previews = files.map(file => URL.createObjectURL(file));
    setImagePreviews(previews);
    setMessage({ type: '', text: '' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!studentId.trim() || !studentName.trim()) {
      setMessage({ type: 'error', text: 'Please enter student ID and name' });
      return;
    }

    if (images.length === 0) {
      setMessage({ type: 'error', text: 'Please upload at least one image' });
      return;
    }

    if (selectedCourses.length === 0) {
      setMessage({ type: 'error', text: 'Please select at least one course' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const formData = new FormData();
      formData.append('student_id', studentId);
      formData.append('name', studentName);
      formData.append('enrolled_courses', JSON.stringify(selectedCourses));
      
      images.forEach((image, index) => {
        formData.append('images', image);
      });

      const response = await axios.post('/api/students/add', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setMessage({ type: 'success', text: response.data.message });
      
      // Reset form
      setStudentId('');
      setStudentName('');
      setImages([]);
      setImagePreviews([]);
      setSelectedCourses([]);
      
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.error || 'Failed to add student'
      });
    } finally {
      setLoading(false);
    }
  };

  const removeImage = (index) => {
    const newImages = images.filter((_, i) => i !== index);
    const newPreviews = imagePreviews.filter((_, i) => i !== index);
    setImages(newImages);
    setImagePreviews(newPreviews);
  };

  return (
    <div className="student-management">
      <div className="management-card">
        <h2>Add New Student</h2>
        <p className="subtitle">Register a student with their face images for attendance recognition</p>

        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="studentId">Student ID *</label>
              <input
                type="text"
                id="studentId"
                value={studentId}
                onChange={(e) => setStudentId(e.target.value)}
                placeholder="e.g., bscs22100"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="studentName">Student Name *</label>
              <input
                type="text"
                id="studentName"
                value={studentName}
                onChange={(e) => setStudentName(e.target.value)}
                placeholder="e.g., John Doe"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Enrolled Courses * (Select all applicable)</label>
            <div className="courses-grid">
              {courses.map((course) => (
                <label key={course.code} className="course-checkbox">
                  <input
                    type="checkbox"
                    checked={selectedCourses.includes(course.code)}
                    onChange={() => handleCourseToggle(course.code)}
                  />
                  <span className="course-label">
                    <strong>{course.code}</strong>
                    <small>{course.name}</small>
                  </span>
                </label>
              ))}
            </div>
            {selectedCourses.length > 0 && (
              <p className="selected-count">
                {selectedCourses.length} course(s) selected
              </p>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="images">Upload Face Images (2-5 recommended) *</label>
            <input
              type="file"
              id="images"
              accept="image/*"
              multiple
              onChange={handleImageSelect}
              style={{ display: 'none' }}
            />
            <label htmlFor="images" className="file-input-label">
              <span className="upload-icon">📸</span>
              {images.length === 0 ? 'Select Images' : `${images.length} image(s) selected`}
            </label>
          </div>

          {imagePreviews.length > 0 && (
            <div className="image-previews">
              {imagePreviews.map((preview, index) => (
                <div key={index} className="preview-item">
                  <img src={preview} alt={`Preview ${index + 1}`} />
                  <button
                    type="button"
                    className="remove-btn"
                    onClick={() => removeImage(index)}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}

          {message.text && (
            <div className={`message ${message.type}`}>
              {message.text}
            </div>
          )}

          <button 
            type="submit" 
            className="btn btn-primary" 
            disabled={loading || images.length === 0}
          >
            {loading ? 'Processing...' : 'Add Student'}
          </button>
        </form>

        <div className="info-box">
          <h3>📋 Instructions:</h3>
          <ul>
            <li>Upload 2-5 clear face images of the student</li>
            <li>Images should have good lighting and front-facing angles</li>
            <li>Different expressions/angles improve recognition accuracy</li>
            <li>Avoid sunglasses, masks, or face obstructions</li>
            <li>Each student ID must be unique</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default StudentManagement;
