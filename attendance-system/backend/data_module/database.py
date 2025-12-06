from pymongo import MongoClient
from datetime import datetime, timedelta
import os
import numpy as np

class Database: 
    def __init__(self):
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.client = MongoClient(mongo_uri)
        
        self.db = self.client['attendance_system']
        self.students_collection = self.db['students']
        self.enrollments_collection = self.db['enrollments']
        self.embeddings_collection = self.db['embeddings']
        self.attendance_collection = self.db['attendance']
        self.courses_collection = self.db['courses']
        
        try:
            self._create_indexes()
        except Exception as e:
            print(f"Warning: Could not create indexes: {e}")
    
    def _create_indexes(self):
        """Creating database indexes to have optimized queries"""
        self.students_collection.create_index('student_id', unique=True)
        self.students_collection.create_index('degree_year')
        self.enrollments_collection.create_index([('course_code', 1), ('student_id', 1)], unique=True)
        self.embeddings_collection.create_index('student_id')
        self.attendance_collection.create_index([('course_code', 1), ('timestamp', -1)])
        self.courses_collection.create_index('course_code', unique=True)
    
    def get_all_students(self):
        students = list(self.students_collection.find({}, {'_id': 0}))
        return students
    
    def get_student_by_id(self, student_id):
        return self.students_collection.find_one(
            {'student_id': student_id},
            {'_id': 0}
        )
    
    def get_all_embeddings(self, course_code=None):
        """
        Retrieve all stored embeddings organized by student ID for specific course or all students
        """
        embeddings_dict = {}
        
        if course_code:
            enrollments = list(self.enrollments_collection.find({'course_code': course_code}))
            student_ids = [e['student_id'] for e in enrollments]
            query = {'student_id': {'$in': student_ids}}
        else:
            query = {}
        
        embeddings_cursor = self.embeddings_collection.find(query)
        
        for doc in embeddings_cursor:
            student_id = doc['student_id']
            embeddings = [np.array(emb) for emb in doc['embeddings']]
            embeddings_dict[student_id] = embeddings
        
        return embeddings_dict
    
    def add_student(self, student_id, name, degree_year, embeddings=None):
        existing = self.students_collection.find_one({'student_id': student_id})
        if existing:
            raise ValueError(f"Student with ID {student_id} already exists")
        
        student = {
            'student_id': student_id,
            'name': name,
            'degree_year': int(degree_year),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        self.students_collection.insert_one(student)
        
        if embeddings and len(embeddings) > 0:
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
        student = self.students_collection.find_one({'student_id': student_id})
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        course = self.courses_collection.find_one({'course_code': course_code})
        if not course:
            raise ValueError(f"Course {course_code} not found")
        
        existing = self.enrollments_collection.find_one({
            'student_id': student_id,
            'course_code': course_code
        })
        if existing:
            raise ValueError(f"Student {student_id} already enrolled in {course_code}")
        
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
        embeddings_list = [emb.tolist() if isinstance(emb, np.ndarray) else emb 
                          for emb in new_embeddings]
        
        existing = self.embeddings_collection.find_one({'student_id': student_id})
        
        if existing:
            self.embeddings_collection.update_one(
                {'student_id': student_id},
                {
                    '$push': {'embeddings': {'$each': embeddings_list}},
                    '$set': {'updated_at': datetime.now()}
                }
            )
        else:
            embedding_doc = {
                'student_id': student_id,
                'embeddings': embeddings_list,
                'created_at': datetime.now()
            }
            self.embeddings_collection.insert_one(embedding_doc)
        
        return {'success': True}
    
    def store_attendance(self, attendance_record):
        attendance_record['created_at'] = datetime.now()
        result = self.attendance_collection.insert_one(attendance_record)
        return {
            'success': True,
            'attendance_id': str(result.inserted_id)
        }
    
    def get_attendance_history(self, class_name=None, date=None):
        """
        Retrieve attendance history with class name and date filters
        """
        query = {}
        
        if class_name:
            query['class_name'] = class_name
        
        if date:
            try:
                start_date = datetime.strptime(date, '%Y-%m-%d')
                end_date = start_date + timedelta(days=1)
                query['timestamp'] = {'$gte': start_date, '$lt': end_date}
            except ValueError:
                pass  
        
        records = list(self.attendance_collection.find(
            query,
            {'_id': 0}
        ).sort('timestamp', -1).limit(100))
        
        for record in records:
            if 'timestamp' in record and isinstance(record['timestamp'], datetime):
                record['timestamp'] = record['timestamp'].isoformat()
            if 'created_at' in record and isinstance(record['created_at'], datetime):
                record['created_at'] = record['created_at'].isoformat()
            
            if 'present' in record and isinstance(record['present'], list):
                enriched_present = []
                for item in record['present']:
                    if isinstance(item, str):
                        student = self.get_student_by_id(item)
                        if student:
                            enriched_present.append({
                                'student_id': item,
                                'name': student.get('name', 'Unknown')
                            })
                        else:
                            enriched_present.append({'student_id': item, 'name': 'Unknown'})
                    else:
                        enriched_present.append(item)
                record['present'] = enriched_present
            
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
        self.students_collection.delete_one({'student_id': student_id})
        self.embeddings_collection.delete_one({'student_id': student_id})
        return {'success': True}
    
    def get_statistics(self):
        return {
            'total_students': self.students_collection.count_documents({}),
            'total_attendance_records': self.attendance_collection.count_documents({}),
            'students_with_embeddings': self.embeddings_collection.count_documents({})
        }
    
    def initialize_sample_data(self):
        if self.students_collection.count_documents({}) > 0:
            return {'message': 'Sample data already exists'}
        
        sample_students = [
            {'student_id': 'bscs22147', 'name': 'Abdul Moqeet'},
            {'student_id': 'bscs22059', 'name': 'Amna Amir'},

        ]
        
        for student in sample_students:
            try:
                random_embeddings = [np.random.rand(128) for _ in range(3)]
                self.add_student(
                    student['student_id'],
                    student['name'],
                    random_embeddings
                )
            except ValueError:
                pass 
        
        return {'message': 'Sample data initialized successfully'}
      
    def create_course(self, course_code, course_name):
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
        courses = list(self.courses_collection.find({}, {'_id': 0}).sort('course_code', 1))
        return courses
    
    def get_course_by_code(self, course_code):
        return self.courses_collection.find_one({'course_code': course_code}, {'_id': 0})
    
    def get_students_in_course(self, course_code):
        enrollments = list(self.enrollments_collection.find({'course_code': course_code}))
        student_ids = [e['student_id'] for e in enrollments]
        
        students = list(self.students_collection.find(
            {'student_id': {'$in': student_ids}},
            {'_id': 0}
        ).sort('student_id', 1))
        
        for student in students:
            embedding = self.embeddings_collection.find_one({'student_id': student['student_id']})
            student['embedding_count'] = len(embedding.get('embeddings', [])) if embedding else 0
        
        return students
    
    def get_students_by_year(self, degree_year=None):
        query = {}
        if degree_year:
            query['degree_year'] = int(degree_year)
        
        students = list(self.students_collection.find(query, {'_id': 0}).sort('student_id', 1))
        
        for student in students:
            embedding = self.embeddings_collection.find_one({'student_id': student['student_id']})
            student['embedding_count'] = len(embedding.get('embeddings', [])) if embedding else 0
        
        return students
    
    def delete_course(self, course_code):
        self.students_collection.delete_many({'course_code': course_code})
        self.courses_collection.delete_one({'course_code': course_code})
        return {'success': True, 'message': f'Course {course_code} deleted'}
    
    def close(self):
        self.client.close()
