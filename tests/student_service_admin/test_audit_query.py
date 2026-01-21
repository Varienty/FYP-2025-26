import sys
sys.path.insert(0, 'common')
import db_utils
import json

# Test the exact query from reports_controller.py
query = """SELECT al.id, al.created_at as timestamp, 
           al.user_type as editor, al.action as changeType,
           s.student_id, CONCAT(s.first_name, ' ', s.last_name) as studentName,
           al.old_values as previousValue, al.new_values as newValue,
           al.record_id
           FROM audit_logs al
           LEFT JOIN attendance a ON al.record_id = a.id AND al.table_name = 'attendance'
           LEFT JOIN students s ON a.student_id = s.id
           WHERE al.action LIKE '%attendance%'
           ORDER BY al.created_at DESC LIMIT 5"""

print("=== TESTING AUDIT LOG QUERY ===\n")
records = db_utils.query_all(query, ())

for r in records:
    print(f"Audit ID: {r['id']}")
    print(f"Record ID: {r['record_id']}")
    print(f"Student ID: {r['student_id']}")
    print(f"Student Name: {r['studentName']}")
    print(f"Editor: {r['editor']}")
    
    # Parse JSON
    try:
        old_val = json.loads(r['previousValue']) if r['previousValue'] else {}
        new_val = json.loads(r['newValue']) if r['newValue'] else {}
        print(f"Old Status: {old_val.get('status', 'N/A')}")
        print(f"New Status: {new_val.get('status', 'N/A')}")
    except:
        print("Could not parse JSON")
    
    print("-" * 70)

# Also check what's in the attendance table for record_id 1478
print("\n\n=== CHECKING ATTENDANCE RECORD 1478 ===\n")
att = db_utils.query_one("""
    SELECT a.id, a.student_id, s.id as student_internal_id,
           s.student_id as student_code, 
           CONCAT(s.first_name, ' ', s.last_name) as name
    FROM attendance a
    JOIN students s ON a.student_id = s.id
    WHERE a.id = 1478
""", ())

if att:
    print(f"Attendance ID: {att['id']}")
    print(f"Student Internal ID (a.student_id): {att['student_id']}")
    print(f"Student Internal ID (s.id): {att['student_internal_id']}")
    print(f"Student Code (s.student_id): {att['student_code']}")
    print(f"Student Name: {att['name']}")
