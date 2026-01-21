#!/usr/bin/env python3
"""
Test login endpoints directly using Python requests
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import requests
import json

def test_login_endpoints():
    print("=" * 70)
    print("TESTING LOGIN ENDPOINTS")
    print("=" * 70)
    
    # Define test cases: (role, endpoint, payload)
    tests = [
        (
            "System Admin",
            "http://127.0.0.1:5009/api/auth/login",
            {"email": "admin@attendance.com", "password": "password"}
        ),
        (
            "Student Service Admin",
            "http://127.0.0.1:5001/api/auth/login",
            {"email": "studentservice@attendance.com", "password": "password"}
        ),
        (
            "Lecturer",
            "http://127.0.0.1:5003/api/lecturer/auth/login",
            {"email": "john.smith@university.com", "password": "password"}
        ),
    ]
    
    for role, endpoint, payload in tests:
        print(f"\n--- Testing {role} ---")
        print(f"Endpoint: {endpoint}")
        print(f"Payload: {json.dumps(payload)}")
        
        try:
            response = requests.post(endpoint, json=payload, timeout=5)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            if response.ok:
                print(f"✓ SUCCESS")
            else:
                print(f"✗ FAILED")
        except requests.exceptions.ConnectionError:
            print(f"✗ CONNECTION ERROR - Server not running on {endpoint}")
        except Exception as e:
            print(f"✗ ERROR: {e}")

if __name__ == "__main__":
    print("\nBefore running this test, ensure all Flask servers are running:")
    print("  - System Admin: python3 System\\ Administrator/controller/sysadmin_main.py (port 5009)")
    print("  - SSA: python3 Student\\ Service\\ Administrator/controller/ssa_main.py (port 5001)")
    print("  - Lecturer: python3 Lecturer/controller/lecturer_auth_controller.py (port 5003)")
    print("\nWaiting 2 seconds...\n")
    
    import time
    time.sleep(2)
    
    test_login_endpoints()
