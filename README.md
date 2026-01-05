# 📋 QR Code Attendance Management System

A comprehensive Streamlit web application for managing event attendance using QR codes and email verification.

## ✨ Features

- **📧 Email Management**
  - Add emails manually or via file upload (CSV, Excel, TXT)
  - Automatically generate unique QR codes for each email
  - Send QR codes via email using SMTP

- **📷 QR Code Scanning**
  - Scan QR codes via webcam
  - Upload QR code images for scanning
  - Manual QR code ID entry option

- **📊 Real-time Dashboard**
  - View total emails sent
  - Track number of attendees vs absentees
  - Monitor attendance rate in real-time

- **📋 Records Management**
  - View all attendance records
  - Filter and search functionality
  - Export to Excel or CSV

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Windows Additional Requirement

For QR code scanning with `pyzbar`, you need to install the Visual C++ Redistributable:

1. Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Install the redistributable
3. Restart your terminal/IDE

Alternatively, you can install `zbar` using conda:
```bash
conda install -c conda-forge zbar
```

### Setup Instructions

1. **Clone or navigate to the project directory:**
   ```bash
   cd attendance_app
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

5. **Open in browser:**
   The app will automatically open at `http://localhost:8501`

## 📁 Project Structure

```
attendance_app/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── data/
│   └── attendance_records.xlsx  # Attendance data (auto-created)
├── qr_codes/                 # Generated QR code images (auto-created)
└── modules/
    ├── __init__.py           # Package initialization
    ├── qr_generator.py       # QR code generation module
    ├── qr_scanner.py         # QR code scanning module
    ├── email_sender.py       # Email sending module
    └── data_handler.py       # Data/Excel handling module
```

## ⚙️ Configuration

### Email Settings (Gmail)

1. **Enable 2-Factor Authentication** on your Google account
2. Go to [Google Account Settings](https://myaccount.google.com/)
3. Navigate to **Security** → **2-Step Verification**
4. At the bottom, click **App passwords**
5. Generate a new app password for "Mail"
6. Use this 16-character password in the app settings

### SMTP Settings for Common Providers

| Provider | SMTP Server | Port |
|----------|-------------|------|
| Gmail | smtp.gmail.com | 587 |
| Outlook | smtp-mail.outlook.com | 587 |
| Yahoo | smtp.mail.yahoo.com | 587 |

## 🚀 Usage Guide

### 1. Configure Email Settings
- Go to **⚙️ Settings** page
- Enter your SMTP server details
- Enter your email and app password
- Click **Test Connection** to verify

### 2. Add Attendees
- Go to **📧 Email Management** page
- Enter emails manually OR upload a file
- Click **Generate & Send Emails** to create QR codes and send them

### 3. Scan Attendance
- Go to **📷 QR Scanner** page
- Use webcam or upload QR code image
- Click **Mark Attendance** to record

### 4. Monitor Dashboard
- Go to **📊 Dashboard** page
- View real-time attendance statistics
- See recent activity

### 5. Export Records
- Go to **📋 Records** page
- Filter and search records
- Download as Excel or CSV

## 📝 File Format for Email Upload

### CSV Format
```csv
email
user1@example.com
user2@example.com
```

### Text File Format
```
user1@example.com
user2@example.com
user3@example.com
```

### Excel Format
- First column should contain email addresses
- Column header should include "email" (case-insensitive)

## 🔧 Troubleshooting

### QR Code Scanning Issues
- Ensure good lighting conditions
- Hold the QR code steady
- Make sure the entire QR code is visible
- Try uploading an image instead of using webcam

### Email Sending Issues
- Verify SMTP settings are correct
- For Gmail, ensure you're using an App Password
- Check if your email provider allows SMTP access
- Verify internet connection

### pyzbar Installation Issues on Windows
If you get an error about missing DLLs:
1. Install Visual C++ Redistributable
2. Or use: `pip install pyzbar[windows]`

## 📄 License

This project is open-source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

Made with ❤️ using Streamlit
