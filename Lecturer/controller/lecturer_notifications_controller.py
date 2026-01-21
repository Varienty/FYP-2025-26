#!/usr/bin/env python3
"""
Lecturer Notifications Controller
Handles notification management for lecturers
Port: 5007
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from common.db_utils import query_all, query_one, execute

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)


@app.route('/api/lecturer/notifications', methods=['GET'])
def get_notifications():
    """
    Get all notifications for a lecturer
    Query params: lecturerId (e.g., LEC001)
    """
    try:
        lecturer_id = request.args.get('lecturerId')

        if not lecturer_id:
            return jsonify({
                'success': False,
                'message': 'lecturerId is required'
            }), 400

        # Convert lecturer_id (LEC001) to database ID
        lecturer = query_one(
            "SELECT id FROM lecturers WHERE lecturer_id = %s",
            (lecturer_id,)
        )

        if not lecturer:
            return jsonify({
                'success': False,
                'message': 'Lecturer not found'
            }), 404

        lecturer_db_id = lecturer['id']

        # Fetch notifications from database using database ID
        notifications = query_all(
            """
            SELECT id, recipient_type, recipient_id, notification_type as type,
                   title, message, related_table, related_id, is_read as `read`,
                   created_at, read_at
            FROM notifications
            WHERE recipient_type = 'lecturer' AND recipient_id = %s
            ORDER BY created_at DESC
            LIMIT 100
            """,
            (lecturer_db_id,)
        )

        # Convert datetime objects to strings
        result = []
        for notif in notifications:
            result.append({
                'id': notif['id'],
                'type': notif['type'],
                'title': notif['title'],
                'message': notif['message'],
                'read': bool(notif['read']),
                'timestamp': notif['created_at'].isoformat() if notif['created_at'] else None,
                'created_at': notif['created_at'].isoformat() if notif['created_at'] else None
            })

        return jsonify({
            'success': True,
            'notifications': result
        }), 200

    except Exception as e:
        print(f"Error fetching notifications: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/notification/mark-read', methods=['POST'])
def mark_all_read():
    """
    Mark all notifications as read for a lecturer
    Body: { "lecturerId": "LEC001" }
    """
    try:
        data = request.get_json()
        lecturer_id = data.get('lecturerId')

        if not lecturer_id:
            return jsonify({
                'success': False,
                'message': 'lecturerId is required'
            }), 400

        # Convert lecturer_id to database ID
        lecturer = query_one(
            "SELECT id FROM lecturers WHERE lecturer_id = %s",
            (lecturer_id,)
        )

        if not lecturer:
            return jsonify({
                'success': False,
                'message': 'Lecturer not found'
            }), 404

        # Update all notifications to mark as read
        execute(
            """
            UPDATE notifications
            SET is_read = 1, read_at = NOW()
            WHERE recipient_type = 'lecturer' AND recipient_id = %s AND is_read = 0
            """,
            (lecturer['id'],)
        )

        return jsonify({
            'success': True,
            'message': 'All notifications marked as read'
        }), 200

    except Exception as e:
        print(f"Error marking notifications as read: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/notifications/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """
    Delete a specific notification
    """
    try:
        # Delete the notification
        result = execute(
            "DELETE FROM notifications WHERE id = %s",
            (notification_id,)
        )

        if result > 0:
            return jsonify({
                'success': True,
                'message': 'Notification deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Notification not found'
            }), 404

    except Exception as e:
        print(f"Error deleting notification: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/notifications/clear-all', methods=['DELETE'])
def clear_all_notifications():
    """
    Clear all notifications for a lecturer
    Body: { "lecturerId": "LEC001" }
    """
    try:
        data = request.get_json()
        lecturer_id = data.get('lecturerId')

        if not lecturer_id:
            return jsonify({
                'success': False,
                'message': 'lecturerId is required'
            }), 400

        # Convert lecturer_id to database ID
        lecturer = query_one(
            "SELECT id FROM lecturers WHERE lecturer_id = %s",
            (lecturer_id,)
        )

        if not lecturer:
            return jsonify({
                'success': False,
                'message': 'Lecturer not found'
            }), 404

        # Delete all notifications for this lecturer
        result = execute(
            """
            DELETE FROM notifications
            WHERE recipient_type = 'lecturer' AND recipient_id = %s
            """,
            (lecturer['id'],)
        )

        return jsonify({
            'success': True,
            'message': f'Cleared {result} notifications',
            'count': result
        }), 200

    except Exception as e:
        print(f"Error clearing notifications: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/notifications/generate-class-reminders', methods=['POST'])
def generate_class_reminders():
    """
    Generate notifications for classes starting soon
    Checks timetable and creates notifications for classes starting within the next 15 minutes
    """
    try:
        from datetime import datetime, timedelta, date as dt_date

        now = datetime.now()
        current_time = now.time()
        current_date = now.date()
        current_day = current_date.strftime('%A')  # Monday, Tuesday, etc.

        # Query timetable for classes happening NOW or starting soon (within next 30 min)
        # This catches both ongoing classes and upcoming classes
        upcoming_classes = query_all(
            """
            SELECT
                t.id as timetable_id,
                t.start_time,
                t.end_time,
                t.room,
                t.day_of_week,
                m.id as module_id,
                m.module_code,
                m.module_name,
                l.id as lecturer_db_id,
                l.lecturer_id,
                l.first_name,
                l.last_name
            FROM timetable t
            JOIN modules m ON t.module_id = m.id
            JOIN lecturers l ON m.lecturer_id = l.id
            WHERE t.day_of_week = %s
              AND (
                  -- Class is currently in session
                  (t.start_time <= %s AND t.end_time >= %s)
                  OR
                  -- Class starts within next 30 minutes
                  (t.start_time > %s AND t.start_time <= ADDTIME(%s, '00:30:00'))
              )
              AND IFNULL(t.is_active, 1) = 1
            """,
            (current_day, current_time, current_time, current_time, current_time)
        )

        notifications_created = 0

        for cls in upcoming_classes:
            # Check if notification already exists for this class today
            existing = query_one(
                """
                SELECT id FROM notifications
                WHERE recipient_type = 'lecturer'
                  AND recipient_id = %s
                  AND notification_type = 'class_starting'
                  AND related_table = 'timetable'
                  AND related_id = %s
                  AND DATE(created_at) = %s
                """,
                (cls['lecturer_db_id'], cls['timetable_id'], current_date)
            )

            if not existing:
                # Format start_time (handle both time and timedelta objects from database)
                start_time = cls['start_time']
                if isinstance(start_time, timedelta):
                    # Convert timedelta to time string
                    total_seconds = int(start_time.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    time_str = f"{hours:02d}:{minutes:02d}"
                else:
                    # It's a time object
                    time_str = start_time.strftime('%H:%M')

                # Check if class has already started or is upcoming
                # Convert times to comparable format (seconds since midnight)
                def time_to_seconds(t):
                    if isinstance(t, timedelta):
                        return int(t.total_seconds())
                    else:  # time object
                        return t.hour * 3600 + t.minute * 60 + t.second

                current_seconds = time_to_seconds(current_time)
                start_seconds = time_to_seconds(cls['start_time'])
                end_seconds = time_to_seconds(cls['end_time'])

                if start_seconds <= current_seconds <= end_seconds:
                    # Class is currently in session
                    title = f"Class In Session: {cls['module_code']}"
                    message = f"{cls['module_name']} is now in session in {cls['room']}"
                else:
                    # Class starting soon
                    title = f"Class Starting Soon: {cls['module_code']}"
                    message = f"{cls['module_name']} starts at {time_str} in {cls['room']}"

                execute(
                    """
                    INSERT INTO notifications
                    (recipient_type, recipient_id, notification_type, title, message,
                     related_table, related_id, is_read, created_at)
                    VALUES ('lecturer', %s, 'class_starting', %s, %s, 'timetable', %s, 0, NOW())
                    """,
                    (cls['lecturer_db_id'], title, message, cls['timetable_id'])
                )
                notifications_created += 1

        return jsonify({
            'success': True,
            'message': f'Generated {notifications_created} class reminder(s)',
            'count': notifications_created
        }), 200

    except Exception as e:
        print(f"Error generating class reminders: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("Lecturer Notifications Controller running on http://localhost:5007")
    print("Available endpoints:")
    print("  GET    /api/lecturer/notifications?lecturerId=LEC001")
    print("  POST   /api/lecturer/notification/mark-read")
    print("  POST   /api/lecturer/notifications/generate-class-reminders")
    print("  DELETE /api/lecturer/notifications/{id}")
    print("  DELETE /api/lecturer/notifications/clear-all")
    app.run(host='0.0.0.0', port=5007, debug=True)
