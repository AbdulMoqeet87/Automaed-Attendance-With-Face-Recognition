import cv2
import base64
from datetime import datetime
from ml_module.face_recognizer import FaceRecognizer
from data_module.database import Database

class AttendanceController:
    def __init__(self):
        self.face_recognizer = FaceRecognizer()
        self.database = Database()
        
    def validate_image_format(self, image_path):
        try:
            img = cv2.imread(image_path)
            if img is None:
                return False, "Unable to read image file"
            return True, None
        except Exception as e:
            return False, f"Image validation error: {str(e)}"
    
    def process_attendance(self, image_path, course_code):
        """
        Only marks students present/absent if they are enrolled in the specified course
        """
        is_valid, error_msg = self.validate_image_format(image_path)
        if not is_valid:
            raise ValueError(error_msg)
        
        student_db = self.database.get_students_in_course(course_code)
        
        if len(student_db) == 0:
            img = cv2.imread(image_path)
            faces = self.face_recognizer.detect_faces(img)
            
            unrecognized_faces = []
            annotated_img = img.copy()
            for (x, y, w, h) in faces:
                face_img = img[y:y+h, x:x+w]
                unrecognized_faces.append(face_img)
                cv2.rectangle(annotated_img, (x, y), (x+w, y+h), (0, 165, 255), 2)
                cv2.putText(annotated_img, 'Unknown', (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 165, 255), 2)
            
            unrecognized_list = []
            for face_img in unrecognized_faces:
                _, buffer = cv2.imencode('.jpg', face_img)
                face_base64 = base64.b64encode(buffer).decode('utf-8')
                unrecognized_list.append(face_base64)
            
            _, buffer = cv2.imencode('.jpg', annotated_img)
            annotated_base64 = base64.b64encode(buffer).decode('utf-8')
            
            timestamp = datetime.now()
            return {
                'class_name': course_code,
                'timestamp': timestamp.isoformat(),
                'present': [],
                'absent': [],
                'unrecognized': unrecognized_list,
                'annotated_image': annotated_base64,
                'total_detected': len(unrecognized_list),
                'total_students': 0,
                'message': f'No students enrolled in course {course_code}. All detected faces marked as unrecognized.'
            }
        
        all_embeddings = self.database.get_all_embeddings(course_code=course_code)
        embeddings_db = {sid: emb for sid, emb in all_embeddings.items() if any(s['student_id'] == sid for s in student_db)}
        
        ml_results = self.face_recognizer.detect_and_recognize(image_path, embeddings_db)
        
        present_student_ids = ml_results['recognized_students']
        unrecognized_faces = ml_results['unrecognized']
        annotated_img = ml_results['annotated_img']
        
        present_list = []
        for student_id in present_student_ids:
            student = next((s for s in student_db if s['student_id'] == student_id), None)
            if student:
                present_list.append({
                    'student_id': student['student_id'],
                    'name': student['name'],
                    'confidence': student_id.get('confidence', None) if isinstance(student_id, dict) else None
                })
        
        present_ids = [s['student_id'] for s in present_list]
        absent_list = [
            {
                'student_id': student['student_id'],
                'name': student['name']
            }
            for student in student_db 
            if student['student_id'] not in present_ids
        ]
        
        unrecognized_list = []
        for face_img in unrecognized_faces:
            _, buffer = cv2.imencode('.jpg', face_img)
            face_base64 = base64.b64encode(buffer).decode('utf-8')
            unrecognized_list.append(face_base64)
        
        _, buffer = cv2.imencode('.jpg', annotated_img)
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')
        
        timestamp = datetime.now()
        return {
            'class_name': course_code,
            'timestamp': timestamp.isoformat(),
            'present': present_list,
            'absent': absent_list,
            'unrecognized': unrecognized_list,
            'annotated_image': annotated_base64,
            'total_detected': len(present_list) + len(unrecognized_list),
            'total_students': len(student_db)
        }
    
    def get_all_students(self):
        return self.database.get_all_students()
    
    def add_student(self, student_data):
        if 'student_id' not in student_data or 'name' not in student_data or 'degree_year' not in student_data:
            raise ValueError("student_id, name, and degree_year are required")
        
        if 'embeddings' in student_data:
            return self.database.add_student(
                student_data['student_id'],
                student_data['name'],
                student_data['degree_year'],
                student_data['embeddings']
            )
        
        elif 'images' in student_data:
            embeddings = []
            for img_data in student_data['images']:
                img_bytes = base64.b64decode(img_data)
                embedding = self.face_recognizer.generate_embedding_from_bytes(img_bytes)
                embeddings.append(embedding)
            
            return self.database.add_student(
                student_data['student_id'],
                student_data['name'],
                student_data['degree_year'],
                embeddings
            )
        else:
            return self.database.add_student(
                student_data['student_id'],
                student_data['name'],
                student_data['degree_year'],
                []
            )
    
    def enroll_student_in_course(self, student_id, course_code):
        return self.database.enroll_student_in_course(student_id, course_code)
    
    def get_students_by_year(self, degree_year=None):
        return self.database.get_students_by_year(degree_year)
    
    def submit_attendance(self, attendance_data):
        attendance_record = {
            'class_name': attendance_data['class_name'],
            'timestamp': datetime.fromisoformat(attendance_data['timestamp']) if isinstance(attendance_data.get('timestamp'), str) else datetime.now(),
            'present': attendance_data.get('present', []),
            'absent': attendance_data.get('absent', []),
            'unrecognized_count': attendance_data.get('unrecognized_count', 0)
        }
        
        return self.database.store_attendance(attendance_record)
    
    def get_attendance_history(self, class_name=None, date=None):
        return self.database.get_attendance_history(class_name, date)
    
    def compute_absent(self, student_db, present_list):
        present_ids = [s['student_id'] for s in present_list]
        return [s for s in student_db if s['student_id'] not in present_ids]
    
    def create_course(self, course_code, course_name):
        return self.database.create_course(course_code, course_name)
    
    def get_all_courses(self):
        return self.database.get_all_courses()
    
    def get_course_by_code(self, course_code):
        return self.database.get_course_by_code(course_code)
    
    def get_students_in_course(self, course_code):
        return self.database.get_students_in_course(course_code)
