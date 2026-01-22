#!/usr/bin/env python3
"""
Database migration script - auto-creates tables on EB startup if they don't exist
"""
import os
import sys
from common.db_utils import get_connection

def check_tables_exist():
    """Check if main tables exist"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        # Check for key tables
        required_tables = ['students', 'lecturers', 'classes', 'attendance_sessions']
        existing = [t for t in required_tables if t in tables]
        
        print(f"Found {len(existing)}/{len(required_tables)} required tables")
        return len(existing) == len(required_tables)
    except Exception as e:
        print(f"Error checking tables: {e}")
        return False

def run_migration():
    """Run migration from schema_clean.sql"""
    schema_file = os.path.join(os.path.dirname(__file__), 'sql', 'schema_clean.sql')
    
    if not os.path.exists(schema_file):
        print(f"ERROR: Schema file not found: {schema_file}")
        return False
    
    print(f"Reading schema from: {schema_file}")
    
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split by semicolons and filter out empty statements
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        conn = get_connection()
        cursor = conn.cursor()
        
        print(f"Executing {len(statements)} SQL statements...")
        
        for i, statement in enumerate(statements, 1):
            # Skip comments and USE statements (we're already connected to the right DB)
            if statement.startswith('--') or statement.startswith('/*') or statement.upper().startswith('USE '):
                continue
            
            # Skip DROP/CREATE DATABASE (we're using RDS with existing DB)
            if 'DROP DATABASE' in statement.upper() or 'CREATE DATABASE' in statement.upper():
                continue
            
            try:
                cursor.execute(statement)
                if i % 10 == 0:
                    print(f"  Executed {i}/{len(statements)} statements...")
            except Exception as e:
                # Ignore "table already exists" errors
                if 'already exists' in str(e).lower():
                    continue
                print(f"Warning on statement {i}: {e}")
                # Continue with other statements
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"ERROR during migration: {e}")
        return False

def main():
    print("=" * 60)
    print("DATABASE MIGRATION")
    print("=" * 60)
    
    if not os.getenv('DATABASE_URL') and not os.getenv('RDS_HOSTNAME'):
        print("WARNING: No DATABASE_URL or RDS_HOSTNAME set. Skipping migration.")
        sys.exit(0)
    
    print("Checking if tables exist...")
    
    if check_tables_exist():
        print("✓ Tables already exist. Skipping migration.")
        sys.exit(0)
    
    print("Tables not found. Running migration...")
    
    if run_migration():
        print("✓ Migration successful!")
        sys.exit(0)
    else:
        print("✗ Migration failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
