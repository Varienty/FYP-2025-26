"""
Student Service Administrator - Attendance Management Controller
Handles marking, adjusting, and retrieving attendance records.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from common import db_utils

attendance_bp = Blueprint('ssa_attendance', __name__, url_prefix='/api/attendance')

@attendance_bp.route('/classes', methods=['GET'])
def get_classes():
    """Get list of all active classes"""
    try:
        classes = db_utils.query_all(
            """SELECT c.id, c.module_code, c.module_name,
               CONCAT(l.first_name, ' ', l.last_name) as lecturer_name,
               c.term, c.academic_year
               FROM modules c
               LEFT JOIN lecturers l ON c.lecturer_id = l.id
               WHERE c.is_active = TRUE
               ORDER BY c.module_code""",
            ()
        )

        result = []
        for cls in classes:
            result.append({
                'id': cls['id'],
                'code': cls['module_code'],
                'name': cls['module_name'],
                'fullName': f"{cls['module_code']} - {cls['module_name']}",
                'lecturer': cls['lecturer_name'],
                'term': cls['term'],
                'academicYear': cls['academic_year']
            })
        
        return jsonify({'ok': True, 'classes': result}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@attendance_bp.route('/daily-summary', methods=['GET'])
def daily_summary():
    """Get daily attendance summary from database"""
    today = request.args.get('date', date.today().isoformat())
    
    # Get attendance stats for today
    stats = db_utils.query_one(
        """SELECT 
           COUNT(*) as total,
           SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present,
           SUM(CASE WHEN status = 'absent' THEN 1 ELSE 0 END) as absent,
           SUM(CASE WHEN status = 'late' THEN 1 ELSE 0 END) as late
           FROM attendance
           WHERE DATE(check_in_time) = %s""",
        (today,)
    )
    
    total = int(stats['total'] or 0)
    present = int(stats['present'] or 0)
    absent = int(stats['absent'] or 0)
    late = int(stats['late'] or 0)
    
    # Get total enrolled students for rate calculation
    total_students = db_utils.query_one("SELECT COUNT(*) as count FROM students WHERE is_active = TRUE")
    student_count = int(total_students['count'] or 400)
    
    attendance_rate = round((present / student_count * 100), 1) if student_count > 0 else 0.0
    
    # Get trends for last 7 days
    trends = []
    for i in range(6, -1, -1):
        check_date = date.today() - timedelta(days=i)
        day_stats = db_utils.query_one(
            """SELECT 
               COUNT(*) as total,
               SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present
               FROM attendance
               WHERE DATE(check_in_time) = %s""",
            (check_date.isoformat(),)
        )
        day_present = int(day_stats['present'] or 0)
        day_rate = round((day_present / student_count * 100), 1) if student_count > 0 else 0.0
        
        day_label = 'Today' if i == 0 else check_date.strftime('%a')
        trends.append({'date': day_label, 'rate': float(day_rate)})
    
    # Get peak absence days (group by day of week)
    peak_days = db_utils.query_all(
        """SELECT 
           DAYNAME(check_in_time) as day_name,
           COUNT(*) as total_records,
           SUM(CASE WHEN status = 'absent' THEN 1 ELSE 0 END) as absences
           FROM attendance
           WHERE check_in_time >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
           GROUP BY DAYNAME(check_in_time), DAYOFWEEK(check_in_time)
           ORDER BY absences DESC
           LIMIT 2"""
    )
    
    peak_absence_days = []
    for day in peak_days:
        total_records = int(day['total_records'] or 1)
        absences = int(day['absences'] or 0)
        percentage = round((absences / total_records * 100), 1)
        peak_absence_days.append({
            'day': day['day_name'],
            'absences': absences,
            'percentage': float(percentage)
        })
    
    # Generate systemic issues based on real data
    systemic_issues = []
    if peak_absence_days:
        avg_percentage = sum(d['percentage'] for d in peak_absence_days) / len(peak_absence_days)
        for day in peak_absence_days:
            if day['percentage'] > avg_percentage:
                systemic_issues.append(
                    f"{day['day']} shows consistently high absence rate ({day['percentage']}% vs. {round(avg_percentage, 1)}% average)"
                )
    
    if attendance_rate < 80:
        systemic_issues.append(f'Overall attendance rate ({attendance_rate}%) is below target threshold (80%)')
    
    return jsonify({
        'ok': True,
        'attendanceRate': float(attendance_rate),
        'presentCount': present,
        'absentCount': absent,
        'lateCount': late,
        'totalStudents': student_count,
        'distribution': {
            'present': present,
            'absent': absent,
            'late': late
        },
        'trends': trends,
        'peakAbsenceDays': peak_absence_days,
        'systemicIssues': systemic_issues
    }), 200

@attendance_bp.route('/filter-options', methods=['GET'])
def get_filter_options():
    """Get distinct intake periods and academic years for filters"""
    intake_periods = db_utils.query_all(
        "SELECT DISTINCT intake_period FROM students WHERE is_active = TRUE ORDER BY intake_period",
        ()
    )
    academic_years = db_utils.query_all(
        "SELECT DISTINCT academic_year FROM students WHERE is_active = TRUE AND academic_year IS NOT NULL ORDER BY academic_year DESC",
        ()
    )
    
    return jsonify({
        'ok': True,
        'intakePeriods': [p['intake_period'] for p in intake_periods],
        'academicYears': [y['academic_year'] for y in academic_years]
    }), 200

@attendance_bp.route('/mark', methods=['GET', 'POST'])
def mark_attendance():
    """Get students for a class or mark attendance"""
    if request.method == 'GET':
        # Get students from database with filters
        module_id = request.args.get('moduleId', 1)
        intake_period = request.args.get('intakePeriod')
        academic_year = request.args.get('academicYear')
        
        # Build query with filters
        query = """SELECT s.id, s.student_id, CONCAT(s.first_name, ' ', s.last_name) as name,
               s.email, s.intake_period, s.academic_year, 'unmarked' as status
               FROM students s
               JOIN student_enrollments se ON s.id = se.student_id
               WHERE se.module_id = %s AND se.status = 'active' AND s.is_active = TRUE"""
        
        params = [module_id]
        
        # Add intake period filter
        if intake_period:
            query += " AND s.intake_period = %s"
            params.append(intake_period)
        
        # Add academic year filter
        if academic_year:
            query += " AND s.academic_year = %s"
            params.append(academic_year)
        
        query += " ORDER BY s.student_id"
        
        students = db_utils.query_all(query, tuple(params))
        
        result = []
        for s in students:
            result.append({
                'id': s['student_id'],
                'name': s['name'],
                'email': s['email'],
                'status': 'unmarked'
            })
        
        return jsonify({'ok': True, 'students': result}), 200
    
    elif request.method == 'POST':
        # Save attendance records to database
        data = request.get_json()
        timestamp = datetime.now()
        module_id = data[0].get('moduleId', 1) if len(data) > 0 else 1
        
        for record in data:
            student_id_str = record['studentId']
            status = record['status']
            remarks = record.get('remarks', '')
            
            # Get student's internal ID
            student = db_utils.query_one(
                "SELECT id FROM students WHERE student_id = %s",
                (student_id_str,)
            )
            
            if student:
                # Insert attendance record
                db_utils.execute(
                    """INSERT INTO attendance (student_id, module_id, check_in_time, status, is_manual)
                       VALUES (%s, %s, %s, %s, TRUE)""",
                    (student['id'], module_id, timestamp, status)
                )
                
                # Log in audit_logs
                db_utils.execute(
                    """INSERT INTO audit_logs (user_type, user_id, action, table_name, record_id, new_values)
                       VALUES ('student_service_admin', 1, 'mark_attendance', 'attendance', %s, %s)""",
                    (student['id'], f'{{"status": "{status}", "remarks": "{remarks}"}}')
                )
        
        return jsonify({
            'ok': True,
            'message': f'{len(data)} attendance records saved',
            'count': len(data)
        }), 200

@attendance_bp.route('/adjust', methods=['POST'])
def adjust_attendance():
    """Adjust existing attendance record in database"""
    data = request.get_json()
    
    record_id = data.get('recordId')
    student_id_str = data.get('studentId')
    previous_status = data.get('previousStatus')
    new_status = data.get('newStatus')
    reason = data.get('reason', '')
    notes = data.get('notes', '')
    
    if not record_id:
        return jsonify({'ok': False, 'message': 'Record ID is required'}), 400
    
    # Get student's internal ID for logging
    student = db_utils.query_one(
        "SELECT id FROM students WHERE student_id = %s",
        (student_id_str,)
    )
    
    if not student:
        return jsonify({'ok': False, 'message': 'Student not found'}), 404
    
    # Update specific attendance record by ID
    db_utils.execute(
        """UPDATE attendance 
           SET status = %s, manually_edited_by = 1, edit_reason = %s
           WHERE id = %s""",
        (new_status, reason, record_id)
    )
    
    # Log in audit_logs
    db_utils.execute(
        """INSERT INTO audit_logs (user_type, user_id, action, table_name, record_id, old_values, new_values)
           VALUES ('student_service_admin', 1, 'adjust_attendance', 'attendance', %s, %s, %s)""",
        (record_id, 
         f'{{"status": "{previous_status}"}}',
         f'{{"status": "{new_status}", "reason": "{reason}", "notes": "{notes}"}}')
    )
    
    return jsonify({
        'ok': True,
        'message': 'Attendance record adjusted successfully'
    }), 200

@attendance_bp.route('/search', methods=['GET'])
def search_attendance():
    """Search for specific attendance record in database"""
    student_id_str = request.args.get('studentId')
    student_name = request.args.get('studentName')
    module_id = request.args.get('class', 1)
    date_filter = request.args.get('date')
    
    if not student_id_str and not student_name:
        return jsonify({'ok': False, 'message': 'Student ID or Name required'}), 400
    
    # Get student's internal ID
    if student_id_str:
        student = db_utils.query_one(
            "SELECT id, student_id, CONCAT(first_name, ' ', last_name) as name FROM students WHERE student_id = %s",
            (student_id_str,)
        )
    else:
        # Search by name (partial match)
        student = db_utils.query_one(
            "SELECT id, student_id, CONCAT(first_name, ' ', last_name) as name FROM students WHERE CONCAT(first_name, ' ', last_name) LIKE %s",
            (f'%{student_name}%',)
        )
    
    if not student:
        return jsonify({'ok': False, 'message': 'Student not found'}), 404
    
    # Search attendance record
    query = """SELECT a.id, s.student_id, CONCAT(s.first_name, ' ', s.last_name) as name,
               c.module_code, DATE(a.check_in_time) as date, a.status, 
               COALESCE(a.edit_reason, 'No remarks') as remarks
               FROM attendance a
               JOIN students s ON a.student_id = s.id
               JOIN modules c ON a.module_id = c.id
               WHERE s.id = %s AND a.module_id = %s"""
    
    params = [student['id'], module_id]
    
    if date_filter:
        query += " AND DATE(a.check_in_time) = %s"
        params.append(date_filter)
    
    query += " ORDER BY a.check_in_time DESC LIMIT 1"
    
    record = db_utils.query_one(query, tuple(params))
    
    if not record:
        return jsonify({'ok': False, 'message': 'No attendance record found'}), 404

    return jsonify({
        'ok': True,
        'record': {
            'id': record['id'],
            'studentId': record['student_id'],
            'name': record['name'],
            'class': record['module_code'],
            'date': record['date'].isoformat() if record['date'] else None,
            'status': record['status'],
            'remarks': record['remarks']
        }
    }), 200


# ============================================================================
# NEW SESSION-BASED ATTENDANCE ENDPOINTS
# ============================================================================

@attendance_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """Get all individual lesson sessions for a module within date range"""
    try:
        module_id = request.args.get('moduleId')
        start_date_str = request.args.get('startDate')
        end_date_str = request.args.get('endDate')

        if not module_id:
            return jsonify({'ok': False, 'error': 'moduleId is required'}), 400

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Get timetable entries for this module with their specific dates
        timetable_entries = db_utils.query_all("""
            SELECT
                id,
                day_of_week,
                start_time,
                end_time,
                room,
                class_date
            FROM timetable
            WHERE module_id = %s
              AND is_active = 1
        """, (module_id,))

        sessions = []

        # Map day names to numbers (0=Monday, 6=Sunday)
        day_map = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }

        for entry in timetable_entries:
            # Convert timedelta to time string
            start_time = entry['start_time']
            end_time = entry['end_time']

            if hasattr(start_time, 'total_seconds'):
                hours = int(start_time.total_seconds() // 3600)
                minutes = int((start_time.total_seconds() % 3600) // 60)
                start_time_str = f"{hours:02d}:{minutes:02d}"
            else:
                start_time_str = str(start_time)

            if hasattr(end_time, 'total_seconds'):
                hours = int(end_time.total_seconds() // 3600)
                minutes = int((end_time.total_seconds() % 3600) // 60)
                end_time_str = f"{hours:02d}:{minutes:02d}"
            else:
                end_time_str = str(end_time)

            # Check if this is a specific date or recurring lesson
            if entry['class_date']:
                # Specific date lesson - only create session if within date range
                lesson_date = entry['class_date']
                if isinstance(lesson_date, str):
                    lesson_date = datetime.strptime(lesson_date, '%Y-%m-%d').date()

                if start_date <= lesson_date <= end_date:
                    sessions.append({
                        'id': f"{entry['id']}_{lesson_date.isoformat()}",
                        'timetableId': entry['id'],
                        'date': lesson_date.isoformat(),
                        'startTime': start_time_str,
                        'endTime': end_time_str,
                        'room': entry['room'],
                        'dayOfWeek': entry['day_of_week']
                    })
            else:
                # Recurring lesson - generate occurrences for matching day of week
                if entry['day_of_week'] not in day_map:
                    continue

                target_day = day_map[entry['day_of_week']]

                # Find all dates in range that match this day of week
                current_date = start_date
                while current_date <= end_date:
                    if current_date.weekday() == target_day:
                        sessions.append({
                            'id': f"{entry['id']}_{current_date.isoformat()}",
                            'timetableId': entry['id'],
                            'date': current_date.isoformat(),
                            'startTime': start_time_str,
                            'endTime': end_time_str,
                            'room': entry['room'],
                            'dayOfWeek': entry['day_of_week']
                        })
                    current_date += timedelta(days=1)

        # Sort by date and time
        sessions.sort(key=lambda x: (x['date'], x['startTime']))

        return jsonify({'ok': True, 'sessions': sessions}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@attendance_bp.route('/students', methods=['GET'])
def get_students_for_module():
    """Get all enrolled students for a module"""
    try:
        module_id = request.args.get('moduleId')

        if not module_id:
            return jsonify({'ok': False, 'error': 'moduleId is required'}), 400

        students = db_utils.query_all("""
            SELECT
                s.id,
                s.student_id as studentId,
                CONCAT(s.first_name, ' ', s.last_name) as name,
                s.email
            FROM student_enrollments se
            JOIN students s ON se.student_id = s.id
            WHERE se.module_id = %s
              AND s.is_active = 1
            ORDER BY s.student_id
        """, (module_id,))

        return jsonify({'ok': True, 'students': students}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@attendance_bp.route('/records', methods=['GET'])
def get_attendance_records():
    """Get existing attendance records for sessions"""
    try:
        module_id = request.args.get('moduleId')
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')

        if not module_id:
            return jsonify({'ok': False, 'error': 'moduleId is required'}), 400

        records = db_utils.query_all("""
            SELECT
                a.student_id,
                a.timetable_id,
                DATE(a.check_in_time) as attendance_date,
                a.status,
                CASE WHEN mc.id IS NOT NULL THEN 1 ELSE 0 END as has_mc
            FROM attendance a
            LEFT JOIN medical_certificates mc ON
                mc.student_id = a.student_id AND
                mc.class_id = %s AND
                DATE(a.check_in_time) BETWEEN mc.start_date AND mc.end_date AND
                mc.status = 'approved'
            WHERE a.module_id = %s
              AND DATE(a.check_in_time) BETWEEN %s AND %s
              AND a.timetable_id IS NOT NULL
        """, (module_id, module_id, start_date, end_date))

        # Convert to dictionary keyed by student_sessionId (where sessionId = timetableId_date)
        records_dict = {}
        for record in records:
            timetable_id = record['timetable_id']
            if not timetable_id:  # Skip if NULL
                continue

            date_str = record['attendance_date'].isoformat() if hasattr(record['attendance_date'], 'isoformat') else str(record['attendance_date'])
            session_id = f"{timetable_id}_{date_str}"
            key = f"{record['student_id']}_{session_id}"
            records_dict[key] = {
                'status': record['status'],
                'hasMc': bool(record['has_mc'])
            }

        # Also get approved MCs that might not have attendance records yet
        # This ensures MCs show up on the grid even if attendance hasn't been marked
        approved_mcs = db_utils.query_all("""
            SELECT
                mc.student_id,
                mc.start_date,
                mc.end_date,
                t.id as timetable_id
            FROM medical_certificates mc
            CROSS JOIN timetable t
            WHERE mc.class_id = %s
              AND mc.status = 'approved'
              AND t.module_id = %s
              AND t.is_active = 1
        """, (module_id, module_id))

        # For each approved MC, mark all matching sessions as having MC
        for mc in approved_mcs:
            mc_start = mc['start_date']
            mc_end = mc['end_date']
            timetable_id = mc['timetable_id']

            # Generate all dates in the MC range
            current_date = mc_start if isinstance(mc_start, date) else datetime.strptime(str(mc_start), '%Y-%m-%d').date()
            end_date_obj = mc_end if isinstance(mc_end, date) else datetime.strptime(str(mc_end), '%Y-%m-%d').date()

            while current_date <= end_date_obj:
                date_str = current_date.isoformat()
                session_id = f"{timetable_id}_{date_str}"
                key = f"{mc['student_id']}_{session_id}"

                # Only add if not already in records_dict, or update hasMc flag
                if key not in records_dict:
                    records_dict[key] = {
                        'status': 'excused',
                        'hasMc': True
                    }
                else:
                    records_dict[key]['hasMc'] = True

                current_date += timedelta(days=1)

        return jsonify({'ok': True, 'records': records_dict}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@attendance_bp.route('/mark-bulk', methods=['POST'])
def mark_bulk_attendance():
    """Save multiple attendance records at once"""
    try:
        data = request.get_json()
        records = data.get('records', [])
        admin_info = data.get('adminInfo', {})  # Admin details from frontend

        if not records:
            return jsonify({'ok': False, 'error': 'No records provided'}), 400

        saved_count = 0
        for record in records:
            student_id = record.get('studentId')
            session_id = record.get('sessionId')  # Format: "timetableId_YYYY-MM-DD"
            module_id = record.get('moduleId')
            status = record.get('status')

            # Parse session ID to extract timetable_id and date
            try:
                parts = session_id.split('_')
                timetable_id = parts[0]
                lesson_date = parts[1]  # YYYY-MM-DD

                # Create check_in_time with the lesson date
                check_in_datetime = f"{lesson_date} {datetime.now().strftime('%H:%M:%S')}"

            except (IndexError, ValueError):
                # Fallback if session ID format is wrong
                timetable_id = session_id
                check_in_datetime = datetime.now().isoformat()

            # Get student details for audit log
            student = db_utils.query_one("""
                SELECT student_id, CONCAT(first_name, ' ', last_name) as name
                FROM students WHERE id = %s
            """, (student_id,))

            # Check if record already exists for this student, timetable, and date
            existing = db_utils.query_one("""
                SELECT id, status FROM attendance
                WHERE student_id = %s
                  AND timetable_id = %s
                  AND DATE(check_in_time) = %s
            """, (student_id, timetable_id, lesson_date))

            old_status = existing['status'] if existing else 'unmarked'

            if existing:
                # Update existing record
                db_utils.execute("""
                    UPDATE attendance
                    SET status = %s
                    WHERE id = %s
                """, (status, existing['id']))
                attendance_id = existing['id']
            else:
                # Insert new record
                db_utils.execute("""
                    INSERT INTO attendance
                    (student_id, module_id, timetable_id, status, check_in_time)
                    VALUES (%s, %s, %s, %s, %s)
                """, (student_id, module_id, timetable_id, status, check_in_datetime))
                attendance_id = db_utils.query_one("SELECT LAST_INSERT_ID() as id")['id']

            # Only log to audit_logs if the status actually changed
            if old_status != status:
                import json
                db_utils.execute("""
                    INSERT INTO audit_logs
                    (user_type, user_id, admin_name, admin_email, student_id, student_name,
                     module_id, lesson_date, action, table_name, record_id,
                     old_values, new_values, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, (
                    'student_service_admin',
                    admin_info.get('id', 1),
                    admin_info.get('name', 'SSA'),
                    admin_info.get('email', 'admin@school.edu'),
                    student['student_id'] if student else '',
                    student['name'] if student else '',
                    module_id,
                    lesson_date,
                    f'mark_{status}',
                    'attendance',
                    attendance_id,
                    json.dumps({'status': old_status}),
                    json.dumps({'status': status})
                ))

            saved_count += 1

        return jsonify({'ok': True, 'saved': saved_count}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@attendance_bp.route('/medical-certificates', methods=['GET'])
def get_medical_certificates():
    """Get medical certificates for a module"""
    try:
        module_id = request.args.get('moduleId')
        status = request.args.get('status', 'pending')

        if not module_id:
            return jsonify({'ok': False, 'error': 'moduleId is required'}), 400

        certificates = db_utils.query_all("""
            SELECT
                mc.id,
                mc.student_id,
                s.student_id as studentId,
                CONCAT(s.first_name, ' ', s.last_name) as studentName,
                mc.start_date as startDate,
                mc.end_date as endDate,
                mc.reason,
                mc.certificate_file as certificateFile,
                mc.uploaded_at as uploadedAt,
                mc.status
            FROM medical_certificates mc
            JOIN students s ON mc.student_id = s.id
            WHERE mc.class_id = %s
              AND mc.status = %s
            ORDER BY mc.uploaded_at DESC
        """, (module_id, status))

        return jsonify({'ok': True, 'certificates': certificates}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@attendance_bp.route('/medical-certificates/<int:mc_id>/approve', methods=['POST'])
def approve_medical_certificate(mc_id):
    """Approve a medical certificate and mark affected attendance as excused"""
    try:
        data = request.get_json()
        notes = data.get('notes', '')

        # Get MC details
        mc = db_utils.query_one("""
            SELECT student_id, class_id, start_date, end_date
            FROM medical_certificates
            WHERE id = %s
        """, (mc_id,))

        if not mc:
            return jsonify({'ok': False, 'error': 'MC not found'}), 404

        # Update MC status
        db_utils.execute("""
            UPDATE medical_certificates
            SET status = 'approved',
                reviewed_by = 1,
                review_notes = %s,
                reviewed_at = NOW()
            WHERE id = %s
        """, (notes, mc_id))

        # Update related attendance records to 'excused' or create them
        db_utils.execute("""
            UPDATE attendance
            SET status = 'excused'
            WHERE student_id = %s
              AND module_id = %s
              AND DATE(check_in_time) BETWEEN %s AND %s
        """, (mc['student_id'], mc['class_id'], mc['start_date'], mc['end_date']))

        return jsonify({'ok': True, 'message': 'MC approved successfully'}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@attendance_bp.route('/medical-certificates/<int:mc_id>/reject', methods=['POST'])
def reject_medical_certificate(mc_id):
    """Reject a medical certificate"""
    try:
        data = request.get_json()
        notes = data.get('notes', '')

        # Update MC status
        db_utils.execute("""
            UPDATE medical_certificates
            SET status = 'rejected',
                reviewed_by = 1,
                review_notes = %s,
                reviewed_at = NOW()
            WHERE id = %s
        """, (notes, mc_id))

        return jsonify({'ok': True, 'message': 'MC rejected'}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@attendance_bp.route('/audit-log', methods=['GET'])
def get_audit_log():
    """Get audit log with filters"""
    try:
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        module_id = request.args.get('moduleId')
        change_type = request.args.get('changeType')
        admin_name = request.args.get('adminName')
        student_id = request.args.get('studentId')

        # Build query
        conditions = ["DATE(al.created_at) BETWEEN %s AND %s"]
        params = [start_date, end_date]

        if module_id:
            conditions.append("module_id = %s")
            params.append(module_id)

        if change_type:
            conditions.append("action = %s")
            params.append(change_type)

        if admin_name:
            conditions.append("admin_name LIKE %s")
            params.append(f"%{admin_name}%")

        if student_id:
            conditions.append("student_id LIKE %s")
            params.append(f"%{student_id}%")

        where_clause = " AND ".join(conditions)

        # Query audit logs with module name
        logs = db_utils.query_all(f"""
            SELECT
                al.*,
                m.module_code,
                m.module_name
            FROM audit_logs al
            LEFT JOIN modules m ON al.module_id = m.id
            WHERE {where_clause}
            ORDER BY al.created_at DESC
            LIMIT 1000
        """, tuple(params))

        # Format for frontend
        import json
        records = []
        for log in logs:
            old_values = json.loads(log['old_values']) if log['old_values'] else {}
            new_values = json.loads(log['new_values']) if log['new_values'] else {}

            records.append({
                'id': log['id'],
                'timestamp': log['created_at'].isoformat() if log['created_at'] else None,
                'adminName': log['admin_name'],
                'adminEmail': log['admin_email'],
                'studentId': log['student_id'],
                'studentName': log['student_name'],
                'moduleId': log['module_id'],
                'moduleName': f"{log['module_code']} - {log['module_name']}" if log['module_code'] else 'N/A',
                'lessonDate': log['lesson_date'].isoformat() if log['lesson_date'] else None,
                'changeType': log['action'],
                'previousValue': old_values.get('status', '--'),
                'newValue': new_values.get('status', '--'),
                'reason': new_values.get('reason', '')
            })

        return jsonify({'ok': True, 'records': records}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
