#!/usr/bin/env python3
"""Check what's in the database"""
import mysql.connector
import os

db_url = os.getenv('DATABASE_URL')
from urllib.parse import urlparse
url = urlparse(db_url)

conn = mysql.connector.connect(
    host=url.hostname,
    user=url.username,
    password=url.password,
    database=url.path.lstrip('/')
)

cursor = conn.cursor(dictionary=True)

print("=" * 60)
print("DATABASE CONTENTS CHECK")
print("=" * 60)

cursor.execute("SELECT * FROM system_admins")
admins = cursor.fetchall()
print(f"\nSystem Admins ({len(admins)}):")
for admin in admins:
    print(f"  - {admin}")

cursor.execute("SELECT * FROM student_service_admins")
ssas = cursor.fetchall()
print(f"\nStudent Service Admins ({len(ssas)}):")
for ssa in ssas:
    print(f"  - {ssa}")

cursor.execute("SELECT * FROM lecturers")
lecturers = cursor.fetchall()
print(f"\nLecturers ({len(lecturers)}):")
for lecturer in lecturers:
    print(f"  - {lecturer}")

cursor.execute("SELECT * FROM students")
students = cursor.fetchall()
print(f"\nStudents ({len(students)}):")
for student in students:
    print(f"  - {student}")

cursor.close()
conn.close()
print("\n" + "=" * 60)
