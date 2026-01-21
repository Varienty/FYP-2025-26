#!/usr/bin/env python3
"""
Lecturer Notification Controller
Handles notification subscription and delivery
Corresponds to US17 (Notification System)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from common.db_utils import query_all, execute, query_one

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True, allow_headers=["Content-Type", "Authorization"])

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


@app.route('/api/lecturer/notification/subscribe', methods=['POST'])
def subscribe():
    """
    US17 - Subscribe to Notifications (Sequence Diagram #17)
    Subscribes lecturer to session notifications
    """
    try:
        data = request.get_json()
        lecturer_code = data.get('lecturerId')
        email = data.get('email')
        lecturer_db_id = resolve_lecturer_id(lecturer_code, email)
        if not lecturer_db_id:
            return jsonify({'success': False, 'message': 'Lecturer not found'}), 404

        # No subscription table in schema; acknowledge subscription in response
        return jsonify({'success': True, 'message': 'Subscribed to notifications', 'subscription': {
            'lecturerId': lecturer_code or lecturer_db_id,
            'subscribedAt': datetime.now().isoformat(),
            'active': True
        }}), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/notification/unsubscribe', methods=['POST'])
def unsubscribe():
    """
    US17 - Unsubscribe from Notifications
    Unsubscribes lecturer from notifications
    """
    try:
        data = request.get_json()
        return jsonify({'success': True, 'message': 'Unsubscribed successfully'}), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/notifications', methods=['GET'])
def get_notifications():
    """
    US17 - Get Notification History
    Returns all notifications for the lecturer
    """
    try:
        lecturer_code = request.args.get('lecturerId')
        email = request.args.get('email')
        
        lecturer_db_id = resolve_lecturer_id(lecturer_code, email)
        
        if not lecturer_db_id:
            return jsonify({'success': False, 'message': 'Lecturer not found'}), 404

        rows = query_all(
            """
            SELECT id, notification_type, title, message, is_read, created_at
            FROM notifications
            WHERE recipient_type = 'lecturer' AND recipient_id = %s
            ORDER BY created_at DESC
            LIMIT 200
            """,
            (lecturer_db_id,),
        )

        notifications = [
            {
                'notificationId': r['id'],
                'type': r['notification_type'],
                'title': r['title'],
                'message': r['message'],
                'timestamp': r['created_at'].isoformat() if hasattr(r['created_at'], 'isoformat') else str(r['created_at']),
                'read': bool(r['is_read']),
            }
            for r in rows
        ]

        return jsonify({'success': True, 'notifications': notifications}), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/notification/send', methods=['POST'])
def send_notification():
    """
    US17 - Send Notification (Internal use)
    Sends a notification to subscribed lecturer
    """
    try:
        data = request.get_json()
        lecturer_code = data.get('lecturerId')
        email = data.get('email')
        lecturer_db_id = resolve_lecturer_id(lecturer_code, email)
        if not lecturer_db_id:
            return jsonify({'success': False, 'message': 'Lecturer not found'}), 404

        notification_type = data.get('type', 'info')
        message = data.get('message', '')
        title = data.get('title', notification_type.title())

        execute(
            """
            INSERT INTO notifications (recipient_type, recipient_id, notification_type, title, message)
            VALUES ('lecturer', %s, %s, %s, %s)
            """,
            (lecturer_db_id, notification_type, title, message),
        )

        return jsonify({'success': True, 'notification': {
            'type': notification_type,
            'title': title,
            'message': message,
            'timestamp': datetime.now().isoformat(),
        }}), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/notification/mark-read', methods=['POST'])
def mark_read():
    """
    US17 - Mark Notification as Read
    Updates notification read status
    """
    try:
        data = request.get_json()
        notification_id = data.get('notificationId')
        if not notification_id:
            return jsonify({'success': False, 'message': 'Notification ID required'}), 400
        updated = execute(
            "UPDATE notifications SET is_read = 1, read_at = NOW() WHERE id = %s",
            (notification_id,),
        )
        if updated:
            return jsonify({'success': True, 'message': 'Notification marked as read'}), 200
        return jsonify({'success': False, 'message': 'Notification not found'}), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("Lecturer Notification Controller running on http://localhost:5007")
    print("Available endpoints:")
    print("  POST /api/lecturer/notification/subscribe")
    print("  POST /api/lecturer/notification/unsubscribe")
    print("  GET  /api/lecturer/notifications")
    print("  POST /api/lecturer/notification/send")
    print("  POST /api/lecturer/notification/mark-read")
    app.run(host='0.0.0.0', port=5007, debug=True)
