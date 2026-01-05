"""
QR Code Attendance Management System

A Streamlit web application for managing attendance using QR codes and email verification.

Author: Attendance System
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
import io

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    APP_TITLE, APP_ICON, DATA_DIR, QR_CODES_DIR, 
    ATTENDANCE_FILE, DEFAULT_EMAIL_SETTINGS
)
from modules.qr_generator import generate_qr_codes_batch
from modules.email_sender import EmailSender, test_smtp_connection
from modules.data_handler import AttendanceDataHandler, parse_emails_from_file
from modules.qr_scanner import (
    decode_qr_from_uploaded_file, 
    parse_qr_data,
    process_webcam_image
)

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_handler' not in st.session_state:
    st.session_state.data_handler = AttendanceDataHandler(ATTENDANCE_FILE)

if 'email_settings' not in st.session_state:
    st.session_state.email_settings = DEFAULT_EMAIL_SETTINGS.copy()

if 'emails_to_process' not in st.session_state:
    st.session_state.emails_to_process = []


def main():
    """Main application function."""
    
    # Sidebar navigation
    st.sidebar.title(f"{APP_ICON} Navigation")
    
    page = st.sidebar.radio(
        "Select Page",
        ["📊 Dashboard", "📧 Email Management", "📷 QR Scanner", "⚙️ Settings", "📋 Records"]
    )
    
    # Display selected page
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "📧 Email Management":
        show_email_management()
    elif page == "📷 QR Scanner":
        show_qr_scanner()
    elif page == "⚙️ Settings":
        show_settings()
    elif page == "📋 Records":
        show_records()


def show_dashboard():
    """Display the attendance dashboard."""
    
    st.title("📊 Attendance Dashboard")
    st.markdown("---")
    
    # Get statistics
    stats = st.session_state.data_handler.get_statistics()
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📧 Total Emails Sent",
            value=stats['total'],
            help="Total number of QR codes generated and sent"
        )
    
    with col2:
        st.metric(
            label="✅ Attended",
            value=stats['attended'],
            delta=f"{stats['attendance_rate']:.1f}%" if stats['total'] > 0 else "0%",
            help="Number of people who have attended"
        )
    
    with col3:
        st.metric(
            label="❌ Not Attended",
            value=stats['not_attended'],
            help="Number of people who haven't attended yet"
        )
    
    with col4:
        st.metric(
            label="📈 Attendance Rate",
            value=f"{stats['attendance_rate']:.1f}%",
            help="Percentage of attendees"
        )
    
    st.markdown("---")
    
    # Attendance chart
    if stats['total'] > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Attendance Overview")
            
            # Create pie chart data
            chart_data = pd.DataFrame({
                'Status': ['Attended', 'Not Attended'],
                'Count': [stats['attended'], stats['not_attended']]
            })
            
            st.bar_chart(chart_data.set_index('Status'))
        
        with col2:
            st.subheader("📋 Recent Activity")
            
            # Show recent attended records
            df = st.session_state.data_handler.get_all_records()
            attended_df = df[df['Attendance_Status'] == 'Attended'].copy()
            
            if len(attended_df) > 0:
                attended_df = attended_df.sort_values('Timestamp', ascending=False).head(10)
                st.dataframe(
                    attended_df[['Email', 'Timestamp']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No attendance records yet.")
    else:
        st.info("No data available. Start by adding email addresses in the Email Management page.")
    
    # Refresh button
    if st.button("🔄 Refresh Dashboard"):
        st.rerun()


def show_email_management():
    """Display email management page for adding emails and generating QR codes."""
    
    st.title("📧 Email Management")
    st.markdown("Add email addresses to generate QR codes and send them via email.")
    st.markdown("---")
    
    # Tabs for different input methods
    tab1, tab2 = st.tabs(["📝 Manual Entry", "📁 File Upload"])
    
    with tab1:
        st.subheader("Enter Email Addresses")
        
        # Text area for manual email entry
        emails_text = st.text_area(
            "Enter email addresses (one per line)",
            height=150,
            placeholder="email1@example.com\nemail2@example.com\nemail3@example.com"
        )
        
        if st.button("➕ Add Emails", key="add_manual"):
            if emails_text:
                emails = [e.strip() for e in emails_text.split('\n') if e.strip() and '@' in e]
                if emails:
                    st.session_state.emails_to_process = emails
                    st.success(f"Added {len(emails)} email(s) to queue")
                else:
                    st.warning("No valid email addresses found")
            else:
                st.warning("Please enter email addresses")
    
    with tab2:
        st.subheader("Upload Email List")
        
        uploaded_file = st.file_uploader(
            "Upload file containing email addresses",
            type=['csv', 'xlsx', 'xls', 'txt'],
            help="Supported formats: CSV, Excel (xlsx/xls), Text file"
        )
        
        if uploaded_file is not None:
            emails, message = parse_emails_from_file(
                uploaded_file.getvalue(),
                uploaded_file.name
            )
            
            st.info(message)
            
            if emails:
                st.write("Preview of emails found:")
                preview_df = pd.DataFrame({'Email': emails[:10]})
                st.dataframe(preview_df, use_container_width=True, hide_index=True)
                
                if len(emails) > 10:
                    st.write(f"... and {len(emails) - 10} more")
                
                if st.button("➕ Add These Emails", key="add_uploaded"):
                    st.session_state.emails_to_process = emails
                    st.success(f"Added {len(emails)} email(s) to queue")
    
    st.markdown("---")
    
    # Process queued emails
    if st.session_state.emails_to_process:
        st.subheader("📤 Process Queued Emails")
        st.write(f"**{len(st.session_state.emails_to_process)} email(s)** ready to process")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔲 Generate QR Codes Only"):
                with st.spinner("Generating QR codes..."):
                    # Generate QR codes
                    results = generate_qr_codes_batch(
                        st.session_state.emails_to_process,
                        QR_CODES_DIR
                    )
                    
                    # Add to database
                    success, message = st.session_state.data_handler.add_records(results)
                    
                    if success:
                        st.success(f"✅ Generated {len(results)} QR codes! {message}")
                        st.session_state.emails_to_process = []
                    else:
                        st.error(message)
        
        with col2:
            if st.button("📧 Generate & Send Emails"):
                # Check email settings
                settings = st.session_state.email_settings
                if not settings['sender_email'] or not settings['sender_password']:
                    st.error("Please configure email settings first in the Settings page.")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Generate QR codes
                    status_text.text("Generating QR codes...")
                    results = generate_qr_codes_batch(
                        st.session_state.emails_to_process,
                        QR_CODES_DIR
                    )
                    
                    # Add to database
                    st.session_state.data_handler.add_records(results)
                    
                    # Send emails
                    status_text.text("Sending emails...")
                    email_sender = EmailSender(
                        settings['smtp_server'],
                        settings['smtp_port'],
                        settings['sender_email'],
                        settings['sender_password']
                    )
                    
                    # Prepare recipients
                    recipients = [
                        {'email': r['email'], 'qr_code_path': r['qr_code_path']}
                        for r in results
                    ]
                    
                    # Send with progress
                    def update_progress(progress):
                        progress_bar.progress(progress)
                    
                    email_results = email_sender.send_bulk_emails(
                        recipients,
                        settings['email_subject'],
                        settings['email_body_template'],
                        progress_callback=update_progress
                    )
                    
                    # Show results
                    sent_count = len(email_results['sent'])
                    failed_count = len(email_results['failed'])
                    
                    progress_bar.progress(100)
                    status_text.empty()
                    
                    st.success(f"✅ Sent {sent_count} email(s)")
                    
                    if failed_count > 0:
                        st.warning(f"⚠️ Failed to send {failed_count} email(s)")
                        with st.expander("View failed emails"):
                            for fail in email_results['failed']:
                                st.write(f"- {fail['email']}: {fail['message']}")
                    
                    st.session_state.emails_to_process = []
        
        with col3:
            if st.button("🗑️ Clear Queue"):
                st.session_state.emails_to_process = []
                st.success("Queue cleared")
                st.rerun()


def show_qr_scanner():
    """Display QR code scanner page."""
    
    st.title("📷 QR Code Scanner")
    st.markdown("Scan QR codes to mark attendance.")
    st.markdown("---")
    
    # Tabs for different scanning methods
    tab1, tab2 = st.tabs(["📁 Upload Image", "📸 Webcam"])
    
    with tab1:
        st.subheader("Upload QR Code Image")
        
        uploaded_qr = st.file_uploader(
            "Upload QR code image",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
            key="qr_upload"
        )
        
        if uploaded_qr is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(uploaded_qr, caption="Uploaded QR Code", use_container_width=True)
            
            with col2:
                # Reset file pointer
                uploaded_qr.seek(0)
                
                # Decode QR code
                qr_data, message = decode_qr_from_uploaded_file(uploaded_qr)
                
                if qr_data:
                    st.success(message)
                    
                    # Parse QR data
                    unique_id, email = parse_qr_data(qr_data)
                    
                    if unique_id:
                        st.info(f"**QR Code ID:** {unique_id}")
                        if email:
                            st.info(f"**Email:** {email}")
                        
                        # Mark attendance button
                        if st.button("✅ Mark Attendance", key="mark_upload"):
                            success, msg, found_email = st.session_state.data_handler.mark_attendance(unique_id)
                            
                            if success:
                                st.success(f"🎉 {msg}")
                                if found_email:
                                    st.balloons()
                                    st.info(f"**Attendee:** {found_email}")
                            else:
                                st.warning(f"⚠️ {msg}")
                                if found_email:
                                    st.info(f"**Email:** {found_email}")
                else:
                    st.error(message)
    
    with tab2:
        st.subheader("Webcam Scanner")
        st.info("📸 Use your webcam to scan QR codes")
        
        # Webcam input
        camera_image = st.camera_input("Take a photo of the QR code")
        
        if camera_image is not None:
            # Process the webcam image
            qr_data, message, processed_img = process_webcam_image(camera_image)
            
            # Display processed image
            if processed_img is not None:
                st.image(processed_img, caption="Processed Image", use_container_width=True)
            
            if qr_data:
                st.success(message)
                
                # Parse QR data
                unique_id, email = parse_qr_data(qr_data)
                
                if unique_id:
                    st.info(f"**QR Code ID:** {unique_id}")
                    if email:
                        st.info(f"**Email:** {email}")
                    
                    # Mark attendance button
                    if st.button("✅ Mark Attendance", key="mark_webcam"):
                        success, msg, found_email = st.session_state.data_handler.mark_attendance(unique_id)
                        
                        if success:
                            st.success(f"🎉 {msg}")
                            if found_email:
                                st.balloons()
                                st.info(f"**Attendee:** {found_email}")
                        else:
                            st.warning(f"⚠️ {msg}")
                            if found_email:
                                st.info(f"**Email:** {found_email}")
            else:
                st.warning(message)
    
    st.markdown("---")
    
    # Manual QR ID entry
    st.subheader("🔢 Manual QR Code Entry")
    st.write("If scanning doesn't work, enter the QR code ID manually:")
    
    manual_qr_id = st.text_input("Enter QR Code ID")
    
    if st.button("✅ Mark Attendance (Manual)", key="mark_manual"):
        if manual_qr_id:
            success, msg, found_email = st.session_state.data_handler.mark_attendance(manual_qr_id.strip())
            
            if success:
                st.success(f"🎉 {msg}")
                if found_email:
                    st.balloons()
                    st.info(f"**Attendee:** {found_email}")
            else:
                st.warning(f"⚠️ {msg}")
                if found_email:
                    st.info(f"**Email:** {found_email}")
        else:
            st.warning("Please enter a QR code ID")


def show_settings():
    """Display settings page."""
    
    st.title("⚙️ Settings")
    st.markdown("Configure email and application settings.")
    st.markdown("---")
    
    # Email settings
    st.subheader("📧 Email Configuration")
    
    with st.form("email_settings_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            smtp_server = st.text_input(
                "SMTP Server",
                value=st.session_state.email_settings['smtp_server'],
                help="e.g., smtp.gmail.com for Gmail"
            )
            
            smtp_port = st.number_input(
                "SMTP Port",
                value=st.session_state.email_settings['smtp_port'],
                min_value=1,
                max_value=65535,
                help="Usually 587 for TLS, 465 for SSL"
            )
        
        with col2:
            sender_email = st.text_input(
                "Sender Email",
                value=st.session_state.email_settings['sender_email'],
                help="Your email address"
            )
            
            sender_password = st.text_input(
                "Email Password/App Password",
                value=st.session_state.email_settings['sender_password'],
                type="password",
                help="For Gmail, use an App Password"
            )
        
        email_subject = st.text_input(
            "Email Subject",
            value=st.session_state.email_settings['email_subject']
        )
        
        email_body = st.text_area(
            "Email Body Template",
            value=st.session_state.email_settings['email_body_template'],
            height=150
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("💾 Save Settings"):
                st.session_state.email_settings.update({
                    'smtp_server': smtp_server,
                    'smtp_port': int(smtp_port),
                    'sender_email': sender_email,
                    'sender_password': sender_password,
                    'email_subject': email_subject,
                    'email_body_template': email_body
                })
                st.success("Settings saved successfully!")
        
        with col2:
            if st.form_submit_button("🔍 Test Connection"):
                if sender_email and sender_password:
                    with st.spinner("Testing connection..."):
                        success, message = test_smtp_connection(
                            smtp_server,
                            int(smtp_port),
                            sender_email,
                            sender_password
                        )
                        
                        if success:
                            st.success(f"✅ {message}")
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.warning("Please enter email credentials")
    
    st.markdown("---")
    
    # Gmail help section
    with st.expander("📖 Gmail Setup Instructions"):
        st.markdown("""
        ### Setting up Gmail for this application
        
        1. **Enable 2-Factor Authentication** on your Google account
        2. Go to [Google Account Settings](https://myaccount.google.com/)
        3. Navigate to **Security** → **2-Step Verification**
        4. At the bottom, click **App passwords**
        5. Generate a new app password for "Mail"
        6. Use this 16-character password in the settings above
        
        **Important:** Never share your app password!
        """)
    
    st.markdown("---")
    
    # Danger zone
    st.subheader("⚠️ Danger Zone")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All Records", type="secondary"):
            st.warning("Are you sure? This will delete all attendance records!")
            
    with col2:
        confirm = st.checkbox("I understand this action cannot be undone")
        
        if confirm:
            if st.button("⚠️ Confirm Delete All", type="primary"):
                success, message = st.session_state.data_handler.clear_all_records()
                if success:
                    # Also clear QR codes directory
                    for f in os.listdir(QR_CODES_DIR):
                        os.remove(os.path.join(QR_CODES_DIR, f))
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)


def show_records():
    """Display all attendance records."""
    
    st.title("📋 Attendance Records")
    st.markdown("View and export all attendance records.")
    st.markdown("---")
    
    # Get all records
    df = st.session_state.data_handler.get_all_records()
    
    if len(df) > 0:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "Attended", "Not Attended"]
            )
        
        with col2:
            search_email = st.text_input("Search by Email")
        
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                ["Email", "Attendance_Status", "Timestamp"]
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['Attendance_Status'] == status_filter]
        
        if search_email:
            filtered_df = filtered_df[
                filtered_df['Email'].str.contains(search_email, case=False, na=False)
            ]
        
        # Sort
        filtered_df = filtered_df.sort_values(sort_by)
        
        # Display count
        st.write(f"Showing {len(filtered_df)} of {len(df)} records")
        
        # Display table
        display_df = filtered_df[['Email', 'QR_Code_ID', 'Attendance_Status', 'Timestamp']].copy()
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Email": st.column_config.TextColumn("Email", width="medium"),
                "QR_Code_ID": st.column_config.TextColumn("QR Code ID", width="large"),
                "Attendance_Status": st.column_config.TextColumn("Status", width="small"),
                "Timestamp": st.column_config.TextColumn("Timestamp", width="medium")
            }
        )
        
        st.markdown("---")
        
        # Export options
        st.subheader("📥 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export to Excel
            export_buffer = io.BytesIO()
            export_df = filtered_df[['Email', 'QR_Code_ID', 'Attendance_Status', 'Timestamp']]
            export_df.to_excel(export_buffer, index=False, engine='openpyxl')
            export_buffer.seek(0)
            
            st.download_button(
                label="📥 Download as Excel",
                data=export_buffer,
                file_name=f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col2:
            # Export to CSV
            csv_data = filtered_df[['Email', 'QR_Code_ID', 'Attendance_Status', 'Timestamp']].to_csv(index=False)
            
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name=f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No records found. Start by adding email addresses in the Email Management page.")


if __name__ == "__main__":
    main()
