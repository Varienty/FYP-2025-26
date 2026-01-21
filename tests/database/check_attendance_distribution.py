import sys
sys.path.insert(0, 'common')
import db_utils

# Check attendance distribution
print("=== STUDENT ATTENDANCE DISTRIBUTION ===\n")

data = db_utils.query_all("""
    SELECT s.student_id, CONCAT(s.first_name, ' ', s.last_name) as name, 
           s.program,
           COUNT(CASE WHEN a.status = 'present' THEN 1 END) as present,
           COUNT(a.id) as total,
           ROUND(COUNT(CASE WHEN a.status = 'present' THEN 1 END) * 100.0 / NULLIF(COUNT(a.id), 0), 1) as attendance
    FROM students s
    LEFT JOIN attendance a ON s.id = a.student_id
    WHERE s.is_active = TRUE
    GROUP BY s.id
    ORDER BY attendance ASC
""", ())

critical = 0
warning = 0
good = 0

for r in data:
    att = r['attendance'] or 0
    severity = 'CRITICAL' if att < 60 else ('WARNING' if att < 75 else 'GOOD')
    
    if att < 60:
        critical += 1
    elif att < 75:
        warning += 1
    else:
        good += 1
    
    print(f"{r['student_id']}: {r['name']:20s} ({r['program']:25s}) - {att:5.1f}% [{severity}] ({r['present']}/{r['total']})")

print(f"\n=== SUMMARY ===")
print(f"Critical (<60%): {critical}")
print(f"Warning (60-75%): {warning}")
print(f"Good (>=75%): {good}")
print(f"Total: {len(data)}")
