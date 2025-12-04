from pymongo import MongoClient
from datetime import datetime, timedelta
import os
import numpy as np

class Database:
    """
    Data Module - Manages all data storage and retrieval
    Handles student profiles, embeddings, and attendance records
    """
    
    def __init__(self):
        # MongoDB connection
        # Default to local MongoDB, can be configured via environment variable
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.client = MongoClient(mongo_uri)
        
        # Database and collections
        self.db = self.client['attendance_system']
        self.students_collection = self.db['students']
        self.enrollments_collection = self.db['enrollments']
        self.embeddings_collection = self.db['embeddings']
        self.attendance_collection = self.db['attendance']
        self.courses_collection = self.db['courses']
        
        # Create indexes for better performance (gracefully handle errors)
        try:
            self._create_indexes()
        except Exception as e:
            print(f"Warning: Could not create indexes: {e}")
            print("System will work but queries may be slower")
    
    def _create_indexes(self):
        """Create database indexes for optimized queries"""
        self.students_collection.create_index('student_id', unique=True)
        self.students_collection.create_index('degree_year')
        self.enrollments_collection.create_index([('course_code', 1), ('student_id', 1)], unique=True)
        self.embeddings_collection.create_index('student_id')
        self.attendance_collection.create_index([('course_code', 1), ('timestamp', -1)])
        self.courses_collection.create_index('course_code', unique=True)
    
    def get_all_students(self):
        """
        Retrieve all registered students
        Returns: List of student dictionaries
        """
        students = list(self.students_collection.find({}, {'_id': 0}))
        return students
    
    def get_student_by_id(self, student_id):
        """Get a specific student by ID"""
        return self.students_collection.find_one(
            {'student_id': student_id},
            {'_id': 0}
        )
    
    def get_all_embeddings(self, course_code=None):
        """
        Retrieve all stored embeddings organized by student ID
        Args:
            course_code: Optional filter by course (gets embeddings for students enrolled in that course)
        Returns: Dict of {student_id: [embeddings]}
        """
        embeddings_dict = {}
        
        # If course_code is provided, only get embeddings for students enrolled in that course
        if course_code:
            # Get student IDs enrolled in the course
            enrollments = list(self.enrollments_collection.find({'course_code': course_code}))
            student_ids = [e['student_id'] for e in enrollments]
            query = {'student_id': {'$in': student_ids}}
        else:
            query = {}
        
        embeddings_cursor = self.embeddings_collection.find(query)
        
        for doc in embeddings_cursor:
            student_id = doc['student_id']
            # Convert stored list back to numpy array
            embeddings = [np.array(emb) for emb in doc['embeddings']]
            embeddings_dict[student_id] = embeddings
        
        return embeddings_dict
    
    def add_student(self, student_id, name, degree_year, embeddings=None):
        """
        Add a new student globally (not tied to any course yet)
        Args:
            student_id: Unique student identifier
            name: Student's name
            degree_year: Year student started their degree (e.g., 2022)
            embeddings: List of face embeddings (optional)
        """
        # Check if student already exists
        existing = self.students_collection.find_one({'student_id': student_id})
        if existing:
            raise ValueError(f"Student with ID {student_id} already exists")
        
        # Create student record
        student = {
            'student_id': student_id,
            'name': name,
            'degree_year': int(degree_year),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Insert student
        self.students_collection.insert_one(student)
        
        # Store embeddings if provided
        if embeddings and len(embeddings) > 0:
            # Convert numpy arrays to lists for MongoDB storage
            embeddings_list = [emb.tolist() if isinstance(emb, np.ndarray) else emb 
                              for emb in embeddings]
            
            embedding_doc = {
                'student_id': student_id,
                'embeddings': embeddings_list,
                'created_at': datetime.now()
            }
            self.embeddings_collection.insert_one(embedding_doc)
        
        return {
            'success': True,
            'message': f'Student {student_id} added successfully'
        }
    
    def enroll_student_in_course(self, student_id, course_code):
        """
        Enroll an existing student in a course
        """
        # Check if student exists
        student = self.students_collection.find_one({'student_id': student_id})
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        # Check if course exists
        course = self.courses_collection.find_one({'course_code': course_code})
        if not course:
            raise ValueError(f"Course {course_code} not found")
        
        # Check if already enrolled
        existing = self.enrollments_collection.find_one({
            'student_id': student_id,
            'course_code': course_code
        })
        if existing:
            raise ValueError(f"Student {student_id} already enrolled in {course_code}")
        
        # Create enrollment
        enrollment = {
            'student_id': student_id,
            'course_code': course_code,
            'enrolled_at': datetime.now()
        }
        self.enrollments_collection.insert_one(enrollment)
        
        return {
            'success': True,
            'message': f'Student {student_id} enrolled in {course_code}'
        }
    
    def update_student_embeddings(self, student_id, new_embeddings):
        """
        Update or add embeddings for an existing student
        """
        # Convert to list format
        embeddings_list = [emb.tolist() if isinstance(emb, np.ndarray) else emb 
                          for emb in new_embeddings]
        
        # Check if embeddings exist
        existing = self.embeddings_collection.find_one({'student_id': student_id})
        
        if existing:
            # Append to existing embeddings
            self.embeddings_collection.update_one(
                {'student_id': student_id},
                {
                    '$push': {'embeddings': {'$each': embeddings_list}},
                    '$set': {'updated_at': datetime.now()}
                }
            )
        else:
            # Create new embedding document
            embedding_doc = {
                'student_id': student_id,
                'embeddings': embeddings_list,
                'created_at': datetime.now()
            }
            self.embeddings_collection.insert_one(embedding_doc)
        
        return {'success': True}
    
    def store_attendance(self, attendance_record):
        """
        Store attendance record in database
        Args:
            attendance_record: Dict containing class_name, timestamp, present, absent lists
        """
        # Add metadata
        attendance_record['created_at'] = datetime.now()
        
        # Insert into database
        result = self.attendance_collection.insert_one(attendance_record)
        
        return {
            'success': True,
            'attendance_id': str(result.inserted_id)
        }
    
    def get_attendance_history(self, class_name=None, date=None):
        """
        Retrieve attendance history with optional filters
        Args:
            class_name: Filter by specific class
            date: Filter by specific date (YYYY-MM-DD format)
        """
        query = {}
        
        if class_name:
            query['class_name'] = class_name
        
        if date:
            # Parse date and create range query
            try:
                start_date = datetime.strptime(date, '%Y-%m-%d')
                end_date = start_date + timedelta(days=1)
                query['timestamp'] = {'$gte': start_date, '$lt': end_date}
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        # Retrieve records, sorted by most recent first
        records = list(self.attendance_collection.find(
            query,
            {'_id': 0}
        ).sort('timestamp', -1).limit(100))
        
        # enrich with student names
        for record in records:
            # Convert datetime objects to ISO format strings
            if 'timestamp' in record and isinstance(record['timestamp'], datetime):
                record['timestamp'] = record['timestamp'].isoformat()
            if 'created_at' in record and isinstance(record['created_at'], datetime):
                record['created_at'] = record['created_at'].isoformat()
            
            # add student names to present list
            if 'present' in record and isinstance(record['present'], list):
                enriched_present = []
                for item in record['present']:
                    if isinstance(item, str):
                        # it's just a student ID, get the name
                        student = self.get_student_by_id(item)
                        if student:
                            enriched_present.append({
                                'student_id': item,
                                'name': student.get('name', 'Unknown')
                            })
                        else:
                            enriched_present.append({'student_id': item, 'name': 'Unknown'})
                    else:
                        # already has name
                        enriched_present.append(item)
                record['present'] = enriched_present
            
            # add student names to absent list
            if 'absent' in record and isinstance(record['absent'], list):
                enriched_absent = []
                for item in record['absent']:
                    if isinstance(item, str):
                        student = self.get_student_by_id(item)
                        if student:
                            enriched_absent.append({
                                'student_id': item,
                                'name': student.get('name', 'Unknown')
                            })
                        else:
                            enriched_absent.append({'student_id': item, 'name': 'Unknown'})
                    else:
                        enriched_absent.append(item)
                record['absent'] = enriched_absent
        
        return records
    
    def delete_student(self, student_id):
        """Delete a student and their embeddings"""
        # Delete student record
        self.students_collection.delete_one({'student_id': student_id})
        
        # Delete embeddings
        self.embeddings_collection.delete_one({'student_id': student_id})
        
        return {'success': True}
    
    def get_statistics(self):
        """Get database statistics"""
        return {
            'total_students': self.students_collection.count_documents({}),
            'total_attendance_records': self.attendance_collection.count_documents({}),
            'students_with_embeddings': self.embeddings_collection.count_documents({})
        }
    
    def initialize_sample_data(self):
        """
        Initialize database with sample student data for testing
        This should be called only once during setup
        """
        # Check if data already exists
        if self.students_collection.count_documents({}) > 0:
            return {'message': 'Sample data already exists'}
        
        # Sample students
        sample_students = [
            {'student_id': 'bscs22147', 'name': 'Abdul Moqeet'},
            {'student_id': 'bscs22059', 'name': 'Amna Amir'},

        ]
        
        for student in sample_students:
            try:
                # Generate random embeddings for testing
                random_embeddings = [np.random.rand(128) for _ in range(3)]
                self.add_student(
                    student['student_id'],
                    student['name'],
                    random_embeddings
                )
            except ValueError:
                pass  # Student already exists
        
        return {'message': 'Sample data initialized successfully'}
    
    # ===== Course Management Methods =====
    
    def create_course(self, course_code, course_name):
        """
        Create a new course
        Args:
            course_code: Unique course identifier (e.g., CS101)
            course_name: Course name (e.g., Introduction to Programming)
        """
        existing = self.courses_collection.find_one({'course_code': course_code})
        if existing:
            raise ValueError(f"Course with code {course_code} already exists")
        
        course = {
            'course_code': course_code,
            'course_name': course_name,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        self.courses_collection.insert_one(course)
        return {'success': True, 'message': f'Course {course_code} created successfully'}
    
    def get_all_courses(self):
        """Get all courses"""
        courses = list(self.courses_collection.find({}, {'_id': 0}).sort('course_code', 1))
        return courses
    
    def get_course_by_code(self, course_code):
        """Get specific course by code"""
        return self.courses_collection.find_one({'course_code': course_code}, {'_id': 0})
    
    def get_students_in_course(self, course_code):
        """Get all students enrolled in a specific course with their details"""
        # Get enrollments for this course
        enrollments = list(self.enrollments_collection.find({'course_code': course_code}))
        student_ids = [e['student_id'] for e in enrollments]
        
        # Get student details
        students = list(self.students_collection.find(
            {'student_id': {'$in': student_ids}},
            {'_id': 0}
        ).sort('student_id', 1))
        
        # Add embedding count to each student
        for student in students:
            embedding = self.embeddings_collection.find_one({'student_id': student['student_id']})
            student['embedding_count'] = len(embedding.get('embeddings', [])) if embedding else 0
        
        return students
    
    def get_students_by_year(self, degree_year=None):
        """Get all students, optionally filtered by degree year"""
        query = {}
        if degree_year:
            query['degree_year'] = int(degree_year)
        
        students = list(self.students_collection.find(query, {'_id': 0}).sort('student_id', 1))
        
        # Add embedding count to each student
        for student in students:
            embedding = self.embeddings_collection.find_one({'student_id': student['student_id']})
            student['embedding_count'] = len(embedding.get('embeddings', [])) if embedding else 0
        
        return students
    
    def delete_course(self, course_code):
        """Delete a course and all its students"""
        # Delete all students in the course
        self.students_collection.delete_many({'course_code': course_code})
        # Delete course
        self.courses_collection.delete_one({'course_code': course_code})
        return {'success': True, 'message': f'Course {course_code} deleted'}
    
    def close(self):
        """Close database connection"""
        self.client.close()
