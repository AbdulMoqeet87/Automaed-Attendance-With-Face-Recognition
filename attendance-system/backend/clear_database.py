"""
Clear all students and embeddings from database
Run this when switching face recognition methods
"""
from data_module.database import Database

def clear_all_data():
    db = Database()
    
    # Delete all students
    result_students = db.students_collection.delete_many({})
    print(f"Deleted {result_students.deleted_count} students")
    
    # Delete all embeddings
    result_embeddings = db.embeddings_collection.delete_many({})
    print(f"Deleted {result_embeddings.deleted_count} embeddings")
    
    # Optionally delete attendance records
    delete_attendance = input("\nDelete attendance records too? (y/n): ").lower()
    if delete_attendance == 'y':
        result_attendance = db.attendance_collection.delete_many({})
        print(f"Deleted {result_attendance.deleted_count} attendance records")
    
    print("\n✓ Database cleared! You can now register students with FaceNet embeddings.")

if __name__ == "__main__":
    print("="*70)
    print("WARNING: This will delete all students and embeddings!")
    print("="*70)
    confirm = input("\nAre you sure? Type 'yes' to continue: ")
    
    if confirm.lower() == 'yes':
        clear_all_data()
    else:
        print("Operation cancelled.")
