"""Quick test to verify password hashing"""
from common.db_utils import query_one
import bcrypt

# Get lecturer from DB
lecturer = query_one("SELECT password FROM lecturers WHERE lecturer_id = 'LEC001'")
print(f"Password hash from DB: {lecturer['password']}")
print(f"Hash starts with: {lecturer['password'][:7]}")

# Test password verification
test_password = "password"
try:
    result = bcrypt.checkpw(test_password.encode('utf-8'), lecturer['password'].encode('utf-8'))
    print(f"\nVerifying 'password': {result}")
except Exception as e:
    print(f"\nError verifying: {e}")

# Try creating a new hash
new_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(f"\nNew hash for 'password': {new_hash}")
print(f"New hash starts with: {new_hash[:7]}")

# Verify new hash
result2 = bcrypt.checkpw(test_password.encode('utf-8'), new_hash.encode('utf-8'))
print(f"Verifying against new hash: {result2}")
