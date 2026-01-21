"""
Test script for Student Service Administrator - Authentication
Tests: US27 (Login), US28 (Logout), US30 (Password Reset)
"""

import requests
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:5008"

# Test credentials
SSA_CREDENTIALS = {
    'username': 'admin',
    'password': 'password'
}

def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")

def test_ssa_login():
    """Test US27 - SSA Login"""
    print_test_header("SSA Login (US27)")
    
    try:
        # Valid login
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=SSA_CREDENTIALS,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('user'):
                print(f"✓ PASS | Login successful")
                print(f"  User: {data['user']['username']}")
                print(f"  Role: {data['user']['role']}")
                print(f"  Email: {data['user']['email']}")
                return True, data['user']['username']
            else:
                print(f"✗ FAIL | Login failed: {data.get('message')}")
                return False, None
        else:
            print(f"✗ FAIL | HTTP {response.status_code}: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"✗ FAIL | Controller not running on port 5008")
        return False, None
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False, None

def test_invalid_login():
    """Test invalid login attempts"""
    print_test_header("Invalid Login Attempts")
    
    test_cases = [
        {'username': 'wrong', 'password': 'password', 'desc': 'Wrong username'},
        {'username': 'admin', 'password': 'wrong', 'desc': 'Wrong password'},
        {'username': '', 'password': 'password', 'desc': 'Empty username'},
        {'username': 'admin', 'password': '', 'desc': 'Empty password'}
    ]
    
    passed = 0
    for case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={'username': case['username'], 'password': case['password']},
                timeout=5
            )
            
            if response.status_code == 401:
                print(f"✓ PASS | {case['desc']} - Correctly rejected")
                passed += 1
            else:
                print(f"✗ FAIL | {case['desc']} - Should reject (got {response.status_code})")
        except Exception as e:
            print(f"✗ FAIL | {case['desc']} - Error: {str(e)}")
    
    return passed == len(test_cases)

def test_password_reset():
    """Test US30 - Password Reset Request"""
    print_test_header("Password Reset (US30)")
    
    try:
        # Request password reset
        response = requests.post(
            f"{BASE_URL}/api/auth/reset",
            json={'email': 'admin@university.edu'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✓ PASS | Password reset request sent")
                print(f"  Message: {data.get('message')}")
                return True
            else:
                print(f"✗ FAIL | Reset failed: {data.get('message')}")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def test_change_password():
    """Test US30 - Change Password"""
    print_test_header("Change Password (US30)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/change-password",
            json={
                'username': 'admin',
                'currentPassword': 'password',
                'newPassword': 'newpassword123'
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✓ PASS | Password changed successfully")
                return True
            else:
                print(f"✗ FAIL | Change failed: {data.get('message')}")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def test_logout():
    """Test US28 - SSA Logout"""
    print_test_header("SSA Logout (US28)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/logout",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✓ PASS | Logout successful")
                return True
            else:
                print(f"✗ FAIL | Logout failed")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def main():
    """Run all authentication tests"""
    print("\n" + "="*60)
    print("STUDENT SERVICE ADMINISTRATOR - AUTHENTICATION TESTS")
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
    login_result, username = test_ssa_login()
    results.append(('SSA Login (US27)', login_result))
    
    invalid_result = test_invalid_login()
    results.append(('Invalid Login Attempts', invalid_result))
    
    reset_result = test_password_reset()
    results.append(('Password Reset (US30)', reset_result))
    
    change_result = test_change_password()
    results.append(('Change Password (US30)', change_result))
    
    logout_result = test_logout()
    results.append(('SSA Logout (US28)', logout_result))
    
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
