"""QR Code Scanner Module.

This module handles QR code scanning from images and webcam.

Implementation note:
- Uses OpenCV's built-in QRCodeDetector to avoid external system dependencies
    (e.g., `zbar`) that often break in hosted environments like Streamlit Cloud.
"""

import io
from typing import List, Optional, Tuple

from PIL import Image


def decode_qr_from_image(image_bgr) -> List[dict]:
    """Decode QR code(s) from an image array.

    Args:
        image_bgr: NumPy array of the image (BGR format from OpenCV)

    Returns:
        List[dict]: Each item contains at least {"data": str, "points": Optional[np.ndarray]}.
    """
    import cv2
    import numpy as np
    
    results: List[dict] = []

    try:
        detector = cv2.QRCodeDetector()

        # OpenCV versions vary: prefer detectAndDecodeMulti when available.
        if hasattr(detector, "detectAndDecodeMulti"):
            ok, decoded_info, points, _ = detector.detectAndDecodeMulti(image_bgr)
            if ok and decoded_info is not None:
                for idx, data in enumerate(decoded_info):
                    if data:
                        pts = None
                        if points is not None and len(points) > idx:
                            pts = points[idx]
                        results.append({"data": data, "points": pts})
        else:
            data, points, _ = detector.detectAndDecode(image_bgr)
            if data:
                results.append({"data": data, "points": points})

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
    import cv2
    import numpy as np
    
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


def draw_qr_bounding_box(image, decoded_objects: list):
    """
    Draw bounding boxes around detected QR codes.
    
    Args:
        image: Original image
        decoded_objects: List of decoded QR objects
        
    Returns:
        np.ndarray: Image with bounding boxes drawn
    """
    import cv2
    import numpy as np
    
    img_copy = image.copy()
    
    for obj in decoded_objects:
        pts = obj.get("points")
        if pts is None:
            continue

        pts = np.array(pts, dtype=np.int32)
        if pts.ndim == 2:
            pts = pts.reshape((-1, 1, 2))
        cv2.polylines(img_copy, [pts], True, (0, 255, 0), 3)
    
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
        import cv2
        
        self.camera_id = camera_id
        self.cap = None
    
    def start(self):
        """Start the webcam capture."""
        import cv2
        
        self.cap = cv2.VideoCapture(self.camera_id)
    
    def stop(self):
        """Stop the webcam capture."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def capture_frame(self) -> Optional:
        """
        Capture a single frame from the webcam.
        
        Returns:
            Optional: Captured frame or None
        """
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None
    
    def scan_frame(self, frame) -> List[dict]:
        """
        Scan a frame for QR codes.
        
        Args:
            frame: Image frame to scan
            
        Returns:
            List[dict]: List of decoded QR codes
        """
        return decode_qr_from_image(frame)


def process_webcam_image(image_data) -> Tuple[Optional[str], str, Optional]:
    """
    Process webcam image data for QR code detection.
    
    Args:
        image_data: Image data from Streamlit's camera_input
        
    Returns:
        Tuple[Optional[str], str, Optional]: 
            (QR code data, message, processed image)
    """
    import cv2
    import numpy as np
    
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
            processed_img = draw_qr_bounding_box(image_bgr, decoded)
            processed_img = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)

            qr_data = decoded[0]["data"]
            return qr_data, "QR code detected!", processed_img
        else:
            return None, "No QR code detected. Please try again.", image_array
            
    except Exception as e:
        return None, f"Error processing webcam image: {str(e)}", None
