import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ImageUpload.css';

function ImageUpload({ onAttendanceProcessed, onLoadingStart }) {
  const [selectedImage, setSelectedImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [className, setClassName] = useState('');
  const [courses, setCourses] = useState([]);
  const [error, setError] = useState('');

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

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Please select a valid image file (JPEG/PNG)');
        return;
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('Image size should be less than 10MB');
        return;
      }

      setSelectedImage(file);
      setPreview(URL.createObjectURL(file));
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedImage) {
      setError('Please select an image');
      return;
    }

    if (!className.trim()) {
      setError('Please enter a class name');
      return;
    }

    const formData = new FormData();
    formData.append('image', selectedImage);
    formData.append('class_name', className);

    try {
      onLoadingStart();
      const response = await axios.post('/api/process-attendance', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      onAttendanceProcessed(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to process attendance. Please try again.');
      onLoadingStart(); // Stop loading
    }
  };

  const handleReset = () => {
    setSelectedImage(null);
    setPreview(null);
    setClassName('');
    setError('');
  };

  return (
    <div className="image-upload-container">
      <div className="upload-card">
        <h2>Upload Classroom Image</h2>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="className">Select Course</label>
            <select
              id="className"
              value={className}
              onChange={(e) => setClassName(e.target.value)}
              required
              className="course-select"
            >
              <option value="">-- Select a course --</option>
              {courses.map((course) => (
                <option key={course.code} value={course.code}>
                  {course.code} - {course.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="imageInput" className="file-input-label">
              <span className="upload-icon">📁</span>
              {selectedImage ? 'Change Image' : 'Select Classroom Image'}
            </label>
            <input
              type="file"
              id="imageInput"
              accept="image/*"
              onChange={handleImageSelect}
              style={{ display: 'none' }}
            />
          </div>

          {preview && (
            <div className="image-preview">
              <img src={preview} alt="Preview" />
            </div>
          )}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="button-group">
            <button type="submit" className="btn btn-primary" disabled={!selectedImage || !className}>
              Process Attendance
            </button>
            {(selectedImage || className) && (
              <button type="button" className="btn btn-secondary" onClick={handleReset}>
                Reset
              </button>
            )}
          </div>
        </form>

        <div className="info-box">
          <h3>Instructions:</h3>
          <ul>
            <li>Ensure the classroom image is clear and well-lit</li>
            <li>Faces should be visible and not obscured</li>
            <li>Supported formats: JPEG, PNG</li>
            <li>Maximum file size: 10MB</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default ImageUpload;
