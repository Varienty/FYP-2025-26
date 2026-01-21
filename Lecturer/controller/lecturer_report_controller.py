#!/usr/bin/env python3
"""
Lecturer Report Controller
Handles attendance report generation and downloading
Corresponds to US15 (Attendance Report)
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
from datetime import datetime, timedelta
import io

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from common.db_utils import query_all, query_one, execute

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)


@app.route('/api/lecturer/report/generate', methods=['POST'])
def generate_report():
    """
    US15 - Generate Attendance Report (Sequence Diagram #15)
    Creates attendance report based on parameters
    """
    try:
        data = request.get_json()
        module_code = data.get('moduleId', '')
        date_range = data.get('dateRange', {})
        metrics = data.get('metrics', 'summary')
        lecturer_code = data.get('lecturerId')
        email = data.get('email')

        if not module_code:
            return jsonify({
                'success': False,
                'message': 'Class ID is required'
            }), 400
        # Resolve class by code and ensure lecturer owns it if provided
        cls = query_one("SELECT id, module_name FROM modules WHERE module_code = %s", (module_code,))
        if not cls:
            return jsonify({'success': False, 'message': 'Class not found'}), 404
        module_id = cls['id']
        print(f"Class ID resolved: {module_id} ({cls['module_name']})")

        # Build filters
        conditions = ["a.module_id = %s"]
        params = [module_id]
        if date_range.get('start'):
            conditions.append("DATE(a.check_in_time) >= %s")
            params.append(date_range['start'])
        if date_range.get('end'):
            conditions.append("DATE(a.check_in_time) <= %s")
            params.append(date_range['end'])
        where_clause = " AND ".join(conditions)

        # Aggregate per student
        query_sql = f"""
            SELECT s.student_id AS id,
                   CONCAT(s.first_name, ' ', s.last_name) AS name,
                   SUM(a.status = 'present') AS present,
                   SUM(a.status = 'absent') AS absent,
                   SUM(a.status = 'late') AS late
            FROM attendance a
            JOIN students s ON s.id = a.student_id
            WHERE {where_clause}
            GROUP BY s.id
            ORDER BY s.student_id
            """
        rows = query_all(query_sql, tuple(params))

        students = [
            {
                'id': r['id'],
                'name': r['name'],
                'present': int(r['present'] or 0),
                'absent': int(r['absent'] or 0),
                'late': int(r['late'] or 0),
            }
            for r in rows
        ]

        total_sessions = sum(s['present'] + s['absent'] + s['late'] for s in students) // max(len(students), 1)
        total_present = sum(s['present'] for s in students)
        total_attendance = (total_present / max((len(students) * max(total_sessions, 1)), 1)) * 100

        report = {
            'moduleId': module_code,
            'dateRange': date_range,
            'totalSessions': total_sessions,
            'students': students,
            'avgAttendance': round(total_attendance, 1),
            'generatedAt': datetime.now().isoformat()
        }

        # Persist report metadata
        execute(
            """
            INSERT INTO reports (report_type, report_name, generated_by_type, generated_by_id, filters, file_format, status)
            VALUES ('attendance', %s, 'lecturer', COALESCE((SELECT id FROM lecturers WHERE lecturer_id = %s), (SELECT id FROM lecturers WHERE email = %s)), %s, 'csv', 'completed')
            """,
            (f"Attendance Report - {module_code}", lecturer_code, email, json.dumps({'moduleId': module_code, 'dateRange': date_range})),
        )

        return jsonify({
            'success': True,
            'report': report
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/report/download', methods=['POST'])
def download_report():
    """
    US15 - Download Report (Sequence Diagram #15)
    Generates downloadable file (PDF or CSV)
    """
    try:
        data = request.get_json()
        report_data = data.get('reportData', {})
        file_format = data.get('format', 'csv')

        if not report_data:
            return jsonify({'success': False, 'message': 'Report data is required'}), 400

        if file_format == 'csv':
            # Generate CSV
            csv_content = 'Student ID,Name,Present,Absent,Late,Attendance %\n'
            for student in report_data.get('students', []):
                total = student['present'] + student['absent'] + student['late']
                percentage = (student['present'] / total * 100) if total > 0 else 0
                csv_content += f"{student['id']},{student['name']},{student['present']},{student['absent']},{student['late']},{percentage:.1f}%\n"

            # Return CSV as file
            return send_file(
                io.BytesIO(csv_content.encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f"attendance_report_{datetime.now().strftime('%Y%m%d')}.csv"
            )

        elif file_format == 'pdf':
            # In production, generate actual PDF here
            # For now, return mock PDF content
            mock_pdf = f"Mock PDF Report for {report_data.get('moduleId', 'Unknown')}\nGenerated: {datetime.now()}"
            
            return send_file(
                io.BytesIO(mock_pdf.encode()),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"attendance_report_{datetime.now().strftime('%Y%m%d')}.pdf"
            )

        else:
            return jsonify({
                'success': False,
                'message': 'Unsupported file format'
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("Lecturer Report Controller running on http://localhost:5005")
    print("Available endpoints:")
    print("  POST /api/lecturer/report/generate")
    print("  POST /api/lecturer/report/download")
    app.run(host='0.0.0.0', port=5005, debug=True, use_reloader=False)
