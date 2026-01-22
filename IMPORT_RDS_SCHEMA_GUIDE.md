# Import SQL Schema and Data to AWS RDS - Complete Guide

## 📋 Overview

Your code works locally because your local MySQL has the correct schema with the `modules` table and all data. AWS RDS is **empty** - no tables imported yet. We need to import:

1. **Schema** ([sql/schema.sql](sql/schema.sql)) - All table structures
2. **Sample Data** ([sql/additional_data.sql](sql/additional_data.sql)) - Initial test data
3. **Attendance Data** ([student_attendance.sql](student_attendance.sql)) - Your 750+ attendance records

---

## 🔧 Method 1: Using MySQL Workbench (Easiest - GUI)

### Step 1: Download MySQL Workbench
- Download: https://dev.mysql.com/downloads/workbench/
- Install and launch MySQL Workbench

### Step 2: Create RDS Connection
1. Click **"+"** next to "MySQL Connections"
2. Enter connection details:
   - **Connection Name:** `FYP AWS RDS`
   - **Hostname:** `studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com`
   - **Port:** `3306`
   - **Username:** `admin`
   - **Password:** Click "Store in Vault" → Enter your RDS password
3. Click **Test Connection** → Should show success
4. Click **OK**

### Step 3: Import Schema
1. Double-click your new connection
2. Go to **Server → Data Import**
3. Select **"Import from Self-Contained File"**
4. Browse to: `C:\Users\amosy\OneDrive\Documents\GitHub\FYP-2025-26\sql\schema.sql`
5. Under "Default Target Schema" → Select or create `studentattendance`
6. Click **Start Import**
7. Wait for completion

### Step 4: Import Additional Data
1. Repeat Step 3 but with: `sql\additional_data.sql`
2. Click **Start Import**

### Step 5: Import Attendance Records
1. Repeat Step 3 but with: `student_attendance.sql` (in root folder)
2. Click **Start Import**

### Step 6: Verify
```sql
USE studentattendance;
SHOW TABLES;
SELECT COUNT(*) FROM modules;
SELECT COUNT(*) FROM students;
SELECT COUNT(*) FROM attendance;
```

---

## 🔧 Method 2: Using PowerShell/Terminal (Command Line)

### Step 1: Ensure MySQL Client Installed
```powershell
# Check if mysql command exists
mysql --version

# If not found, download from: https://dev.mysql.com/downloads/mysql/
```

### Step 2: Import Schema
```powershell
cd C:\Users\amosy\OneDrive\Documents\GitHub\FYP-2025-26

mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -p studentattendance < sql/schema.sql
```
**Enter your RDS password when prompted**

### Step 3: Import Additional Data
```powershell
mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -p studentattendance < sql/additional_data.sql
```

### Step 4: Import Attendance Records
```powershell
mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -p studentattendance < student_attendance.sql
```

### Step 5: Verify Import
```powershell
mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -p studentattendance -e "SHOW TABLES; SELECT COUNT(*) as total_modules FROM modules; SELECT COUNT(*) as total_students FROM students;"
```

---

## 🔧 Method 3: Using Python Script (Automated)

Create this script in your project root as `import_to_rds.py`:

```python
import mysql.connector
import os
from pathlib import Path

# RDS Connection details
RDS_CONFIG = {
    'host': 'studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com',
    'user': 'admin',
    'password': input('Enter RDS Password: '),  # Or hardcode temporarily
    'database': 'studentattendance',
    'port': 3306
}

def execute_sql_file(cursor, filepath):
    """Execute SQL file"""
    print(f"Executing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Split by semicolon and execute each statement
    statements = sql_content.split(';')
    
    for statement in statements:
        statement = statement.strip()
        if statement and not statement.startswith('--'):
            try:
                cursor.execute(statement)
                print(f"✓ Executed: {statement[:50]}...")
            except Exception as e:
                print(f"✗ Error: {e}")
                print(f"Statement: {statement[:100]}")

def main():
    print("=== Importing SQL to AWS RDS ===\n")
    
    # Connect to RDS
    print("Connecting to RDS...")
    conn = mysql.connector.connect(**RDS_CONFIG)
    cursor = conn.cursor()
    print("✓ Connected!\n")
    
    # Files to import
    files = [
        'sql/schema.sql',
        'sql/additional_data.sql',
        'student_attendance.sql'
    ]
    
    for filepath in files:
        if Path(filepath).exists():
            execute_sql_file(cursor, filepath)
            conn.commit()
            print(f"✓ Committed {filepath}\n")
        else:
            print(f"✗ File not found: {filepath}\n")
    
    # Verify
    print("=== Verification ===")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"Total tables: {len(tables)}")
    
    cursor.execute("SELECT COUNT(*) FROM modules")
    print(f"Modules: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM students")
    print(f"Students: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM attendance")
    print(f"Attendance records: {cursor.fetchone()[0]}")
    
    cursor.close()
    conn.close()
    print("\n✓ Import complete!")

if __name__ == '__main__':
    main()
```

**Run it:**
```powershell
python import_to_rds.py
```

---

## 🔍 Verification Checklist

After importing, run these queries to verify:

```sql
-- Check all tables exist
SHOW TABLES;

-- Expected tables:
-- system_admins, student_service_admins, lecturers, students
-- classes, modules, timetable, student_enrollments
-- attendance, attendance_sessions, attendance_policies
-- medical_certificates, notifications, etc.

-- Check record counts
SELECT COUNT(*) FROM modules;              -- Should have ~15 records
SELECT COUNT(*) FROM students;             -- Should have ~750 records
SELECT COUNT(*) FROM lecturers;            -- Should have ~9 records
SELECT COUNT(*) FROM attendance;           -- Should have ~717 records
SELECT COUNT(*) FROM system_admins;        -- Should have ~1 record
SELECT COUNT(*) FROM student_service_admins; -- Should have ~1 record

-- Check sample data
SELECT * FROM modules LIMIT 5;
SELECT * FROM students LIMIT 5;
SELECT * FROM attendance LIMIT 5;
```

---

## 🚨 Troubleshooting

### Error: "Access denied"
- Check RDS Security Group allows your IP address
- Go to AWS Console → RDS → Security Groups
- Add Inbound Rule: Type=MySQL/Aurora, Port=3306, Source=My IP

### Error: "Can't connect to MySQL server"
- Check RDS endpoint is correct
- Check RDS is publicly accessible (Modify → Public access → Yes)
- Check VPC settings allow external connections

### Error: "Database doesn't exist"
Create database first:
```sql
CREATE DATABASE IF NOT EXISTS studentattendance;
USE studentattendance;
```

### Large SQL files timing out
Split imports:
```powershell
# Import in smaller chunks
mysql ... < sql/schema.sql
mysql ... < sql/additional_data.sql
mysql ... < student_attendance.sql
```

---

## ✅ After Import Success

Once imported, test your debug page again:

**Visit:** http://fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com/debug

**Section 6 should now show:**
- ✓ Users - X records returned
- ✓ Modules - ~15 records returned
- ✓ Lecturers - ~9 records returned  
- ✓ Students - ~750 records returned
- ✓ Timetable - X records returned
- ✓ Classes - X records returned
- ✓ Daily Summary - X records returned

All application pages will now load data correctly!

---

## 📝 Quick Command Reference

**Connect to RDS:**
```bash
mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -p
```

**Import single file:**
```bash
mysql -h [HOST] -u admin -p studentattendance < filename.sql
```

**Export from local (for backup):**
```bash
mysqldump -u root -p studentattendance > backup.sql
```

---

**Choose Method 1 (MySQL Workbench) if you prefer GUI, or Method 2 (Command Line) for quick import!**
