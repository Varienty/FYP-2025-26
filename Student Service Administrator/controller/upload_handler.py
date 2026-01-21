"""
Simple Student Upload Handler
Handles CSV and Excel file uploads and inserts students into database
"""

from flask import Blueprint, request, jsonify
import csv
import io
import hashlib
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from common import db_utils

# Try to import openpyxl for Excel support
try:
    import openpyxl
    EXCEL_SUPPORT = True
except ImportError:
    EXCEL_SUPPORT = False

upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')


@upload_bp.route('/students', methods=['POST'])
def upload_students():
    """Upload students from CSV or Excel file"""
    try:
        # Get file and form data
        if 'file' not in request.files:
            return jsonify({'ok': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        program = request.form.get('program', '')
        academic_year = request.form.get('academicYear', '')
        intake = request.form.get('intake', '')

        # Extract intake year from academic year (e.g., "2024/2025" -> "2024")
        intake_year = academic_year.split('/')[0] if academic_year else ''

        # Parse the file based on extension
        filename = file.filename.lower()
        students = []

        if filename.endswith('.csv'):
            # Parse CSV
            content = file.stream.read().decode('UTF-8')
            csv_file = io.StringIO(content)
            reader = csv.DictReader(csv_file)

            for row in reader:
                # Skip empty rows
                if not any(row.values()):
                    continue
                students.append(row)

        elif filename.endswith(('.xlsx', '.xls')):
            if not EXCEL_SUPPORT:
                return jsonify({'ok': False, 'error': 'Excel support not available. Please use CSV.'}), 400

            # Parse Excel
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active

            # Get headers from first row
            headers = []
            for cell in sheet[1]:
                headers.append(cell.value)

            # Read data rows
            for row in sheet.iter_rows(min_row=2, values_only=True):
                # Skip empty rows
                if not any(row):
                    continue

                student = {}
                for i, value in enumerate(row):
                    if i < len(headers) and headers[i]:
                        student[headers[i]] = value
                students.append(student)
        else:
            return jsonify({'ok': False, 'error': 'Unsupported file format. Please use CSV or Excel.'}), 400

        # Process and insert students
        successful = 0
        failed = 0
        errors = []

        for student in students:
            try:
                # Extract student data - try different column name variations
                student_id = (student.get('StudentID') or student.get('Student ID') or
                             student.get('student_id') or student.get('ID') or '').strip()

                first_name = (student.get('FirstName') or student.get('First Name') or
                             student.get('first_name') or '').strip()

                last_name = (student.get('LastName') or student.get('Last Name') or
                            student.get('last_name') or '').strip()

                email = (student.get('Email') or student.get('email') or '').strip()

                phone = (student.get('Phone') or student.get('phone') or '').strip()

                # If FirstName and LastName are empty, try splitting "Name" column
                if not first_name and not last_name:
                    full_name = (student.get('Name') or student.get('name') or '').strip()
                    if full_name:
                        parts = full_name.split(' ', 1)
                        first_name = parts[0]
                        last_name = parts[1] if len(parts) > 1 else ''

                # Validate required fields
                if not student_id or not email or not first_name:
                    errors.append(f"Row with StudentID '{student_id}': Missing required fields")
                    failed += 1
                    continue

                # Generate default password (hashed student_id)
                password = hashlib.sha256(student_id.encode()).hexdigest()

                # Check if student already exists
                existing = db_utils.query_one(
                    "SELECT id FROM students WHERE student_id = %s OR email = %s",
                    (student_id, email)
                )

                if existing:
                    # Update existing student
                    db_utils.execute("""
                        UPDATE students
                        SET first_name = %s, last_name = %s, email = %s, phone = %s,
                            program = %s, intake_period = %s, intake_year = %s,
                            academic_year = %s, updated_at = NOW()
                        WHERE student_id = %s
                    """, (first_name, last_name, email, phone, program, intake,
                          intake_year, academic_year, student_id))
                else:
                    # Insert new student
                    db_utils.execute("""
                        INSERT INTO students
                        (student_id, first_name, last_name, email, phone, password,
                         program, intake_period, intake_year, academic_year, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                    """, (student_id, first_name, last_name, email, phone, password,
                          program, intake, intake_year, academic_year))

                successful += 1

            except Exception as e:
                errors.append(f"Error processing {student_id}: {str(e)}")
                failed += 1

        return jsonify({
            'ok': True,
            'message': f'Successfully processed {successful} students',
            'total': len(students),
            'successful': successful,
            'failed': failed,
            'errors': errors[:10]  # Return first 10 errors
        }), 200

    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@upload_bp.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({'ok': True, 'message': 'Upload handler is working'}), 200
