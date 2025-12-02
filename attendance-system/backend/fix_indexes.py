"""
Fix Database Indexes
Drops old indexes and creates new ones for the course-centric schema
"""
from data_module.database import Database

def fix_indexes():
    db = Database()
    
    print("Fixing database indexes...")
    
    try:
        # Get current indexes
        print("\nCurrent indexes on students collection:")
        for index in db.students_collection.list_indexes():
            print(f"  - {index['name']}: {index.get('key', {})}")
        
        # Drop the old student_id unique index if it exists
        try:
            db.students_collection.drop_index('student_id_1')
            print("\n✓ Dropped old 'student_id_1' index")
        except Exception as e:
            if 'index not found' in str(e).lower():
                print("\n• Old index already removed")
            else:
                print(f"\n⚠ Could not drop old index: {e}")
        
        # Drop all indexes except _id
        print("\nDropping all indexes except _id...")
        db.students_collection.drop_indexes()
        print("✓ All custom indexes dropped")
        
        # Recreate the correct composite index
        print("\nRecreating correct indexes...")
        db._create_indexes()
        print("✓ New indexes created")
        
        # Verify new indexes
        print("\nNew indexes on students collection:")
        for index in db.students_collection.list_indexes():
            print(f"  - {index['name']}: {index.get('key', {})}")
        
        print("\n✅ Index fix completed successfully!")
        print("\nYou can now add students with the same student_id to different courses.")
        
    except Exception as e:
        print(f"\n❌ Error fixing indexes: {str(e)}")

if __name__ == "__main__":
    fix_indexes()
