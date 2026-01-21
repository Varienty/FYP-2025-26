import requests

# Test login
print("Testing login...")
response = requests.post("http://localhost:5003/api/lecturer/auth/login", json={
    "email": "john.smith@university.com",
    "password": "password"
})
print(f"Status: {response.status_code}")
data = response.json()
print(f"Response: {data}")

if data.get('success'):
    token = data.get('token')
    print(f"\n✓ Login successful! Token: {token[:30]}...")
    
    # Test logout
    print("\nTesting logout...")
    response2 = requests.post("http://localhost:5003/api/lecturer/auth/logout", 
                             headers={"Authorization": f"Bearer {token}"})
    print(f"Status: {response2.status_code}")
    print(f"Response: {response2.json()}")
else:
    print("✗ Login failed")
