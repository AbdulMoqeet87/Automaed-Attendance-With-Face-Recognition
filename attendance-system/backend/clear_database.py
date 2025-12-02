"""
Clear Database Script
Removes all data from the attendance system database collections.
Use this when migrating from the old schema to the new course-centric schema.
"""
from data_module.database import Database

def clear_all_data():
    db = Database()
    
    try:
        # Delete all students
        result_students = db.students_collection.delete_many({})
        print(f"Deleted {result_students.deleted_count} students")
        
        # Delete all embeddings
        result_embeddings = db.embeddings_collection.delete_many({})
        print(f"Deleted {result_embeddings.deleted_count} embeddings")
        
        # Delete all enrollments
        result_enrollments = db.enrollments_collection.delete_many({})
        print(f"Deleted {result_enrollments.deleted_count} enrollments")
        
        # Delete all courses
        result_courses = db.courses_collection.delete_many({})
        print(f"Deleted {result_courses.deleted_count} courses")
        
        # Optionally delete attendance records
        delete_attendance = input("\nDelete attendance records too? (y/n): ").lower()
        if delete_attendance == 'y':
            result_attendance = db.attendance_collection.delete_many({})
            print(f"Deleted {result_attendance.deleted_count} attendance records")
        
        print("\n✅ Database cleared successfully!")
        print("\nNew Workflow:")
        print("1. Add students globally in 'Manage Students' tab with degree year")
        print("2. Create courses via the Courses tab")
        print("3. Enroll existing students in courses by selecting from list")
        print("4. Take attendance using the Take Attendance tab")
        
    except Exception as e:
        print(f"\n❌ Error clearing database: {str(e)}")

if __name__ == "__main__":
    print("="*70)
    print("WARNING: This will delete all data from the new schema!")
    print("Collections: students, embeddings, enrollments, courses, attendance")
    print("="*70)
    confirm = input("\nAre you sure? Type 'yes' to continue: ")
    
    if confirm.lower() == 'yes':
        clear_all_data()
    else:
        print("Operation cancelled.")
