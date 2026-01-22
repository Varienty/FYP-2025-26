import mysql.connector
import sys
from datetime import datetime

# Local database connection (using typical local dev credentials)
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Adjust if your local root has a password
    'database': 'studentattendance'
}

try:
    print("Connecting to local MySQL database...")
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    # Get all attendance records
    cursor.execute("SELECT * FROM attendance ORDER BY attendance_id")
    records = cursor.fetchall()
    
    # Get column names
    cursor.execute("DESCRIBE attendance")
    columns = [col[0] for col in cursor.fetchall()]
    
    print(f"Found {len(records)} attendance records")
    print(f"Columns: {columns}")
    
    # Generate SQL INSERT statements
    sql_output = []
    sql_output.append("-- Attendance records export")
    sql_output.append(f"-- Generated on {datetime.now()}")
    sql_output.append("")
    
    for record in records:
        values = []
        for i, val in enumerate(record):
            if val is None:
                values.append("NULL")
            elif isinstance(val, str):
                # Escape single quotes
                escaped = val.replace("'", "''")
                values.append(f"'{escaped}'")
            elif isinstance(val, (int, float)):
                values.append(str(val))
            else:
                values.append(f"'{val}'")
        
        col_names = ", ".join(columns)
        vals_str = ", ".join(values)
        sql_output.append(f"INSERT INTO attendance ({col_names}) VALUES ({vals_str});")
    
    # Write to file
    output_file = 'student_attendance.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(sql_output))
    
    print(f"\n✅ Successfully exported {len(records)} records to {output_file}")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as err:
    print(f"❌ Database error: {err}")
    print("\nIf connection fails, check your local MySQL credentials in the script.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
