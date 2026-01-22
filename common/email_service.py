import smtplib
import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_PORT', '587'))
        self.smtp_user = os.getenv('EMAIL_USER', 'kennethang1997@gmail.com')
        self.smtp_password = os.getenv('EMAIL_PASSWORD', 'aliq nhpp fwiv ussj')
        self.from_email = os.getenv('EMAIL_FROM', 'UOW Student Attendance System <noreply@attendance.com>')

    def generate_reset_code(self, length=8):
        """Generate a random reset code"""
        characters = string.ascii_lowercase + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))

    def send_password_reset_email(self, to_email, user_name, reset_code, reset_link):
        """Send a password reset email with a beautiful HTML template"""

        subject = "Password Reset Request - Student Attendance System"

        # HTML email template matching your example
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f4f4;
        }}
        .email-container {{
            max-width: 600px;
            margin: 40px auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            color: #ffffff;
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 18px;
            color: #333333;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        .message {{
            color: #666666;
            line-height: 1.6;
            margin-bottom: 20px;
        }}
        .reset-button {{
            display: inline-block;
            background-color: #667eea;
            color: #ffffff !important;
            text-decoration: none;
            padding: 14px 40px;
            border-radius: 6px;
            font-weight: 600;
            margin: 20px 0;
            text-align: center;
        }}
        .reset-button:hover {{
            background-color: #5568d3;
        }}
        .code-section {{
            background-color: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 30px 0;
        }}
        .code-title {{
            font-size: 14px;
            color: #666666;
            margin-bottom: 10px;
        }}
        .reset-code {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            letter-spacing: 4px;
            font-family: 'Courier New', monospace;
        }}
        .warning {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            font-size: 14px;
        }}
        .warning-icon {{
            color: #856404;
            font-weight: bold;
        }}
        .link-section {{
            background-color: #f8f9fa;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
            font-size: 12px;
            color: #666666;
            word-break: break-all;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: #999999;
            border-top: 1px solid #eeeeee;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>Password Reset Request</h1>
        </div>

        <div class="content">
            <div class="greeting">Hello {user_name},</div>

            <div class="message">
                We received a request to reset your password for your Student Attendance System account.
            </div>

            <div class="message">
                Click the button below to reset your password:
            </div>

            <div style="text-align: center;">
                <a href="{reset_link}" class="reset-button">Reset Password</a>
            </div>

            <div class="code-section">
                <div class="code-title">Or enter this verification code:</div>
                <div class="reset-code">{reset_code}</div>
            </div>

            <div class="warning">
                <span class="warning-icon">⚠️ Important:</span> This link will expire in <strong>5 minutes</strong> for security reasons.
            </div>

            <div class="message">
                If the button doesn't work, you can copy and paste this link into your browser:
            </div>

            <div class="link-section">
                {reset_link}
            </div>

            <div class="message" style="margin-top: 30px;">
                If you didn't request a password reset, please ignore this email. Your password will remain unchanged.
            </div>
        </div>

        <div class="footer">
            <p>This is an automated email from Student Attendance System.</p>
            <p>Please do not reply to this email.</p>
            <p>&copy; {datetime.now().year} UOW Student Attendance System. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

        # Plain text version for email clients that don't support HTML
        text_body = f"""
Password Reset Request - Student Attendance System

Hello {user_name},

We received a request to reset your password for your Student Attendance System account.

Reset Code: {reset_code}

Or visit this link: {reset_link}

Important: This link will expire in 5 minutes for security reasons.

If you didn't request a password reset, please ignore this email.

---
UOW Student Attendance System
"""

        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.from_email
            message['To'] = to_email

            # Attach plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            message.attach(part1)
            message.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)

            return {
                'ok': True,
                'reset_code': reset_code,
                'message': 'Password reset email sent successfully'
            }

        except Exception as e:
            print(f"Error sending email: {e}")
            return {
                'ok': False,
                'error': str(e)
            }

# Example usage
if __name__ == '__main__':
    email_service = EmailService()

    # Generate reset code and link - use environment-aware URL
    reset_code = email_service.generate_reset_code()
    
    # Dynamically build reset link based on deployment environment
    protocol = os.getenv('URL_PROTOCOL', 'https')
    domain = os.getenv('DOMAIN_NAME', 'localhost')
    port = os.getenv('PORT', '5000')
    
    if domain == 'localhost':
        reset_link = f"http://{domain}:{port}/reset_password.html?token={reset_code}"
    else:
        reset_link = f"{protocol}://{domain}/reset_password.html?token={reset_code}"

    # Send email
    result = email_service.send_password_reset_email(
        to_email="kennethang1997@gmail.com",
        user_name="Kenneth Ang",
        reset_code=reset_code,
        reset_link=reset_link
    )

    print(result)
