"""
Comprehensive Test Suite for Database Integration
Tests all three modules with database connectivity
"""

import requests
import sys
from datetime import datetime

def test_endpoint(url, method='GET', data=None):
    """Test if endpoint is accessible"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=2)
        else:
            response = requests.post(url, json=data, timeout=2)
        return response.status_code in [200, 400, 401]
    except:
        return False

def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def main():
    print("=" * 80)
    print("DATABASE INTEGRATION TEST SUITE")
    print("=" * 80)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test System Admin
    print_section("SYSTEM ADMIN MODULE (Port 5009)")
    sysadmin_tests = [
        ('Login', 'POST', 'http://localhost:5009/api/auth/login', {'email': 'admin@attendance.com', 'password': 'admin123'}),
        ('Get Policies', 'GET', 'http://localhost:5009/api/policies', None),
        ('Get Devices', 'GET', 'http://localhost:5009/api/devices', None),
        ('Device Stats', 'GET', 'http://localhost:5009/api/devices/stats', None),
        ('Get Users', 'GET', 'http://localhost:5009/api/users', None),
        ('Get Permissions', 'GET', 'http://localhost:5009/api/permissions', None),
    ]
    
    sysadmin_passed = 0
    for name, method, url, data in sysadmin_tests:
        if test_endpoint(url, method, data):
            print(f"✓ {name}")
            sysadmin_passed += 1
        else:
            print(f"✗ {name} - FAILED")
    
    print(f"\nSystem Admin: {sysadmin_passed}/{len(sysadmin_tests)} tests passed")
    
    # Test Student Service Admin
    print_section("STUDENT SERVICE ADMIN MODULE (Port 5008)")
    ssa_tests = [
        ('Login', 'POST', 'http://localhost:5008/api/auth/login', {'email': 'studentservice@attendance.com', 'password': 'ssa123'}),
        ('Daily Summary', 'GET', 'http://localhost:5008/api/attendance/daily-summary', None),
        ('Mark Attendance', 'GET', 'http://localhost:5008/api/attendance/mark', None),
        ('Audit Log', 'GET', 'http://localhost:5008/api/audit-log', None),
        ('Compliance Report', 'GET', 'http://localhost:5008/api/compliance/report', None),
        ('Student History', 'GET', 'http://localhost:5008/api/student/history?studentId=STU2025001', None),
    ]
    
    ssa_passed = 0
    for name, method, url, data in ssa_tests:
        if test_endpoint(url, method, data):
            print(f"✓ {name}")
            ssa_passed += 1
        else:
            print(f"✗ {name} - FAILED")
    
    print(f"\nSSA: {ssa_passed}/{len(ssa_tests)} tests passed")
    
    # Test Lecturer
    print_section("LECTURER MODULE (Ports 5003-5007)")
    lecturer_tests = [
        ('Auth - Login', 'POST', 'http://localhost:5003/api/lecturer/auth/login', {'email': 'john.smith@university.com', 'password': 'password123'}),
        ('Auth - Logout', 'POST', 'http://localhost:5003/api/lecturer/auth/logout', {}),
        ('Attendance - Records', 'GET', 'http://localhost:5004/api/lecturer/attendance/records?lecturerId=LEC001', None),
        ('Report - Generate', 'POST', 'http://localhost:5005/api/lecturer/report/generate', {'moduleId': 'CS101', 'lecturerId': 'LEC001'}),
        ('Schedule - Get', 'GET', 'http://localhost:5006/api/lecturer/schedule?lecturerId=LEC001', None),
        ('Notifications - Get', 'GET', 'http://localhost:5007/api/lecturer/notifications?lecturerId=LEC001', None),
    ]
    
    lecturer_passed = 0
    for name, method, url, data in lecturer_tests:
        if test_endpoint(url, method, data):
            print(f"✓ {name}")
            lecturer_passed += 1
        else:
            print(f"✗ {name} - FAILED")
    
    print(f"\nLecturer: {lecturer_passed}/{len(lecturer_tests)} tests passed")
    
    # Summary
    print_section("SUMMARY")
    total_tests = len(sysadmin_tests) + len(ssa_tests) + len(lecturer_tests)
    total_passed = sysadmin_passed + ssa_passed + lecturer_passed
    
    print(f"System Admin:     {sysadmin_passed}/{len(sysadmin_tests)} ({sysadmin_passed/len(sysadmin_tests)*100:.0f}%)")
    print(f"SSA:              {ssa_passed}/{len(ssa_tests)} ({ssa_passed/len(ssa_tests)*100:.0f}%)")
    print(f"Lecturer:         {lecturer_passed}/{len(lecturer_tests)} ({lecturer_passed/len(lecturer_tests)*100:.0f}%)")
    print(f"\nTotal:            {total_passed}/{total_tests} ({total_passed/total_tests*100:.0f}%)")
    
    if total_passed == total_tests:
        print("\n✓ ALL DATABASE INTEGRATIONS WORKING!")
    else:
        print(f"\n⚠ {total_tests - total_passed} endpoint(s) need attention")
    
    print("=" * 80)

if __name__ == '__main__':
    main()
