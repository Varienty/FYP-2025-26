#!/usr/bin/env python3
"""
Diagnose login issues by checking all auth tables
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from common import db_utils
import bcrypt

def check_all_tables():
    print("=" * 70)
    print("CHECKING ALL AUTHENTICATION TABLES")
    print("=" * 70)
    
    tables = [
        ('system_admins', 'System Admin'),
        ('student_service_admins', 'Student Service Admin'),
        ('lecturers', 'Lecturer'),
    ]
    
    # Check for demo accounts
    demo_accounts = [
        'haha@gmail.com',
        'admin@attendance.com',
        'studentservice@attendance.com',
        'john.smith@university.com',
    ]
    
    for table_name, role_label in tables:
        print(f"\n--- {role_label} Table: {table_name} ---")
        
        for email in demo_accounts:
            row = db_utils.query_one(
                f"SELECT id, email, password, first_name, last_name FROM {table_name} WHERE email=%s",
                (email,)
            )
            
            if row:
                stored_hash = row['password']
                # Normalize $2y$ to $2b$ for Python bcrypt
                if stored_hash.startswith('$2y$'):
                    test_hash = '$2b$' + stored_hash[4:]
                else:
                    test_hash = stored_hash
                
                try:
                    matches = bcrypt.checkpw(b'password', test_hash.encode('utf-8'))
                except Exception as e:
                    matches = False
                    print(f"  ERROR checking hash: {e}")
                
                print(f"  ✓ {email} found")
                print(f"    First: {row['first_name']}, Last: {row['last_name']}")
                print(f"    Hash matches 'password'? {matches}")
            else:
                print(f"  ✗ {email} NOT FOUND")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\nIf you see ✗ for your account in all three tables:")
    print("  → You need to INSERT it into the correct table")
    print("\nIf you see ✓ but 'Hash matches' is False:")
    print("  → The stored hash doesn't match 'password' plaintext")
    print("  → Either the password is different, or the hash is corrupted")
    print("\nFrontend login paths:")
    print("  - Lecturer role → queries 'lecturers' table")
    print("  - System Admin role → queries 'system_admins' table")
    print("  - SSA role → queries 'student_service_admins' table")

if __name__ == "__main__":
    try:
        check_all_tables()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
