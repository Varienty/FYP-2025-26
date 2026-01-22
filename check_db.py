#!/usr/bin/env python3
"""Check what's in the database"""
import mysql.connector

# Hardcode RDS connection (same as your DATABASE_URL)
conn = mysql.connector.connect(
    host='studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com',
    user='admin',
    password='iamtrying',
    database='student_attendance'
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
