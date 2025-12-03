"""
Test MongoDB Atlas connection
"""
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    try:
        # Get MongoDB URI from environment
        mongo_uri = os.getenv('MONGODB_URI')
        
        if not mongo_uri:
            print("❌ ERROR: MONGODB_URI not found in environment variables")
            return False
        
        print(f"🔄 Connecting to MongoDB Atlas...")
        print(f"   URI: {mongo_uri[:50]}...")
        
        # Create client with timeout
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        
        # Get database
        db = client['AttendanceSystem']
        print(f"\n📊 Database: {db.name}")
        
        # List collections
        collections = db.list_collection_names()
        print(f"📋 Collections: {collections if collections else 'No collections yet'}")
        
        # Get database stats
        stats = db.command("dbStats")
        print(f"\n📈 Database Stats:")
        print(f"   - Collections: {stats.get('collections', 0)}")
        print(f"   - Data Size: {stats.get('dataSize', 0)} bytes")
        print(f"   - Storage Size: {stats.get('storageSize', 0)} bytes")
        
        # Test write operation (create a test document)
        test_collection = db['connection_test']
        test_doc = {'test': True, 'timestamp': str(os.popen('date /t').read().strip())}
        result = test_collection.insert_one(test_doc)
        print(f"\n✅ Test write successful! Document ID: {result.inserted_id}")
        
        # Clean up test document
        test_collection.delete_one({'_id': result.inserted_id})
        print("🧹 Test document cleaned up")
        
        client.close()
        print("\n✅ All tests passed! MongoDB connection is working properly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
