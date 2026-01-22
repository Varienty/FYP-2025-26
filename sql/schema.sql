-- Student Attendance System Database Schema (Multi-Role)
-- Run this script in phpMyAdmin to create the database and tables

DROP DATABASE IF EXISTS student_attendance;
CREATE DATABASE student_attendance;
USE student_attendance;

-- ==========================================
-- USER MANAGEMENT TABLES
-- ==========================================

-- System Administrators table (created first, no dependencies)
CREATE TABLE IF NOT EXISTS system_admins (
  id INT PRIMARY KEY AUTO_INCREMENT,
  admin_id VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  phone VARCHAR(20),
  permissions JSON,
  profile_image VARCHAR(255),
  reset_token VARCHAR(255),
  reset_token_expiry DATETIME,
  is_active BOOLEAN DEFAULT TRUE,
  last_login TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Student Service Administrators table (created second, no dependencies)
CREATE TABLE IF NOT EXISTS student_service_admins (
  id INT PRIMARY KEY AUTO_INCREMENT,
  admin_id VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  phone VARCHAR(20),
  department VARCHAR(100),
  permissions JSON,
  profile_image VARCHAR(255),
  reset_token VARCHAR(255),
  reset_token_expiry DATETIME,
  is_active BOOLEAN DEFAULT TRUE,
  last_login TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Lecturers table (created third, no dependencies)
CREATE TABLE IF NOT EXISTS lecturers (
  id INT PRIMARY KEY AUTO_INCREMENT,
  lecturer_id VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  phone VARCHAR(20),
  department VARCHAR(100),
  profile_image VARCHAR(255),
  reset_token VARCHAR(255),
  reset_token_expiry DATETIME,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Students table (created after student_service_admins because it references it)
CREATE TABLE IF NOT EXISTS students (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  phone VARCHAR(20),
  address TEXT,
  face_data TEXT,
  profile_image VARCHAR(255),
  intake_period ENUM('April', 'July', 'September', 'January') NOT NULL,
  intake_year YEAR NOT NULL,
  academic_year VARCHAR(20),
  program VARCHAR(100),
  level ENUM('Diploma', 'Degree', 'Masters', 'PhD') DEFAULT 'Degree',
  created_by_admin_id INT,
  reset_token VARCHAR(255),
  reset_token_expiry DATETIME,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (created_by_admin_id) REFERENCES student_service_admins(id) ON DELETE SET NULL,
  INDEX idx_intake (intake_period, intake_year),
  INDEX idx_program (program, level)
);

-- ==========================================
-- ACADEMIC STRUCTURE TABLES
-- ==========================================

-- Intake periods management
CREATE TABLE IF NOT EXISTS intake_periods (
  id INT PRIMARY KEY AUTO_INCREMENT,
  intake_name VARCHAR(50) NOT NULL,
  intake_period ENUM('April', 'July', 'September', 'January') NOT NULL,
  intake_year YEAR NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  registration_deadline DATE,
  max_students INT,
  current_students INT DEFAULT 0,
  status ENUM('upcoming', 'open', 'closed', 'completed') DEFAULT 'upcoming',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY unique_intake (intake_period, intake_year)
);

-- Classes table
CREATE TABLE IF NOT EXISTS classes (
  id INT PRIMARY KEY AUTO_INCREMENT,
  class_code VARCHAR(20) UNIQUE NOT NULL,
  class_name VARCHAR(100) NOT NULL,
  description TEXT,
  lecturer_id INT,
  academic_year VARCHAR(20),
  semester VARCHAR(20),
  credits INT DEFAULT 3,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (lecturer_id) REFERENCES lecturers(id) ON DELETE SET NULL
);

-- Timetable table
CREATE TABLE IF NOT EXISTS timetable (
  id INT PRIMARY KEY AUTO_INCREMENT,
  class_id INT NOT NULL,
  day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  room VARCHAR(50),
  is_active BOOLEAN DEFAULT TRUE,
  FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
);

-- Student enrollments
CREATE TABLE IF NOT EXISTS student_enrollments (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id INT NOT NULL,
  class_id INT NOT NULL,
  enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status ENUM('active', 'dropped', 'completed') DEFAULT 'active',
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
  UNIQUE KEY unique_enrollment (student_id, class_id)
);

-- ==========================================
-- ATTENDANCE MANAGEMENT TABLES
-- ==========================================

-- Attendance records
CREATE TABLE IF NOT EXISTS attendance (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id INT NOT NULL,
  class_id INT NOT NULL,
  timetable_id INT,
  check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status ENUM('present', 'late', 'absent', 'excused') DEFAULT 'present',
  face_confidence DECIMAL(5,2),
  is_manual BOOLEAN DEFAULT FALSE,
  manually_edited_by INT,
  edit_reason TEXT,
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
  FOREIGN KEY (timetable_id) REFERENCES timetable(id) ON DELETE SET NULL,
  INDEX idx_student_date (student_id, check_in_time),
  INDEX idx_class_date (class_id, check_in_time)
);

-- Attendance sessions (for real-time monitoring - User Story #14, #17)
CREATE TABLE IF NOT EXISTS attendance_sessions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  class_id INT NOT NULL,
  timetable_id INT,
  lecturer_id INT NOT NULL,
  session_date DATE NOT NULL,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  status ENUM('scheduled', 'ongoing', 'completed', 'cancelled') DEFAULT 'scheduled',
  total_students INT DEFAULT 0,
  present_count INT DEFAULT 0,
  late_count INT DEFAULT 0,
  absent_count INT DEFAULT 0,
  FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
  FOREIGN KEY (timetable_id) REFERENCES timetable(id) ON DELETE SET NULL,
  FOREIGN KEY (lecturer_id) REFERENCES lecturers(id) ON DELETE CASCADE,
  INDEX idx_session_date (session_date, class_id)
);

-- Medical certificates
CREATE TABLE IF NOT EXISTS medical_certificates (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id INT NOT NULL,
  certificate_file VARCHAR(255) NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  reason TEXT,
  status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
  reviewed_by INT,
  review_notes TEXT,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  reviewed_at TIMESTAMP NULL,
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- ==========================================
-- SYSTEM CONFIGURATION TABLES
-- ==========================================

-- System configuration (User Story #22, #26)
CREATE TABLE IF NOT EXISTS system_config (
  id INT PRIMARY KEY AUTO_INCREMENT,
  config_key VARCHAR(100) UNIQUE NOT NULL,
  config_value TEXT,
  config_type VARCHAR(50),
  description TEXT,
  updated_by INT,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Attendance policies (User Story #26)
CREATE TABLE IF NOT EXISTS attendance_policies (
  id INT PRIMARY KEY AUTO_INCREMENT,
  policy_name VARCHAR(100) NOT NULL,
  grace_period_minutes INT DEFAULT 10,
  late_threshold_minutes INT DEFAULT 15,
  minimum_attendance_percentage DECIMAL(5,2) DEFAULT 75.00,
  applies_to ENUM('university', 'department', 'course') DEFAULT 'university',
  entity_id INT,
  is_active BOOLEAN DEFAULT TRUE,
  created_by INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Apply policies to classes
CREATE TABLE IF NOT EXISTS class_policies (
  id INT PRIMARY KEY AUTO_INCREMENT,
  class_id INT NOT NULL,
  policy_id INT NOT NULL,
  FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
  FOREIGN KEY (policy_id) REFERENCES attendance_policies(id) ON DELETE CASCADE,
  UNIQUE KEY unique_class_policy (class_id, policy_id)
);

-- ==========================================
-- AUDIT & LOGGING TABLES
-- ==========================================

-- Audit logs (User Story #29)
CREATE TABLE IF NOT EXISTS audit_logs (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_type ENUM('student', 'lecturer', 'system_admin', 'student_service_admin') NOT NULL,
  user_id INT NOT NULL,
  action VARCHAR(100) NOT NULL,
  table_name VARCHAR(50),
  record_id INT,
  old_values JSON,
  new_values JSON,
  ip_address VARCHAR(45),
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user (user_type, user_id),
  INDEX idx_action (action),
  INDEX idx_date (created_at)
);

-- Notifications (User Story #17)
CREATE TABLE IF NOT EXISTS notifications (
  id INT PRIMARY KEY AUTO_INCREMENT,
  recipient_type ENUM('student', 'lecturer', 'system_admin', 'student_service_admin') NOT NULL,
  recipient_id INT NOT NULL,
  notification_type VARCHAR(50) NOT NULL,
  title VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  related_table VARCHAR(50),
  related_id INT,
  is_read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  read_at TIMESTAMP NULL,
  INDEX idx_recipient (recipient_type, recipient_id, is_read)
);

-- ==========================================
-- SYSTEM MONITORING TABLES
-- ==========================================

-- Hardware devices (cameras, sensors, etc.) - User Story #22, #23
CREATE TABLE IF NOT EXISTS devices (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  type VARCHAR(50) NOT NULL COMMENT 'camera, sensor, server, etc.',
  status ENUM('online', 'offline', 'maintenance') DEFAULT 'offline',
  last_seen TIMESTAMP,
  latency_ms INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_status (status),
  INDEX idx_last_seen (last_seen)
);

-- System alerts (User Story #25)
CREATE TABLE IF NOT EXISTS system_alerts (
  id INT PRIMARY KEY AUTO_INCREMENT,
  alert_type ENUM('camera_offline', 'sensor_offline', 'system_error', 'security') NOT NULL,
  severity ENUM('low', 'medium', 'high', 'critical') NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  device_id VARCHAR(100),
  location VARCHAR(100),
  status ENUM('new', 'acknowledged', 'resolved') DEFAULT 'new',
  acknowledged_by INT,
  resolved_by INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  acknowledged_at TIMESTAMP NULL,
  resolved_at TIMESTAMP NULL,
  INDEX idx_status (status, severity)
);

-- ==========================================
-- REPORTS & ANALYTICS TABLES
-- ==========================================

-- Generated reports (User Story #15, #36, #32)
CREATE TABLE IF NOT EXISTS reports (
  id INT PRIMARY KEY AUTO_INCREMENT,
  report_type VARCHAR(50) NOT NULL,
  report_name VARCHAR(255) NOT NULL,
  generated_by_type ENUM('lecturer', 'system_admin', 'student_service_admin') NOT NULL,
  generated_by_id INT NOT NULL,
  filters JSON,
  file_path VARCHAR(255),
  file_format ENUM('pdf', 'csv', 'xlsx') DEFAULT 'pdf',
  status ENUM('generating', 'completed', 'failed') DEFAULT 'generating',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_generated_by (generated_by_type, generated_by_id)
);

-- ==========================================
-- INSERT SAMPLE DATA
-- ==========================================

-- Sample System Admins
INSERT INTO system_admins (admin_id, email, password, first_name, last_name, permissions) VALUES
('SYSADMIN001', 'admin@attendance.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'System', 'Administrator', '{"all": true}'),
('SYSADMIN002', 'sysadmin@university.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Tech', 'Admin', '{"all": true}');

-- Sample Student Service Admins
INSERT INTO student_service_admins (admin_id, email, password, first_name, last_name, department, permissions) VALUES
('SSA001', 'studentservice@attendance.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Student Service', 'Administrator', 'Student Affairs', '{"attendance": true, "students": true, "reports": true, "medical_certificates": true}'),
('SSA002', 'registry@university.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Registry', 'Officer', 'Registrar Office', '{"attendance": true, "students": true, "reports": true}');

-- Sample Lecturers
INSERT INTO lecturers (lecturer_id, email, password, first_name, last_name, department) VALUES
('LEC001', 'john.smith@university.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'John', 'Smith', 'Computer Science'),
('LEC002', 'jane.doe@university.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Jane', 'Doe', 'Computer Science'),
('LEC003', 'mike.johnson@university.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Mike', 'Johnson', 'Computer Science');

-- Sample Classes with Lecturer IDs
INSERT INTO classes (class_code, class_name, description, lecturer_id, academic_year, semester) VALUES
('CS101', 'Introduction to Computer Science', 'Basic programming concepts', 1, '2024/2025', 'Semester 1'),
('CS201', 'Data Structures', 'Advanced data structures and algorithms', 2, '2024/2025', 'Semester 1'),
('CS301', 'Database Systems', 'Database design and management', 3, '2024/2025', 'Semester 1');

-- Sample Timetable
INSERT INTO timetable (class_id, day_of_week, start_time, end_time, room) VALUES
(1, 'Monday', '09:00:00', '11:00:00', 'Room 101'),
(1, 'Wednesday', '09:00:00', '11:00:00', 'Room 101'),
(2, 'Tuesday', '14:00:00', '16:00:00', 'Room 202'),
(2, 'Thursday', '14:00:00', '16:00:00', 'Room 202'),
(3, 'Friday', '10:00:00', '12:00:00', 'Room 303');

-- Sample System Configuration
INSERT INTO system_config (config_key, config_value, config_type, description) VALUES
('default_grace_period', '10', 'integer', 'Default grace period in minutes for late arrivals'),
('min_attendance_percentage', '75', 'decimal', 'Minimum attendance percentage required'),
('enable_face_recognition', 'true', 'boolean', 'Enable/disable face recognition feature'),
('max_upload_size', '5242880', 'integer', 'Maximum file upload size in bytes (5MB)'),
('session_timeout', '3600', 'integer', 'Session timeout in seconds');

-- Sample Attendance Policy
INSERT INTO attendance_policies (policy_name, grace_period_minutes, late_threshold_minutes, minimum_attendance_percentage, applies_to, is_active) VALUES
('University Default Policy', 10, 15, 75.00, 'university', TRUE),
('Computer Science Department Policy', 5, 10, 80.00, 'department', TRUE);

-- Apply policies to classes
INSERT INTO class_policies (class_id, policy_id) VALUES
(1, 1),
(2, 1),
(3, 2);

-- Sample Intake Periods
INSERT INTO intake_periods (intake_name, intake_period, intake_year, start_date, end_date, registration_deadline, max_students, status) VALUES
('April 2024 Intake', 'April', 2024, '2024-04-01', '2024-07-31', '2024-03-15', 500, 'completed'),
('July 2024 Intake', 'July', 2024, '2024-07-01', '2024-10-31', '2024-06-15', 500, 'completed'),
('April 2025 Intake', 'April', 2025, '2025-04-01', '2025-07-31', '2025-03-15', 500, 'open'),
('July 2025 Intake', 'July', 2025, '2025-07-01', '2025-10-31', '2025-06-15', 500, 'upcoming');

-- Sample Students (created by Student Service Admin)
INSERT INTO students (student_id, email, password, first_name, last_name, phone, intake_period, intake_year, academic_year, program, level, created_by_admin_id) VALUES
('STU2025001', 'alice.wong@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Alice', 'Wong', '0123456789', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1),
('STU2025002', 'bob.tan@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Bob', 'Tan', '0123456788', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1),
('STU2024003', 'charlie.lee@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Charlie', 'Lee', '0123456787', 'July', 2024, '2024/2025', 'Information Technology', 'Diploma', 1),
('STU2024004', 'diana.kumar@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Diana', 'Kumar', '0123456786', 'July', 2024, '2024/2025', 'Software Engineering', 'Degree', 2);

-- Enroll sample students in classes
INSERT INTO student_enrollments (student_id, class_id, status) VALUES
(1, 1, 'active'),
(1, 2, 'active'),
(2, 1, 'active'),
(2, 3, 'active'),
(3, 1, 'active'),
(4, 2, 'active'),
(4, 3, 'active');
