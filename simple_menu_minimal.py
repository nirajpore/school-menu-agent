#!/usr/bin/env python3
"""
Simple School Menu Agent - Minimal working version
"""

import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pdfplumber

def main():
    print("🏫 School Menu Agent - Starting...")
    
    try:
        # Try to extract from PDF
        pdf_path = os.getenv('PDF_PATH', './menu.pdf')
        
        if not os.path.exists(pdf_path):
            print("❌ PDF file not found")
            return
        
        print("✅ PDF found, extracting...")
        
        # Extract text from PDF
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or "" + "\n"
        
        print(f"✅ Extracted {len(text)} characters")
        
        # Simple email test
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        email_to = os.getenv('EMAIL_TO')
        
        if not all([smtp_server, smtp_username, smtp_password, email_to]):
            print("❌ Email configuration missing")
            return
        
        # Create simple email
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%A %d %B %Y')
        
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email_to
        msg['Subject'] = f"School Menu Test - {tomorrow}"
        
        body = f"📋 School Menu Test for {tomorrow}\n\n"
        body += "This is a test email to confirm the system works.\n"
        body += "Menu extraction was successful!"
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print("✅ Test email sent successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()