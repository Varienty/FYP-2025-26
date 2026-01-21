"""
Test script for Lecturer module functionality
Tests authentication, dashboard, attendance, reports, schedule, and notifications
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5003"  # Lecturer auth controller port
session_token = None

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(test_name, success, message="", data=None):
    """Print test result"""
    status = "✓ PASS" if success else "✗ FAIL"
    print(f"{status} | {test_name}")
    if message:
        print(f"       {message}")
    if data and isinstance(data, dict):
        for key, value in data.items():
            print(f"       - {key}: {value}")
    print()

def test_lecturer_login():
    """Test US12 - Lecturer Login"""
    global session_token
    
    print_section("TEST 1: LECTURER LOGIN (US12)")
    
    # Test valid login - John Smith (LEC001)
    payload = {
        "email": "john.smith@university.com",
        "password": "password"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/lecturer/auth/login", json=payload, timeout=5)
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            user = data.get('user', {})
            session_token = data.get('token')
            lecturer_info = {
                "Name": f"{user.get('first_name')} {user.get('last_name')}",
                "Email": user.get('email'),
                "Department": user.get('department'),
                "Lecturer ID": user.get('lecturer_id'),
                "Session Token": session_token[:20] + "..." if session_token else "None"
            }
            print_result("Valid Login", True, "John Smith logged in successfully", lecturer_info)
            return True
        else:
            print_result("Valid Login", False, f"Login failed: {data.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_result("Valid Login", False, "Connection error - Make sure lecturer_auth_controller.py is running on port 5003")
        return False
    except Exception as e:
        print_result("Valid Login", False, f"Error: {str(e)}")
        return False

def test_invalid_login():
    """Test login with invalid credentials"""
    print_section("TEST 2: INVALID LOGIN ATTEMPTS")
    
    tests = [
        {
            "name": "Wrong Password",
            "payload": {"email": "john.smith@university.com", "password": "wrongpassword"}
        },
        {
            "name": "Non-existent User",
            "payload": {"email": "nonexistent@university.com", "password": "password"}
        },
        {
            "name": "Empty Email",
            "payload": {"email": "", "password": "password"}
        },
        {
            "name": "Empty Password",
            "payload": {"email": "john.smith@university.com", "password": ""}
        }
    ]
    
    all_passed = True
    for test in tests:
        try:
            response = requests.post(f"{BASE_URL}/api/lecturer/auth/login", json=test['payload'], timeout=5)
            data = response.json()
            
            # Should fail (success=False or error status)
            if response.status_code >= 400 or not data.get('success'):
                print_result(test['name'], True, f"Correctly rejected: {data.get('message', 'Invalid credentials')}")
            else:
                print_result(test['name'], False, "Should have been rejected but was accepted")
                all_passed = False
                
        except Exception as e:
            print_result(test['name'], False, f"Error: {str(e)}")
            all_passed = False
    
    return all_passed

def test_lecturer_data():
    """Test lecturer database data"""
    print_section("TEST 3: LECTURER DATABASE VERIFICATION")
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from common.db_utils import query_all, query_one
    
    try:
        # Get all lecturers
        lecturers = query_all("SELECT lecturer_id, first_name, last_name, email, department FROM lecturers ORDER BY id")
        print(f"✓ Found {len(lecturers)} lecturers in database:")
        for lec in lecturers:
            print(f"  - {lec['lecturer_id']}: {lec['first_name']} {lec['last_name']} ({lec['email']}) - {lec['department']}")
        
        # Get classes for LEC001 (John Smith)
        classes = query_all("""
            SELECT c.id, c.module_code, c.module_name, c.semester, c.academic_year,
                   COUNT(DISTINCT se.student_id) as enrolled_students
            FROM modules c
            LEFT JOIN student_enrollments se ON c.id = se.module_id
            WHERE c.lecturer_id = (SELECT id FROM lecturers WHERE lecturer_id = 'LEC001')
            GROUP BY c.id
        """)
        
        print(f"\n✓ John Smith (LEC001) teaches {len(classes)} class(es):")
        for cls in classes:
            print(f"  - {cls['module_code']}: {cls['module_name']} ({cls['semester']}, {cls['academic_year']}) - {cls['enrolled_students']} students")
        
        # Get recent sessions for LEC001
        sessions = query_all("""
            SELECT a.id, a.session_date, c.module_code, c.module_name, a.status, a.total_students
            FROM attendance_sessions a
            JOIN modules c ON a.module_id = c.id
            WHERE a.lecturer_id = (SELECT id FROM lecturers WHERE lecturer_id = 'LEC001')
            ORDER BY a.session_date DESC
            LIMIT 5
        """)
        
        print(f"\n✓ Recent attendance sessions for LEC001 ({len(sessions)} sessions):")
        for sess in sessions:
            print(f"  - {sess['session_date']} | {sess['module_code']}: {sess['module_name']} | {sess['status']} | {sess['total_students']} students")
        
        # Get notifications for LEC001
        notifications = query_all("""
            SELECT notification_type, title, message, is_read, created_at
            FROM notifications
            WHERE recipient_type = 'lecturer' 
            AND recipient_id = (SELECT id FROM lecturers WHERE lecturer_id = 'LEC001')
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        print(f"\n✓ Notifications for LEC001 ({len(notifications)} notifications):")
        for notif in notifications:
            read_status = "Read" if notif['is_read'] else "Unread"
            print(f"  - [{notif['notification_type']}] {notif['title']} - {read_status}")
        
        print_result("Database Verification", True, f"All data retrieved successfully")
        return True
        
    except Exception as e:
        print_result("Database Verification", False, f"Error: {str(e)}")
        return False

def test_logout():
    """Test US19 - Lecturer Logout"""
    print_section("TEST 4: LECTURER LOGOUT (US19)")
    
    if not session_token:
        print_result("Logout", False, "No active session token")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {session_token}"}
        response = requests.post(f"{BASE_URL}/api/lecturer/auth/logout", headers=headers, timeout=5)
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            print_result("Logout", True, "Logged out successfully")
            return True
        else:
            print_result("Logout", False, f"Logout failed: {data.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print_result("Logout", False, f"Error: {str(e)}")
        return False

def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} | {test_name}")
    
    print("-" * 70)
    print(f"Total: {passed}/{total} tests passed ({passed*100//total}%)")
    
    if passed == total:
        print("✓ ALL TESTS PASSED!")
    else:
        print(f"✗ {total - passed} test(s) failed")
    
    print("=" * 70)

def main():
    """Run all lecturer tests"""
    print("\n" + "=" * 70)
    print("LECTURER MODULE TEST SUITE")
    print("=" * 70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing against: {BASE_URL}")
    print()
    print("PREREQUISITES:")
    print("  1. Database is running and populated with test data")
    print("  2. lecturer_auth_controller.py is running on port 5003")
    print("     Run: python Lecturer/controller/lecturer_auth_controller.py")
    print("\nStarting tests...")
    
    results = {}
    
    # Run tests
    results['Lecturer Login'] = test_lecturer_login()
    results['Invalid Login Attempts'] = test_invalid_login()
    results['Database Verification'] = test_lecturer_data()
    results['Lecturer Logout'] = test_logout()
    
    # Print summary
    print_summary(results)

if __name__ == "__main__":
    main()
