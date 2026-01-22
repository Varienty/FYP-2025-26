#!/usr/bin/env python3
"""Initialize database tables and test users"""
import mysql.connector

password = input("Enter RDS password: ")

conn = mysql.connector.connect(
    host='studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com',
    user='admin',
    password=password,
    database='student_attendance'
)

cursor = conn.cursor()
print("Connected! Creating tables...")

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    program VARCHAR(100),
    year_of_study INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS lecturers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lecturer_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS student_service_admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS system_admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

print("Tables created! Inserting test users...")

cursor.execute("INSERT INTO system_admins (admin_id, email, password, first_name, last_name) VALUES ('SA001', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqXqGxYvW6', 'Admin', 'User')")
cursor.execute("INSERT INTO student_service_admins (admin_id, email, password, first_name, last_name) VALUES ('SSA001', 'ssa@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqXqGxYvW6', 'SSA', 'Admin')")
cursor.execute("INSERT INTO lecturers (lecturer_id, email, password, first_name, last_name, department) VALUES ('L001', 'lecturer@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqXqGxYvW6', 'John', 'Doe', 'Computer Science')")
cursor.execute("INSERT INTO students (student_id, email, password, first_name, last_name, program, year_of_study) VALUES ('S001', 'student@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqXqGxYvW6', 'Jane', 'Smith', 'Computer Science', 2)")

conn.commit()

cursor.execute("SHOW TABLES;")
tables = cursor.fetchall()
print(f"✓ Created {len(tables)} tables:")
for table in tables:
    print(f"  - {table[0]}")

cursor.close()
conn.close()
print("✓ Database setup complete!")
