-- ============================================================================
-- Migration: Rename 'classes' table to 'modules'
-- Rename columns: class_code -> module_code, class_name -> module_name
-- Date: 2025-12-22
-- ============================================================================

-- Start transaction
START TRANSACTION;

-- Step 1: Rename the table from 'classes' to 'modules'
RENAME TABLE `classes` TO `modules`;

-- Step 2: Rename columns in the 'modules' table
ALTER TABLE `modules`
    CHANGE COLUMN `class_code` `module_code` VARCHAR(20) NOT NULL,
    CHANGE COLUMN `class_name` `module_name` VARCHAR(255) NOT NULL;

-- Step 3: Update foreign key column names in related tables

-- Update timetable table
ALTER TABLE `timetable`
    CHANGE COLUMN `class_id` `module_id` INT(11) NOT NULL;

-- Update student_enrollments table
ALTER TABLE `student_enrollments`
    CHANGE COLUMN `class_id` `module_id` INT(11) NOT NULL;

-- Update attendance table
ALTER TABLE `attendance`
    CHANGE COLUMN `class_id` `module_id` INT(11) NOT NULL;

-- Step 4: Drop existing foreign keys (if they exist)
SET @db_name = DATABASE();

-- Find and drop foreign keys for timetable
SELECT CONCAT('ALTER TABLE timetable DROP FOREIGN KEY ', CONSTRAINT_NAME, ';')
INTO @drop_fk_timetable
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = @db_name
  AND TABLE_NAME = 'timetable'
  AND COLUMN_NAME = 'module_id'
  AND CONSTRAINT_NAME != 'PRIMARY'
LIMIT 1;

-- Find and drop foreign keys for student_enrollments
SELECT CONCAT('ALTER TABLE student_enrollments DROP FOREIGN KEY ', CONSTRAINT_NAME, ';')
INTO @drop_fk_enrollments
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = @db_name
  AND TABLE_NAME = 'student_enrollments'
  AND COLUMN_NAME = 'module_id'
  AND CONSTRAINT_NAME != 'PRIMARY'
LIMIT 1;

-- Find and drop foreign keys for attendance
SELECT CONCAT('ALTER TABLE attendance DROP FOREIGN KEY ', CONSTRAINT_NAME, ';')
INTO @drop_fk_attendance
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = @db_name
  AND TABLE_NAME = 'attendance'
  AND COLUMN_NAME = 'module_id'
  AND CONSTRAINT_NAME != 'PRIMARY'
LIMIT 1;

-- Execute drops if they exist
PREPARE stmt1 FROM COALESCE(@drop_fk_timetable, 'SELECT 1');
EXECUTE stmt1;
DEALLOCATE PREPARE stmt1;

PREPARE stmt2 FROM COALESCE(@drop_fk_enrollments, 'SELECT 1');
EXECUTE stmt2;
DEALLOCATE PREPARE stmt2;

PREPARE stmt3 FROM COALESCE(@drop_fk_attendance, 'SELECT 1');
EXECUTE stmt3;
DEALLOCATE PREPARE stmt3;

-- Step 5: Recreate foreign keys with new column names
ALTER TABLE `timetable`
    ADD CONSTRAINT `fk_timetable_module`
    FOREIGN KEY (`module_id`) REFERENCES `modules` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `student_enrollments`
    ADD CONSTRAINT `fk_enrollments_module`
    FOREIGN KEY (`module_id`) REFERENCES `modules` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `attendance`
    ADD CONSTRAINT `fk_attendance_module`
    FOREIGN KEY (`module_id`) REFERENCES `modules` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE;

-- Commit transaction
COMMIT;

-- ============================================================================
-- Migration completed successfully
-- ============================================================================
