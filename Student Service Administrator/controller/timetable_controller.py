"""
Timetable & Module Assignment Controller
Handles module assignments, student enrollments, and timetable scheduling
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from datetime import datetime, date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from common import db_utils

app = Flask(__name__)
CORS(app)


# ============================================================================
# MODULE MANAGEMENT
# ============================================================================

@app.route('/api/ssa/modules', methods=['GET'])
def get_all_modules():
    """Get all modules with lecturer information"""
    try:
        modules = db_utils.query_all("""
            SELECT
                m.id,
                m.module_code,
                m.module_name,
                m.description,
                m.lecturer_id,
                m.academic_year,
                m.term,
                m.credits,
                m.is_active,
                l.first_name as lecturer_first_name,
                l.last_name as lecturer_last_name,
                l.email as lecturer_email,
                (SELECT COUNT(*) FROM student_enrollments WHERE module_id = m.id) as enrolled_count
            FROM modules m
            LEFT JOIN lecturers l ON m.lecturer_id = l.id
            ORDER BY m.module_code
        """)

        return jsonify({'ok': True, 'modules': modules})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/ssa/modules/<int:module_id>', methods=['GET'])
def get_module(module_id):
    """Get a specific module"""
    try:
        module = db_utils.query_one("""
            SELECT
                m.*,
                l.first_name as lecturer_first_name,
                l.last_name as lecturer_last_name,
                l.email as lecturer_email
            FROM modules m
            LEFT JOIN lecturers l ON m.lecturer_id = l.id
            WHERE m.id = %s
        """, (module_id,))

        if not module:
            return jsonify({'ok': False, 'error': 'Module not found'}), 404

        return jsonify({'ok': True, 'module': module})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/ssa/modules', methods=['POST'])
def create_module():
    """Create a new module"""
    try:
        data = request.get_json()

        module_code = data.get('module_code')
        module_name = data.get('module_name')
        description = data.get('description', '')
        credits = data.get('credits', 3)
        academic_year = data.get('academic_year')
        term = data.get('term')

        if not all([module_code, module_name]):
            return jsonify({'ok': False, 'error': 'module_code and module_name are required'}), 400

        # Check if module code already exists
        existing = db_utils.query_one(
            "SELECT id FROM modules WHERE module_code = %s",
            (module_code,)
        )

        if existing:
            return jsonify({'ok': False, 'error': 'Module code already exists'}), 400

        # Insert new module
        db_utils.execute("""
            INSERT INTO modules
            (module_code, module_name, description, credits, academic_year, term, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
        """, (module_code, module_name, description, credits, academic_year, term))

        return jsonify({'ok': True, 'message': 'Module created successfully'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/ssa/modules/<int:module_id>/assign-lecturer', methods=['POST'])
def assign_lecturer_to_module(module_id):
    """Assign a lecturer to a module"""
    try:
        data = request.get_json()
        lecturer_id = data.get('lecturer_id')

        if not lecturer_id:
            return jsonify({'ok': False, 'error': 'lecturer_id is required'}), 400

        # Check if lecturer exists
        lecturer = db_utils.query_one("SELECT id FROM lecturers WHERE id = %s", (lecturer_id,))
        if not lecturer:
            return jsonify({'ok': False, 'error': 'Lecturer not found'}), 404

        # Update module
        db_utils.execute(
            "UPDATE modules SET lecturer_id = %s WHERE id = %s",
            (lecturer_id, module_id)
        )

        return jsonify({'ok': True, 'message': 'Lecturer assigned successfully'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


# ============================================================================
# LECTURER MANAGEMENT
# ============================================================================

@app.route('/api/ssa/lecturers', methods=['GET'])
def get_all_lecturers():
    """Get all lecturers"""
    try:
        lecturers = db_utils.query_all("""
            SELECT
                id,
                first_name,
                last_name,
                email,
                phone,
                department,
                is_active
            FROM lecturers
            WHERE is_active = 1
            ORDER BY first_name, last_name
        """)

        return jsonify({'ok': True, 'lecturers': lecturers})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


# ============================================================================
# STUDENT ENROLLMENT
# ============================================================================

@app.route('/api/ssa/modules/<int:module_id>/students', methods=['GET'])
def get_module_students(module_id):
    """Get all students enrolled in a module"""
    try:
        students = db_utils.query_all("""
            SELECT
                s.id,
                s.student_id,
                s.first_name,
                s.last_name,
                s.email,
                se.enrollment_date,
                se.status
            FROM student_enrollments se
            JOIN students s ON se.student_id = s.id
            WHERE se.module_id = %s
            ORDER BY s.student_id
        """, (module_id,))

        return jsonify({'ok': True, 'students': students})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/ssa/students', methods=['GET'])
def get_all_students():
    """Get all active students"""
    try:
        students = db_utils.query_all("""
            SELECT
                id,
                student_id,
                first_name,
                last_name,
                email,
                intake_period,
                intake_year
            FROM students
            WHERE is_active = 1
            ORDER BY student_id
        """)

        return jsonify({'ok': True, 'students': students})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/ssa/modules/<int:module_id>/enroll', methods=['POST'])
def enroll_students(module_id):
    """Enroll students in a module"""
    try:
        data = request.get_json()
        student_ids = data.get('student_ids', [])

        if not student_ids:
            return jsonify({'ok': False, 'error': 'student_ids array is required'}), 400

        enrolled_count = 0
        already_enrolled = []

        for student_id in student_ids:
            # Check if already enrolled
            existing = db_utils.query_one("""
                SELECT id FROM student_enrollments
                WHERE student_id = %s AND module_id = %s
            """, (student_id, module_id))

            if existing:
                already_enrolled.append(student_id)
                continue

            # Enroll student
            db_utils.execute("""
                INSERT INTO student_enrollments
                (student_id, module_id, enrollment_date, status)
                VALUES (%s, %s, CURDATE(), 'active')
            """, (student_id, module_id))
            enrolled_count += 1

        return jsonify({
            'ok': True,
            'message': f'Enrolled {enrolled_count} student(s)',
            'enrolled_count': enrolled_count,
            'already_enrolled': already_enrolled
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/ssa/modules/<int:module_id>/unenroll/<int:student_id>', methods=['DELETE'])
def unenroll_student(module_id, student_id):
    """Unenroll a student from a module"""
    try:
        db_utils.execute("""
            DELETE FROM student_enrollments
            WHERE student_id = %s AND module_id = %s
        """, (student_id, module_id))

        return jsonify({'ok': True, 'message': 'Student unenrolled successfully'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


# ============================================================================
# TIMETABLE MANAGEMENT
# ============================================================================

@app.route('/api/ssa/timetable', methods=['GET'])
def get_all_timetables():
    """Get all timetable entries"""
    try:
        timetables = db_utils.query_all("""
            SELECT
                t.id,
                t.module_id,
                t.day_of_week,
                t.start_time,
                t.end_time,
                t.room,
                t.class_date,
                t.is_active,
                m.module_code,
                m.module_name,
                l.first_name as lecturer_first_name,
                l.last_name as lecturer_last_name
            FROM timetable t
            JOIN modules m ON t.module_id = m.id
            LEFT JOIN lecturers l ON m.lecturer_id = l.id
            ORDER BY t.class_date, t.start_time
        """)

        # Convert timedelta to time string and date objects to string
        for tt in timetables:
            if hasattr(tt.get('start_time'), 'total_seconds'):
                hours = int(tt['start_time'].total_seconds() // 3600)
                minutes = int((tt['start_time'].total_seconds() % 3600) // 60)
                tt['start_time'] = f"{hours:02d}:{minutes:02d}:00"
            if hasattr(tt.get('end_time'), 'total_seconds'):
                hours = int(tt['end_time'].total_seconds() // 3600)
                minutes = int((tt['end_time'].total_seconds() % 3600) // 60)
                tt['end_time'] = f"{hours:02d}:{minutes:02d}:00"

            # Convert date object to ISO string (YYYY-MM-DD)
            if tt.get('class_date'):
                if hasattr(tt['class_date'], 'isoformat'):
                    tt['class_date'] = tt['class_date'].isoformat()
                elif isinstance(tt['class_date'], date):
                    tt['class_date'] = tt['class_date'].strftime('%Y-%m-%d')

        return jsonify({'ok': True, 'timetables': timetables})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/ssa/timetable/<int:module_id>', methods=['GET'])
def get_module_timetable(module_id):
    """Get timetable for a specific module"""
    try:
        timetables = db_utils.query_all("""
            SELECT *
            FROM timetable
            WHERE module_id = %s
            ORDER BY day_of_week, start_time
        """, (module_id,))

        return jsonify({'ok': True, 'timetables': timetables})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/ssa/timetable', methods=['POST'])
def create_timetable():
    """Create a new timetable entry"""
    try:
        data = request.get_json()

        module_id = data.get('module_id')
        day_of_week = data.get('day_of_week')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        room = data.get('room')
        class_date = data.get('class_date')  # Optional: for specific date classes

        if not all([module_id, day_of_week, start_time, end_time]):
            return jsonify({'ok': False, 'error': 'Missing required fields'}), 400

        # Check for conflicts - only check same date if class_date is specified
        if class_date:
            # For specific date lessons, only check conflicts on the exact same date
            conflict = db_utils.query_one("""
                SELECT id FROM timetable
                WHERE room = %s
                  AND class_date = %s
                  AND is_active = 1
                  AND (
                    (start_time <= %s AND end_time > %s) OR
                    (start_time < %s AND end_time >= %s) OR
                    (start_time >= %s AND end_time <= %s)
                  )
            """, (room, class_date, start_time, start_time, end_time, end_time, start_time, end_time))
        else:
            # For recurring weekly lessons, check conflicts on same day of week
            conflict = db_utils.query_one("""
                SELECT id FROM timetable
                WHERE room = %s
                  AND day_of_week = %s
                  AND class_date IS NULL
                  AND is_active = 1
                  AND (
                    (start_time <= %s AND end_time > %s) OR
                    (start_time < %s AND end_time >= %s) OR
                    (start_time >= %s AND end_time <= %s)
                  )
            """, (room, day_of_week, start_time, start_time, end_time, end_time, start_time, end_time))

        if conflict:
            return jsonify({'ok': False, 'error': 'Time slot conflict in this room'}), 400

        # Insert timetable entry
        db_utils.execute("""
            INSERT INTO timetable
            (module_id, day_of_week, start_time, end_time, room, class_date, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
        """, (module_id, day_of_week, start_time, end_time, room, class_date))

        return jsonify({'ok': True, 'message': 'Timetable entry created successfully'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/ssa/timetable/<int:timetable_id>', methods=['PUT'])
def update_timetable(timetable_id):
    """Update a timetable entry"""
    try:
        data = request.get_json()

        day_of_week = data.get('day_of_week')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        room = data.get('room')

        db_utils.execute("""
            UPDATE timetable
            SET day_of_week = %s, start_time = %s, end_time = %s, room = %s
            WHERE id = %s
        """, (day_of_week, start_time, end_time, room, timetable_id))

        return jsonify({'ok': True, 'message': 'Timetable entry updated successfully'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/ssa/timetable/<int:timetable_id>', methods=['DELETE'])
def delete_timetable(timetable_id):
    """Delete a timetable entry"""
    try:
        db_utils.execute("DELETE FROM timetable WHERE id = %s", (timetable_id,))
        return jsonify({'ok': True, 'message': 'Timetable entry deleted successfully'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'SSA Timetable Controller'})


if __name__ == '__main__':
    print("=" * 60)
    print("SSA Timetable & Module Assignment Controller")
    print("=" * 60)
    print("\nRunning on: http://127.0.0.1:5010")
    print("\nEndpoints:")
    print("  - Modules: /api/ssa/modules")
    print("  - Lecturers: /api/ssa/lecturers")
    print("  - Students: /api/ssa/students")
    print("  - Enrollment: /api/ssa/modules/<id>/enroll")
    print("  - Timetable: /api/ssa/timetable")
    print("=" * 60)

    app.run(debug=True, port=5010, host='127.0.0.1', use_reloader=False)
