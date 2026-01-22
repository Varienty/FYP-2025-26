#!/usr/bin/env python3
"""
Import SQL Schema and Data to AWS RDS
Quick automated script to import all SQL files to RDS database
"""

import mysql.connector
import os
from pathlib import Path
from getpass import getpass

# RDS Connection details
RDS_CONFIG = {
    'host': 'studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com',
    'user': 'admin',
    'database': 'studentattendance',
    'port': 3306
}

def execute_sql_file(cursor, conn, filepath):
    """Execute SQL file with better error handling"""
    print(f"\n{'='*60}")
    print(f"Executing: {filepath}")
    print('='*60)
    
    if not Path(filepath).exists():
        print(f"✗ ERROR: File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Split by semicolon and execute each statement
    statements = [s.strip() for s in sql_content.split(';') if s.strip()]
    
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements, 1):
        # Skip comments
        if statement.startswith('--') or statement.startswith('/*'):
            continue
            
        try:
            cursor.execute(statement)
            success_count += 1
            # Show progress every 10 statements
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(statements)} statements...")
        except mysql.connector.Error as e:
            error_count += 1
            # Show error but continue
            print(f"  ⚠ Warning on statement {i}: {e}")
            # Show problematic statement (first 100 chars)
            print(f"    Statement: {statement[:100]}...")
    
    # Commit after each file
    conn.commit()
    print(f"\n✓ Completed: {success_count} successful, {error_count} warnings")
    return True

def verify_import(cursor):
    """Verify data was imported correctly"""
    print(f"\n{'='*60}")
    print("VERIFICATION RESULTS")
    print('='*60)
    
    # Check tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"\n✓ Total tables created: {len(tables)}")
    print(f"  Tables: {', '.join([t[0] for t in tables[:10]])}...")
    
    # Check record counts
    checks = [
        ('modules', 'Modules/Classes'),
        ('students', 'Students'),
        ('lecturers', 'Lecturers'),
        ('attendance', 'Attendance Records'),
        ('system_admins', 'System Admins'),
        ('student_service_admins', 'Student Service Admins'),
        ('timetable', 'Timetable Entries'),
        ('attendance_policies', 'Attendance Policies')
    ]
    
    print("\nRecord Counts:")
    for table, description in checks:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✓ {description:25} {count:6} records")
        except mysql.connector.Error:
            print(f"  ✗ {description:25} (table not found)")

def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║      Import SQL Schema & Data to AWS RDS Database        ║
║              FYP Attendance System                        ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    # Get password
    password = getpass("Enter RDS Password (admin): ")
    RDS_CONFIG['password'] = password
    
    try:
        # Connect to RDS
        print("\n[1/4] Connecting to AWS RDS...")
        conn = mysql.connector.connect(**RDS_CONFIG)
        cursor = conn.cursor()
        print("✓ Connected successfully!")
        
        # Files to import in order
        files = [
            ('sql/schema.sql', 'Database Schema (Tables)'),
            ('sql/additional_data.sql', 'Additional Sample Data'),
            ('student_attendance.sql', 'Attendance Records (750+)')
        ]
        
        # Import each file
        for i, (filepath, description) in enumerate(files, 2):
            print(f"\n[{i}/4] Importing {description}...")
            if Path(filepath).exists():
                execute_sql_file(cursor, conn, filepath)
            else:
                print(f"⚠ Skipping {filepath} (not found)")
        
        # Verify import
        print(f"\n[4/4] Verifying import...")
        verify_import(cursor)
        
        # Close connection
        cursor.close()
        conn.close()
        
        print(f"\n{'='*60}")
        print("✓ IMPORT COMPLETE!")
        print('='*60)
        print("\nNext steps:")
        print("1. Test debug page: /debug")
        print("2. Login with: admin@attendance.com / password")
        print("3. Check all pages load data correctly")
        print()
        
    except mysql.connector.Error as e:
        print(f"\n✗ ERROR: {e}")
        print("\nTroubleshooting:")
        print("- Check RDS password is correct")
        print("- Check RDS Security Group allows your IP")
        print("- Check RDS is publicly accessible")
        return 1
    except FileNotFoundError as e:
        print(f"\n✗ ERROR: {e}")
        print("- Make sure you run this from project root directory")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
