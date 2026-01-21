"""
Test script for Student Service Administrator - Reports & File Upload
Tests: US32 (Compliance Report), US35 (Upload Class List), US36 (Student History)
"""

import requests
import sys
from datetime import datetime
import io

BASE_URL = "http://127.0.0.1:5008"

def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")

def test_compliance_report():
    """Test US32 - Compliance Report"""
    print_test_header("Compliance Report (US32)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/compliance/report",
            params={
                'threshold': '75',
                'department': 'Engineering',
                'severity': 'critical'
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('students'):
                students = data['students']
                print(f"✓ PASS | Compliance report generated")
                print(f"  Students below threshold: {len(students)}")
                
                for student in students[:3]:  # Show first 3
                    print(f"  - {student['id']} ({student['name']})")
                    print(f"    Attendance: {student['attendance']}%")
                    print(f"    Severity: {student['severity']}")
                
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

def test_student_history():
    """Test US36 - Student Attendance History"""
    print_test_header("Student History Report (US36)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/student/history",
            params={
                'search': 'STU0001',
                'year': '2024',
                'semester': '1'
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('history'):
                history = data['history']
                student = data.get('student', {})
                
                print(f"✓ PASS | Student history retrieved")
                print(f"  Student: {student.get('id')} - {student.get('name')}")
                print(f"  Department: {student.get('department')}")
                print(f"  Overall Attendance: {history.get('overallAttendance')}%")
                print(f"  Courses: {history.get('courseCount')}")
                print(f"  Total Attended: {history.get('totalAttended')}")
                print(f"  Total Missed: {history.get('totalMissed')}")
                print(f"  Total Late: {history.get('totalLate')}")
                
                # Show course breakdown
                if history.get('courseStats'):
                    print(f"  Course Breakdown:")
                    for course in history['courseStats'][:3]:
                        print(f"    - {course['code']}: {course['attended']}/{course['total']} attended")
                
                return True
            else:
                print(f"✗ FAIL | No history returned")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def test_upload_class_list():
    """Test US35 - Upload Class List"""
    print_test_header("Upload Class List (US35)")
    
    # Create a dummy CSV file
    csv_content = """Student ID,Name,Email
STU0001,Alice Johnson,alice@uni.edu
STU0002,Bob Smith,bob@uni.edu
STU0003,Carol White,carol@uni.edu"""
    
    files = {
        'file': ('class_list.csv', io.StringIO(csv_content), 'text/csv')
    }
    data = {
        'class': 'CS101'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/class-list/upload",
            files=files,
            data=data,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print(f"✓ PASS | Class list uploaded")
                print(f"  Total Students: {result.get('totalStudents')}")
                print(f"  Successful: {result.get('successful')}")
                print(f"  Failed: {result.get('failed')}")
                return True
            else:
                print(f"✗ FAIL | Upload failed: {result.get('message')}")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def test_upload_photos():
    """Test US35 - Upload Student Photos"""
    print_test_header("Upload Student Photos (US35)")
    
    # Create dummy photo files
    dummy_photo = io.BytesIO(b"fake image data")
    files = [
        ('photos', ('student1.jpg', dummy_photo, 'image/jpeg')),
        ('photos', ('student2.jpg', io.BytesIO(b"fake image data"), 'image/jpeg')),
        ('photos', ('student3.jpg', io.BytesIO(b"fake image data"), 'image/jpeg'))
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/class-list/upload-photos",
            files=files,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print(f"✓ PASS | Photos uploaded")
                print(f"  Count: {result.get('count')} photos")
                print(f"  Message: {result.get('message')}")
                return True
            else:
                print(f"✗ FAIL | Upload failed: {result.get('message')}")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def main():
    """Run all reports tests"""
    print("\n" + "="*60)
    print("STUDENT SERVICE ADMINISTRATOR - REPORTS TESTS")
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
    results.append(('Compliance Report (US32)', test_compliance_report()))
    results.append(('Student History (US36)', test_student_history()))
    results.append(('Upload Class List (US35)', test_upload_class_list()))
    results.append(('Upload Photos (US35)', test_upload_photos()))
    
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
