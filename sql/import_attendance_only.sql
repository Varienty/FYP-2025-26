-- Import only attendance data (skip CREATE TABLE since attendance table already exists)
-- This extracts only the INSERT statements from student_attendance.sql

INSERT INTO `attendance` (`id`, `student_id`, `class_id`, `timetable_id`, `check_in_time`, `status`, `face_confidence`, `is_manual`, `manually_edited_by`, `edit_reason`) VALUES
(3, 3, 1, 1, '2025-12-04 16:28:33', 'absent', NULL, 1, NULL, NULL),
(8, 9, 1, 1, '2025-12-04 16:28:33', 'absent', NULL, 1, NULL, NULL),
(9, 10, 1, 1, '2025-12-04 16:30:42', 'present', 95.50, 0, NULL, NULL),
(10, 11, 1, 1, '2025-12-04 16:31:05', 'present', 97.20, 0, NULL, NULL),
(11, 12, 1, 1, '2025-12-04 16:29:33', 'late', 94.80, 0, NULL, NULL),
(12, 13, 1, 1, '2025-12-04 16:32:01', 'present', 96.10, 0, NULL, NULL),
(13, 14, 1, 1, '2025-12-04 16:33:18', 'present', 98.30, 0, NULL, NULL),
(14, 15, 1, 1, '2025-12-04 16:28:45', 'present', 95.75, 0, NULL, NULL),
(15, 16, 1, 1, '2025-12-04 16:30:15', 'present', 97.85, 0, NULL, NULL),
(16, 17, 2, 3, '2025-12-04 14:30:12', 'present', 96.20, 0, NULL, NULL),
(17, 18, 2, 3, '2025-12-04 14:31:44', 'present', 94.50, 0, NULL, NULL),
(18, 19, 2, 3, '2025-12-04 14:29:56', 'late', 93.10, 0, NULL, NULL),
(19, 20, 2, 3, '2025-12-04 14:32:33', 'present', 97.65, 0, NULL, NULL),
(20, 1, 3, 5, '2025-12-05 10:15:22', 'present', 98.50, 0, NULL, NULL),
(21, 2, 3, 5, '2025-12-05 10:16:45', 'present', 96.30, 0, NULL, NULL),
(22, 4, 3, 5, '2025-12-05 10:14:33', 'present', 95.80, 0, NULL, NULL),
(23, 7, 3, 5, '2025-12-05 10:17:12', 'late', 92.70, 0, NULL, NULL),
(24, 1, 1, 2, '2025-12-05 09:30:44', 'present', 97.45, 0, NULL, NULL),
(25, 2, 1, 2, '2025-12-05 09:31:12', 'present', 96.78, 0, NULL, NULL),
(26, 3, 1, 2, '2025-12-05 09:32:01', 'present', 95.25, 0, NULL, NULL);
