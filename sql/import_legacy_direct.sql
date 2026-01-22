-- ============================================================================
-- Direct Legacy User Import
-- ============================================================================
-- Run this SQL directly on your RDS instance.
-- It imports key user accounts from the legacy dump without requiring
-- a staging schema.
--
-- Use: mysql -h <RDS_HOST> -u admin -p<PASSWORD> student_attendance < import_legacy_direct.sql
--
-- These users have bcrypt-hashed passwords (they work with our auth system).
-- Default password for all is: password
-- ============================================================================

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_SAFE_UPDATES = 0;

-- ============================================================================
-- 1) System Admins from Legacy
-- ============================================================================

INSERT IGNORE INTO system_admins (
  admin_id, email, password, first_name, last_name, phone, 
  permissions, is_active, created_at, updated_at
)
VALUES
  ('SYSADMIN001', 'admin@attendance.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 
   'System', 'Administrator', NULL, '{"all": true}', 1, NOW(), NOW()),
  ('SYSADMIN002', 'sysadmin@university.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
   'Tech', 'Admin', NULL, '{"all": true}', 1, NOW(), NOW());

-- ============================================================================
-- 2) Student Service Admins from Legacy
-- ============================================================================

INSERT IGNORE INTO student_service_admins (
  admin_id, email, password, first_name, last_name, phone, 
  department, is_active, created_at, updated_at
)
VALUES
  ('SSA002', 'registry@university.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
   'Registry', 'Officer', NULL, 'Registrar Office', 1, NOW(), NOW()),
  ('SSA72548', 'studentservice@attendance.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
   'Student', 'Service Administrator', NULL, NULL, 1, NOW(), NOW());

-- ============================================================================
-- 3) Lecturers from Legacy
-- ============================================================================

INSERT IGNORE INTO lecturers (
  lecturer_id, email, password, first_name, last_name, phone, 
  department, is_active, created_at, updated_at
)
VALUES
  ('LEC001', 'john.smith@university.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
   'John', 'Smith', NULL, NULL, 1, NOW(), NOW()),
  ('LEC002', 'jane.doe@university.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
   'Jane', 'Doe', NULL, 'Computer Science', 1, NOW(), NOW()),
  ('LEC003', 'mike.johnson@university.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
   'Mike', 'Johnson', NULL, 'Computer Science', 1, NOW(), NOW());

-- ============================================================================
-- 4) Students from Legacy (sample - first 10)
-- ============================================================================

INSERT IGNORE INTO students (
  student_id, email, password, first_name, last_name, phone, 
  intake_period, intake_year, academic_year, program, `level`, 
  is_active, created_at, updated_at
)
VALUES
  ('STU2025001', 'alice.wong@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
   'Alice', 'Wong', '0123456789', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1, NOW(), NOW()),
  ('STU2025002', 'bob.tan@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
   'Bob', 'Tan', '0123456788', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1, NOW(), NOW()),
  ('STU2024003', 'charlie.lee@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
   'Charlie', 'Lee', '0123456787', 'July', 2024, '2024/2025', 'Information Technology', 'Diploma', 1, NOW(), NOW()),
  ('STU2024004', 'diana.kumar@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
   'Diana', 'Kumar', '0123456786', 'July', 2024, '2024/2025', 'Software Engineering', 'Degree', 1, NOW(), NOW()),
  ('STU2025005', 'eva.lim@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
   'Eva', 'Lim', '0123456710', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1, NOW(), NOW()),
  ('STU2025006', 'farid.azmi@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
   'Farid', 'Azmi', '0123456711', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1, NOW(), NOW()),
  ('STU2025007', 'grace.ong@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
   'Grace', 'Ong', '0123456712', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1, NOW(), NOW()),
  ('STU2025008', 'haris.rahman@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
   'Haris', 'Rahman', '0123456713', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1, NOW(), NOW()),
  ('STU2025009', 'isha.nair@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
   'Isha', 'Nair', '0123456714', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1, NOW(), NOW()),
  ('STU2025010', 'jack.lee@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
   'Jack', 'Lee', '0123456715', 'April', 2025, '2025/2026', 'Software Engineering', 'Degree', 1, NOW(), NOW());

-- ============================================================================
-- Verify Import
-- ============================================================================

SELECT 'system_admins' as table_name, COUNT(*) as count FROM system_admins
UNION ALL
SELECT 'student_service_admins', COUNT(*) FROM student_service_admins
UNION ALL
SELECT 'lecturers', COUNT(*) FROM lecturers
UNION ALL
SELECT 'students', COUNT(*) FROM students;

SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 1;

-- ============================================================================
-- DONE!
-- ============================================================================
-- You can now login with one of these accounts:
--   Email: admin@attendance.com | Password: password | Role: System Admin
--   Email: studentservice@attendance.com | Password: password | Role: SSA
--   Email: john.smith@university.com | Password: password | Role: Lecturer
--   Email: alice.wong@student.edu | Password: password | Role: Student
-- ============================================================================
