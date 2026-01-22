#!/usr/bin/env python3
"""Update all test user passwords to a known hash"""
import mysql.connector
import bcrypt

# Generate correct hash for "password"
password = "password"
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

print(f"Generated hash: {hashed}")

conn = mysql.connector.connect(
    host='studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com',
    user='admin',
    password='iamtrying',
    database='student_attendance'
)

cursor = conn.cursor()

cursor.execute("UPDATE system_admins SET password = %s WHERE email = 'admin@example.com'", (hashed,))
cursor.execute("UPDATE student_service_admins SET password = %s WHERE email = 'ssa@example.com'", (hashed,))
cursor.execute("UPDATE lecturers SET password = %s WHERE email = 'lecturer@example.com'", (hashed,))
cursor.execute("UPDATE students SET password = %s WHERE email = 'student@example.com'", (hashed,))

conn.commit()
print("✓ All passwords updated to: password")
cursor.close()
conn.close()
