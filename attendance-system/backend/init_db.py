from data_module.database import Database

def main():
    print("Initializing database with sample data...")
    
    db = Database()
    
    # Initialize sample students
    result = db.initialize_sample_data()
    print(result['message'])
    
    # Display statistics
    stats = db.get_statistics()
    print("\nDatabase Statistics:")
    print(f"  Total Students: {stats['total_students']}")
    print(f"  Students with Embeddings: {stats['students_with_embeddings']}")
    print(f"  Attendance Records: {stats['total_attendance_records']}")
    
    # List all students
    print("\nRegistered Students:")
    students = db.get_all_students()
    for student in students:
        print(f"  - {student['student_id']}: {student['name']}")
    
    db.close()
    print("\nInitialization complete!")

if __name__ == '__main__':
    main()
