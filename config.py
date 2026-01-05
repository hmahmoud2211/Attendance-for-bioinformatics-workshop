"""
Configuration settings for the Attendance Management Application.
"""

import os

# Application settings
APP_TITLE = "QR Code Attendance Management System"
APP_ICON = "📋"

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
QR_CODES_DIR = os.path.join(BASE_DIR, "qr_codes")

# Excel file settings
ATTENDANCE_FILE = os.path.join(DATA_DIR, "attendance_records.xlsx")
EXCEL_COLUMNS = ["Email", "QR_Code_ID", "Attendance_Status", "Timestamp"]

# Default attendance status
STATUS_NOT_ATTENDED = "Not Attended"
STATUS_ATTENDED = "Attended"

# Email settings (to be configured by admin)
DEFAULT_EMAIL_SETTINGS = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "",
    "sender_password": "",  # App password for Gmail
    "email_subject": "Your Attendance QR Code",
    "email_body_template": """
Dear Attendee,

Please find your unique QR code attached to this email.

Present this QR code at the event for attendance verification.

Best regards,
Event Management Team
"""
}

# QR Code settings
QR_CODE_SIZE = 10  # Box size
QR_CODE_BORDER = 4
QR_CODE_VERSION = 1

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(QR_CODES_DIR, exist_ok=True)
