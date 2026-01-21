"""Quick test of all lecturer controllers"""
import requests

def test_controller(name, port, endpoint, params=None, json_data=None, method='GET'):
    """Test a controller endpoint"""
    url = f"http://localhost:{port}{endpoint}"
    try:
        if method == 'GET':
            response = requests.get(url, params=params, timeout=3)
        else:
            response = requests.post(url, json=json_data, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✓ {name} (port {port}): WORKING")
                return True
        print(f"✗ {name} (port {port}): HTTP {response.status_code}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"✗ {name} (port {port}): NOT RUNNING")
        return False
    except Exception as e:
        print(f"✗ {name} (port {port}): ERROR - {str(e)}")
        return False

print("=" * 60)
print("LECTURER CONTROLLERS - QUICK STATUS CHECK")
print("=" * 60)

results = []

# Auth (port 5003)
results.append(test_controller(
    "Auth Controller", 5003,
    "/api/lecturer/auth/login",
    json_data={"email": "john.smith@university.com", "password": "password"},
    method='POST'
))

# Schedule (port 5006)
results.append(test_controller(
    "Schedule Controller", 5006,
    "/api/lecturer/schedule",
    params={"lecturerId": "LEC001"}
))

# Attendance (port 5004)
results.append(test_controller(
    "Attendance Controller", 5004,
    "/api/lecturer/attendance/records",
    params={"lecturerId": "LEC001", "moduleCode": "CS101"}
))

# Reports (port 5005)
results.append(test_controller(
    "Report Controller", 5005,
    "/api/lecturer/report/generate",
    json_data={
        "lecturerId": "LEC001",
        "moduleId": "CS101",
        "dateRange": {"start": "2025-11-01", "end": "2025-11-30"}
    },
    method='POST'
))

# Notifications (port 5007)
results.append(test_controller(
    "Notification Controller", 5007,
    "/api/lecturer/notifications",
    params={"lecturerId": "LEC001"}
))

print("=" * 60)
passed = sum(results)
total = len(results)
print(f"RESULT: {passed}/{total} controllers working ({passed*100//total}%)")
if passed == total:
    print("✓ ALL SYSTEMS OPERATIONAL")
else:
    print(f"✗ {total-passed} controller(s) need attention")
print("=" * 60)
