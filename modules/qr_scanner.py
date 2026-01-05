"""
QR Code Scanner Module

This module handles QR code scanning from images and webcam.
"""

import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image
from typing import Optional, Tuple, List
import io


def decode_qr_from_image(image: np.ndarray) -> List[dict]:
    """
    Decode QR code(s) from an image array.
    
    Args:
        image: NumPy array of the image (BGR format from OpenCV)
        
    Returns:
        List[dict]: List of decoded QR code data
    """
    results = []
    
    try:
        # Convert to grayscale for better detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Try decoding QR codes
        decoded_objects = decode(gray)
        
        # If no results, try with the original image
        if not decoded_objects:
            decoded_objects = decode(image)
        
        for obj in decoded_objects:
            if obj.type == 'QRCODE':
                data = obj.data.decode('utf-8')
                results.append({
                    "data": data,
                    "type": obj.type,
                    "rect": obj.rect
                })
    
    except Exception as e:
        print(f"Error decoding QR code: {e}")
    
    return results


def decode_qr_from_uploaded_file(uploaded_file) -> Tuple[Optional[str], str]:
    """
    Decode QR code from an uploaded file.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Tuple[Optional[str], str]: (QR code data, message)
    """
    try:
        # Read image from uploaded file
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if image is None:
            return None, "Could not read the image file."
        
        # Decode QR codes
        decoded = decode_qr_from_image(image)
        
        if decoded:
            qr_data = decoded[0]["data"]
            return qr_data, "QR code decoded successfully!"
        else:
            return None, "No QR code found in the image. Please try a clearer image."
            
    except Exception as e:
        return None, f"Error processing image: {str(e)}"


def parse_qr_data(qr_data: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse QR code data to extract unique ID and email.
    
    Args:
        qr_data: Raw QR code data string
        
    Returns:
        Tuple[Optional[str], Optional[str]]: (unique_id, email)
    """
    try:
        if '|' in qr_data:
            parts = qr_data.split('|')
            if len(parts) >= 2:
                unique_id = parts[0]
                email = parts[1]
                return unique_id, email
        
        # If no separator, assume entire data is the unique ID
        return qr_data, None
        
    except Exception:
        return None, None


def draw_qr_bounding_box(image: np.ndarray, decoded_objects: list) -> np.ndarray:
    """
    Draw bounding boxes around detected QR codes.
    
    Args:
        image: Original image
        decoded_objects: List of decoded QR objects
        
    Returns:
        np.ndarray: Image with bounding boxes drawn
    """
    img_copy = image.copy()
    
    for obj in decoded_objects:
        # Draw rectangle
        points = obj.polygon
        if len(points) == 4:
            pts = np.array(points, dtype=np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(img_copy, [pts], True, (0, 255, 0), 3)
        else:
            # Use bounding rect if polygon is not available
            rect = obj.rect
            cv2.rectangle(img_copy, 
                         (rect.left, rect.top), 
                         (rect.left + rect.width, rect.top + rect.height),
                         (0, 255, 0), 3)
    
    return img_copy


class WebcamScanner:
    """
    Class to handle webcam-based QR code scanning.
    Note: This is primarily for demonstration. Real-time webcam 
    scanning in Streamlit requires special handling.
    """
    
    def __init__(self, camera_id: int = 0):
        """
        Initialize the webcam scanner.
        
        Args:
            camera_id: Camera device ID
        """
        self.camera_id = camera_id
        self.cap = None
    
    def start(self):
        """Start the webcam capture."""
        self.cap = cv2.VideoCapture(self.camera_id)
    
    def stop(self):
        """Stop the webcam capture."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from the webcam.
        
        Returns:
            Optional[np.ndarray]: Captured frame or None
        """
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None
    
    def scan_frame(self, frame: np.ndarray) -> List[dict]:
        """
        Scan a frame for QR codes.
        
        Args:
            frame: Image frame to scan
            
        Returns:
            List[dict]: List of decoded QR codes
        """
        return decode_qr_from_image(frame)


def process_webcam_image(image_data) -> Tuple[Optional[str], str, Optional[np.ndarray]]:
    """
    Process webcam image data for QR code detection.
    
    Args:
        image_data: Image data from Streamlit's camera_input
        
    Returns:
        Tuple[Optional[str], str, Optional[np.ndarray]]: 
            (QR code data, message, processed image)
    """
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data.getvalue()))
        
        # Convert PIL Image to numpy array
        image_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image_array
        
        # Decode QR codes
        decoded = decode_qr_from_image(image_bgr)
        
        # Draw bounding boxes on detected QR codes
        if decoded:
            # Get the raw decoded objects for drawing
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            raw_decoded = decode(gray)
            if not raw_decoded:
                raw_decoded = decode(image_bgr)
            
            if raw_decoded:
                processed_img = draw_qr_bounding_box(image_bgr, raw_decoded)
                # Convert back to RGB for display
                processed_img = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)
            else:
                processed_img = image_array
            
            qr_data = decoded[0]["data"]
            return qr_data, "QR code detected!", processed_img
        else:
            return None, "No QR code detected. Please try again.", image_array
            
    except Exception as e:
        return None, f"Error processing webcam image: {str(e)}", None
