"""
Test database connection
Run this to verify your .env configuration is correct
"""
import sys
import os

# Add project root to path so we can import common modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.db_utils import get_connection, query_all

def test_connection():
    print("Testing database connection...")
    print("-" * 50)
    
    try:
        # Test 1: Get connection
        conn = get_connection()
        print("✓ Database connection successful!")
        
        # Test 2: Query lecturers table
        print("\nTesting query: SELECT * FROM lecturers LIMIT 3")
        lecturers = query_all("SELECT * FROM lecturers LIMIT 3")
        print(f"✓ Found {len(lecturers)} lecturers:")
        for lec in lecturers:
            print(f"  - {lec.get('first_name')} {lec.get('last_name')} ({lec.get('email')})")
        
        # Test 3: Query students table
        print("\nTesting query: SELECT * FROM students LIMIT 3")
        students = query_all("SELECT * FROM students LIMIT 3")
        print(f"✓ Found {len(students)} students:")
        for stu in students:
            print(f"  - {stu.get('first_name')} {stu.get('last_name')} ({stu.get('student_id')})")
        
        # Test 4: Query classes table
        print("\nTesting query: SELECT * FROM modules LIMIT 3")
        classes = query_all("SELECT * FROM modules LIMIT 3")
        print(f"✓ Found {len(classes)} classes:")
        for cls in classes:
            print(f"  - {cls.get('module_code')}: {cls.get('module_name')}")
        
        conn.close()
        
        print("\n" + "=" * 50)
        print("✓ All database tests passed!")
        print("=" * 50)
        print("\nYour database is ready to use!")
        
    except Exception as e:
        print(f"\n✗ Database connection failed!")
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check that MySQL is running")
        print("2. Verify your .env file has correct credentials")
        print("3. Ensure 'student_attendance' database exists")
        print("4. Check that schema.sql and sample_data.sql were imported")
        return False
    
    return True

if __name__ == "__main__":
    test_connection()
