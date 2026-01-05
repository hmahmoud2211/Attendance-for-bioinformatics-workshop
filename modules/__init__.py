"""
Modules package for Attendance Management Application.
"""

from .qr_generator import generate_qr_for_email, generate_qr_codes_batch
from .email_sender import EmailSender, test_smtp_connection
from .data_handler import AttendanceDataHandler, parse_emails_from_file
from .qr_scanner import (
    decode_qr_from_image,
    decode_qr_from_uploaded_file,
    parse_qr_data,
    process_webcam_image
)

__all__ = [
    'generate_qr_for_email',
    'generate_qr_codes_batch',
    'EmailSender',
    'test_smtp_connection',
    'AttendanceDataHandler',
    'parse_emails_from_file',
    'decode_qr_from_image',
    'decode_qr_from_uploaded_file',
    'parse_qr_data',
    'process_webcam_image'
]
