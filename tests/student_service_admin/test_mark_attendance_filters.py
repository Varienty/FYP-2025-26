import sys
sys.path.insert(0, 'common')
import db_utils

# Get sample classes
classes = db_utils.query_all('SELECT id, module_code, module_name FROM modules LIMIT 5', ())
print("=== Available Classes ===")
for c in classes:
    print(f"Class {c['id']}: {c['module_code']} - {c['module_name']}")

# Get students enrolled in class 1 with different filters
print("\n=== Students in Class 1 (No Filter) ===")
students = db_utils.query_all("""
    SELECT s.student_id, CONCAT(s.first_name, ' ', s.last_name) as name, s.intake_period, s.academic_year
    FROM students s
    JOIN student_enrollments se ON s.id = se.student_id
    WHERE se.module_id = 1 AND se.status = 'active' AND s.is_active = TRUE
    ORDER BY s.student_id
""", ())
print(f"Total: {len(students)}")
for st in students[:5]:
    print(f"  {st['student_id']}: {st['name']} ({st['intake_period']}, {st['academic_year']})")

print("\n=== Students in Class 1 (April Intake) ===")
students_april = db_utils.query_all("""
    SELECT s.student_id, CONCAT(s.first_name, ' ', s.last_name) as name, s.intake_period, s.academic_year
    FROM students s
    JOIN student_enrollments se ON s.id = se.student_id
    WHERE se.module_id = 1 AND se.status = 'active' AND s.is_active = TRUE AND s.intake_period = 'April'
    ORDER BY s.student_id
""", ())
print(f"Total: {len(students_april)}")
for st in students_april[:5]:
    print(f"  {st['student_id']}: {st['name']} ({st['intake_period']}, {st['academic_year']})")

print("\n=== Students in Class 1 (2024/2025 Academic Year) ===")
students_2024 = db_utils.query_all("""
    SELECT s.student_id, CONCAT(s.first_name, ' ', s.last_name) as name, s.intake_period, s.academic_year
    FROM students s
    JOIN student_enrollments se ON s.id = se.student_id
    WHERE se.module_id = 1 AND se.status = 'active' AND s.is_active = TRUE AND s.academic_year = '2024/2025'
    ORDER BY s.student_id
""", ())
print(f"Total: {len(students_2024)}")
for st in students_2024[:5]:
    print(f"  {st['student_id']}: {st['name']} ({st['intake_period']}, {st['academic_year']})")
