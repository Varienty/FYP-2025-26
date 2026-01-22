-- Safe import from legacy dump into live schema (users only)
-- Source schema: student_attendance_legacy
-- Target schema: student_attendance
-- This script imports only login-related users to avoid FK issues.

SET SQL_SAFE_UPDATES = 0;
SET FOREIGN_KEY_CHECKS = 0;
START TRANSACTION;

-- Ensure target schema is selected
USE student_attendance;

-- 1) System Admins: de-dup by email, do not preserve legacy id
INSERT INTO system_admins (
  admin_id, email, password, first_name, last_name, phone,
  permissions, profile_image, reset_token, reset_token_expiry,
  is_active, last_login, created_at, updated_at
)
SELECT 
  l.admin_id, l.email, l.password, l.first_name, l.last_name, l.phone,
  l.permissions, l.profile_image, l.reset_token, l.reset_token_expiry,
  COALESCE(l.is_active, 1), l.last_login, NOW(), NOW()
FROM student_attendance_legacy.system_admins l
LEFT JOIN system_admins t ON t.email = l.email
WHERE t.id IS NULL;

-- 2) Student Service Admins: de-dup by email
INSERT INTO student_service_admins (
  admin_id, email, password, first_name, last_name, phone,
  department, permissions, profile_image, reset_token, reset_token_expiry,
  is_active, last_login, created_at, updated_at
)
SELECT 
  l.admin_id, l.email, l.password, l.first_name, l.last_name, l.phone,
  l.department, l.permissions, l.profile_image, l.reset_token, l.reset_token_expiry,
  COALESCE(l.is_active, 1), l.last_login, NOW(), NOW()
FROM student_attendance_legacy.student_service_admins l
LEFT JOIN student_service_admins t ON t.email = l.email
WHERE t.id IS NULL;

-- 3) Lecturers: de-dup by email
INSERT INTO lecturers (
  lecturer_id, email, password, first_name, last_name, phone,
  department, profile_image, reset_token, reset_token_expiry,
  is_active, created_at, updated_at
)
SELECT 
  l.lecturer_id, l.email, l.password, l.first_name, l.last_name, l.phone,
  l.department, l.profile_image, l.reset_token, l.reset_token_expiry,
  COALESCE(l.is_active, 1), NOW(), NOW()
FROM student_attendance_legacy.lecturers l
LEFT JOIN lecturers t ON t.email = l.email
WHERE t.id IS NULL;

-- 4) Students: de-dup by email
INSERT INTO students (
  student_id, email, password, first_name, last_name, phone,
  address, face_data, profile_image, intake_period, intake_year,
  academic_year, program, `level`, created_by_admin_id, reset_token,
  reset_token_expiry, is_active, created_at, updated_at
)
SELECT 
  l.student_id, l.email, l.password, l.first_name, l.last_name, l.phone,
  l.address, l.face_data, l.profile_image, l.intake_period, l.intake_year,
  l.academic_year, l.program, l.`level`, NULL, l.reset_token,
  l.reset_token_expiry, COALESCE(l.is_active, 1), NOW(), NOW()
FROM student_attendance_legacy.students l
LEFT JOIN students t ON t.email = l.email
WHERE t.id IS NULL;

COMMIT;
SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 1;

-- Notes:
-- - This script purposefully skips importing IDs to avoid collisions.
-- - Relationships (classes, enrollments, attendance) are not imported here.
--   They require a phase-2 script with ID mapping to preserve referential integrity.
-- - Run order:
--   1) Create and import student_attendance_legacy database from student_attendance.sql
--   2) Execute this script against the live student_attendance database
--   3) Verify new users can log in
