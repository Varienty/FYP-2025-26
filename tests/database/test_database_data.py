"""
Comprehensive test script to verify all database data after import.
Tests tables, counts, and relationships to ensure data integrity.
"""

import mysql.connector
from common.db_utils import get_connection
from datetime import datetime

def test_database():
    """Run comprehensive database tests"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("=" * 70)
    print("DATABASE DATA VERIFICATION TEST")
    print("=" * 70)
    print(f"Test run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test queries
    tests = [
        {
            'name': 'System Admins',
            'query': 'SELECT COUNT(*) as count FROM system_admins',
            'expected_min': 2
        },
        {
            'name': 'Student Service Admins',
            'query': 'SELECT COUNT(*) as count FROM student_service_admins',
            'expected_min': 2
        },
        {
            'name': 'Lecturers',
            'query': 'SELECT COUNT(*) as count FROM lecturers',
            'expected_min': 3
        },
        {
            'name': 'Students',
            'query': 'SELECT COUNT(*) as count FROM students',
            'expected_min': 20
        },
        {
            'name': 'Classes',
            'query': 'SELECT COUNT(*) as count FROM modules',
            'expected_min': 3
        },
        {
            'name': 'Student Enrollments',
            'query': 'SELECT COUNT(*) as count FROM student_enrollments',
            'expected_min': 30
        },
        {
            'name': 'Timetable Entries',
            'query': 'SELECT COUNT(*) as count FROM timetable',
            'expected_min': 5
        },
        {
            'name': 'Attendance Sessions',
            'query': 'SELECT COUNT(*) as count FROM attendance_sessions',
            'expected_min': 9
        },
        {
            'name': 'Attendance Records',
            'query': 'SELECT COUNT(*) as count FROM attendance',
            'expected_min': 100
        },
        {
            'name': 'Medical Certificates',
            'query': 'SELECT COUNT(*) as count FROM medical_certificates',
            'expected_min': 6
        },
        {
            'name': 'Notifications',
            'query': 'SELECT COUNT(*) as count FROM notifications',
            'expected_min': 9
        },
        {
            'name': 'Audit Logs',
            'query': 'SELECT COUNT(*) as count FROM audit_logs',
            'expected_min': 6
        },
        {
            'name': 'System Alerts',
            'query': 'SELECT COUNT(*) as count FROM system_alerts',
            'expected_min': 3
        },
        {
            'name': 'Devices',
            'query': 'SELECT COUNT(*) as count FROM devices',
            'expected_min': 6
        },
        {
            'name': 'Policies',
            'query': 'SELECT COUNT(*) as count FROM policies',
            'expected_min': 2
        },
        {
            'name': 'Attendance Policies',
            'query': 'SELECT COUNT(*) as count FROM attendance_policies',
            'expected_min': 2
        },
        {
            'name': 'Reports',
            'query': 'SELECT COUNT(*) as count FROM reports',
            'expected_min': 3
        },
        {
            'name': 'System Config',
            'query': 'SELECT COUNT(*) as count FROM system_config',
            'expected_min': 9
        }
    ]
    
    print("TABLE COUNTS:")
    print("-" * 70)
    
    for test in tests:
        try:
            cursor.execute(test['query'])
            result = cursor.fetchone()
            count = result['count']
            
            if count >= test['expected_min']:
                status = "✓ PASS"
                tests_passed += 1
                color = ""
            else:
                status = "✗ FAIL"
                tests_failed += 1
                color = ""
            
            print(f"{status} | {test['name']:<30} | Count: {count:>4} (expected ≥ {test['expected_min']})")
            
        except Exception as e:
            print(f"✗ FAIL | {test['name']:<30} | Error: {str(e)}")
            tests_failed += 1
    
    # Detailed sample data checks
    print("\n" + "=" * 70)
    print("SAMPLE DATA VERIFICATION:")
    print("-" * 70)
    
    # Check students data
    cursor.execute("SELECT student_id, first_name, last_name, email FROM students ORDER BY id LIMIT 5")
    students = cursor.fetchall()
    print(f"\n✓ First 5 Students:")
    for s in students:
        print(f"  - {s['student_id']}: {s['first_name']} {s['last_name']} ({s['email']})")
    
    # Check attendance statistics
    cursor.execute("""
        SELECT 
            status, 
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM attendance), 2) as percentage
        FROM attendance 
        GROUP BY status
        ORDER BY count DESC
    """)
    attendance_stats = cursor.fetchall()
    print(f"\n✓ Attendance Status Distribution:")
    for stat in attendance_stats:
        print(f"  - {stat['status'].capitalize():<10}: {stat['count']:>3} ({stat['percentage']:>5}%)")
    
    # Check recent sessions
    cursor.execute("""
        SELECT 
            c.module_code,
            c.module_name,
            a.session_date,
            a.status,
            a.total_students
        FROM attendance_sessions a
        JOIN modules c ON a.module_id = c.id
        ORDER BY a.session_date DESC
        LIMIT 5
    """)
    sessions = cursor.fetchall()
    print(f"\n✓ Recent Attendance Sessions:")
    for sess in sessions:
        print(f"  - {sess['session_date']} | {sess['module_code']}: {sess['module_name']} | Students: {sess['total_students']} | {sess['status']}")
    
    # Check medical certificates
    cursor.execute("""
        SELECT 
            mc.id,
            s.student_id,
            s.first_name,
            mc.start_date,
            mc.end_date,
            mc.status
        FROM medical_certificates mc
        JOIN students s ON mc.student_id = s.id
        ORDER BY mc.uploaded_at DESC
        LIMIT 5
    """)
    certificates = cursor.fetchall()
    print(f"\n✓ Recent Medical Certificates:")
    for cert in certificates:
        print(f"  - MC#{cert['id']} | {cert['student_id']}: {cert['first_name']} | {cert['start_date']} to {cert['end_date']} | {cert['status']}")
    
    # Check notifications
    cursor.execute("""
        SELECT 
            recipient_type,
            notification_type,
            title,
            is_read
        FROM notifications
        ORDER BY created_at DESC
        LIMIT 5
    """)
    notifications = cursor.fetchall()
    print(f"\n✓ Recent Notifications:")
    for notif in notifications:
        read_status = "Read" if notif['is_read'] else "Unread"
        print(f"  - [{notif['recipient_type']}] {notif['title']} ({notif['notification_type']}) - {read_status}")
    
    # Check devices
    cursor.execute("SELECT id, name, type, status, last_seen FROM devices ORDER BY last_seen DESC")
    devices = cursor.fetchall()
    print(f"\n✓ Registered Devices:")
    for dev in devices:
        print(f"  - {dev['id']:<15} | {dev['name']:<25} | {dev['type']:<10} | {dev['status']:<10} | Last seen: {dev['last_seen']}")
    
    # Foreign key integrity checks
    print("\n" + "=" * 70)
    print("FOREIGN KEY INTEGRITY CHECKS:")
    print("-" * 70)
    
    fk_tests = [
        {
            'name': 'Students → Created By Admin',
            'query': """
                SELECT COUNT(*) as count 
                FROM students s 
                LEFT JOIN student_service_admins ssa ON s.created_by_admin_id = ssa.id 
                WHERE s.created_by_admin_id IS NOT NULL AND ssa.id IS NULL
            """
        },
        {
            'name': 'Enrollments → Student & Class',
            'query': """
                SELECT COUNT(*) as count 
                FROM student_enrollments se 
                LEFT JOIN students s ON se.student_id = s.id 
                LEFT JOIN modules c ON se.module_id = c.id 
                WHERE s.id IS NULL OR c.id IS NULL
            """
        },
        {
            'name': 'Attendance → Student & Class',
            'query': """
                SELECT COUNT(*) as count 
                FROM attendance a 
                LEFT JOIN students s ON a.student_id = s.id 
                LEFT JOIN modules c ON a.module_id = c.id 
                WHERE s.id IS NULL OR c.id IS NULL
            """
        }
    ]
    
    fk_passed = 0
    fk_failed = 0
    
    for test in fk_tests:
        cursor.execute(test['query'])
        result = cursor.fetchone()
        orphaned = result['count']
        
        if orphaned == 0:
            print(f"✓ PASS | {test['name']:<40} | No orphaned records")
            fk_passed += 1
        else:
            print(f"✗ FAIL | {test['name']:<40} | {orphaned} orphaned records found")
            fk_failed += 1
    
    # Final summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY:")
    print("-" * 70)
    print(f"Table Count Tests:     {tests_passed} passed, {tests_failed} failed")
    print(f"FK Integrity Tests:    {fk_passed} passed, {fk_failed} failed")
    print(f"Total:                 {tests_passed + fk_passed} passed, {tests_failed + fk_failed} failed")
    print("=" * 70)
    
    if tests_failed == 0 and fk_failed == 0:
        print("✓ ALL TESTS PASSED! Database is ready for production-like testing.")
    else:
        print("✗ SOME TESTS FAILED. Please review the data.")
    
    print()
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    try:
        test_database()
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {str(e)}")
        print("Make sure the database is running and .env is configured correctly.")
