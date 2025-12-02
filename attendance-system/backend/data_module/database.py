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
        self.embeddings_collection = self.db['embeddings']
        self.attendance_collection = self.db['attendance']
        
        # Create indexes for better performance
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for optimized queries"""
        self.students_collection.create_index('student_id', unique=True)
        self.embeddings_collection.create_index('student_id')
        self.attendance_collection.create_index([('class_name', 1), ('timestamp', -1)])
    
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
    
    def get_all_embeddings(self):
        """
        Retrieve all stored embeddings organized by student ID
        Returns: Dict of {student_id: [embeddings]}
        """
        embeddings_dict = {}
        embeddings_cursor = self.embeddings_collection.find({})
        
        for doc in embeddings_cursor:
            student_id = doc['student_id']
            # Convert stored list back to numpy array
            embeddings = [np.array(emb) for emb in doc['embeddings']]
            embeddings_dict[student_id] = embeddings
        
        return embeddings_dict
    
    def add_student(self, student_id, name, embeddings=None, enrolled_courses=None):
        """
        Add a new student to the database
        Args:
            student_id: Unique student identifier
            name: Student's name
            embeddings: List of face embeddings (optional)
            enrolled_courses: List of course codes student is enrolled in (optional)
        """
        # Check if student already exists
        existing = self.students_collection.find_one({'student_id': student_id})
        if existing:
            raise ValueError(f"Student with ID {student_id} already exists")
        
        # Create student record
        student = {
            'student_id': student_id,
            'name': name,
            'enrolled_courses': enrolled_courses if enrolled_courses else [],
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
        
        # Convert datetime objects to ISO format strings
        for record in records:
            if 'timestamp' in record and isinstance(record['timestamp'], datetime):
                record['timestamp'] = record['timestamp'].isoformat()
            if 'created_at' in record and isinstance(record['created_at'], datetime):
                record['created_at'] = record['created_at'].isoformat()
        
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
            {'student_id': 'bscs22001', 'name': 'Ali Ahmed'},
            {'student_id': 'bscs22002', 'name': 'Sara Khan'},
            {'student_id': 'bscs22003', 'name': 'Hassan Ali'},
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
    
    def close(self):
        """Close database connection"""
        self.client.close()
