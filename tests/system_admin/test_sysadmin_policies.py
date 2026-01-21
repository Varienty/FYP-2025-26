"""
Test script for System Administrator - Policy Management
Tests: US20 (View/Create Policies), US21 (Update/Delete Policies)
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

def test_get_policies():
    """Test US20 - Get All Policies"""
    print_test_header("Get All Policies (US20)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/policies",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('policies'):
                policies = data['policies']
                print(f"✓ PASS | Retrieved {len(policies)} policies")
                
                if policies:
                    sample = policies[0]
                    print(f"  Sample Policy:")
                    print(f"    Name: {sample['name']}")
                    print(f"    Min Percentage: {sample['minPercentage']}%")
                    print(f"    Grace Period: {sample['grace']} min")
                    print(f"    Late Threshold: {sample['late']} min")
                
                return True
            else:
                print(f"✗ FAIL | No policies returned")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def test_create_policy():
    """Test US20 - Create New Policy"""
    print_test_header("Create New Policy (US20)")
    
    new_policy = {
        'name': 'Test Policy',
        'minPercentage': 85,
        'grace': 15,
        'late': 45,
        'scope': 'department',
        'activeFrom': '2025-01-01',
        'activeTo': '2025-12-31'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/policies",
            json=new_policy,
            timeout=5
        )
        
        if response.status_code == 201:
            data = response.json()
            if data.get('ok') and data.get('policy'):
                policy = data['policy']
                print(f"✓ PASS | Policy created successfully")
                print(f"  ID: {policy['id']}")
                print(f"  Name: {policy['name']}")
                print(f"  Min %: {policy['minPercentage']}%")
                return True, policy['id']
            else:
                print(f"✗ FAIL | Creation failed")
                return False, None
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False, None

def test_update_policy(policy_id):
    """Test US21 - Update Existing Policy"""
    print_test_header("Update Policy (US21)")
    
    if not policy_id:
        print(f"✗ SKIP | No policy ID to update")
        return False
    
    update_data = {
        'name': 'Updated Test Policy',
        'minPercentage': 90,
        'grace': 20
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/policies/{policy_id}",
            json=update_data,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('policy'):
                policy = data['policy']
                print(f"✓ PASS | Policy updated successfully")
                print(f"  New Name: {policy['name']}")
                print(f"  New Min %: {policy['minPercentage']}%")
                print(f"  New Grace: {policy['grace']} min")
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

def test_delete_policy(policy_id):
    """Test US21 - Delete Policy"""
    print_test_header("Delete Policy (US21)")
    
    if not policy_id:
        print(f"✗ SKIP | No policy ID to delete")
        return False
    
    try:
        response = requests.delete(
            f"{BASE_URL}/api/policies/{policy_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✓ PASS | Policy deleted successfully")
                print(f"  ID: {policy_id}")
                return True
            else:
                print(f"✗ FAIL | Deletion failed")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def main():
    """Run all policy management tests"""
    print("\n" + "="*60)
    print("SYSTEM ADMINISTRATOR - POLICY MANAGEMENT TESTS")
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
    get_result = test_get_policies()
    results.append(('Get Policies (US20)', get_result))
    
    create_result, policy_id = test_create_policy()
    results.append(('Create Policy (US20)', create_result))
    
    update_result = test_update_policy(policy_id)
    results.append(('Update Policy (US21)', update_result))
    
    delete_result = test_delete_policy(policy_id)
    results.append(('Delete Policy (US21)', delete_result))
    
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
