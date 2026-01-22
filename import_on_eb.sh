#!/bin/bash
# Import legacy users into RDS
cd /var/app/current

mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -piamtrying student_attendance << 'EOF'
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_SAFE_UPDATES = 0;

-- System Admins
INSERT IGNORE INTO system_admins (admin_id, email, password, first_name, last_name, permissions, is_active, created_at, updated_at) 
VALUES ('SYSADMIN001', 'admin@attendance.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'System', 'Administrator', '{"all": true}', 1, NOW(), NOW());

-- SSA
INSERT IGNORE INTO student_service_admins (admin_id, email, password, first_name, last_name, is_active, created_at, updated_at)
VALUES ('SSA72548', 'studentservice@attendance.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Student', 'Service Administrator', 1, NOW(), NOW());

-- Lecturers
INSERT IGNORE INTO lecturers (lecturer_id, email, password, first_name, last_name, is_active, created_at, updated_at)
VALUES ('LEC001', 'john.smith@university.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'John', 'Smith', 1, NOW(), NOW());

-- Students (sample)
INSERT IGNORE INTO students (student_id, email, password, first_name, last_name, intake_period, intake_year, academic_year, program, `level`, is_active, created_at, updated_at)
VALUES ('STU2025001', 'alice.wong@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Alice', 'Wong', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1, NOW(), NOW());

-- Verify
SELECT 'system_admins' as table_name, COUNT(*) as count FROM system_admins
UNION ALL
SELECT 'student_service_admins', COUNT(*) FROM student_service_admins
UNION ALL
SELECT 'lecturers', COUNT(*) FROM lecturers
UNION ALL
SELECT 'students', COUNT(*) FROM students;

SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 1;
EOF

echo "Import complete!"
