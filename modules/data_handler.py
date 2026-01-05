"""
Data Handler Module

This module handles all Excel/data operations for attendance records.
"""

import pandas as pd
import os
from datetime import datetime
from typing import Optional, Tuple
import openpyxl


class AttendanceDataHandler:
    """
    Class to handle attendance data operations using Excel files.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize the data handler with the Excel file path.
        
        Args:
            file_path: Path to the Excel file for storing attendance data
        """
        self.file_path = file_path
        self.columns = ["Email", "QR_Code_ID", "Attendance_Status", "Timestamp", "QR_Code_Path"]
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """
        Ensure the Excel file exists with proper headers.
        """
        if not os.path.exists(self.file_path):
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            # Create empty DataFrame with columns
            df = pd.DataFrame(columns=self.columns)
            df.to_excel(self.file_path, index=False, engine='openpyxl')
    
    def load_data(self) -> pd.DataFrame:
        """
        Load attendance data from Excel file.
        
        Returns:
            pd.DataFrame: Attendance data
        """
        try:
            df = pd.read_excel(self.file_path, engine='openpyxl')
            # Ensure all columns exist
            for col in self.columns:
                if col not in df.columns:
                    df[col] = ""
            return df
        except Exception as e:
            # Return empty DataFrame if file is corrupted or missing
            return pd.DataFrame(columns=self.columns)
    
    def save_data(self, df: pd.DataFrame) -> bool:
        """
        Save attendance data to Excel file.
        
        Args:
            df: DataFrame to save
            
        Returns:
            bool: Success status
        """
        try:
            df.to_excel(self.file_path, index=False, engine='openpyxl')
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def add_records(self, records: list) -> Tuple[bool, str]:
        """
        Add new attendance records to the Excel file.
        
        Args:
            records: List of dictionaries containing email, qr_code_id, qr_code_path
            
        Returns:
            Tuple[bool, str]: (success status, message)
        """
        try:
            df = self.load_data()
            
            new_records = []
            duplicates = []
            
            for record in records:
                email = record.get("email", "").strip().lower()
                
                # Check for duplicates
                if email in df["Email"].str.lower().values:
                    duplicates.append(email)
                    continue
                
                new_records.append({
                    "Email": email,
                    "QR_Code_ID": record.get("qr_code_id", ""),
                    "Attendance_Status": "Not Attended",
                    "Timestamp": "",
                    "QR_Code_Path": record.get("qr_code_path", "")
                })
            
            if new_records:
                new_df = pd.DataFrame(new_records)
                df = pd.concat([df, new_df], ignore_index=True)
                self.save_data(df)
            
            message = f"Added {len(new_records)} records."
            if duplicates:
                message += f" Skipped {len(duplicates)} duplicate(s): {', '.join(duplicates[:5])}"
                if len(duplicates) > 5:
                    message += f"... and {len(duplicates) - 5} more"
            
            return True, message
            
        except Exception as e:
            return False, f"Error adding records: {str(e)}"
    
    def mark_attendance(self, qr_code_id: str) -> Tuple[bool, str, Optional[str]]:
        """
        Mark attendance for a given QR code ID.
        
        Args:
            qr_code_id: The unique QR code ID to mark as attended
            
        Returns:
            Tuple[bool, str, Optional[str]]: (success status, message, email if found)
        """
        try:
            df = self.load_data()
            
            # Find the record with matching QR code ID
            mask = df["QR_Code_ID"] == qr_code_id
            
            if not mask.any():
                return False, "QR code not found in records.", None
            
            # Check if already marked
            if df.loc[mask, "Attendance_Status"].values[0] == "Attended":
                email = df.loc[mask, "Email"].values[0]
                timestamp = df.loc[mask, "Timestamp"].values[0]
                return False, f"Already marked as attended on {timestamp}", email
            
            # Update attendance status and timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.loc[mask, "Attendance_Status"] = "Attended"
            df.loc[mask, "Timestamp"] = current_time
            
            email = df.loc[mask, "Email"].values[0]
            
            self.save_data(df)
            
            return True, f"Attendance marked successfully at {current_time}", email
            
        except Exception as e:
            return False, f"Error marking attendance: {str(e)}", None
    
    def get_statistics(self) -> dict:
        """
        Get attendance statistics.
        
        Returns:
            dict: Statistics including total, attended, not attended counts
        """
        df = self.load_data()
        
        total = len(df)
        attended = len(df[df["Attendance_Status"] == "Attended"])
        not_attended = total - attended
        
        return {
            "total": total,
            "attended": attended,
            "not_attended": not_attended,
            "attendance_rate": (attended / total * 100) if total > 0 else 0
        }
    
    def get_all_records(self) -> pd.DataFrame:
        """
        Get all attendance records.
        
        Returns:
            pd.DataFrame: All attendance records
        """
        return self.load_data()
    
    def email_exists(self, email: str) -> bool:
        """
        Check if an email already exists in records.
        
        Args:
            email: Email address to check
            
        Returns:
            bool: True if email exists
        """
        df = self.load_data()
        return email.strip().lower() in df["Email"].str.lower().values
    
    def get_record_by_qr_id(self, qr_code_id: str) -> Optional[dict]:
        """
        Get a record by QR code ID.
        
        Args:
            qr_code_id: QR code ID to search for
            
        Returns:
            Optional[dict]: Record data if found, None otherwise
        """
        df = self.load_data()
        mask = df["QR_Code_ID"] == qr_code_id
        
        if mask.any():
            record = df[mask].iloc[0]
            return record.to_dict()
        
        return None
    
    def clear_all_records(self) -> Tuple[bool, str]:
        """
        Clear all attendance records.
        
        Returns:
            Tuple[bool, str]: (success status, message)
        """
        try:
            df = pd.DataFrame(columns=self.columns)
            self.save_data(df)
            return True, "All records cleared successfully."
        except Exception as e:
            return False, f"Error clearing records: {str(e)}"
    
    def export_to_excel(self, output_path: str) -> Tuple[bool, str]:
        """
        Export attendance data to a new Excel file.
        
        Args:
            output_path: Path for the exported file
            
        Returns:
            Tuple[bool, str]: (success status, message)
        """
        try:
            df = self.load_data()
            # Select only relevant columns for export
            export_columns = ["Email", "QR_Code_ID", "Attendance_Status", "Timestamp"]
            export_df = df[export_columns]
            export_df.to_excel(output_path, index=False, engine='openpyxl')
            return True, f"Data exported successfully to {output_path}"
        except Exception as e:
            return False, f"Error exporting data: {str(e)}"


def parse_emails_from_file(file_content: bytes, filename: str) -> Tuple[list, str]:
    """
    Parse email addresses from uploaded file.
    
    Args:
        file_content: File content as bytes
        filename: Name of the uploaded file
        
    Returns:
        Tuple[list, str]: (list of emails, message)
    """
    emails = []
    
    try:
        if filename.endswith('.csv'):
            import io
            content = file_content.decode('utf-8')
            df = pd.read_csv(io.StringIO(content))
            # Look for email column
            email_col = None
            for col in df.columns:
                if 'email' in col.lower():
                    email_col = col
                    break
            
            if email_col is None and len(df.columns) > 0:
                email_col = df.columns[0]
            
            if email_col:
                emails = df[email_col].dropna().tolist()
                
        elif filename.endswith(('.xlsx', '.xls')):
            import io
            df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
            # Look for email column
            email_col = None
            for col in df.columns:
                if 'email' in col.lower():
                    email_col = col
                    break
            
            if email_col is None and len(df.columns) > 0:
                email_col = df.columns[0]
            
            if email_col:
                emails = df[email_col].dropna().tolist()
                
        elif filename.endswith('.txt'):
            content = file_content.decode('utf-8')
            emails = [line.strip() for line in content.split('\n') if line.strip()]
        
        else:
            return [], "Unsupported file format. Please use .csv, .xlsx, .xls, or .txt"
        
        # Clean and validate emails
        valid_emails = []
        for email in emails:
            email = str(email).strip()
            if '@' in email and '.' in email:
                valid_emails.append(email)
        
        return valid_emails, f"Found {len(valid_emails)} valid email(s)"
        
    except Exception as e:
        return [], f"Error parsing file: {str(e)}"
