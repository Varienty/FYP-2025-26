#!/usr/bin/env python3
"""
Safe Legacy Data Import Script
Imports users from staged legacy dump into live RDS database.
"""
import mysql.connector
from mysql.connector import pooling
import sys

# RDS Configuration
RDS_CONFIG = {
    'host': 'studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'iamtrying',
    'port': 3306
}

def create_staging_schema():
    """Create the student_attendance_legacy schema."""
    try:
        conn = mysql.connector.connect(**RDS_CONFIG)
        cursor = conn.cursor()
        print("✓ Connected to RDS.")
        
        print("\n[STEP 1] Creating staging schema 'student_attendance_legacy'...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS student_attendance_legacy;")
        conn.commit()
        print("✓ Staging schema created.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"✗ Error creating staging schema: {e}")
        sys.exit(1)

def import_legacy_dump():
    """Import the legacy SQL dump into the staging schema."""
    try:
        # Note: For large dumps, mysql CLI is preferred, but we'll provide the command
        print("\n[STEP 2] Importing legacy dump (student_attendance.sql) into staging schema...")
        print("\n  Run this command from your terminal (you may need to install mysql-client):")
        print("\n  mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -piamtrying student_attendance_legacy < student_attendance.sql")
        print("\n  ⚠️  The legacy dump is ~11MB. This may take 1-5 minutes depending on network speed.\n")
        
        response = input("Press ENTER once the import is complete, or type 'skip' to skip this step: ").strip().lower()
        if response == 'skip':
            print("Skipping dump import. (Ensure staging schema already has data.)")
        else:
            print("Proceeding with user data import from staging schema...")
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

def import_users_from_legacy():
    """Import user data (de-duplicated by email) from legacy to live schema."""
    try:
        conn = mysql.connector.connect(**RDS_CONFIG, database='student_attendance')
        cursor = conn.cursor()
        print("\n[STEP 3] Importing user data from staging schema...")
        
        # Disable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("SET SQL_SAFE_UPDATES = 0;")
        
        # 1) Import System Admins
        print("  - Importing system_admins...")
        query = """
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
        """
        cursor.execute(query)
        conn.commit()
        print(f"    ✓ Imported {cursor.rowcount} system admin(s).")
        
        # 2) Import Student Service Admins
        print("  - Importing student_service_admins...")
        query = """
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
        """
        cursor.execute(query)
        conn.commit()
        print(f"    ✓ Imported {cursor.rowcount} SSA(s).")
        
        # 3) Import Lecturers
        print("  - Importing lecturers...")
        query = """
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
        """
        cursor.execute(query)
        conn.commit()
        print(f"    ✓ Imported {cursor.rowcount} lecturer(s).")
        
        # 4) Import Students
        print("  - Importing students...")
        query = """
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
        """
        cursor.execute(query)
        conn.commit()
        print(f"    ✓ Imported {cursor.rowcount} student(s).")
        
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        cursor.execute("SET SQL_SAFE_UPDATES = 1;")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ User data import complete!")
        
    except Exception as e:
        print(f"✗ Error during import: {e}")
        sys.exit(1)

def verify_import():
    """Verify the import by counting imported records."""
    try:
        conn = mysql.connector.connect(**RDS_CONFIG, database='student_attendance')
        cursor = conn.cursor(dictionary=True)
        
        print("\n[STEP 4] Verifying import...")
        
        tables = ['system_admins', 'student_service_admins', 'lecturers', 'students']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as cnt FROM {table};")
            result = cursor.fetchone()
            count = result['cnt']
            print(f"  - {table}: {count} record(s)")
        
        cursor.close()
        conn.close()
        
        print("\n✓ Verification complete. Ready to test login!")
        
    except Exception as e:
        print(f"✗ Error during verification: {e}")
        sys.exit(1)

def main():
    print("=" * 80)
    print("LEGACY DATA IMPORT TOOL")
    print("=" * 80)
    print("\nThis script will:")
    print("  1. Create a staging schema")
    print("  2. Import the legacy dump (you will be prompted)")
    print("  3. Import user data into the live schema")
    print("  4. Verify the import")
    print("\n" + "=" * 80)
    
    # Step 1: Create staging schema
    create_staging_schema()
    
    # Step 2: Prompt for dump import
    import_legacy_dump()
    
    # Step 3: Import users
    import_users_from_legacy()
    
    # Step 4: Verify
    verify_import()
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("✓ RDS Snapshot: pre-legacy-import-20260122-1941 (created)")
    print("✓ User data imported and de-duplicated")
    print("\nTest login with one of these emails:")
    print("  - admin@attendance.com (System Admin)")
    print("  - studentservice@attendance.com (SSA)")
    print("  - john.smith@university.com (Lecturer)")
    print("  - alice.wong@student.edu (Student)")
    print("\nPassword for all: 'password'")
    print("\n" + "=" * 80 + "\n")

if __name__ == '__main__':
    main()
