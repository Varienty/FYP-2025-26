"""
Student Service Administrator - Main Application
Runs all SSA controllers on a single port (5008)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from auth_controller import auth_bp
from attendance_controller import attendance_bp
from reports_controller import reports_bp
from upload_handler import upload_bp
import sys
import os
import hashlib
import csv
import io

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from common import db_utils

# Try to import openpyxl for Excel support
try:
    import openpyxl
    EXCEL_SUPPORT = True
except ImportError:
    EXCEL_SUPPORT = False

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(upload_bp)

@app.route('/api/ssa/programs', methods=['GET'])
def get_programs():
    """Get distinct programs from students table"""
    try:
        programs = db_utils.query_all("""
            SELECT DISTINCT program
            FROM students
            WHERE program IS NOT NULL AND program != ''
            ORDER BY program
        """)

        program_list = [p['program'] for p in programs]
        return jsonify({'ok': True, 'programs': program_list}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/ssa/modules', methods=['GET'])
def get_modules():
    """Get all modules"""
    try:
        modules = db_utils.query_all("""
            SELECT
                m.id,
                m.module_code,
                m.module_name,
                m.term,
                m.academic_year,
                CONCAT(l.first_name, ' ', l.last_name) as lecturer_name
            FROM modules m
            LEFT JOIN lecturers l ON m.lecturer_id = l.id
            WHERE m.is_active = 1
            ORDER BY m.module_code
        """)

        return jsonify({'ok': True, 'modules': modules}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/class-list/upload', methods=['POST'])
def upload_class_list():
    """Upload and process student class list from CSV/Excel file"""
    import sys
    try:
        print("=" * 80, file=sys.stderr)
        print("UPLOAD REQUEST RECEIVED", file=sys.stderr)
        print("=" * 80, file=sys.stderr)

        if 'file' not in request.files:
            return jsonify({'ok': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        program = request.form.get('program')
        academic_year = request.form.get('academicYear')
        intake = request.form.get('intake')

        print(f"Program: {program}", file=sys.stderr)
        print(f"Academic Year: {academic_year}", file=sys.stderr)
        print(f"Intake: {intake}", file=sys.stderr)
        print(f"Filename: {file.filename}", file=sys.stderr)

        if not all([program, academic_year, intake]):
            return jsonify({'ok': False, 'error': 'Missing required fields'}), 400

        # Extract intake year from academic year (e.g., "2024/2025" -> 2024)
        intake_year = academic_year.split('/')[0]

        # Parse file
        students_data = []
        filename = file.filename.lower()

        if filename.endswith('.csv'):
            # Parse CSV
            content = file.stream.read().decode('UTF8')
            print(f"CSV Content ({len(content)} bytes):", file=sys.stderr)
            print(content[:500], file=sys.stderr)  # Print first 500 chars

            stream = io.StringIO(content, newline=None)
            csv_reader = csv.DictReader(stream)
            # Filter out empty rows
            all_rows = list(csv_reader)
            students_data = [row for row in all_rows if any(row.values())]

            print(f"Total rows read: {len(all_rows)}", file=sys.stderr)
            print(f"Non-empty rows: {len(students_data)}", file=sys.stderr)
            print(f"First row: {students_data[0] if students_data else 'NONE'}", file=sys.stderr)

        elif filename.endswith(('.xlsx', '.xls')) and EXCEL_SUPPORT:
            # Parse Excel
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active
            headers = [cell.value for cell in sheet[1]]

            for row in sheet.iter_rows(min_row=2, values_only=True):
                student = {}
                for idx, value in enumerate(row):
                    if idx < len(headers) and headers[idx]:
                        student[headers[idx]] = value
                if any(student.values()):  # Skip empty rows
                    students_data.append(student)
        else:
            return jsonify({'ok': False, 'error': 'Unsupported file format'}), 400

        # Process and insert students
        successful = 0
        failed = 0
        failed_records = []

        print(f"Processing {len(students_data)} students...")

        for idx, student in enumerate(students_data):
            print(f"Processing row {idx + 1}: {student}")
            try:
                # Required fields
                student_id = student.get('StudentID') or student.get('Student ID') or student.get('student_id')
                first_name = student.get('FirstName') or student.get('First Name') or student.get('first_name')
                last_name = student.get('LastName') or student.get('Last Name') or student.get('last_name')
                email = student.get('Email') or student.get('email')

                # Split name if only one "Name" column provided
                if not first_name and not last_name:
                    full_name = student.get('Name') or student.get('name') or ''
                    name_parts = full_name.strip().split(' ', 1)
                    first_name = name_parts[0] if len(name_parts) > 0 else ''
                    last_name = name_parts[1] if len(name_parts) > 1 else ''

                # Optional fields
                phone = student.get('Phone') or student.get('phone') or ''

                # Validation
                if not student_id or not first_name or not email:
                    failed += 1
                    failed_records.append(f"{student_id or 'Unknown'}: Missing required fields")
                    continue

                # Generate default password ("password" for all new students)
                default_password = hashlib.sha256("password".encode()).hexdigest()

                # Check if student already exists
                existing = db_utils.query_one(
                    "SELECT id FROM students WHERE student_id = %s",
                    (student_id,)
                )

                if existing:
                    # Update existing student
                    db_utils.execute("""
                        UPDATE students
                        SET first_name = %s, last_name = %s, email = %s, phone = %s,
                            program = %s, intake_period = %s, intake_year = %s, academic_year = %s
                        WHERE student_id = %s
                    """, (first_name, last_name, email, phone, program, intake, intake_year, academic_year, student_id))
                else:
                    # Insert new student
                    db_utils.execute("""
                        INSERT INTO students
                        (student_id, first_name, last_name, email, phone, password,
                         program, intake_period, intake_year, academic_year, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                    """, (student_id, first_name, last_name, email, phone, default_password,
                          program, intake, intake_year, academic_year))

                successful += 1
                print(f"Successfully processed: {student_id}")

            except Exception as e:
                failed += 1
                failed_records.append(f"{student_id}: {str(e)}")
                print(f"Failed to process {student_id}: {str(e)}")

        # Collect processed student IDs for verification
        processed_ids = []
        for student in students_data:
            sid = student.get('StudentID') or student.get('Student ID') or student.get('student_id') or 'Unknown'
            processed_ids.append(sid)

        return jsonify({
            'ok': True,
            'message': f'Processed {successful + failed} students',
            'totalStudents': len(students_data),
            'successful': successful,
            'failed': failed,
            'failedRecords': failed_records,
            'processedStudentIDs': processed_ids[:10]  # Return first 10 IDs for debugging
        }), 200

    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {'status': 'ok', 'message': 'SSA Controller running'}, 200

if __name__ == '__main__':
    print("=" * 60)
    print("Student Service Administrator Controller")
    print("=" * 60)
    print("Running on: http://127.0.0.1:5008")
    print("Endpoints:")
    print("  - Auth: /api/auth/*")
    print("  - Attendance: /api/attendance/*")
    print("  - Reports: /api/*")
    print("=" * 60)
    app.run(debug=True, port=5008, host='127.0.0.1', use_reloader=False)
