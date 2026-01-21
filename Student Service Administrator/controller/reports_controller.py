"""
Student Service Administrator - Reports Controller
Handles compliance reports, audit logs, and student history reports.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from common import db_utils

reports_bp = Blueprint('ssa_reports', __name__, url_prefix='/api')

@reports_bp.route('/audit-log', methods=['GET'])
def get_audit_log():
    """Get audit log of manual attendance edits from database"""
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    edit_type = request.args.get('type')
    editor = request.args.get('editor')
    
    # Query audit_logs table with student information
    # JOIN through attendance table to get student info
    query = """SELECT al.id, al.created_at as timestamp, 
               al.user_type as editor, al.action as changeType,
               s.student_id, CONCAT(s.first_name, ' ', s.last_name) as studentName,
               al.old_values as previousValue, al.new_values as newValue,
               al.record_id
               FROM audit_logs al
               LEFT JOIN attendance a ON al.record_id = a.id AND al.table_name = 'attendance'
               LEFT JOIN students s ON a.student_id = s.id
               WHERE al.action LIKE '%attendance%'"""
    
    params = []
    
    if start_date:
        query += " AND DATE(al.created_at) >= %s"
        params.append(start_date)
    if end_date:
        query += " AND DATE(al.created_at) <= %s"
        params.append(end_date)
    if editor:
        query += " AND al.user_type LIKE %s"
        params.append(f'%{editor}%')
    
    query += " ORDER BY al.created_at DESC LIMIT 200"
    
    records = db_utils.query_all(query, tuple(params) if params else ())
    
    result = []
    for r in records:
        # Parse JSON values
        import json
        try:
            old_values = json.loads(r['previousValue']) if r['previousValue'] else {}
            new_values = json.loads(r['newValue']) if r['newValue'] else {}
        except:
            old_values = {}
            new_values = {}
        
        # Extract reason and notes
        reason = new_values.get('reason', 'Manual edit')
        notes = new_values.get('notes', '')
        
        # Determine change type based on what changed
        change_type = 'status_change'
        if 'status' in old_values and 'status' in new_values:
            change_type = 'status_change'
        elif 'reason' in new_values:
            change_type = 'remarks_added'
        
        result.append({
            'id': r['id'],
            'timestamp': r['timestamp'].isoformat() if r['timestamp'] else None,
            'editor': r['editor'] or 'system',
            'studentId': r['student_id'] or 'Unknown',
            'studentName': r['studentName'] or 'Unknown',
            'changeType': change_type,
            'previousValue': old_values.get('status', ''),
            'newValue': new_values.get('status', ''),
            'reason': f"{reason} {notes}".strip()
        })
    
    return jsonify({'ok': True, 'records': result}), 200

@reports_bp.route('/compliance/report', methods=['GET'])
def compliance_report():
    """Generate compliance report for students below threshold from database"""
    threshold = int(request.args.get('threshold', 75))
    module_id = request.args.get('module_id')
    academic_year = request.args.get('academic_year')
    intake = request.args.get('intake')

    # Base query to get students with attendance below threshold
    # Total classes = ALL timetable entries
    # Attendance % calculated based on past classes only (starts at 100%, drops when missed)
    query = """SELECT s.student_id as id,
               CONCAT(s.first_name, ' ', s.last_name) as name,
               m.module_code, m.module_name,
               s.intake_period, s.academic_year,
               COUNT(DISTINCT CASE WHEN a.status = 'present' THEN a.id END) as classesAttended,
               COUNT(DISTINCT CASE WHEN a.status IN ('absent', 'late') THEN a.id END) as classesMissed,
               COUNT(DISTINCT t.id) as totalClasses,
               CASE
                   WHEN COUNT(DISTINCT CASE WHEN t.class_date <= CURDATE() THEN t.id END) = 0 THEN 100.0
                   ELSE ROUND(COUNT(DISTINCT CASE WHEN a.status = 'present' THEN a.id END) * 100.0 / NULLIF(COUNT(DISTINCT CASE WHEN t.class_date <= CURDATE() THEN t.id END), 0), 1)
               END as attendance
               FROM students s"""

    params = []

    # If filtering by module, join with student_enrollments and attendance for that module
    if module_id:
        query += """
               INNER JOIN student_enrollments se ON s.id = se.student_id
               INNER JOIN modules m ON se.module_id = m.id
               LEFT JOIN timetable t ON m.id = t.module_id AND t.is_active = 1
               LEFT JOIN attendance a ON s.id = a.student_id AND a.timetable_id = t.id
               WHERE s.is_active = TRUE AND m.id = %s"""
        params.append(module_id)
    else:
        # No module filter - get overall attendance across all enrolled modules
        query += """
               INNER JOIN student_enrollments se ON s.id = se.student_id
               INNER JOIN modules m ON se.module_id = m.id
               LEFT JOIN timetable t ON m.id = t.module_id AND t.is_active = 1
               LEFT JOIN attendance a ON s.id = a.student_id AND a.timetable_id = t.id
               WHERE s.is_active = TRUE"""

    # Add academic year filter
    if academic_year:
        query += " AND s.academic_year = %s"
        params.append(academic_year)

    # Add intake filter
    if intake:
        query += " AND s.intake_period = %s"
        params.append(intake)

    # Group by student
    if module_id:
        query += """ GROUP BY s.id, s.student_id, s.first_name, s.last_name,
                    m.module_code, m.module_name, s.intake_period, s.academic_year"""
    else:
        query += """ GROUP BY s.id, s.student_id, s.first_name, s.last_name,
                    s.intake_period, s.academic_year"""

    # Filter by threshold
    query += """ HAVING attendance < %s OR attendance IS NULL"""
    params.append(threshold)

    query += " ORDER BY attendance ASC LIMIT 100"

    students_data = db_utils.query_all(query, tuple(params))

    students = []
    for s in students_data:
        attendance = s['attendance'] or 0
        severity_level = 'critical' if attendance < 60 else ('warning' if attendance < threshold else 'ok')

        # Build module info
        if module_id and s.get('module_code'):
            department = f"{s['module_code']} - {s['module_name']}"
        else:
            department = 'Overall'

        students.append({
            'id': s['id'],
            'name': s['name'],
            'department': department,
            'attendance': float(attendance),
            'classesAttended': s['classesAttended'] or 0,
            'classesMissed': s['classesMissed'] or 0,
            'totalClasses': s['totalClasses'] or 0,
            'severity': severity_level,
            'intake_period': s.get('intake_period'),
            'academic_year': s.get('academic_year')
        })

    return jsonify({'ok': True, 'students': students}), 200

@reports_bp.route('/student/history', methods=['GET'])
def student_history():
    """Get individual student attendance history from database"""
    search_term = request.args.get('search')
    year = request.args.get('year')
    semester = request.args.get('semester')
    
    if not search_term:
        return jsonify({'ok': False, 'message': 'Search term required'}), 400
    
    # Get student data - search by ID, email, or partial name
    student = db_utils.query_one(
        """SELECT student_id as id, CONCAT(first_name, ' ', last_name) as name,
           email, program as department
           FROM students
           WHERE student_id LIKE %s OR email LIKE %s OR 
                 CONCAT(first_name, ' ', last_name) LIKE %s
           LIMIT 1""",
        (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
    )
    
    if not student:
        return jsonify({'ok': False, 'message': 'No students found in database'}), 404
    
    # Build filter conditions
    filter_conditions = []
    filter_params = [student['id']]
    
    if year:
        filter_conditions.append("c.academic_year = %s")
        filter_params.append(year)
    
    if semester:
        filter_conditions.append("c.semester = %s")
        filter_params.append(semester)
    
    filter_clause = " AND " + " AND ".join(filter_conditions) if filter_conditions else ""
    
    # Get attendance statistics
    stats_query = """SELECT 
           COUNT(DISTINCT a.module_id) as courseCount,
           COUNT(CASE WHEN a.status = 'present' THEN 1 END) as totalAttended,
           COUNT(CASE WHEN a.status = 'absent' THEN 1 END) as totalMissed,
           COUNT(CASE WHEN a.status = 'late' THEN 1 END) as totalLate,
           ROUND(COUNT(CASE WHEN a.status = 'present' THEN 1 END) * 100.0 / NULLIF(COUNT(a.id), 0), 1) as overallAttendance
           FROM students s
           LEFT JOIN attendance a ON s.id = a.student_id
           LEFT JOIN modules c ON a.module_id = c.id
           WHERE s.student_id = %s""" + filter_clause
    
    stats = db_utils.query_one(stats_query, tuple(filter_params))
    
    # Get course-wise stats - total = ALL timetable entries, attendance % based on past classes only
    course_stats_query = """SELECT c.module_code as code, c.module_name as name,
           COUNT(DISTINCT CASE WHEN a.status = 'present' THEN a.id END) as attended,
           COUNT(DISTINCT t.id) as total,
           COUNT(DISTINCT CASE WHEN a.status = 'late' THEN a.id END) as late,
           CASE
               WHEN COUNT(DISTINCT CASE WHEN t.class_date <= CURDATE() THEN t.id END) = 0 THEN 100.0
               ELSE ROUND(COUNT(DISTINCT CASE WHEN a.status = 'present' THEN a.id END) * 100.0 / NULLIF(COUNT(DISTINCT CASE WHEN t.class_date <= CURDATE() THEN t.id END), 0), 1)
           END as attendance
           FROM students s
           JOIN student_enrollments se ON s.id = se.student_id
           JOIN modules c ON se.module_id = c.id
           LEFT JOIN timetable t ON c.id = t.module_id AND t.is_active = 1
           LEFT JOIN attendance a ON s.id = a.student_id AND a.timetable_id = t.id
           WHERE s.student_id = %s""" + filter_clause + """
           GROUP BY c.id, c.module_code, c.module_name
           ORDER BY c.module_code"""
    
    course_stats = db_utils.query_all(course_stats_query, tuple(filter_params))

    # Debug: Print the query and results
    import sys
    print("=" * 80, file=sys.stderr)
    print(f"STUDENT HISTORY DEBUG for {search_term}", file=sys.stderr)
    print(f"Query: {course_stats_query}", file=sys.stderr)
    print(f"Params: {tuple(filter_params)}", file=sys.stderr)
    print(f"Results: {course_stats}", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    sys.stderr.flush()

    history = {
        'courseCount': stats['courseCount'] or 0,
        'totalAttended': stats['totalAttended'] or 0,
        'totalMissed': stats['totalMissed'] or 0,
        'totalLate': stats['totalLate'] or 0,
        'overallAttendance': float(stats['overallAttendance'] or 0),
        'courseStats': [
            {
                'code': c['code'],
                'name': c['name'],
                'attended': c['attended'] or 0,
                'total': c['total'] or 0,
                'late': c['late'] or 0,
                'attendance': float(c['attendance']) if c.get('attendance') is not None else 100.0
            }
            for c in course_stats
        ],
        'dailyRecords': [],
        'trend': [
            {'month': 'Aug', 'rate': 85},
            {'month': 'Sep', 'rate': 87},
            {'month': 'Oct', 'rate': 89},
            {'month': 'Nov', 'rate': 88}
        ]
    }
    
    return jsonify({'ok': True, 'student': student, 'history': history}), 200

@reports_bp.route('/class-list/upload', methods=['POST'])
def upload_class_list():
    """Upload class list file"""
    if 'file' not in request.files:
        return jsonify({'ok': False, 'message': 'No file uploaded'}), 400
    
    file = request.files['file']
    module_name = request.form.get('class')
    
    # Demo response
    return jsonify({
        'ok': True,
        'message': 'Class list uploaded successfully',
        'totalStudents': 35,
        'successful': 35,
        'failed': 0
    }), 200

@reports_bp.route('/class-list/upload-photos', methods=['POST'])
def upload_class_photos():
    """Upload student photos for face recognition"""
    if 'photos' not in request.files:
        return jsonify({'ok': False, 'message': 'No photos uploaded'}), 400
    
    files = request.files.getlist('photos')
    
    return jsonify({
        'ok': True,
        'message': f'{len(files)} photos uploaded successfully',
        'count': len(files)
    }), 200
