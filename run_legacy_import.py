#!/usr/bin/env python3
"""
Schema-aware legacy user import script - safe for varying table schemas.
Usage: python3 run_legacy_import.py
"""
import os
import datetime as dt
import mysql.connector

# Get DB credentials from environment or use defaults
RDS_HOST = os.getenv('RDS_HOSTNAME', 'studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com')
RDS_USER = os.getenv('RDS_USERNAME', 'admin')
RDS_PASS = os.getenv('RDS_PASSWORD', 'iamtrying')
RDS_DB = os.getenv('RDS_DB_NAME', 'studentattendance')

print("Connecting to RDS...")
conn = mysql.connector.connect(host=RDS_HOST, user=RDS_USER, password=RDS_PASS, database=RDS_DB)
cursor = conn.cursor()

def get_columns(table: str) -> set:
    cursor.execute(
        """
        SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
        """,
        (table,)
    )
    return {row[0] for row in cursor.fetchall()}

def row_exists_by_email(table: str, email_col: str, email: str) -> bool:
    cursor.execute(f"SELECT 1 FROM {table} WHERE {email_col} = %s LIMIT 1", (email,))
    return cursor.fetchone() is not None

def insert_row(table: str, email_col: str, data: dict):
    # Skip if already present by email
    if row_exists_by_email(table, email_col, data[email_col]):
        return False
    available = get_columns(table)
    # Filter to existing columns only
    filtered = {k: v for k, v in data.items() if k in available}
    if not filtered:
        return False
    cols = ", ".join([f"`{c}`" for c in filtered.keys()])
    placeholders = ", ".join(["%s"] * len(filtered))
    sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
    cursor.execute(sql, list(filtered.values()))
    return True

now = dt.datetime.utcnow()

print("Importing legacy users (schema-aware)...")

# Data rows
sysadmin_rows = [
    {
        'admin_id': 'SYSADMIN001',
        'email': 'admin@attendance.com',
        'password': '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
        'first_name': 'System',
        'last_name': 'Administrator',
        'permissions': '{"all": true}',
        'is_active': 1,
        'created_at': now,
        'updated_at': now,
    }
]

ssa_rows = [
    {
        'admin_id': 'SSA72548',
        'email': 'studentservice@attendance.com',
        'password': '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
        'first_name': 'Student',
        'last_name': 'Service Administrator',
        'is_active': 1,
        'created_at': now,
        'updated_at': now,
    },
    {
        'admin_id': 'SSA002',
        'email': 'registry@university.com',
        'password': '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
        'first_name': 'Registry',
        'last_name': 'Officer',
        'department': 'Registrar Office',
        'is_active': 1,
        'created_at': now,
        'updated_at': now,
    },
]

lecturer_rows = [
    {
        'lecturer_id': 'LEC001',
        'email': 'john.smith@university.com',
        'password': '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
        'first_name': 'John',
        'last_name': 'Smith',
        'is_active': 1,
        'created_at': now,
        'updated_at': now,
    },
    {
        'lecturer_id': 'LEC002',
        'email': 'jane.doe@university.com',
        'password': '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
        'first_name': 'Jane',
        'last_name': 'Doe',
        'department': 'Computer Science',
        'is_active': 1,
        'created_at': now,
        'updated_at': now,
    },
    {
        'lecturer_id': 'LEC003',
        'email': 'mike.johnson@university.com',
        'password': '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
        'first_name': 'Mike',
        'last_name': 'Johnson',
        'department': 'Computer Science',
        'is_active': 1,
        'created_at': now,
        'updated_at': now,
    },
]

student_rows = [
    {
        'student_id': 'STU2025001',
        'email': 'alice.wong@student.edu',
        'password': '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
        'first_name': 'Alice',
        'last_name': 'Wong',
        'phone': '0123456789',
        'intake_period': 'April',
        'intake_year': 2025,
        'academic_year': '2025/2026',
        'program': 'Computer Science',
        'level': 'Degree',
        'is_active': 1,
        'created_at': now,
        'updated_at': now,
    },
    {
        'student_id': 'STU2025002',
        'email': 'bob.tan@student.edu',
        'password': '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
        'first_name': 'Bob',
        'last_name': 'Tan',
        'phone': '0123456788',
        'intake_period': 'April',
        'intake_year': 2025,
        'academic_year': '2025/2026',
        'program': 'Computer Science',
        'level': 'Degree',
        'is_active': 1,
        'created_at': now,
        'updated_at': now,
    },
    {
        'student_id': 'STU2024003',
        'email': 'charlie.lee@student.edu',
        'password': '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
        'first_name': 'Charlie',
        'last_name': 'Lee',
        'phone': '0123456787',
        'intake_period': 'July',
        'intake_year': 2024,
        'academic_year': '2024/2025',
        'program': 'Information Technology',
        'level': 'Diploma',
        'is_active': 1,
        'created_at': now,
        'updated_at': now,
    },
]

# Perform inserts safely
inserted_counts = { 'system_admins': 0, 'student_service_admins': 0, 'lecturers': 0, 'students': 0 }

for row in sysadmin_rows:
    if insert_row('system_admins', 'email', row):
        inserted_counts['system_admins'] += 1

for row in ssa_rows:
    if insert_row('student_service_admins', 'email', row):
        inserted_counts['student_service_admins'] += 1

for row in lecturer_rows:
    if insert_row('lecturers', 'email', row):
        inserted_counts['lecturers'] += 1

for row in student_rows:
    if insert_row('students', 'email', row):
        inserted_counts['students'] += 1

conn.commit()

# Verify
print("\nVerifying import...")
for table in ['system_admins', 'student_service_admins', 'lecturers', 'students']:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"  {table}: {cursor.fetchone()[0]}")
    except Exception as e:
        print(f"  {table}: (could not count) {e}")

cursor.close()
conn.close()

print("\nInserted (new rows):", inserted_counts)
print("\n✓ Import complete! Test login with:")
print("  - admin@attendance.com | password: password")
print("  - studentservice@attendance.com | password: password")
print("  - john.smith@university.com | password: password")
print("  - alice.wong@student.edu | password: password")
