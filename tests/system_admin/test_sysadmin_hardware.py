"""
Test script for System Administrator - Hardware Monitoring
Tests: US22 (View Hardware Status), US23 (Update Device Status)
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

def test_get_devices():
    """Test US22 - Get All Devices"""
    print_test_header("Get All Hardware Devices (US22)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/devices",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('devices'):
                devices = data['devices']
                print(f"✓ PASS | Retrieved {len(devices)} devices")
                
                # Count by status
                online = sum(1 for d in devices if d['status'] == 'online')
                offline = sum(1 for d in devices if d['status'] == 'offline')
                maintenance = sum(1 for d in devices if d['status'] == 'maintenance')
                
                print(f"  Online: {online}")
                print(f"  Offline: {offline}")
                print(f"  Maintenance: {maintenance}")
                
                # Show sample device
                if devices:
                    sample = devices[0]
                    print(f"  Sample Device:")
                    print(f"    ID: {sample['id']}")
                    print(f"    Name: {sample['name']}")
                    print(f"    Type: {sample['type']}")
                    print(f"    Status: {sample['status']}")
                    print(f"    Location: {sample.get('location', 'N/A')}")
                
                return True
            else:
                print(f"✗ FAIL | No devices returned")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def test_device_stats():
    """Test US22 - Get Device Statistics"""
    print_test_header("Get Device Statistics (US22)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/devices/stats",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('stats'):
                stats = data['stats']
                print(f"✓ PASS | Device statistics retrieved")
                print(f"  Total Devices: {stats['total']}")
                print(f"  Online: {stats['online']}")
                print(f"  Offline: {stats['offline']}")
                print(f"  Maintenance: {stats['maintenance']}")
                print(f"  Uptime: {stats['uptime']}%")
                return True
            else:
                print(f"✗ FAIL | No stats returned")
                return False
        else:
            print(f"✗ FAIL | HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def test_update_device():
    """Test US23 - Update Device Status"""
    print_test_header("Update Device Status (US23)")
    
    # Update cam_3 from offline to maintenance
    device_id = "cam_3"
    update_data = {
        'status': 'maintenance',
        'name': 'Updated Lab Camera'
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/devices/{device_id}",
            json=update_data,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('device'):
                device = data['device']
                print(f"✓ PASS | Device updated successfully")
                print(f"  ID: {device['id']}")
                print(f"  New Name: {device['name']}")
                print(f"  New Status: {device['status']}")
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

def test_update_nonexistent_device():
    """Test US23 - Update Non-existent Device (Error Case)"""
    print_test_header("Update Non-existent Device (US23)")
    
    device_id = "nonexistent_device"
    update_data = {'status': 'online'}
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/devices/{device_id}",
            json=update_data,
            timeout=5
        )
        
        if response.status_code == 404:
            print(f"✓ PASS | Non-existent device correctly rejected")
            return True
        else:
            print(f"✗ FAIL | Should return 404 (got {response.status_code})")
            return False
            
    except Exception as e:
        print(f"✗ FAIL | Error: {str(e)}")
        return False

def main():
    """Run all hardware monitoring tests"""
    print("\n" + "="*60)
    print("SYSTEM ADMINISTRATOR - HARDWARE MONITORING TESTS")
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
    
    # Run tests
    results.append(('Get Devices (US22)', test_get_devices()))
    results.append(('Device Statistics (US22)', test_device_stats()))
    results.append(('Update Device (US23)', test_update_device()))
    results.append(('Update Non-existent Device (US23)', test_update_nonexistent_device()))
    
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
