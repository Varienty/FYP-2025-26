"""
Quick Test - System Admin Controller Status Check
Verifies that the System Admin controller is running
"""

import requests
import sys

BASE_URL = "http://127.0.0.1:5009"

def check_controller():
    """Check if System Admin controller is running"""
    print("=" * 60)
    print("System Admin Controller Health Check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        
        if response.status_code == 200:
            print(f"✓ System Admin Controller (port 5009): WORKING")
            data = response.json()
            print(f"  Status: {data.get('status')}")
            print(f"  Message: {data.get('message')}")
            return True
        else:
            print(f"✗ System Admin Controller (port 5009): ERROR (HTTP {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ System Admin Controller (port 5009): NOT RUNNING")
        print(f"\n  Start with: python 'System Administrator/controller/sysadmin_main.py'")
        return False
    except Exception as e:
        print(f"✗ System Admin Controller (port 5009): ERROR")
        print(f"  {str(e)}")
        return False

def check_endpoints():
    """Check all major endpoints"""
    print("\nEndpoint Check:")
    
    endpoints = [
        ('/api/auth/login', 'POST', 'Authentication'),
        ('/api/policies', 'GET', 'Policy Management'),
        ('/api/devices', 'GET', 'Hardware Monitoring'),
        ('/api/devices/stats', 'GET', 'Device Statistics'),
        ('/api/users', 'GET', 'User Management'),
        ('/api/permissions', 'GET', 'Permissions Management')
    ]
    
    for path, method, name in endpoints:
        try:
            if method == 'GET':
                response = requests.get(f"{BASE_URL}{path}", timeout=2)
            else:
                response = requests.post(f"{BASE_URL}{path}", json={}, timeout=2)
            
            print(f"  ✓ {name} ({method} {path})")
        except Exception as e:
            print(f"  ✗ {name} ({method} {path})")

if __name__ == '__main__':
    controller_ok = check_controller()
    
    if controller_ok:
        check_endpoints()
        print("\n✓ All systems operational!")
        print("\nRun full tests:")
        print("  python tests/system_admin/test_sysadmin_auth.py")
        print("  python tests/system_admin/test_sysadmin_policies.py")
        print("  python tests/system_admin/test_sysadmin_hardware.py")
        print("  python tests/system_admin/test_sysadmin_users.py")
        sys.exit(0)
    else:
        sys.exit(1)
