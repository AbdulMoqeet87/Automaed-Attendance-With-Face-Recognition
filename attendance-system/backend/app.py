from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from application_module.attendance_controller import AttendanceController
from courses import get_all_courses

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

attendance_controller = AttendanceController()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/courses', methods=['GET', 'POST'])
def manage_courses():
    """
    GET: Get list of all courses
    POST: Create a new course
    """
    if request.method == 'GET':
        try:
            courses = attendance_controller.get_all_courses()
            return jsonify(courses), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            if not data or 'course_code' not in data or 'course_name' not in data:
                return jsonify({'error': 'course_code and course_name are required'}), 400
            
            result = attendance_controller.create_course(
                data['course_code'],
                data['course_name']
            )
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/courses/<course_code>/students', methods=['GET', 'POST'])
def manage_course_students(course_code):
    if request.method == 'GET':
        try:
            students = attendance_controller.get_students_in_course(course_code)
            return jsonify(students), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data or 'student_id' not in data:
                return jsonify({'error': 'student_id is required'}), 400
            
            result = attendance_controller.enroll_student_in_course(
                data['student_id'],
                course_code
            )
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/students', methods=['GET'])
def get_all_students_filtered():
    try:
        degree_year = request.args.get('degree_year')
        students = attendance_controller.get_students_by_year(degree_year)
        return jsonify(students), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-attendance', methods=['POST'])
def process_attendance():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        if 'course_code' not in request.form:
            return jsonify({'error': 'No course code provided'}), 400
        
        file = request.files['image']
        course_code = request.form['course_code']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Only JPEG/PNG allowed'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        result = attendance_controller.process_attendance(filepath, course_code)
        
        return jsonify(result), 200
        
    except Exception as e:
        app.logger.error(f"Error processing attendance: {str(e)}")
        return jsonify({'error': f'Failed to process attendance: {str(e)}'}), 500

@app.route('/api/students/add', methods=['POST'])
def add_student_with_images():
    try:
        if 'student_id' not in request.form or 'name' not in request.form or 'degree_year' not in request.form:
            return jsonify({'error': 'Student ID, name, and degree year are required'}), 400
        
        if 'images' not in request.files:
            return jsonify({'error': 'At least one image is required'}), 400
        
        student_id = request.form['student_id']
        name = request.form['name']
        degree_year = request.form['degree_year']
        
        files = request.files.getlist('images')
        
        if len(files) == 0:
            return jsonify({'error': 'No images provided'}), 400
        
        if len(files) > 5:
            return jsonify({'error': 'Maximum 5 images allowed'}), 400
        
        from ml_module.face_recognizer import FaceRecognizer
        import cv2
        import numpy as np
        
        recognizer = FaceRecognizer()
        embeddings = []
        errors = []
        
        for idx, file in enumerate(files):
            if not allowed_file(file.filename):
                errors.append(f"Image {idx + 1}: Invalid file format")
                continue
            
            try:
                file_bytes = np.frombuffer(file.read(), np.uint8)
                img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                
                if img is None:
                    errors.append(f"Image {idx + 1}: Could not read image")
                    continue
                
                faces = recognizer.detect_faces(img)
                
                if len(faces) == 0:
                    errors.append(f"Image {idx + 1}: No face detected")
                    continue
                
                largest_face = max(faces, key=lambda f: f[2] * f[3])
                x, y, w, h = largest_face
                face_img = img[y:y+h, x:x+w]
                
                embedding = recognizer.generate_embedding(face_img)
                embeddings.append(embedding)
                
            except Exception as e:
                errors.append(f"Image {idx + 1}: {str(e)}")
                continue
        
        if len(embeddings) == 0:
            error_msg = 'No valid face embeddings generated. ' + '; '.join(errors)
            return jsonify({'error': error_msg}), 400
        
        result = attendance_controller.add_student({
            'student_id': student_id,
            'name': name,
            'degree_year': degree_year,
            'embeddings': embeddings
        })
        
        response_data = {
            'success': True,
            'message': f'Student {student_id} ({name}) added successfully with {len(embeddings)} face embedding(s)',
            'embeddings_count': len(embeddings)
        }
        
        if errors:
            response_data['warnings'] = errors
        
        return jsonify(response_data), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"Error adding student: {str(e)}")
        return jsonify({'error': f'Failed to add student: {str(e)}'}), 500

@app.route('/api/students', methods=['POST'])
def add_student():
    try:
        data = request.get_json()
        result = attendance_controller.add_student(data)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attendance/submit', methods=['POST'])
def submit_attendance():
    """
    Submit and save attendance record to database
    """
    try:
        data = request.get_json()
        
        if not data or 'class_name' not in data:
            return jsonify({'error': 'Class name is required'}), 400
        
        result = attendance_controller.submit_attendance(data)
        
        return jsonify({
            'success': True,
            'message': 'Attendance submitted successfully',
            'attendance_id': result.get('attendance_id')
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error submitting attendance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/attendance/history', methods=['GET'])
def get_attendance_history():
    try:
        class_name = request.args.get('class_name')
        date = request.args.get('date')
        
        history = attendance_controller.get_attendance_history(class_name, date)
        return jsonify(history), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large. Maximum size is 10MB'}), 413

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
