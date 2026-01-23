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
-- These are optional since CHANGE COLUMN handles it gracefully
ALTER TABLE `timetable` DROP FOREIGN KEY IF EXISTS `fk_timetable_class`;
ALTER TABLE `student_enrollments` DROP FOREIGN KEY IF EXISTS `fk_enrollments_class`;
ALTER TABLE `attendance` DROP FOREIGN KEY IF EXISTS `fk_attendance_class`;

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
