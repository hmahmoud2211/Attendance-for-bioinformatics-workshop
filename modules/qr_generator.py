"""
QR Code Generation Module

This module handles the generation of unique QR codes for each email address.
"""

import qrcode
import uuid
import os
from PIL import Image


def generate_unique_id() -> str:
    """
    Generate a unique identifier for each QR code.
    
    Returns:
        str: A unique UUID string
    """
    return str(uuid.uuid4())


def create_qr_code(data: str, output_path: str, box_size: int = 10, border: int = 4) -> str:
    """
    Create a QR code image from the given data.
    
    Args:
        data: The data to encode in the QR code
        output_path: Path where the QR code image will be saved
        box_size: Size of each box in the QR code
        border: Border size around the QR code
        
    Returns:
        str: Path to the saved QR code image
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create QR code image with custom colors
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    
    return output_path


def generate_qr_for_email(email: str, qr_codes_dir: str) -> tuple:
    """
    Generate a unique QR code for a given email address.
    
    Args:
        email: The email address to generate QR code for
        qr_codes_dir: Directory to save QR code images
        
    Returns:
        tuple: (unique_id, qr_code_path)
    """
    # Generate unique ID
    unique_id = generate_unique_id()
    
    # Create QR code data (combining email and unique ID for verification)
    qr_data = f"{unique_id}|{email}"
    
    # Create filename using unique ID
    filename = f"qr_{unique_id}.png"
    output_path = os.path.join(qr_codes_dir, filename)
    
    # Generate and save QR code
    create_qr_code(qr_data, output_path)
    
    return unique_id, output_path


def generate_qr_codes_batch(emails: list, qr_codes_dir: str) -> list:
    """
    Generate QR codes for a batch of email addresses.
    
    Args:
        emails: List of email addresses
        qr_codes_dir: Directory to save QR code images
        
    Returns:
        list: List of dictionaries containing email, unique_id, and qr_code_path
    """
    results = []
    
    for email in emails:
        email = email.strip()
        if email:
            unique_id, qr_path = generate_qr_for_email(email, qr_codes_dir)
            results.append({
                "email": email,
                "qr_code_id": unique_id,
                "qr_code_path": qr_path
            })
    
    return results
