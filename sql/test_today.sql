-- Test data for today's session (Sunday) to exercise facial recognition endpoints
-- Run this against your RDS (studentattendance) database

-- 1) Create a test module
INSERT INTO modules (module_code, module_name, description, is_active)
VALUES ('TEST101', 'Facial Recog Demo', 'Temporary demo class for today', 1);
SET @module_id := LAST_INSERT_ID();

-- 2) Create a timetable entry for today (Sunday)
INSERT INTO timetable (module_id, day_of_week, start_time, end_time, room, is_active)
VALUES (@module_id, 'Sunday', '09:00:00', '11:00:00', 'Lab-FR1', 1);
SET @tt_id := LAST_INSERT_ID();

-- 3) Create two demo students
INSERT INTO students (student_id, email, password, first_name, last_name, intake_period, intake_year, level, program)
VALUES
  ('S9001', 's9001@example.com', 'demo', 'Alice', 'Tester', 'January', YEAR(CURDATE()), 'Degree', 'CS'),
  ('S9002', 's9002@example.com', 'demo', 'Bob', 'Tester', 'January', YEAR(CURDATE()), 'Degree', 'CS');
SET @stu1 := (SELECT id FROM students WHERE student_id = 'S9001');
SET @stu2 := (SELECT id FROM students WHERE student_id = 'S9002');

-- 4) Enroll the students into the module
INSERT INTO student_enrollments (student_id, module_id, status)
VALUES
  (@stu1, @module_id, 'active'),
  (@stu2, @module_id, 'active');

-- Done. The backend will pick the first active timetable for today (Sunday) automatically.
