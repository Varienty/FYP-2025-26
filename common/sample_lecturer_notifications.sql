-- Sample Lecturer Notifications
-- Run this to populate the notifications table with sample data

-- First, get a sample lecturer ID (assuming lecturer with ID 1 exists)
-- You can replace the recipient_id values with your actual lecturer IDs

-- #3: Class Starting Soon (class_reminder)
INSERT INTO notifications (recipient_type, recipient_id, notification_type, title, message, related_table, related_id, is_read, created_at)
VALUES
('lecturer', 'LEC001', 'class_reminder', 'Class Starting in 15 Minutes',
 'Reminder: CS101 - Introduction to Programming starts at 2:00 PM in Room A101. Don\'t forget to start the attendance session!',
 'timetable', 1, 0, NOW()),

('lecturer', 'LEC001', 'class_reminder', 'Class Starting Soon',
 'Your next class CS201 - Data Structures begins in 30 minutes at Room B203. Prepare your materials.',
 'timetable', 2, 0, DATE_SUB(NOW(), INTERVAL 2 HOUR));

-- #4: Session Reminders - Active Sessions (session_active)
INSERT INTO notifications (recipient_type, recipient_id, notification_type, title, message, related_table, related_id, is_read, created_at)
VALUES
('lecturer', 'LEC001', 'session_active', 'Active Session Running',
 'You have an active attendance session for CS101 that has been running for 2 hours. Please remember to close it when class ends.',
 'attendance_sessions', 1, 0, DATE_SUB(NOW(), INTERVAL 30 MINUTE)),

('lecturer', 'LEC001', 'session_active', 'Attendance Session Still Active',
 'Your attendance session for CS201 started at 9:00 AM is still running. Close it to save attendance records.',
 'attendance_sessions', 2, 0, DATE_SUB(NOW(), INTERVAL 1 HOUR));

-- #8: Unusual Patterns - Attendance Alerts (attendance_alert)
INSERT INTO notifications (recipient_type, recipient_id, notification_type, title, message, related_table, related_id, is_read, created_at)
VALUES
('lecturer', 'LEC001', 'attendance_alert', 'High Absence Rate Detected',
 'Alert: 8 out of 25 students (32%) were absent in today\'s CS101 class. This is significantly higher than the average 12% absence rate.',
 'modules', 1, 0, DATE_SUB(NOW(), INTERVAL 3 HOUR)),

('lecturer', 'LEC001', 'attendance_alert', 'Attendance Drop Warning',
 'CS201 class attendance has decreased by 18% this week compared to last week. Average attendance is now 72%. Consider checking in with students.',
 'modules', 2, 0, DATE_SUB(NOW(), INTERVAL 1 DAY)),

('lecturer', 'LEC001', 'attendance_alert', 'Multiple Students Absent',
 'Unusual pattern: 6 students from Group A were absent today in CS301. You may want to check if there\'s a scheduling conflict.',
 'modules', 3, 1, DATE_SUB(NOW(), INTERVAL 2 DAY));

-- #9: Schedule Changes (schedule_change)
INSERT INTO notifications (recipient_type, recipient_id, notification_type, title, message, related_table, related_id, is_read, created_at)
VALUES
('lecturer', 'LEC001', 'schedule_change', 'Class Rescheduled',
 'Your CS101 class on Friday, Dec 1st has been moved from 2:00 PM to 4:00 PM. Room remains A101.',
 'timetable', 1, 0, DATE_SUB(NOW(), INTERVAL 4 HOUR)),

('lecturer', 'LEC001', 'schedule_change', 'Room Change Notice',
 'Important: CS201 - Data Structures has been moved from Room B203 to Room C305 starting next Monday. Time remains 9:00 AM.',
 'timetable', 2, 0, DATE_SUB(NOW(), INTERVAL 6 HOUR)),

('lecturer', 'LEC001', 'schedule_change', 'Weekly Schedule Updated',
 'Your teaching schedule for next week has been updated. CS301 Thursday class is cancelled due to public holiday.',
 'timetable', 3, 1, DATE_SUB(NOW(), INTERVAL 1 DAY));

-- #10: Facial Recognition Issues - Camera Offline (camera_offline)
INSERT INTO notifications (recipient_type, recipient_id, notification_type, title, message, related_table, related_id, is_read, created_at)
VALUES
('lecturer', 'LEC001', 'camera_offline', 'Camera System Offline',
 'Critical: Facial recognition camera in Room A101 is offline. Manual attendance marking required for your next CS101 class.',
 'devices', 1, 0, DATE_SUB(NOW(), INTERVAL 15 MINUTE)),

('lecturer', 'LEC001', 'camera_offline', 'Camera Connection Lost',
 'Warning: Camera in Room B203 lost connection at 1:45 PM. IT team has been notified. Use manual attendance if issue persists.',
 'devices', 2, 0, DATE_SUB(NOW(), INTERVAL 1 HOUR)),

('lecturer', 'LEC001', 'camera_offline', 'Scheduled Maintenance',
 'Notice: Facial recognition system will undergo maintenance on Saturday, Dec 2nd from 8:00 AM to 12:00 PM. All cameras will be offline.',
 'devices', NULL, 1, DATE_SUB(NOW(), INTERVAL 2 DAY));

-- Summary:
-- 2 Class Reminders
-- 2 Active Session Alerts
-- 3 Attendance Pattern Alerts
-- 3 Schedule Changes
-- 3 Camera/System Issues
-- Total: 13 sample notifications
