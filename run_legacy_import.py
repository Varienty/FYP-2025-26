#!/usr/bin/env python3
"""
Quick legacy user import script - run directly on EB instance
Usage: python3 run_legacy_import.py
"""
import mysql.connector
import os

# Get DB credentials from environment or use defaults
RDS_HOST = os.getenv('RDS_HOSTNAME', 'studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com')
RDS_USER = os.getenv('RDS_USERNAME', 'admin')
RDS_PASS = os.getenv('RDS_PASSWORD', 'iamtrying')
RDS_DB = os.getenv('RDS_DB_NAME', 'student_attendance')

print("Connecting to RDS...")
conn = mysql.connector.connect(
    host=RDS_HOST,
    user=RDS_USER,
    password=RDS_PASS,
    database=RDS_DB
)
cursor = conn.cursor()

print("Importing legacy users...")

# System Admins
cursor.execute("""
    INSERT IGNORE INTO system_admins (admin_id, email, password, first_name, last_name, permissions, is_active, created_at, updated_at) 
    VALUES ('SYSADMIN001', 'admin@attendance.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'System', 'Administrator', '{"all": true}', 1, NOW(), NOW())
""")
print("  ✓ System admin imported")

# Student Service Admins
cursor.execute("""
    INSERT IGNORE INTO student_service_admins (admin_id, email, password, first_name, last_name, is_active, created_at, updated_at) 
    VALUES ('SSA72548', 'studentservice@attendance.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Student', 'Service Administrator', 1, NOW(), NOW())
""")
cursor.execute("""
    INSERT IGNORE INTO student_service_admins (admin_id, email, password, first_name, last_name, department, is_active, created_at, updated_at) 
    VALUES ('SSA002', 'registry@university.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Registry', 'Officer', 'Registrar Office', 1, NOW(), NOW())
""")
print("  ✓ SSA accounts imported")

# Lecturers
cursor.execute("""
    INSERT IGNORE INTO lecturers (lecturer_id, email, password, first_name, last_name, is_active, created_at, updated_at) 
    VALUES ('LEC001', 'john.smith@university.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'John', 'Smith', 1, NOW(), NOW())
""")
cursor.execute("""
    INSERT IGNORE INTO lecturers (lecturer_id, email, password, first_name, last_name, department, is_active, created_at, updated_at) 
    VALUES ('LEC002', 'jane.doe@university.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Jane', 'Doe', 'Computer Science', 1, NOW(), NOW())
""")
cursor.execute("""
    INSERT IGNORE INTO lecturers (lecturer_id, email, password, first_name, last_name, department, is_active, created_at, updated_at) 
    VALUES ('LEC003', 'mike.johnson@university.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Mike', 'Johnson', 'Computer Science', 1, NOW(), NOW())
""")
print("  ✓ Lecturer accounts imported")

# Students (sample)
cursor.execute("""
    INSERT IGNORE INTO students (student_id, email, password, first_name, last_name, phone, intake_period, intake_year, academic_year, program, level, is_active, created_at, updated_at) 
    VALUES ('STU2025001', 'alice.wong@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Alice', 'Wong', '0123456789', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1, NOW(), NOW())
""")
cursor.execute("""
    INSERT IGNORE INTO students (student_id, email, password, first_name, last_name, phone, intake_period, intake_year, academic_year, program, level, is_active, created_at, updated_at) 
    VALUES ('STU2025002', 'bob.tan@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Bob', 'Tan', '0123456788', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1, NOW(), NOW())
""")
cursor.execute("""
    INSERT IGNORE INTO students (student_id, email, password, first_name, last_name, phone, intake_period, intake_year, academic_year, program, level, is_active, created_at, updated_at) 
    VALUES ('STU2024003', 'charlie.lee@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Charlie', 'Lee', '0123456787', 'July', 2024, '2024/2025', 'Information Technology', 'Diploma', 1, NOW(), NOW())
""")
print("  ✓ Student accounts imported")

conn.commit()

# Verify
print("\nVerifying import...")
cursor.execute("SELECT COUNT(*) FROM system_admins")
print(f"  System admins: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM student_service_admins")
print(f"  SSAs: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM lecturers")
print(f"  Lecturers: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM students")
print(f"  Students: {cursor.fetchone()[0]}")

cursor.close()
conn.close()

print("\n✓ Import complete! You can now test login with:")
print("  - admin@attendance.com (password: password)")
print("  - studentservice@attendance.com (password: password)")
print("  - john.smith@university.com (password: password)")
print("  - alice.wong@student.edu (password: password)")
