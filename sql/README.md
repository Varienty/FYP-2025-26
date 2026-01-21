# Database Setup Guide

This folder contains all the SQL files needed to set up the Student Attendance Management System database.

## Quick Start

To set up the database, import these two files **in order**:

1. **`schema.sql`** - Creates all database tables, indexes, and structure
2. **`additional_data.sql`** - Populates the database with sample data (students, classes, attendance records, etc.)

## Import Instructions

### Using MySQL Workbench:
1. Open MySQL Workbench and connect to your MySQL server
2. Click **File** > **Open SQL Script**
3. Select `schema.sql` and click **Execute** (⚡ lightning bolt icon)
4. Wait for completion
5. Repeat steps 2-4 for `additional_data.sql`

### Using Command Line:
```bash
mysql -u root -p student_attendance < schema.sql
mysql -u root -p student_attendance < additional_data.sql
```

### Using phpMyAdmin:
1. Select the `student_attendance` database (create it first if needed)
2. Click the **Import** tab
3. Choose `schema.sql` and click **Go**
4. Repeat for `additional_data.sql`

## What's Included

### schema.sql
- All table definitions (students, lecturers, attendance, devices, etc.)
- Foreign key relationships
- Indexes for performance
- Initial admin accounts (system admin, SSA, lecturers)
- UNIQUE constraints to prevent duplicate attendance records

### additional_data.sql
- **20 students** enrolled across 19 classes
- **19 active classes** (CS101-CS407) with realistic schedules
- **689 attendance sessions** spanning 4 months (Aug-Dec 2025)
- **7,717 complete attendance records** (all students recorded per session)
- **27 timetable entries** with Mon/Wed/Fri or Tue/Thu schedules
- **Realistic attendance patterns**: 75% present, 15% late, 7% absent, 3% excused
- **87-96% attendance rates** across all classes (typical school performance)
- Student enrollments (8-15 students per class)
- Device data for hardware monitoring
- Audit log entries
- Notification data for session tracking

## Sample Login Credentials

After importing both files, you can log in with these accounts:

**System Administrator:**
- Email: `sysadmin@system.edu`
- Password: `password123`

**Student Service Administrator:**
- Email: `ssa@admin.edu`
- Password: `password123`

**Lecturer (John Smith - LEC001):**
- Email: `john.smith@university.com`
- Password: `password123`
- Classes: CS101, CS104, CS204, CS304, CS404, CS407

**Student:**
- Email: `alice.wong@student.edu`
- Password: `password123`

## Database Requirements

- MySQL 8.0 or higher
- Database name: `student_attendance`
- Character set: `utf8mb4`
- Collation: `utf8mb4_unicode_ci`

## Troubleshooting

**Error: "Unknown database 'student_attendance'"**
- Create the database first: `CREATE DATABASE student_attendance;`

**Error: "Table already exists"**
- Drop the database and recreate: 
  ```sql
  DROP DATABASE IF EXISTS student_attendance;
  CREATE DATABASE student_attendance;
  ```

**Foreign key constraint fails**
- Make sure you import `schema.sql` BEFORE `additional_data.sql`
- The order matters!

## Notes

- All passwords are hashed using bcrypt
- Sample data includes realistic attendance patterns
- Some students have attendance below 75% for testing compliance reports
- Device data is pre-populated for hardware monitoring features
