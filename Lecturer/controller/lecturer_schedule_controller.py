#!/usr/bin/env python3
"""
Lecturer Schedule Controller
Handles class schedule and timetable viewing
Corresponds to US16 (Class Schedule)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from common.db_utils import query_one, query_all

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

WEEK_ORDER = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")

def resolve_lecturer_id(lecturer_id: str = None, email: str = None) -> int:
    """Resolve lecturer DB numeric id from lecturer_id code or email."""
    if lecturer_id:
        row = query_one("SELECT id FROM lecturers WHERE lecturer_id = %s", (lecturer_id,))
        if row:
            return row['id']
    if email:
        row = query_one("SELECT id FROM lecturers WHERE email = %s", (email,))
        if row:
            return row['id']
    return 0


@app.route('/api/lecturer/schedule', methods=['GET'])
def get_schedule():
    """
    US16 - View Class Schedule (Sequence Diagram #16)
    Returns lecturer's class schedule
    """
    try:
        lecturer_code = request.args.get('lecturerId')  # e.g., 'LEC001'
        lecturer_db_id = request.args.get('lecturerNumericId')
        email = request.args.get('email')
        semester = request.args.get('semester', 'current')

        if lecturer_db_id:
            try:
                lecturer_db_id = int(lecturer_db_id)
            except Exception:
                lecturer_db_id = 0
        else:
            lecturer_db_id = resolve_lecturer_id(lecturer_code, email)

        if not lecturer_db_id:
            return jsonify({'success': False, 'message': 'Lecturer not found'}), 404

        rows = query_all(
            """
            SELECT c.module_code, c.module_name,
                   t.day_of_week AS day,
                   DATE_FORMAT(t.start_time, '%H:%i') AS start_time,
                   DATE_FORMAT(t.end_time, '%H:%i') AS end_time,
                   t.room
            FROM modules c
            JOIN timetable t ON t.module_id = c.id
            WHERE c.lecturer_id = %s AND IFNULL(t.is_active, 1) = 1
            ORDER BY FIELD(t.day_of_week, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'), t.start_time
            """,
            (lecturer_db_id,),
        )

        classes = [
            {
                'moduleCode': r['module_code'],
                'moduleName': r['module_name'],
                'day': r['day'],
                'startTime': r['start_time'],
                'endTime': r['end_time'],
                'room': r['room'],
            }
            for r in rows
        ]

        return jsonify({'success': True, 'modules': classes, 'lecturerId': lecturer_code or lecturer_db_id, 'semester': semester}), 200

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/schedule/today', methods=['GET'])
def get_today_schedule():
    """
    US16 - Get Today's Classes
    Returns classes scheduled for today
    """
    try:
        lecturer_code = request.args.get('lecturerId')
        email = request.args.get('email')
        lecturer_db_id = resolve_lecturer_id(lecturer_code, email)
        if not lecturer_db_id:
            return jsonify({'success': False, 'message': 'Lecturer not found'}), 404
        today = datetime.now().strftime('%A')
        rows = query_all(
            """
            SELECT c.module_code, c.module_name,
                   t.day_of_week AS day,
                   DATE_FORMAT(t.start_time, '%H:%i') AS start_time,
                   DATE_FORMAT(t.end_time, '%H:%i') AS end_time,
                   t.room
            FROM modules c
            JOIN timetable t ON t.module_id = c.id
            WHERE c.lecturer_id = %s AND t.day_of_week = %s AND IFNULL(t.is_active, 1) = 1
            ORDER BY t.start_time
            """,
            (lecturer_db_id, today),
        )
        today_classes = [
            {
                'moduleCode': r['module_code'],
                'moduleName': r['module_name'],
                'day': r['day'],
                'startTime': r['start_time'],
                'endTime': r['end_time'],
                'room': r['room'],
            }
            for r in rows
        ]

        return jsonify({'success': True, 'modules': today_classes, 'date': datetime.now().strftime('%Y-%m-%d'), 'day': today}), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/classes', methods=['GET'])
def get_classes():
    """
    Get list of classes for a lecturer (for dropdowns)
    """
    try:
        lecturer_id = request.args.get('lecturerId')
        email = request.args.get('email')

        if not lecturer_id and not email:
            return jsonify({
                'success': False,
                'message': 'lecturerId or email is required'
            }), 400

        # Resolve lecturer
        db_lecturer_id = resolve_lecturer_id(lecturer_id, email)
        if not db_lecturer_id:
            return jsonify({
                'success': False,
                'message': 'Lecturer not found'
            }), 404

        # Get all classes taught by this lecturer
        classes = query_all("""
            SELECT id, module_code, module_name, description
            FROM modules
            WHERE lecturer_id = %s AND is_active = 1
            ORDER BY module_code
        """, (db_lecturer_id,))

        return jsonify({
            'success': True,
            'modules': [
                {
                    'id': c['id'],
                    'module_code': c['module_code'],
                    'module_name': c['module_name'],
                    'description': c['description']
                }
                for c in classes
            ]
        }), 200

    except Exception as e:
        print(f"Error in get_classes: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("Lecturer Schedule Controller running on http://localhost:5006")
    print("Available endpoints:")
    print("  GET /api/lecturer/schedule")
    print("  GET /api/lecturer/schedule/today")
    print("  GET /api/lecturer/classes")
    app.run(host='0.0.0.0', port=5006, debug=True)
