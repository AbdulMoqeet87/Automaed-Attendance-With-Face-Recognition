import os
import cv2
import base64
from datetime import datetime
from ml_module.face_recognizer import FaceRecognizer
from data_module.database import Database

class AttendanceController:
    """
    Application Module - Central controller for attendance workflow
    Coordinates between ML Module and Data Module
    """
    
    def __init__(self):
        self.face_recognizer = FaceRecognizer()
        self.database = Database()
        
    def validate_image_format(self, image_path):
        """Validate if the image format is acceptable"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return False, "Unable to read image file"
            return True, None
        except Exception as e:
            return False, f"Image validation error: {str(e)}"
    
    def process_attendance(self, image_path, class_name):
        """
        Main workflow for processing attendance
        Implements the pseudo-code from the design document
        Only marks students present/absent if they are enrolled in the specified course
        """
        # Validate image format
        is_valid, error_msg = self.validate_image_format(image_path)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Fetch stored data from Data Module
        all_students = self.database.get_all_students()
        
        # Filter students enrolled in this course
        student_db = [s for s in all_students if class_name in s.get('enrolled_courses', [])]
        
        if len(student_db) == 0:
            raise ValueError(f"No students are enrolled in course: {class_name}")
        
        # Get embeddings only for enrolled students
        all_embeddings = self.database.get_all_embeddings()
        embeddings_db = {sid: emb for sid, emb in all_embeddings.items() if any(s['student_id'] == sid for s in student_db)}
        
        # Call ML Module for detection & recognition
        ml_results = self.face_recognizer.detect_and_recognize(image_path, embeddings_db)
        
        # Extract results
        present_student_ids = ml_results['recognized_students']
        unrecognized_faces = ml_results['unrecognized']
        annotated_img = ml_results['annotated_img']
        
        # Build present list with student details
        present_list = []
        for student_id in present_student_ids:
            student = next((s for s in student_db if s['student_id'] == student_id), None)
            if student:
                present_list.append({
                    'student_id': student['student_id'],
                    'name': student['name'],
                    'confidence': student_id.get('confidence', None) if isinstance(student_id, dict) else None
                })
        
        # Compute absent list (only from enrolled students)
        present_ids = [s['student_id'] for s in present_list]
        absent_list = [
            {
                'student_id': student['student_id'],
                'name': student['name']
            }
            for student in student_db 
            if student['student_id'] not in present_ids
        ]
        
        # Prepare unrecognized faces for display
        unrecognized_list = []
        for face_img in unrecognized_faces:
            _, buffer = cv2.imencode('.jpg', face_img)
            face_base64 = base64.b64encode(buffer).decode('utf-8')
            unrecognized_list.append(face_base64)
        
        # Convert annotated image to base64
        _, buffer = cv2.imencode('.jpg', annotated_img)
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Store attendance in database
        timestamp = datetime.now()
        attendance_record = {
            'class_name': class_name,
            'timestamp': timestamp,
            'present': present_list,
            'absent': absent_list,
            'unrecognized_count': len(unrecognized_list)
        }
        self.database.store_attendance(attendance_record)
        
        # Return results to Presentation Layer
        return {
            'class_name': class_name,
            'timestamp': timestamp.isoformat(),
            'present': present_list,
            'absent': absent_list,
            'unrecognized': unrecognized_list,
            'annotated_image': annotated_base64,
            'total_detected': len(present_list) + len(unrecognized_list),
            'total_students': len(student_db)
        }
    
    def get_all_students(self):
        """Retrieve all registered students"""
        return self.database.get_all_students()
    
    def add_student(self, student_data):
        """Add a new student to the system"""
        # Validate required fields
        if 'student_id' not in student_data or 'name' not in student_data:
            raise ValueError("student_id and name are required")
        
        # Extract enrolled courses
        enrolled_courses = student_data.get('enrolled_courses', [])
        
        # If embeddings provided directly (from web upload)
        if 'embeddings' in student_data:
            return self.database.add_student(
                student_data['student_id'],
                student_data['name'],
                student_data['embeddings'],
                enrolled_courses
            )
        
        # If images provided (base64 encoded)
        elif 'images' in student_data:
            embeddings = []
            for img_data in student_data['images']:
                # Decode base64 image
                img_bytes = base64.b64decode(img_data)
                # Generate embedding using ML module
                embedding = self.face_recognizer.generate_embedding_from_bytes(img_bytes)
                embeddings.append(embedding)
            
            # Store in database
            return self.database.add_student(
                student_data['student_id'],
                student_data['name'],
                embeddings,
                enrolled_courses
            )
        else:
            # Store student without embeddings (can be added later)
            return self.database.add_student(
                student_data['student_id'],
                student_data['name'],
                [],
                enrolled_courses
            )
    
    def submit_attendance(self, attendance_data):
        """
        Submit and save attendance record to database
        """
        # Prepare attendance record
        attendance_record = {
            'class_name': attendance_data['class_name'],
            'timestamp': datetime.fromisoformat(attendance_data['timestamp']) if isinstance(attendance_data.get('timestamp'), str) else datetime.now(),
            'present': attendance_data.get('present', []),
            'absent': attendance_data.get('absent', []),
            'unrecognized_count': attendance_data.get('unrecognized_count', 0)
        }
        
        # Store in database
        return self.database.store_attendance(attendance_record)
    
    def get_attendance_history(self, class_name=None, date=None):
        """Retrieve attendance history with optional filters"""
        return self.database.get_attendance_history(class_name, date)
    
    def compute_absent(self, student_db, present_list):
        """Helper function to compute absent students"""
        present_ids = [s['student_id'] for s in present_list]
        return [s for s in student_db if s['student_id'] not in present_ids]
