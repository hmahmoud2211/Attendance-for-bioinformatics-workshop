"""
Email Sending Module

This module handles sending QR codes to email addresses using SMTP.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import Tuple, Optional


class EmailSender:
    """
    Class to handle email operations using SMTP.
    """
    
    def __init__(self, smtp_server: str, smtp_port: int, 
                 sender_email: str, sender_password: str):
        """
        Initialize the EmailSender with SMTP credentials.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            sender_email: Sender's email address
            sender_password: Sender's email password or app password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def send_qr_code_email(self, recipient_email: str, qr_code_path: str,
                           subject: str, body: str) -> Tuple[bool, str]:
        """
        Send an email with a QR code attachment.
        
        Args:
            recipient_email: Recipient's email address
            qr_code_path: Path to the QR code image
            subject: Email subject
            body: Email body text
            
        Returns:
            Tuple[bool, str]: (success status, message)
        """
        try:
            # Create message container
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = subject
            
            # Add body text
            message.attach(MIMEText(body, "plain"))
            
            # Attach QR code image
            if os.path.exists(qr_code_path):
                with open(qr_code_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                
                filename = os.path.basename(qr_code_path)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}",
                )
                
                message.attach(part)
            else:
                return False, f"QR code file not found: {qr_code_path}"
            
            # Create secure SSL context
            context = ssl.create_default_context()
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            
            return True, f"Email sent successfully to {recipient_email}"
            
        except smtplib.SMTPAuthenticationError:
            return False, "Authentication failed. Please check your email credentials."
        except smtplib.SMTPException as e:
            return False, f"SMTP error occurred: {str(e)}"
        except Exception as e:
            return False, f"Error sending email: {str(e)}"
    
    def send_bulk_emails(self, recipients: list, subject: str, body_template: str,
                         progress_callback=None) -> dict:
        """
        Send QR code emails to multiple recipients.
        
        Args:
            recipients: List of dicts with 'email' and 'qr_code_path' keys
            subject: Email subject
            body_template: Email body template
            progress_callback: Optional callback function for progress updates
            
        Returns:
            dict: Summary of sent/failed emails
        """
        results = {
            "sent": [],
            "failed": []
        }
        
        total = len(recipients)
        
        for i, recipient in enumerate(recipients):
            email = recipient.get("email")
            qr_path = recipient.get("qr_code_path")
            
            if email and qr_path:
                success, message = self.send_qr_code_email(
                    email, qr_path, subject, body_template
                )
                
                if success:
                    results["sent"].append({"email": email, "message": message})
                else:
                    results["failed"].append({"email": email, "message": message})
            
            # Update progress if callback provided
            if progress_callback:
                progress_callback((i + 1) / total)
        
        return results


def test_smtp_connection(smtp_server: str, smtp_port: int,
                         sender_email: str, sender_password: str) -> Tuple[bool, str]:
    """
    Test SMTP connection without sending an email.
    
    Args:
        smtp_server: SMTP server address
        smtp_port: SMTP server port
        sender_email: Sender's email address
        sender_password: Sender's email password
        
    Returns:
        Tuple[bool, str]: (success status, message)
    """
    try:
        context = ssl.create_default_context()
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
        
        return True, "SMTP connection successful!"
        
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication failed. Please check your credentials."
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"
