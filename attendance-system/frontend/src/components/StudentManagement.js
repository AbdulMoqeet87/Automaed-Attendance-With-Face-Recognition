import React, { useState } from 'react';
import axios from 'axios';
import API_URL from '../config';
import { CameraIcon, UserIcon, InfoIcon, XIcon } from './Icons';
import './StudentManagement.css';

function StudentManagement() {
  const [studentId, setStudentId] = useState('');
  const [studentName, setStudentName] = useState('');
  const [degreeYear, setDegreeYear] = useState('');
  const [images, setImages] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from({length: 10}, (_, i) => currentYear - i);

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

    if (!studentId.trim() || !studentName.trim() || !degreeYear.trim()) {
      setMessage({ type: 'error', text: 'Please enter student ID, name, and degree year' });
      return;
    }

    if (images.length === 0) {
      setMessage({ type: 'error', text: 'Please upload at least one image' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const formData = new FormData();
      formData.append('student_id', studentId);
      formData.append('name', studentName);
      formData.append('degree_year', degreeYear);
      
      images.forEach((image) => {
        formData.append('images', image);
      });

      const response = await axios.post(`${API_URL}/api/students/add`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setMessage({ type: 'success', text: response.data.message });
      
      // Reset form
      setStudentId('');
      setStudentName('');
      setDegreeYear('');
      setImages([]);
      setImagePreviews([]);
      
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
        <p className="subtitle">Register a student globally with their face images. You can later enroll them in courses.</p>

        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="studentId">Student ID / Roll Number *</label>
              <input
                type="text"
                id="studentId"
                value={studentId}
                onChange={(e) => setStudentId(e.target.value)}
                placeholder="e.g., bscs22147"
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
            <label htmlFor="degreeYear">Degree Starting Year *</label>
            <select
              id="degreeYear"
              value={degreeYear}
              onChange={(e) => setDegreeYear(e.target.value)}
              required
            >
              <option value="">Select Year</option>
              {yearOptions.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
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
              <CameraIcon size={20} />
              <span style={{ marginLeft: '0.5rem' }}>
                {images.length === 0 ? 'Select Images' : `${images.length} image(s) selected`}
              </span>
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
                    <XIcon size={16} color="white" />
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
            <UserIcon size={18} />
            <span style={{ marginLeft: '0.5rem' }}>
              {loading ? 'Processing...' : 'Add Student'}
            </span>
          </button>
        </form>

        <div className="info-box">
          <h3>
            <InfoIcon size={18} />
            <span style={{ marginLeft: '0.5rem' }}>Instructions:</span>
          </h3>
          <ul>
            <li>Enter unique student ID/roll number</li>
            <li>Select the year the student started their degree</li>
            <li>Upload 2-5 clear face images with good lighting</li>
            <li>Images should have front-facing angles</li>
            <li>Different expressions/angles improve recognition accuracy</li>
            <li>After adding, go to Courses tab to enroll student in courses</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default StudentManagement;
