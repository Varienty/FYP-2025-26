"""
Test script for System Administrator - User & Permissions Management
Tests: US24 (User Management), US25 (Deactivate User), US26 (Permissions Management)
"""

import requests
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:5009"

def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")

def test_get_users():
    """Test US24 - Get All Users"""
    print_test_header("Get All Users (US24)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/users",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('users'):
                users = data['users']
                print(f"✓ PASS | Retrieved {len(users)} users")
                
                # Count by role
                lecturers = sum(1 for u in users if u['role'] == 'lecturer')
                admins = sum(1 for u in users if u['role'] == 'system-admin')
                ssa = sum(1 for u in users if u['role'] == 'student-service-admin')
                
                print(f"  Lecturers: {lecturers}")
                print(f"  System Admins: {admins}")
                print(f"  SSA: {ssa}")
                
                if users:
                    sample = users[0]
                    print(f"  Sample User:")
                    print(f"    ID: {sample['id']}")
                    print(f"    Name: {sample['name']}")
                    print(f"    Role: {sample['role']}")
                    print(f"    Email: {sample['email']}")
                
                return True
            else:
                print(f"✗ FAIL | No users returned")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def test_create_user():
    """Test US24 - Create New User"""
    print_test_header("Create New User (US24)")
    
    new_user = {
        'name': 'Test Lecturer',
        'email': 'test.lecturer@university.com',
        'role': 'lecturer'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/users",
            json=new_user,
            timeout=5
        )
        
        if response.status_code == 201:
            data = response.json()
            if data.get('ok') and data.get('user'):
                user = data['user']
                print(f"✓ PASS | User created successfully")
                print(f"  ID: {user['id']}")
                print(f"  Name: {user['name']}")
                print(f"  Email: {user['email']}")
                print(f"  Role: {user['role']}")
                return True, user['id']
            else:
                print(f"✗ FAIL | Creation failed")
                return False, None
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False, None

def test_update_user(user_id):
    """Test US24 - Update User"""
    print_test_header("Update User (US24)")
    
    if not user_id:
        print(f"✗ SKIP | No user ID to update")
        return False
    
    update_data = {
        'name': 'Updated Test Lecturer',
        'email': 'updated.lecturer@university.com',
        'role': 'lecturer'
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/users/{user_id}",
            json=update_data,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('user'):
                user = data['user']
                print(f"✓ PASS | User updated successfully")
                print(f"  New Name: {user['name']}")
                print(f"  New Email: {user['email']}")
                return True
            else:
                print(f"✗ FAIL | Update failed")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def test_deactivate_user(user_id):
    """Test US25 - Deactivate User"""
    print_test_header("Deactivate User (US25)")
    
    if not user_id:
        print(f"✗ SKIP | No user ID to deactivate")
        return False
    
    try:
        response = requests.delete(
            f"{BASE_URL}/api/users/{user_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✓ PASS | User deactivated successfully")
                print(f"  ID: {user_id}")
                return True
            else:
                print(f"✗ FAIL | Deactivation failed")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def test_get_permissions():
    """Test US26 - Get Role Permissions"""
    print_test_header("Get Role Permissions (US26)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/permissions",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('permissions'):
                permissions = data['permissions']
                print(f"✓ PASS | Retrieved permissions for {len(permissions)} roles")
                
                for role, perms in permissions.items():
                    print(f"  {role}: {len(perms)} permissions")
                    if perms and perms[0] != 'all':
                        print(f"    Sample: {', '.join(perms[:3])}")
                
                return True
            else:
                print(f"✗ FAIL | No permissions returned")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def test_update_permissions():
    """Test US26 - Update Role Permissions"""
    print_test_header("Update Role Permissions (US26)")
    
    role = "lecturer"
    new_permissions = {
        'permissions': [
            'view_schedule',
            'mark_attendance',
            'generate_reports',
            'view_students',
            'send_notifications'
        ]
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/permissions/{role}",
            json=new_permissions,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✓ PASS | Permissions updated successfully")
                print(f"  Role: {data['role']}")
                print(f"  New Permissions: {len(data['permissions'])}")
                print(f"    {', '.join(data['permissions'])}")
                return True
            else:
                print(f"✗ FAIL | Update failed")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def main():
    """Run all user and permissions tests"""
    print("\n" + "="*60)
    print("SYSTEM ADMINISTRATOR - USER & PERMISSIONS TESTS")
    print("="*60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    
    # Check if controller is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except:
        print(f"\n⚠ ERROR: Controller not running!")
        print(f"Please start: python 'System Administrator/controller/sysadmin_main.py'")
        sys.exit(1)
    
    results = []
    
    # Run tests in sequence
    get_result = test_get_users()
    results.append(('Get Users (US24)', get_result))
    
    create_result, user_id = test_create_user()
    results.append(('Create User (US24)', create_result))
    
    update_result = test_update_user(user_id)
    results.append(('Update User (US24)', update_result))
    
    deactivate_result = test_deactivate_user(user_id)
    results.append(('Deactivate User (US25)', deactivate_result))
    
    perm_get_result = test_get_permissions()
    results.append(('Get Permissions (US26)', perm_get_result))
    
    perm_update_result = test_update_permissions()
    results.append(('Update Permissions (US26)', perm_update_result))
    
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
