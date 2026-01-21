-- Additional test data that does NOT conflict with schema.sql sample data
-- Import this AFTER schema.sql has been successfully imported
-- This adds 16 more students, attendance records, and supporting data

USE student_attendance;

-- =============================
-- Additional Students (IDs 5-20, avoiding 1-4 from schema)
-- =============================

INSERT INTO students (student_id, email, password, first_name, last_name, phone, intake_period, intake_year, academic_year, program, level, created_by_admin_id) VALUES
('STU2025005', 'eva.lim@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Eva', 'Lim', '0123456710', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1),
('STU2025006', 'farid.azmi@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Farid', 'Azmi', '0123456711', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1),
('STU2025007', 'grace.ong@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Grace', 'Ong', '0123456712', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1),
('STU2025008', 'haris.rahman@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Haris', 'Rahman', '0123456713', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1),
('STU2025009', 'isha.nair@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Isha', 'Nair', '0123456714', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1),
('STU2025010', 'jack.lee@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Jack', 'Lee', '0123456715', 'April', 2025, '2025/2026', 'Software Engineering', 'Degree', 2),
('STU2025011', 'kelly.tan@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Kelly', 'Tan', '0123456716', 'April', 2025, '2025/2026', 'Software Engineering', 'Degree', 2),
('STU2025012', 'liam.goh@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Liam', 'Goh', '0123456717', 'April', 2025, '2025/2026', 'Information Technology', 'Diploma', 1),
('STU2025013', 'maya.ahmad@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Maya', 'Ahmad', '0123456718', 'April', 2025, '2025/2026', 'Information Technology', 'Diploma', 1),
('STU2025014', 'nathan.chong@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Nathan', 'Chong', '0123456719', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1),
('STU2025015', 'olivia.ho@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Olivia', 'Ho', '0123456720', 'April', 2025, '2025/2026', 'Computer Science', 'Degree', 1),
('STU2025016', 'pranav.pillai@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Pranav', 'Pillai', '0123456721', 'April', 2025, '2025/2026', 'Database Systems', 'Degree', 1),
('STU2025017', 'qi.yap@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Qi', 'Yap', '0123456722', 'April', 2025, '2025/2026', 'Database Systems', 'Degree', 1),
('STU2025018', 'rachel.swee@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Rachel', 'Swee', '0123456723', 'April', 2025, '2025/2026', 'Data Science', 'Degree', 1),
('STU2025019', 'sanjay.naidu@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Sanjay', 'Naidu', '0123456724', 'April', 2025, '2025/2026', 'Data Science', 'Degree', 1),
('STU2025020', 'tania.ong@student.edu', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Tania', 'Ong', '0123456725', 'April', 2025, '2025/2026', 'Software Engineering', 'Degree', 2);

-- =============================
-- Additional Enrollments (students 5-20)
-- =============================

INSERT INTO student_enrollments (student_id, class_id, status) VALUES
(5, 1, 'active'),(5, 2, 'active'),
(6, 1, 'active'),(6, 2, 'active'),
(7, 1, 'active'),(7, 3, 'active'),
(8, 1, 'active'),
(9, 1, 'active'),(9, 3, 'active'),
(10, 2, 'active'),(10, 3, 'active'),
(11, 2, 'active'),
(12, 1, 'active'),
(13, 1, 'active'),
(14, 1, 'active'),(14, 2, 'active'),
(15, 1, 'active'),(15, 3, 'active'),
(16, 3, 'active'),
(17, 3, 'active'),
(18, 3, 'active'),
(19, 3, 'active'),
(20, 2, 'active');

-- =============================
-- Attendance Sessions (realistic dates)
-- =============================

INSERT INTO attendance_sessions (class_id, timetable_id, lecturer_id, session_date, start_time, end_time, status, total_students) VALUES
(1, 1, 1, '2025-11-18', '2025-11-18 09:00:00', '2025-11-18 11:00:00', 'completed', 12),
(1, 2, 1, '2025-11-20', '2025-11-20 09:00:00', '2025-11-20 11:00:00', 'completed', 12),
(1, 1, 1, '2025-11-25', '2025-11-25 09:00:00', '2025-11-25 11:00:00', 'completed', 12),
(1, 2, 1, '2025-11-27', '2025-11-27 09:00:00', '2025-11-27 11:00:00', 'completed', 12),
(2, 3, 2, '2025-11-19', '2025-11-19 14:00:00', '2025-11-19 16:00:00', 'completed', 10),
(2, 4, 2, '2025-11-21', '2025-11-21 14:00:00', '2025-11-21 16:00:00', 'completed', 10),
(2, 3, 2, '2025-11-26', '2025-11-26 14:00:00', '2025-11-26 16:00:00', 'completed', 10),
(3, 5, 3, '2025-11-22', '2025-11-22 10:00:00', '2025-11-22 12:00:00', 'completed', 8),
(3, 5, 3, '2025-11-29', '2025-11-29 10:00:00', '2025-11-29 12:00:00', 'completed', 8);

-- =============================
-- Attendance Records (spread across sessions)
-- =============================

-- Session 1: Nov 18 CS101
INSERT INTO attendance (student_id, class_id, timetable_id, check_in_time, status, face_confidence, is_manual) VALUES
(1, 1, 1, '2025-11-18 09:03:00', 'present', 97.2, FALSE),
(2, 1, 1, '2025-11-18 09:17:00', 'late', 91.0, FALSE),
(3, 1, 1, NULL, 'absent', NULL, TRUE),
(5, 1, 1, '2025-11-18 09:05:00', 'present', 96.5, FALSE),
(6, 1, 1, '2025-11-18 09:02:00', 'present', 98.1, FALSE),
(7, 1, 1, '2025-11-18 09:18:00', 'late', 92.3, FALSE),
(8, 1, 1, '2025-11-18 09:01:00', 'present', 99.0, FALSE),
(9, 1, 1, NULL, 'absent', NULL, TRUE),
(12, 1, 1, '2025-11-18 09:10:00', 'present', 95.8, FALSE),
(13, 1, 1, '2025-11-18 09:04:00', 'present', 97.5, FALSE),
(14, 1, 1, '2025-11-18 09:15:00', 'late', 93.2, FALSE),
(15, 1, 1, '2025-11-18 09:06:00', 'present', 96.9, FALSE);

-- Session 2: Nov 20 CS101
INSERT INTO attendance (student_id, class_id, timetable_id, check_in_time, status, face_confidence, is_manual) VALUES
(1, 1, 2, '2025-11-20 09:06:00', 'present', 95.3, FALSE),
(2, 1, 2, '2025-11-20 09:02:00', 'present', 98.2, FALSE),
(3, 1, 2, NULL, 'excused', NULL, TRUE),
(5, 1, 2, NULL, 'absent', NULL, TRUE),
(6, 1, 2, '2025-11-20 09:12:00', 'late', 92.8, FALSE),
(7, 1, 2, '2025-11-20 09:03:00', 'present', 97.6, FALSE),
(8, 1, 2, '2025-11-20 09:20:00', 'late', 90.5, FALSE),
(9, 1, 2, '2025-11-20 09:05:00', 'present', 96.1, FALSE),
(12, 1, 2, '2025-11-20 09:07:00', 'present', 95.5, FALSE),
(13, 1, 2, '2025-11-20 09:16:00', 'late', 91.8, FALSE),
(14, 1, 2, '2025-11-20 09:04:00', 'present', 97.0, FALSE),
(15, 1, 2, '2025-11-20 09:08:00', 'present', 96.3, FALSE);

-- Session 3: Nov 25 CS101
INSERT INTO attendance (student_id, class_id, timetable_id, check_in_time, status, face_confidence, is_manual) VALUES
(1, 1, 1, '2025-11-25 09:02:15', 'present', 98.5, FALSE),
(2, 1, 1, '2025-11-25 09:12:03', 'late', 94.1, FALSE),
(3, 1, 1, NULL, 'absent', NULL, TRUE),
(5, 1, 1, '2025-11-25 09:05:44', 'present', 96.0, FALSE),
(6, 1, 1, '2025-11-25 09:16:22', 'late', 92.3, FALSE),
(7, 1, 1, '2025-11-25 09:01:10', 'present', 99.2, FALSE),
(8, 1, 1, NULL, 'excused', NULL, TRUE),
(9, 1, 1, '2025-11-25 09:20:00', 'late', 90.0, FALSE),
(12, 1, 1, '2025-11-25 09:03:30', 'present', 97.8, FALSE),
(13, 1, 1, '2025-11-25 09:04:15', 'present', 96.7, FALSE),
(14, 1, 1, '2025-11-25 09:18:45', 'late', 91.5, FALSE),
(15, 1, 1, '2025-11-25 09:08:11', 'present', 95.4, FALSE);

-- Session 4: Nov 27 CS101
INSERT INTO attendance (student_id, class_id, timetable_id, check_in_time, status, face_confidence, is_manual) VALUES
(1, 1, 2, '2025-11-27 09:01:05', 'present', 98.9, FALSE),
(2, 1, 2, '2025-11-27 09:15:45', 'late', 91.2, FALSE),
(3, 1, 2, '2025-11-27 09:05:20', 'present', 96.8, FALSE),
(5, 1, 2, NULL, 'absent', NULL, TRUE),
(6, 1, 2, '2025-11-27 09:03:21', 'present', 97.1, FALSE),
(7, 1, 2, '2025-11-27 09:07:10', 'present', 95.9, FALSE),
(8, 1, 2, '2025-11-27 09:02:00', 'present', 98.3, FALSE),
(9, 1, 2, '2025-11-27 09:19:30', 'late', 90.8, FALSE),
(12, 1, 2, '2025-11-27 09:10:15', 'present', 94.6, FALSE),
(13, 1, 2, '2025-11-27 09:06:00', 'present', 96.5, FALSE),
(14, 1, 2, '2025-11-27 09:04:40', 'present', 97.2, FALSE),
(15, 1, 2, '2025-11-27 09:17:20', 'late', 92.1, FALSE);

-- Session 5-7: CS201
INSERT INTO attendance (student_id, class_id, timetable_id, check_in_time, status, face_confidence, is_manual) VALUES
(1, 2, 3, '2025-11-19 14:03:00', 'present', 96.7, FALSE),
(4, 2, 3, '2025-11-19 14:05:00', 'present', 97.3, FALSE),
(5, 2, 3, '2025-11-19 14:18:00', 'late', 92.5, FALSE),
(6, 2, 3, '2025-11-19 14:02:00', 'present', 98.0, FALSE),
(10, 2, 3, '2025-11-19 14:03:00', 'present', 96.7, FALSE),
(11, 2, 3, NULL, 'absent', NULL, TRUE),
(14, 2, 3, '2025-11-19 14:16:00', 'late', 91.8, FALSE),
(20, 2, 3, '2025-11-19 14:01:00', 'present', 99.1, FALSE),
(1, 2, 4, '2025-11-21 14:04:00', 'present', 96.2, FALSE),
(4, 2, 4, '2025-11-21 14:02:00', 'present', 98.5, FALSE),
(5, 2, 4, '2025-11-21 14:06:00', 'present', 95.8, FALSE),
(6, 2, 4, '2025-11-21 14:19:00', 'late', 91.3, FALSE),
(10, 2, 4, NULL, 'absent', NULL, TRUE),
(11, 2, 4, '2025-11-21 14:05:00', 'present', 96.9, FALSE),
(14, 2, 4, '2025-11-21 14:20:00', 'late', 90.2, FALSE),
(20, 2, 4, '2025-11-21 14:00:30', 'present', 98.9, FALSE),
(1, 2, 3, '2025-11-26 14:02:33', 'present', 97.8, FALSE),
(4, 2, 3, '2025-11-26 14:01:10', 'present', 99.0, FALSE),
(5, 2, 3, '2025-11-26 14:15:22', 'late', 92.1, FALSE),
(6, 2, 3, '2025-11-26 14:03:45', 'present', 96.4, FALSE),
(10, 2, 3, '2025-11-26 14:02:00', 'present', 97.5, FALSE),
(11, 2, 3, '2025-11-26 14:18:47', 'late', 93.6, FALSE),
(14, 2, 3, NULL, 'absent', NULL, TRUE),
(20, 2, 3, '2025-11-26 14:00:59', 'present', 99.0, FALSE);

-- Session 8-9: CS301
INSERT INTO attendance (student_id, class_id, timetable_id, check_in_time, status, face_confidence, is_manual) VALUES
(2, 3, 5, '2025-11-22 10:05:00', 'present', 96.8, FALSE),
(4, 3, 5, '2025-11-22 10:03:00', 'present', 97.9, FALSE),
(7, 3, 5, '2025-11-22 10:17:00', 'late', 91.5, FALSE),
(9, 3, 5, '2025-11-22 10:04:00', 'present', 96.3, FALSE),
(15, 3, 5, '2025-11-22 10:02:00', 'present', 98.2, FALSE),
(16, 3, 5, '2025-11-22 10:06:00', 'present', 95.7, FALSE),
(17, 3, 5, NULL, 'absent', NULL, TRUE),
(18, 3, 5, '2025-11-22 10:20:00', 'late', 90.4, FALSE),
(2, 3, 5, '2025-11-29 10:03:15', 'present', 97.2, FALSE),
(4, 3, 5, '2025-11-29 10:01:50', 'present', 98.6, FALSE),
(7, 3, 5, '2025-11-29 10:05:30', 'present', 96.1, FALSE),
(9, 3, 5, NULL, 'excused', NULL, TRUE),
(15, 3, 5, '2025-11-29 10:18:10', 'late', 92.3, FALSE),
(16, 3, 5, '2025-11-29 10:04:02', 'present', 96.9, FALSE),
(17, 3, 5, '2025-11-29 10:23:55', 'late', 90.5, FALSE),
(18, 3, 5, NULL, 'absent', NULL, TRUE),
(19, 3, 5, NULL, 'excused', NULL, TRUE);

-- =============================
-- Medical Certificates
-- =============================

INSERT INTO medical_certificates (student_id, certificate_file, start_date, end_date, reason, status, reviewed_by, review_notes) VALUES
(3, 'certs/MC_STU2024003_20251120.pdf', '2025-11-20', '2025-11-20', 'Flu - excused absence', 'approved', 1, 'Valid clinic certificate.'),
(5, 'certs/MC_STU2025005_20251125.pdf', '2025-11-25', '2025-11-25', 'Medical appointment', 'approved', 1, 'Approved.'),
(8, 'certs/MC_STU2025008_20251125.pdf', '2025-11-25', '2025-11-26', 'Food poisoning', 'approved', 1, 'Hospital ER verified.'),
(9, 'certs/MC_STU2025009_20251129.pdf', '2025-11-29', '2025-11-29', 'Dental surgery', 'approved', 2, 'Valid.'),
(18, 'certs/MC_STU2025018_20251129.pdf', '2025-11-29', '2025-11-30', 'Family emergency', 'pending', NULL, NULL),
(19, 'certs/MC_STU2025019_20251129.pdf', '2025-11-29', '2025-11-29', 'Medical checkup', 'pending', NULL, NULL);

-- =============================
-- Notifications
-- =============================

INSERT INTO notifications (recipient_type, recipient_id, notification_type, title, message, related_table, related_id, is_read, read_at) VALUES
('lecturer', 1, 'session_summary', 'CS101 Nov 18 Complete', '12 enrolled, 9 present, 2 late, 1 absent', 'attendance_sessions', 1, TRUE, '2025-11-18 11:15:00'),
('lecturer', 1, 'session_summary', 'CS101 Nov 20 Complete', '12 enrolled, 7 present, 3 late, 1 excused, 1 absent', 'attendance_sessions', 2, TRUE, '2025-11-20 11:20:00'),
('lecturer', 1, 'session_summary', 'CS101 Nov 25 Complete', '12 enrolled, 7 present, 4 late, 1 absent', 'attendance_sessions', 3, FALSE, NULL),
('lecturer', 2, 'session_summary', 'CS201 Nov 19 Complete', '10 enrolled, 6 present, 2 late, 2 absent', 'attendance_sessions', 5, TRUE, '2025-11-19 16:10:00'),
('lecturer', 3, 'session_summary', 'CS301 Nov 22 Complete', '8 enrolled, 5 present, 2 late, 1 absent', 'attendance_sessions', 8, TRUE, '2025-11-22 12:15:00'),
('student', 2, 'attendance_status', 'Late CS101', 'Marked late 2025-11-18. Be punctual.', 'attendance', 2, FALSE, NULL),
('student', 3, 'certificate_approved', 'MC Approved', 'Your MC for Nov 20 approved.', 'medical_certificates', 1, TRUE, '2025-11-21 10:00:00'),
('system_admin', 1, 'device_alert', 'Camera Offline', 'Room 101 camera offline', NULL, NULL, FALSE, NULL),
('student_service_admin', 1, 'report_ready', 'Daily Report Ready', 'Nov 26 report available', 'reports', 1, TRUE, '2025-11-26 12:30:00');

-- =============================
-- Audit Logs
-- =============================

INSERT INTO audit_logs (user_type, user_id, action, table_name, record_id, old_values, new_values, ip_address) VALUES
('lecturer', 1, 'SESSION_COMPLETE', 'attendance_sessions', 1, NULL, '{"status":"completed"}', '192.168.1.10'),
('lecturer', 1, 'SESSION_COMPLETE', 'attendance_sessions', 2, NULL, '{"status":"completed"}', '192.168.1.10'),
('student_service_admin', 1, 'ATTENDANCE_EDIT', 'attendance', 3, '{"status":"present"}', '{"status":"absent"}', '192.168.1.50'),
('student_service_admin', 1, 'MC_APPROVED', 'medical_certificates', 1, '{"status":"pending"}', '{"status":"approved"}', '192.168.1.50'),
('system_admin', 1, 'DEVICE_ACK', 'system_alerts', 1, '{"status":"new"}', '{"status":"acknowledged"}', '192.168.1.100'),
('lecturer', 2, 'REPORT_GENERATED', 'reports', 1, NULL, '{"status":"completed"}', '192.168.1.15');

-- =============================
-- System Alerts & Devices
-- =============================

INSERT INTO system_alerts (alert_type, severity, title, description, device_id, location, status, acknowledged_by) VALUES
('camera_offline', 'high', 'Camera Offline Room 101', 'No frames received', 'CAM-ROOM101', 'Room 101', 'acknowledged', 1),
('sensor_offline', 'medium', 'RFID Intermittent', 'Connection drops', 'RFID-202', 'Room 202', 'new', NULL),
('system_error', 'critical', 'Face Recognition Error', 'GPU driver issue', NULL, 'Server A', 'new', NULL);

INSERT INTO devices (id, name, type, status, last_seen, latency_ms) VALUES
('CAM-ROOM101', 'Room 101 Camera', 'camera', 'offline', '2025-11-25 11:05:00', 0),
('CAM-ROOM202', 'Room 202 Camera', 'camera', 'online', '2025-12-04 14:00:10', 12),
('CAM-ROOM303', 'Room 303 Camera', 'camera', 'online', '2025-12-04 12:05:00', 15),
('RFID-202', 'RFID Reader 202', 'reader', 'online', '2025-12-04 16:00:00', 25),
('RFID-101', 'RFID Reader 101', 'reader', 'online', '2025-12-04 15:30:00', 18),
('TERM-ADM', 'Admin Terminal', 'terminal', 'online', '2025-12-05 10:00:00', 5);

-- =============================
-- Additional Policies
-- =============================

INSERT INTO policies (id, name, min_percentage, grace, late, scope, active_from, active_to) VALUES
('POL-GLOBAL', 'Global Policy', 75, 10, 15, 'global', '2025-01-01', NULL),
('POL-DEPT-CS', 'CS Dept Strict', 80, 5, 10, 'department', '2025-01-01', NULL);

-- =============================
-- Reports
-- =============================

INSERT INTO reports (report_type, report_name, generated_by_type, generated_by_id, filters, file_path, file_format, status) VALUES
('attendance_summary', 'CS101 Nov Summary', 'lecturer', 1, '{"class_id":1,"month":"2025-11"}', 'reports/cs101_nov2025.csv', 'csv', 'completed'),
('attendance_summary', 'CS201 Nov Summary', 'lecturer', 2, '{"class_id":2,"month":"2025-11"}', 'reports/cs201_nov2025.csv', 'csv', 'completed'),
('daily_overview', 'Daily Nov 26', 'student_service_admin', 1, '{"date":"2025-11-26"}', 'reports/daily_20251126.pdf', 'pdf', 'completed');

-- =============================
-- Additional System Config
-- =============================

INSERT INTO system_config (config_key, config_value, config_type, description) VALUES
('notifications_enabled', 'true', 'boolean', 'Enable notifications'),
('hardware_monitoring_enabled', 'true', 'boolean', 'Enable hardware monitor'),
('report_storage_dir', 'reports', 'string', 'Report directory'),
('face_confidence_threshold', '90.0', 'decimal', 'Min confidence for auto-mark');

-- =============================
-- Hardware Devices
-- =============================

INSERT INTO devices (id, name, type, status, last_seen, latency_ms) VALUES
('cam_1', 'Entrance Camera 1 - Building A', 'camera', 'online', NOW(), 120),
('cam_2', 'Lecture Hall Camera - LT-101', 'camera', 'online', NOW(), 90),
('cam_3', 'Lab Camera - Lab 201', 'camera', 'offline', DATE_SUB(NOW(), INTERVAL 2 HOUR), 0),
('reader_1', 'RFID Reader A - Building A Floor 1', 'reader', 'online', NOW(), 40),
('reader_2', 'RFID Reader B - Building B Floor 2', 'reader', 'maintenance', DATE_SUB(NOW(), INTERVAL 1 HOUR), 0),
('sensor_1', 'Door Sensor A - Main Entrance', 'sensor', 'online', NOW(), 35);

