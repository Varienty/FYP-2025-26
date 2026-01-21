"""
Comprehensive test script for all Lecturer module features
Tests schedule, attendance, reports, and notifications
"""

import requests
import json
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from common.db_utils import query_all, query_one

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
    if data:
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"       - {key}: {value}")
        elif isinstance(data, list):
            for item in data:
                print(f"       - {item}")
    print()

# ============================================================================
# SCHEDULE TESTS (US16)
# ============================================================================

def test_schedule_controller():
    """Test US16 - Class Schedule Viewing"""
    print_section("TEST: LECTURER SCHEDULE (US16)")
    
    BASE_URL = "http://localhost:5006"
    
    try:
        # Test 1: Get full schedule for LEC001
        response = requests.get(
            f"{BASE_URL}/api/lecturer/schedule",
            params={"lecturerId": "LEC001"},
            timeout=5
        )
        
        if response.status_code != 200:
            print_result("Get Full Schedule", False, f"HTTP {response.status_code}")
            return False
            
        data = response.json()
        
        if not data.get('success'):
            print_result("Get Full Schedule", False, data.get('message', 'Unknown error'))
            return False
        
        classes = data.get('modules', [])
        print_result("Get Full Schedule", True, f"Found {len(classes)} scheduled classes")
        
        for cls in classes[:3]:  # Show first 3
            print(f"       {cls['day']} {cls['startTime']}-{cls['endTime']}: {cls['moduleCode']} in {cls['room']}")
        
        # Test 2: Get today's schedule
        response2 = requests.get(
            f"{BASE_URL}/api/lecturer/schedule/today",
            params={"lecturerId": "LEC001"},
            timeout=5
        )
        
        if response2.status_code == 200:
            data2 = response2.json()
            today_classes = data2.get('modules', [])
            print_result("Get Today's Schedule", True, f"Found {len(today_classes)} classes today")
        else:
            print_result("Get Today's Schedule", False, f"HTTP {response2.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_result("Schedule Controller", False, "Controller not running on port 5006")
        return False
    except Exception as e:
        print_result("Schedule Controller", False, f"Error: {str(e)}")
        return False

def test_schedule_database():
    """Verify schedule data in database"""
    print_section("TEST: SCHEDULE DATABASE DATA")
    
    try:
        # Get timetable for LEC001
        schedule = query_all("""
            SELECT c.module_code, c.module_name, t.day_of_week, 
                   TIME_FORMAT(t.start_time, '%H:%i') as start_time,
                   TIME_FORMAT(t.end_time, '%H:%i') as end_time,
                   t.room
            FROM modules c
            JOIN timetable t ON t.module_id = c.id
            WHERE c.lecturer_id = (SELECT id FROM lecturers WHERE lecturer_id = 'LEC001')
            ORDER BY FIELD(t.day_of_week, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')
        """)
        
        print(f"✓ Found {len(schedule)} timetable entries for LEC001:")
        for entry in schedule:
            print(f"  - {entry['day_of_week']} {entry['start_time']}-{entry['end_time']}: {entry['module_code']} - {entry['module_name']} ({entry['room']})")
        
        print_result("Schedule Database", True, f"{len(schedule)} entries verified")
        return True
        
    except Exception as e:
        print_result("Schedule Database", False, f"Error: {str(e)}")
        return False

# ============================================================================
# ATTENDANCE TESTS (US14, US18)
# ============================================================================

def test_attendance_controller():
    """Test US14 - Real-Time Attendance and US18 - Filter Records"""
    print_section("TEST: LECTURER ATTENDANCE (US14, US18)")
    
    BASE_URL = "http://localhost:5004"
    
    try:
        # Test 1: Get attendance records for CS101
        response = requests.get(
            f"{BASE_URL}/api/lecturer/attendance/records",
            params={
                "lecturerId": "LEC001",
                "moduleCode": "CS101"
            },
            timeout=5
        )
        
        if response.status_code != 200:
            print_result("Get Attendance Records", False, f"HTTP {response.status_code}")
            return False
            
        data = response.json()
        
        if not data.get('success'):
            print_result("Get Attendance Records", False, data.get('message', 'Unknown error'))
            return False
        
        records = data.get('records', [])
        print_result("Get Attendance Records", True, f"Retrieved {len(records)} attendance records")
        
        # Show summary
        if records:
            present = sum(1 for r in records if r.get('status') == 'present')
            late = sum(1 for r in records if r.get('status') == 'late')
            absent = sum(1 for r in records if r.get('status') == 'absent')
            print(f"       Summary: {present} present, {late} late, {absent} absent")
        
        # Test 2: Filter records by date
        response2 = requests.post(
            f"{BASE_URL}/api/lecturer/attendance/filter",
            json={
                "lecturerId": "LEC001",
                "moduleCode": "CS101",
                "dateRange": {
                    "start": "2025-11-18",
                    "end": "2025-11-30"
                }
            },
            timeout=5
        )
        
        if response2.status_code == 200:
            data2 = response2.json()
            filtered = data2.get('records', [])
            print_result("Filter Records by Date", True, f"Found {len(filtered)} records in Nov 18-30")
        else:
            print_result("Filter Records by Date", False, f"HTTP {response2.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_result("Attendance Controller", False, "Controller not running on port 5004")
        return False
    except Exception as e:
        print_result("Attendance Controller", False, f"Error: {str(e)}")
        return False

def test_attendance_database():
    """Verify attendance data in database"""
    print_section("TEST: ATTENDANCE DATABASE DATA")
    
    try:
        # Get attendance summary for CS101
        summary = query_one("""
            SELECT 
                COUNT(*) as total_records,
                SUM(status = 'present') as present,
                SUM(status = 'late') as late,
                SUM(status = 'absent') as absent,
                SUM(status = 'excused') as excused
            FROM attendance a
            JOIN modules c ON a.module_id = c.id
            WHERE c.module_code = 'CS101'
        """)
        
        print(f"✓ CS101 Attendance Summary:")
        print(f"  - Total Records: {summary['total_records']}")
        print(f"  - Present: {summary['present']}")
        print(f"  - Late: {summary['late']}")
        print(f"  - Absent: {summary['absent']}")
        print(f"  - Excused: {summary['excused']}")
        
        # Get recent sessions
        sessions = query_all("""
            SELECT 
                s.session_date,
                s.status,
                s.total_students,
                COUNT(a.id) as recorded_attendance
            FROM attendance_sessions s
            LEFT JOIN attendance a ON a.module_id = s.module_id 
                AND DATE(a.check_in_time) = s.session_date
            WHERE s.module_id = (SELECT id FROM modules WHERE module_code = 'CS101')
            GROUP BY s.id
            ORDER BY s.session_date DESC
            LIMIT 5
        """)
        
        print(f"\n✓ Recent CS101 Sessions ({len(sessions)} sessions):")
        for sess in sessions:
            print(f"  - {sess['session_date']}: {sess['total_students']} students, {sess['recorded_attendance']} records, status: {sess['status']}")
        
        print_result("Attendance Database", True, f"{summary['total_records']} total records verified")
        return True
        
    except Exception as e:
        print_result("Attendance Database", False, f"Error: {str(e)}")
        return False

# ============================================================================
# REPORT TESTS (US15)
# ============================================================================

def test_report_controller():
    """Test US15 - Attendance Report Generation"""
    print_section("TEST: LECTURER REPORTS (US15)")
    
    BASE_URL = "http://localhost:5005"
    
    try:
        # Test 1: Generate report for CS101
        response = requests.post(
            f"{BASE_URL}/api/lecturer/report/generate",
            json={
                "lecturerId": "LEC001",
                "moduleId": "CS101",
                "dateRange": {
                    "start": "2025-11-01",
                    "end": "2025-11-30"
                },
                "metrics": "detailed"
            },
            timeout=5
        )
        
        if response.status_code != 200:
            print_result("Generate Report", False, f"HTTP {response.status_code}")
            return False
            
        data = response.json()
        
        if not data.get('success'):
            print_result("Generate Report", False, data.get('message', 'Unknown error'))
            return False
        
        report = data.get('report', {})
        print_result("Generate Report", True, f"Report generated for {report.get('moduleId')}")
        
        if report:
            print(f"       Total Sessions: {report.get('totalSessions')}")
            print(f"       Students: {len(report.get('students', []))}")
            print(f"       Avg Attendance: {report.get('avgAttendance')}%")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_result("Report Controller", False, "Controller not running on port 5005")
        return False
    except Exception as e:
        print_result("Report Controller", False, f"Error: {str(e)}")
        return False

def test_report_database():
    """Verify report data in database"""
    print_section("TEST: REPORTS DATABASE DATA")
    
    try:
        # Get existing reports
        reports = query_all("""
            SELECT 
                r.id,
                r.report_type,
                r.report_name,
                r.generated_by_type,
                r.file_format,
                r.status,
                r.created_at
            FROM reports r
            WHERE r.generated_by_type = 'lecturer'
            ORDER BY r.created_at DESC
            LIMIT 5
        """)
        
        print(f"✓ Found {len(reports)} lecturer-generated reports:")
        for report in reports:
            print(f"  - Report #{report['id']}: {report['report_name']} ({report['file_format']}) - {report['status']}")
        
        print_result("Reports Database", True, f"{len(reports)} reports found")
        return True
        
    except Exception as e:
        print_result("Reports Database", False, f"Error: {str(e)}")
        return False

# ============================================================================
# NOTIFICATION TESTS (US17)
# ============================================================================

def test_notification_controller():
    """Test US17 - Notification System"""
    print_section("TEST: LECTURER NOTIFICATIONS (US17)")
    
    BASE_URL = "http://localhost:5007"
    
    try:
        # Test 1: Get notifications for LEC001
        response = requests.get(
            f"{BASE_URL}/api/lecturer/notifications",
            params={"lecturerId": "LEC001"},
            timeout=5
        )
        
        if response.status_code != 200:
            print_result("Get Notifications", False, f"HTTP {response.status_code}")
            return False
            
        data = response.json()
        
        if not data.get('success'):
            print_result("Get Notifications", False, data.get('message', 'Unknown error'))
            return False
        
        notifications = data.get('notifications', [])
        print_result("Get Notifications", True, f"Retrieved {len(notifications)} notifications")
        
        # Show recent notifications
        for notif in notifications[:3]:
            read_status = "Read" if notif.get('isRead') else "Unread"
            print(f"       [{notif.get('type')}] {notif.get('title')} - {read_status}")
        
        # Test 2: Subscribe to notifications
        response2 = requests.post(
            f"{BASE_URL}/api/lecturer/notification/subscribe",
            json={"lecturerId": "LEC001"},
            timeout=5
        )
        
        if response2.status_code == 200:
            print_result("Subscribe to Notifications", True, "Subscription successful")
        else:
            print_result("Subscribe to Notifications", False, f"HTTP {response2.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_result("Notification Controller", False, "Controller not running on port 5007")
        return False
    except Exception as e:
        print_result("Notification Controller", False, f"Error: {str(e)}")
        return False

def test_notification_database():
    """Verify notification data in database"""
    print_section("TEST: NOTIFICATIONS DATABASE DATA")
    
    try:
        # Get notifications for LEC001
        notifications = query_all("""
            SELECT 
                n.id,
                n.notification_type,
                n.title,
                n.message,
                n.is_read,
                n.created_at
            FROM notifications n
            WHERE n.recipient_type = 'lecturer' 
            AND n.recipient_id = (SELECT id FROM lecturers WHERE lecturer_id = 'LEC001')
            ORDER BY n.created_at DESC
        """)
        
        print(f"✓ Found {len(notifications)} notifications for LEC001:")
        
        read_count = sum(1 for n in notifications if n['is_read'])
        unread_count = len(notifications) - read_count
        
        for notif in notifications[:5]:
            read_status = "Read" if notif['is_read'] else "Unread"
            print(f"  - [{notif['notification_type']}] {notif['title']} - {read_status}")
        
        print(f"\n  Summary: {read_count} read, {unread_count} unread")
        
        print_result("Notifications Database", True, f"{len(notifications)} notifications verified")
        return True
        
    except Exception as e:
        print_result("Notifications Database", False, f"Error: {str(e)}")
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

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
    """Run all lecturer feature tests"""
    print("\n" + "=" * 70)
    print("LECTURER MODULE - COMPREHENSIVE FEATURE TESTS")
    print("=" * 70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("PREREQUISITES:")
    print("  1. Database running with test data imported")
    print("  2. All lecturer controllers running:")
    print("     - lecturer_schedule_controller.py on port 5006")
    print("     - lecturer_attendance_controller.py on port 5004")
    print("     - lecturer_report_controller.py on port 5005")
    print("     - lecturer_notification_controller.py on port 5007")
    print("\nStarting tests...")
    
    results = {}
    
    # Schedule tests
    results['Schedule Database'] = test_schedule_database()
    results['Schedule Controller'] = test_schedule_controller()
    
    # Attendance tests
    results['Attendance Database'] = test_attendance_database()
    results['Attendance Controller'] = test_attendance_controller()
    
    # Report tests
    results['Reports Database'] = test_report_database()
    results['Report Controller'] = test_report_controller()
    
    # Notification tests
    results['Notifications Database'] = test_notification_database()
    results['Notification Controller'] = test_notification_controller()
    
    # Print summary
    print_summary(results)

if __name__ == "__main__":
    main()
