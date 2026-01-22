#!/usr/bin/env python3
"""Verify test users in database"""
import os
import sys
import bcrypt
from common.db_utils import get_connection

def verify_users():
    """Check what's in the database"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        print("\n=== CHECKING ALL USER TABLES ===\n")
        
        # Check system_admins
        print("SYSTEM ADMINS:")
        cursor.execute("SELECT admin_id, email, first_name, last_name, password FROM system_admins")
        for user in cursor.fetchall():
            print(f"  Email: {user['email']}")
            print(f"  Name: {user['first_name']} {user['last_name']}")
            print(f"  Password Hash: {user['password'][:30]}..." if user['password'] else "  Password: NULL")
            
            # Try to verify with "password"
            try:
                if user['password'] and user['password'].startswith('$2'):
                    result = bcrypt.checkpw(b'password', user['password'].encode('utf-8'))
                    print(f"  Bcrypt verification (password='password'): {result}")
                else:
                    print(f"  Not a bcrypt hash (plain text): {user['password'] == 'password'}")
            except Exception as e:
                print(f"  Error verifying: {e}")
            print()
        
        # Check student_service_admins
        print("STUDENT SERVICE ADMINS:")
        cursor.execute("SELECT admin_id, email, first_name, last_name, password FROM student_service_admins")
        for user in cursor.fetchall():
            print(f"  Email: {user['email']}")
            print(f"  Name: {user['first_name']} {user['last_name']}")
            print(f"  Password Hash: {user['password'][:30]}..." if user['password'] else "  Password: NULL")
            
            try:
                if user['password'] and user['password'].startswith('$2'):
                    result = bcrypt.checkpw(b'password', user['password'].encode('utf-8'))
                    print(f"  Bcrypt verification (password='password'): {result}")
                else:
                    print(f"  Not a bcrypt hash (plain text): {user['password'] == 'password'}")
            except Exception as e:
                print(f"  Error verifying: {e}")
            print()
        
        # Check lecturers
        print("LECTURERS:")
        cursor.execute("SELECT lecturer_id, email, first_name, last_name, password FROM lecturers")
        for user in cursor.fetchall():
            print(f"  Email: {user['email']}")
            print(f"  Name: {user['first_name']} {user['last_name']}")
            print(f"  Password Hash: {user['password'][:30]}..." if user['password'] else "  Password: NULL")
            
            try:
                if user['password'] and user['password'].startswith('$2'):
                    result = bcrypt.checkpw(b'password', user['password'].encode('utf-8'))
                    print(f"  Bcrypt verification (password='password'): {result}")
                else:
                    print(f"  Not a bcrypt hash (plain text): {user['password'] == 'password'}")
            except Exception as e:
                print(f"  Error verifying: {e}")
            print()
        
        # Check students
        print("STUDENTS:")
        cursor.execute("SELECT student_id, email, first_name, last_name, password FROM students")
        for user in cursor.fetchall():
            print(f"  Email: {user['email']}")
            print(f"  Name: {user['first_name']} {user['last_name']}")
            print(f"  Password Hash: {user['password'][:30]}..." if user['password'] else "  Password: NULL")
            
            try:
                if user['password'] and user['password'].startswith('$2'):
                    result = bcrypt.checkpw(b'password', user['password'].encode('utf-8'))
                    print(f"  Bcrypt verification (password='password'): {result}")
                else:
                    print(f"  Not a bcrypt hash (plain text): {user['password'] == 'password'}")
            except Exception as e:
                print(f"  Error verifying: {e}")
            print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    verify_users()
