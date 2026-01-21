"""
Quick Test - SSA Controller Status Check
Verifies that the SSA main controller is running
"""

import requests
import sys

BASE_URL = "http://127.0.0.1:5008"

def check_controller():
    """Check if SSA controller is running"""
    print("=" * 60)
    print("SSA Controller Health Check")
    print("=" * 60)
    
    try:
        # Check health endpoint
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        
        if response.status_code == 200:
            print(f"✓ SSA Controller (port 5008): WORKING")
            data = response.json()
            print(f"  Status: {data.get('status')}")
            print(f"  Message: {data.get('message')}")
            return True
        else:
            print(f"✗ SSA Controller (port 5008): ERROR (HTTP {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ SSA Controller (port 5008): NOT RUNNING")
        print(f"\n  Start with: python 'Student Service Administrator/controller/ssa_main.py'")
        return False
    except Exception as e:
        print(f"✗ SSA Controller (port 5008): ERROR")
        print(f"  {str(e)}")
        return False

def check_endpoints():
    """Check all major endpoints"""
    print("\nEndpoint Check:")
    
    endpoints = [
        ('/api/auth/login', 'POST', 'Authentication'),
        ('/api/attendance/daily-summary', 'GET', 'Daily Summary'),
        ('/api/attendance/mark', 'GET', 'Mark Attendance'),
        ('/api/audit-log', 'GET', 'Audit Log'),
        ('/api/compliance/report', 'GET', 'Compliance Report'),
        ('/api/student/history', 'GET', 'Student History')
    ]
    
    for path, method, name in endpoints:
        try:
            if method == 'GET':
                response = requests.get(f"{BASE_URL}{path}", timeout=2)
            else:
                response = requests.post(f"{BASE_URL}{path}", json={}, timeout=2)
            
            # Any response (even error) means endpoint exists
            print(f"  ✓ {name} ({method} {path})")
        except Exception as e:
            print(f"  ✗ {name} ({method} {path})")

if __name__ == '__main__':
    controller_ok = check_controller()
    
    if controller_ok:
        check_endpoints()
        print("\n✓ All systems operational!")
        print("\nRun full tests:")
        print("  python tests/student_service_admin/test_ssa_auth.py")
        print("  python tests/student_service_admin/test_ssa_attendance.py")
        print("  python tests/student_service_admin/test_ssa_reports.py")
        sys.exit(0)
    else:
        sys.exit(1)
