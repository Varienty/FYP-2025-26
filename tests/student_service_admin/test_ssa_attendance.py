"""
Test script for Student Service Administrator - Attendance Features
Tests: US29 (Audit Log), US31 (Mark Attendance), US33 (Adjust Attendance), US34 (Daily Summary)
"""

import requests
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:5008"

def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")

def test_daily_summary():
    """Test US34 - Daily Attendance Summary"""
    print_test_header("Daily Summary Dashboard (US34)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/attendance/daily-summary",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✓ PASS | Daily summary retrieved")
                print(f"  Attendance Rate: {data.get('attendanceRate')}%")
                print(f"  Present: {data.get('presentCount')}")
                print(f"  Absent: {data.get('absentCount')}")
                print(f"  Late: {data.get('lateCount')}")
                print(f"  Total Students: {data.get('totalStudents')}")
                
                if data.get('systemicIssues'):
                    print(f"  Systemic Issues: {len(data['systemicIssues'])} detected")
                
                return True
            else:
                print(f"✗ FAIL | Failed to get summary")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def test_get_students_for_marking():
    """Test US31 - Get Student List"""
    print_test_header("Get Students for Marking (US31)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/attendance/mark",
            params={'moduleId': 'CS101', 'date': '2024-12-05'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('students'):
                students = data['students']
                print(f"✓ PASS | Retrieved {len(students)} students")
                print(f"  Sample: {students[0]['id']} - {students[0]['name']}")
                return True
            else:
                print(f"✗ FAIL | No students returned")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def test_mark_attendance():
    """Test US31 - Mark Attendance"""
    print_test_header("Mark Attendance (US31)")
    
    attendance_records = [
        {'studentId': 'STU0001', 'date': '2024-12-05', 'status': 'present', 'remarks': ''},
        {'studentId': 'STU0002', 'date': '2024-12-05', 'status': 'absent', 'remarks': 'Sick'},
        {'studentId': 'STU0003', 'date': '2024-12-05', 'status': 'late', 'remarks': 'Traffic'},
        {'studentId': 'STU0004', 'date': '2024-12-05', 'status': 'present', 'remarks': ''},
        {'studentId': 'STU0005', 'date': '2024-12-05', 'status': 'present', 'remarks': ''}
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/attendance/mark",
            json=attendance_records,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✓ PASS | Marked attendance for {data.get('count', 0)} students")
                print(f"  Message: {data.get('message')}")
                return True
            else:
                print(f"✗ FAIL | Failed to mark attendance")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def test_adjust_attendance():
    """Test US33 - Adjust Attendance Record"""
    print_test_header("Adjust Attendance (US33)")
    
    adjustment = {
        'studentId': 'STU0001',
        'moduleId': 'CS101',
        'date': '2024-12-02',
        'previousStatus': 'absent',
        'newStatus': 'present',
        'reason': 'System error - student was actually present',
        'notes': 'Verified with class recording',
        'editor': 'admin'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/attendance/adjust",
            json=adjustment,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✓ PASS | Attendance record adjusted")
                print(f"  Change: {adjustment['previousStatus']} → {adjustment['newStatus']}")
                print(f"  Reason: {adjustment['reason']}")
                return True
            else:
                print(f"✗ FAIL | Adjustment failed")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def test_search_attendance():
    """Test searching for attendance records"""
    print_test_header("Search Attendance Record")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/attendance/search",
            params={'studentId': 'STU0001', 'date': '2024-12-02'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('record'):
                record = data['record']
                print(f"✓ PASS | Found attendance record")
                print(f"  Student: {record['studentId']} - {record['name']}")
                print(f"  Class: {record['class']}")
                print(f"  Status: {record['status']}")
                return True
            else:
                print(f"✗ FAIL | No record found")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def test_audit_log():
    """Test US29 - Audit Log"""
    print_test_header("Audit Log (US29)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/audit-log",
            params={'start': '2024-12-01', 'end': '2024-12-05'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('records'):
                records = data['records']
                print(f"✓ PASS | Retrieved {len(records)} audit log entries")
                
                if records:
                    sample = records[0]
                    print(f"  Sample Entry:")
                    print(f"    Editor: {sample.get('editor')}")
                    print(f"    Student: {sample.get('studentId')}")
                    print(f"    Change: {sample.get('previousValue')} → {sample.get('newValue')}")
                    print(f"    Reason: {sample.get('reason')}")
                
                return True
            else:
                print(f"✗ FAIL | No audit records returned")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def main():
    """Run all attendance tests"""
    print("\n" + "="*60)
    print("STUDENT SERVICE ADMINISTRATOR - ATTENDANCE TESTS")
    print("="*60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    
    # Check if controller is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except:
        print(f"\n⚠ ERROR: Controller not running!")
        print(f"Please start: python 'Student Service Administrator/controller/ssa_main.py'")
        sys.exit(1)
    
    results = []
    
    # Run tests
    results.append(('Daily Summary (US34)', test_daily_summary()))
    results.append(('Get Students (US31)', test_get_students_for_marking()))
    results.append(('Mark Attendance (US31)', test_mark_attendance()))
    results.append(('Adjust Attendance (US33)', test_adjust_attendance()))
    results.append(('Search Attendance', test_search_attendance()))
    results.append(('Audit Log (US29)', test_audit_log()))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} | {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
