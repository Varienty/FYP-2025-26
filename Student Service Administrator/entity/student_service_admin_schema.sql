-- ============================================================================
-- Student Service Administrator - Database Schema (MySQL)
-- User Stories: US27 - US36
-- ============================================================================

-- StudentServiceAdmin Table (US27, US28, US30)
-- Stores admin user accounts with authentication and password reset support
CREATE TABLE IF NOT EXISTS student_service_admins (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    department VARCHAR(100),
    role VARCHAR(50) NOT NULL DEFAULT 'student-service-admin',
    is_active BOOLEAN DEFAULT TRUE,
    password_reset_token VARCHAR(255),
    password_reset_expiry DATETIME,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- AttendanceRecord Table (US31, US33, US34, US36)
-- Core table for tracking student attendance across classes
CREATE TABLE IF NOT EXISTS attendance_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(50) NOT NULL,
    class_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    session VARCHAR(20),  -- 'morning', 'afternoon', 'evening'
    status ENUM('present', 'absent', 'late') NOT NULL,
    remarks TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_attendance (student_id, class_id, date, session),
    INDEX idx_student_id (student_id),
    INDEX idx_class_id (class_id),
    INDEX idx_date (date),
    INDEX idx_status (status)
);

-- AuditLog Table (US29)
-- Immutable log of all manual attendance edits for accountability and compliance
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    record_id INT NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    change_type ENUM('status_change', 'remarks_added', 'record_deleted', 'adjustment') NOT NULL,
    previous_value VARCHAR(255),
    new_value VARCHAR(255),
    reason TEXT NOT NULL,
    justification TEXT,
    editor VARCHAR(100) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (record_id) REFERENCES attendance_records(id) ON DELETE SET NULL,
    INDEX idx_student_id (student_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_change_type (change_type),
    INDEX idx_editor (editor)
);

-- PasswordResetRequest Table (US30)
-- Temporary records for secure password reset flow
CREATE TABLE IF NOT EXISTS password_reset_requests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    admin_id INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    used_at DATETIME,
    FOREIGN KEY (admin_id) REFERENCES student_service_admins(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_expires_at (expires_at)
);

-- ClassList Table (US35)
-- Stores uploaded class information for face recognition integration
CREATE TABLE IF NOT EXISTS class_lists (
    id INT PRIMARY KEY AUTO_INCREMENT,
    class_id VARCHAR(50) NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    roll_number VARCHAR(50),
    photo_path VARCHAR(255),
    academic_year VARCHAR(20),
    semester INT,
    uploaded_by VARCHAR(100),
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_class_student (class_id, student_id, academic_year),
    INDEX idx_class_id (class_id),
    INDEX idx_student_id (student_id),
    INDEX idx_academic_year (academic_year)
);

-- ComplianceReport Table (US32)
-- Cached compliance data for students below attendance threshold
CREATE TABLE IF NOT EXISTS compliance_reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(50) NOT NULL,
    attendance_percentage DECIMAL(5, 2),
    classes_attended INT,
    classes_missed INT,
    late_arrivals INT,
    severity ENUM('critical', 'warning', 'good') NOT NULL,
    threshold DECIMAL(5, 2),
    academic_year VARCHAR(20),
    semester INT,
    generated_by VARCHAR(100),
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_student_id (student_id),
    INDEX idx_severity (severity),
    INDEX idx_academic_year (academic_year)
);

-- AttendanceSummary Table (US34)
-- Cached daily summary data for dashboard performance
CREATE TABLE IF NOT EXISTS attendance_summaries (
    id INT PRIMARY KEY AUTO_INCREMENT,
    summary_date DATE NOT NULL UNIQUE,
    total_students INT,
    present_count INT,
    absent_count INT,
    late_count INT,
    attendance_rate DECIMAL(5, 2),
    peak_absence_day VARCHAR(20),
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_summary_date (summary_date)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Performance indexes on frequently queried combinations
CREATE INDEX IF NOT EXISTS idx_attendance_student_date ON attendance_records(student_id, date);
CREATE INDEX IF NOT EXISTS idx_attendance_class_date ON attendance_records(class_id, date);
CREATE INDEX IF NOT EXISTS idx_audit_record_timestamp ON audit_logs(record_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_compliance_year_semester ON compliance_reports(academic_year, semester);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: StudentAttendanceStats
-- Aggregates attendance statistics for a student across all courses
CREATE OR REPLACE VIEW student_attendance_stats AS
SELECT 
    ar.student_id,
    COUNT(*) as total_classes,
    SUM(CASE WHEN ar.status = 'present' THEN 1 ELSE 0 END) as classes_attended,
    SUM(CASE WHEN ar.status = 'absent' THEN 1 ELSE 0 END) as classes_absent,
    SUM(CASE WHEN ar.status = 'late' THEN 1 ELSE 0 END) as late_arrivals,
    ROUND(
        (SUM(CASE WHEN ar.status = 'present' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 
        2
    ) as attendance_percentage
FROM attendance_records ar
GROUP BY ar.student_id;

-- View: ComplianceList
-- Lists all students below a given threshold (default 75%)
CREATE OR REPLACE VIEW compliance_list AS
SELECT 
    ar.student_id,
    COUNT(*) as classes_attended,
    SUM(CASE WHEN ar.status = 'absent' THEN 1 ELSE 0 END) as classes_missed,
    ROUND(
        (SUM(CASE WHEN ar.status = 'present' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 
        2
    ) as attendance_percentage,
    CASE 
        WHEN (SUM(CASE WHEN ar.status = 'present' THEN 1 ELSE 0 END) / COUNT(*)) < 0.60 THEN 'critical'
        WHEN (SUM(CASE WHEN ar.status = 'present' THEN 1 ELSE 0 END) / COUNT(*)) < 0.75 THEN 'warning'
        ELSE 'good'
    END as severity
FROM attendance_records ar
GROUP BY ar.student_id
HAVING attendance_percentage < 75;

-- View: AuditTrail
-- Complete audit trail with human-readable information
CREATE OR REPLACE VIEW audit_trail AS
SELECT 
    al.id,
    al.timestamp,
    al.editor,
    al.student_id,
    al.change_type,
    al.previous_value,
    al.new_value,
    al.reason,
    al.justification,
    ar.class_id,
    ar.date
FROM audit_logs al
LEFT JOIN attendance_records ar ON al.record_id = ar.id
ORDER BY al.timestamp DESC;

-- ============================================================================
-- INITIAL DATA (Demo Users)
-- ============================================================================

-- Insert demo admin user
-- Password: 'password' (hashed with bcrypt)
-- In production, use bcrypt hash with proper salt
INSERT IGNORE INTO student_service_admins (username, email, password_hash, first_name, last_name, role)
VALUES (
    'admin',
    'admin@university.edu',
    '$2y$10$example_bcrypt_hash_here',  -- Replace with actual bcrypt hash
    'Admin',
    'User',
    'student-service-admin'
);

-- ============================================================================
-- STORED PROCEDURES FOR COMMON OPERATIONS
-- ============================================================================

-- Procedure: GetDailySummary
-- Returns attendance summary for a specific date
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS GetDailySummary(
    IN p_date DATE
)
BEGIN
    SELECT 
        p_date as summary_date,
        COUNT(DISTINCT ar.student_id) as total_students,
        SUM(CASE WHEN ar.status = 'present' THEN 1 ELSE 0 END) as present_count,
        SUM(CASE WHEN ar.status = 'absent' THEN 1 ELSE 0 END) as absent_count,
        SUM(CASE WHEN ar.status = 'late' THEN 1 ELSE 0 END) as late_count,
        ROUND(
            (SUM(CASE WHEN ar.status = 'present' THEN 1 ELSE 0 END) / COUNT(DISTINCT ar.student_id)) * 100,
            2
        ) as attendance_rate
    FROM attendance_records ar
    WHERE ar.date = p_date;
END //
DELIMITER ;

-- Procedure: LogAttendanceEdit
-- Logs attendance edits to audit trail
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS LogAttendanceEdit(
    IN p_record_id INT,
    IN p_student_id VARCHAR(50),
    IN p_change_type VARCHAR(50),
    IN p_previous_value VARCHAR(255),
    IN p_new_value VARCHAR(255),
    IN p_reason TEXT,
    IN p_editor VARCHAR(100)
)
BEGIN
    INSERT INTO audit_logs (record_id, student_id, change_type, previous_value, new_value, reason, editor)
    VALUES (p_record_id, p_student_id, p_change_type, p_previous_value, p_new_value, p_reason, p_editor);
END //
DELIMITER ;

-- ============================================================================
-- CONSTRAINTS AND TRIGGERS
-- ============================================================================

-- Trigger: Prevent AuditLog deletion (immutability)
DELIMITER //
CREATE TRIGGER IF NOT EXISTS audit_log_prevent_delete
BEFORE DELETE ON audit_logs
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Audit log records cannot be deleted. They are immutable for compliance.';
END //
DELIMITER ;

-- Trigger: Prevent AuditLog update (immutability)
DELIMITER //
CREATE TRIGGER IF NOT EXISTS audit_log_prevent_update
BEFORE UPDATE ON audit_logs
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Audit log records cannot be updated. They are immutable for compliance.';
END //
DELIMITER ;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
