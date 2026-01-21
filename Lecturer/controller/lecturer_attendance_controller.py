#!/usr/bin/env python3
"""
Lecturer Attendance Controller
Handles real-time attendance sessions and record management
Corresponds to US14 (Real-Time List), US18 (Filter Records)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import random

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from common.db_utils import query_all, query_one, execute

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Mock active sessions
active_sessions = {}

def resolve_lecturer_id(lecturer_id: str = None, email: str = None) -> int:
    if lecturer_id:
        row = query_one("SELECT id FROM lecturers WHERE lecturer_id = %s", (lecturer_id,))
        if row:
            return row['id']
    if email:
        row = query_one("SELECT id FROM lecturers WHERE email = %s", (email,))
        if row:
            return row['id']
    return 0


@app.route('/api/lecturer/session/start', methods=['POST'])
def start_session():
    """
    US14 - Start Attendance Session (Sequence Diagram #14)
    Initializes real-time attendance tracking
    """
    try:
        data = request.get_json()
        module_code = data.get('moduleCode', '')
        room = data.get('room', '')
        lecturer_id = data.get('lecturerId', 'LEC001')

        if not module_code:
            return jsonify({
                'success': False,
                'message': 'Class code is required'
            }), 400

        # Resolve class and lecturer ids
        cls = query_one("SELECT id FROM modules WHERE module_code = %s", (module_code,))
        lec = query_one("SELECT id FROM lecturers WHERE lecturer_id = %s", (lecturer_id,))
        if not cls or not lec:
            return jsonify({'success': False, 'message': 'Class or lecturer not found'}), 404

        # Insert attendance_session
        execute(
            """
            INSERT INTO attendance_sessions (module_id, lecturer_id, session_date, start_time, status, total_students)
            VALUES (%s, %s, CURDATE(), NOW(), 'ongoing',
                (SELECT COUNT(*) FROM student_enrollments se WHERE se.module_id = %s AND se.status = 'active'))
            """,
            (cls['id'], lec['id'], cls['id']),
        )
        # Fetch new session id
        sess = query_one(
            "SELECT id, total_students FROM attendance_sessions WHERE module_id = %s AND lecturer_id = %s ORDER BY id DESC LIMIT 1",
            (cls['id'], lec['id']),
        )

        # Create runtime tracker
        sid = str(sess['id'])
        active_sessions[sid] = {
            'sessionId': sid,
            'moduleCode': module_code,
            'room': room,
            'lecturerId': lecturer_id,
            'startTime': datetime.now().isoformat(),
            'status': 'active',
            'studentsDetected': [],
            'totalStudents': sess['total_students'],
        }

        return jsonify({'success': True, 'message': 'Session started successfully', 'session': active_sessions[sid]}), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/session/stop', methods=['POST'])
def stop_session():
    """
    US14 - Stop Attendance Session (Sequence Diagram #14)
    Ends real-time attendance tracking
    """
    try:
        data = request.get_json()
        session_id = data.get('sessionId', '')

        if session_id not in active_sessions:
            return jsonify({
                'success': False,
                'message': 'Session not found'
            }), 404

        # Update DB session status and counts
        sid_int = int(session_id)
        detected = active_sessions[session_id]['studentsDetected']
        present_count = len(detected)
        execute(
            "UPDATE attendance_sessions SET end_time = NOW(), status = 'completed', present_count = %s WHERE id = %s",
            (present_count, sid_int),
        )

        # Finalize runtime state
        active_sessions[session_id]['status'] = 'completed'
        active_sessions[session_id]['endTime'] = datetime.now().isoformat()

        return jsonify({
            'success': True,
            'message': 'Session stopped successfully',
            'session': active_sessions[session_id]
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/session/update', methods=['POST'])
def update_session():
    """
    US14 - Update Session with Detected Student (Sequence Diagram #14)
    Called when face recognition detects a student
    """
    try:
        data = request.get_json()
        session_id = data.get('sessionId', '')
        student = data.get('student', {})

        if session_id not in active_sessions:
            return jsonify({
                'success': False,
                'message': 'Session not found'
            }), 404

        # Add student to detected list
        detected_at = datetime.now()
        active_sessions[session_id]['studentsDetected'].append({
            'student_id': student.get('student_id'),
            'name': student.get('name'),
            'detected_at': detected_at.isoformat(),
            'confidence': student.get('confidence', random.uniform(85, 99))
        })

        # Persist attendance row
        module_code = active_sessions[session_id]['moduleCode']
        cls = query_one("SELECT id FROM modules WHERE module_code = %s", (module_code,))
        stu = query_one("SELECT id FROM students WHERE student_id = %s", (student.get('student_id'),))
        if cls and stu:
            execute(
                """
                INSERT INTO attendance (student_id, module_id, timetable_id, check_in_time, status, face_confidence)
                VALUES (%s, %s, NULL, %s, 'present', %s)
                """,
                (stu['id'], cls['id'], detected_at, float(active_sessions[session_id]['studentsDetected'][-1]['confidence'])),
            )

        return jsonify({
            'success': True,
            'message': 'Student attendance recorded',
            'session': active_sessions[session_id]
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/attendance/records', methods=['GET'])
def get_attendance_records():
    """
    US18 - Get All Attendance Records (Sequence Diagram #18)
    Returns all attendance records for the lecturer
    """
    try:
        lecturer_code = request.args.get('lecturerId')
        lecturer_email = request.args.get('email')
        lecturer_db_id = resolve_lecturer_id(lecturer_code, lecturer_email)
        if not lecturer_db_id:
            return jsonify({'success': False, 'message': 'Lecturer not found'}), 404

        rows = query_all(
            """
            SELECT DATE(a.check_in_time) AS date,
                   c.module_code,
                   s.student_id,
                   CONCAT(s.first_name, ' ', s.last_name) AS student_name,
                   a.status,
                   DATE_FORMAT(a.check_in_time, '%H:%i') AS time
            FROM attendance a
            JOIN modules c ON c.id = a.module_id
            JOIN students s ON s.id = a.student_id
            WHERE c.lecturer_id = %s
            ORDER BY a.check_in_time DESC
            LIMIT 500
            """,
            (lecturer_db_id,),
        )

        records = [
            {
                'date': r['date'].strftime('%Y-%m-%d') if hasattr(r['date'], 'strftime') else r['date'],
                'moduleCode': r['module_code'],
                'studentId': r['student_id'],
                'studentName': r['student_name'],
                'status': r['status'],
                'time': r['time'],
            }
            for r in rows
        ]

        return jsonify({'success': True, 'records': records}), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/attendance/filter', methods=['POST'])
def filter_records():
    """
    US18 - Filter Attendance Records (Sequence Diagram #18)
    Filters records based on criteria
    """
    try:
        data = request.get_json()
        module_code = data.get('moduleCode', '')
        student_id = data.get('studentId', '')
        status = data.get('status', '')
        date_range = data.get('dateRange', {})
        single_date = data.get('date', '')  # Support single date filter
        lecturer_code = data.get('lecturerId')
        lecturer_email = data.get('email')
        lecturer_db_id = resolve_lecturer_id(lecturer_code, lecturer_email)
        if not lecturer_db_id:
            return jsonify({'success': False, 'message': 'Lecturer not found'}), 404

        conditions = ["c.lecturer_id = %s"]
        params = [lecturer_db_id]
        if module_code:
            conditions.append("c.module_code = %s")
            params.append(module_code)
        if student_id:
            conditions.append("s.student_id LIKE %s")
            params.append(f"%{student_id}%")
        if status:
            conditions.append("a.status = %s")
            params.append(status)
        # Handle single date (exact match)
        if single_date:
            conditions.append("DATE(a.check_in_time) = %s")
            params.append(single_date)
        # Handle date range
        if date_range.get('start'):
            conditions.append("DATE(a.check_in_time) >= %s")
            params.append(date_range['start'])
        if date_range.get('end'):
            conditions.append("DATE(a.check_in_time) <= %s")
            params.append(date_range['end'])

        where_clause = " AND ".join(conditions)

        rows = query_all(
            f"""
            SELECT DATE(a.check_in_time) AS date,
                   c.module_code,
                   s.student_id,
                   CONCAT(s.first_name, ' ', s.last_name) AS student_name,
                   a.status,
                   DATE_FORMAT(a.check_in_time, '%H:%i') AS time
            FROM attendance a
            JOIN modules c ON c.id = a.module_id
            JOIN students s ON s.id = a.student_id
            WHERE {where_clause}
            ORDER BY a.check_in_time DESC
            LIMIT 500
            """,
            tuple(params),
        )

        records = [
            {
                'date': r['date'].strftime('%Y-%m-%d') if hasattr(r['date'], 'strftime') else r['date'],
                'moduleCode': r['module_code'],
                'studentId': r['student_id'],
                'studentName': r['student_name'],
                'status': r['status'],
                'time': r['time'],
            }
            for r in rows
        ]

        return jsonify({'success': True, 'records': records}), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/attendance/update-status', methods=['POST'])
def update_attendance_status():
    """
    Update attendance status for a specific student record
    Allows changing status between present, absent, and late
    """
    try:
        data = request.get_json()
        student_id = data.get('studentId')
        module_code = data.get('moduleCode')
        date = data.get('date')
        new_status = data.get('newStatus')
        lecturer_code = data.get('lecturerId')
        
        if not all([student_id, module_code, date, new_status]):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
        
        # Validate status
        if new_status not in ['present', 'absent', 'late']:
            return jsonify({
                'success': False,
                'message': 'Invalid status value'
            }), 400
        
        # Verify lecturer has permission for this class
        lecturer_db_id = resolve_lecturer_id(lecturer_code)
        if not lecturer_db_id:
            return jsonify({'success': False, 'message': 'Lecturer not found'}), 404
        
        # Get student and class IDs
        student = query_one("SELECT id FROM students WHERE student_id = %s", (student_id,))
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'}), 404
        
        class_info = query_one(
            "SELECT id FROM modules WHERE module_code = %s AND lecturer_id = %s",
            (module_code, lecturer_db_id)
        )
        if not class_info:
            return jsonify({'success': False, 'message': 'Class not found or unauthorized'}), 403
        
        # Update attendance record - ONLY update status, keep original check_in_time
        result = execute(
            """UPDATE attendance 
               SET status = %s
               WHERE student_id = %s 
               AND module_id = %s 
               AND DATE(check_in_time) = %s""",
            (new_status, student['id'], class_info['id'], date)
        )
        
        if result == 0:
            # No existing record, create one with the specified date
            execute(
                """INSERT INTO attendance (student_id, module_id, status, check_in_time)
                   VALUES (%s, %s, %s, %s)""",
                (student['id'], class_info['id'], new_status, f"{date} 09:00:00")
            )
        
        return jsonify({
            'success': True,
            'message': 'Status updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """
    Get dashboard statistics for lecturer
    Returns total classes, today's classes, average attendance, and active sessions
    """
    try:
        lecturer_id = request.args.get('lecturerId', 'LEC001')
        lecturer_db_id = resolve_lecturer_id(lecturer_id)
        
        if not lecturer_db_id:
            return jsonify({'success': False, 'message': 'Lecturer not found'}), 404
        
        # Get total classes for this lecturer
        total_classes = query_one(
            "SELECT COUNT(*) as count FROM modules WHERE lecturer_id = %s AND is_active = TRUE",
            (lecturer_db_id,)
        )
        
        # Get today's classes
        today_classes = query_one(
            """SELECT COUNT(*) as count FROM modules c
               JOIN timetable t ON t.module_id = c.id
               WHERE c.lecturer_id = %s AND c.is_active = TRUE
               AND t.day_of_week = DAYNAME(CURDATE())""",
            (lecturer_db_id,)
        )
        
        # Get average attendance percentage across all lecturer's classes
        # Calculate: For each session, what percentage attended? Then average those percentages.
        avg_attendance = query_one(
            """SELECT AVG(session_attendance_rate) as avg_rate
               FROM (
                   SELECT
                       (COUNT(CASE WHEN a.status IN ('present', 'late') THEN 1 END) * 100.0) /
                       NULLIF((SELECT COUNT(*) FROM student_enrollments se
                               WHERE se.module_id = a.module_id AND se.status = 'active'), 0) as session_attendance_rate
                   FROM attendance a
                   JOIN modules c ON a.module_id = c.id
                   LEFT JOIN timetable t ON a.timetable_id = t.id
                   WHERE c.lecturer_id = %s AND c.is_active = TRUE
                   GROUP BY a.module_id, DATE(COALESCE(t.class_date, a.check_in_time))
                   HAVING COUNT(*) > 0
               ) as session_rates""",
            (lecturer_db_id,)
        )
        
        # Get active sessions count
        active_sessions_count = query_one(
            "SELECT COUNT(*) as count FROM attendance_sessions WHERE lecturer_id = %s AND status = 'ongoing'",
            (lecturer_db_id,)
        )
        
        return jsonify({
            'success': True,
            'stats': {
                'totalClasses': int(total_classes['count'] or 0),
                'todayClasses': int(today_classes['count'] or 0),
                'avgAttendance': float(round(float(avg_attendance['avg_rate'] or 0), 1)),
                'activeSessions': int(active_sessions_count['count'] or 0)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("Lecturer Attendance Controller running on http://localhost:5004")
    print("Available endpoints:")
    print("  POST /api/lecturer/session/start")
    print("  POST /api/lecturer/session/stop")
    print("  POST /api/lecturer/session/update")
    print("  GET  /api/lecturer/attendance/records")
    print("  POST /api/lecturer/attendance/filter")
    print("  GET  /api/lecturer/dashboard/stats")
    app.run(host='0.0.0.0', port=5004, debug=True)
